import time
import socket
import ssl
from urllib.parse import urlparse
from datetime import datetime, timezone
import httpx
from models import NetworkSecurityResult, AuditIssue, Severity

async def scan_network_and_security(target_url: str) -> NetworkSecurityResult:
    result = NetworkSecurityResult()
    parsed = urlparse(target_url)
    hostname = parsed.hostname or target_url
    scheme = parsed.scheme or "https"

    # 1. Direct TLS Socket Handshake (SSL Validity & Expiry)
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=7.0) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                result.ssl_valid = True
                
                # Extract issuer
                issuer_dict = dict(x[0] for x in cert.get('issuer', []))
                result.ssl_issuer = issuer_dict.get('organizationName') or issuer_dict.get('commonName', 'Unknown CA')
                
                # Expiry date parsing: format e.g. "May 15 12:00:00 2026 GMT"
                not_after_str = cert.get('notAfter')
                if not_after_str:
                    not_after = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    days_remaining = (not_after - now).days
                    result.ssl_days_remaining = days_remaining
                    
                    if days_remaining < 0:
                        result.ssl_expired = True
                        result.issues.append(AuditIssue(
                            category="Security",
                            item_number=3,
                            title="SSL Certificate Expired",
                            description=f"The SSL certificate expired {abs(days_remaining)} days ago on {not_after_str}.",
                            severity=Severity.CRITICAL,
                            recommendation="Renew the SSL certificate immediately to prevent browser security blockades.",
                            proof={"expired": True, "expiry_date": not_after_str}
                        ))
                    elif days_remaining < 14:
                        result.issues.append(AuditIssue(
                            category="Security",
                            item_number=3,
                            title="SSL Certificate Expiring Soon",
                            description=f"SSL certificate will expire in {days_remaining} days ({not_after_str}).",
                            severity=Severity.WARNING,
                            recommendation="Configure auto-renewal or install a new certificate to avoid sudden site downtime.",
                            proof={"days_remaining": days_remaining, "expiry_date": not_after_str}
                        ))
    except (socket.gaierror, socket.timeout, ssl.SSLError, ConnectionRefusedError, OSError) as e:
        result.ssl_valid = False
        result.issues.append(AuditIssue(
            category="Security",
            item_number=2,
            title="SSL Certificate Invalid or Missing",
            description=f"Direct TLS handshake failed on port 443: {str(e)}",
            severity=Severity.CRITICAL,
            recommendation="Install a trusted SSL certificate (e.g. Let's Encrypt / Cloudflare) to ensure all traffic is encrypted.",
            proof={"error": str(e)}
        ))

    # 2. HTTP to HTTPS Redirection Probe
    async with httpx.AsyncClient(timeout=8.0, verify=False) as client:
        try:
            http_url = f"http://{hostname}/"
            resp_http = await client.get(http_url, follow_redirects=False)
            location = resp_http.headers.get("location", "")
            if resp_http.status_code in (301, 302, 307, 308) and location.startswith("https://"):
                result.http_to_https_redirect = True
            else:
                result.http_to_https_redirect = False
                result.issues.append(AuditIssue(
                    category="Security",
                    item_number=4,
                    title="Insecure HTTP Does Not Redirect to HTTPS",
                    description="Visiting the unencrypted http:// version of the site does not force an immediate permanent redirect to https://.",
                    severity=Severity.WARNING,
                    recommendation="Add a 301 permanent redirect rule from HTTP to HTTPS on your web server or CDN.",
                    proof={"status_code": resp_http.status_code, "location_header": location}
                ))
        except Exception as e:
            result.http_to_https_redirect = False

    # 3. Target HTTPS Reachability, Status Code & TTFB Measurement
    async with httpx.AsyncClient(timeout=10.0, verify=False, follow_redirects=True) as client:
        try:
            full_url = f"https://{hostname}/" if not target_url.startswith("http") else target_url
            start_time = time.perf_counter()
            resp = await client.get(full_url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
            ttfb_seconds = time.perf_counter() - start_time
            result.ttfb_ms = round(ttfb_seconds * 1000, 2)
            result.status_code = resp.status_code
            result.is_live = (resp.status_code == 200)

            # Server & CDN Headers
            result.server_header = resp.headers.get("server")
            if "cf-ray" in resp.headers:
                result.cdn_detected = "Cloudflare"
            elif "x-amz-cf-id" in resp.headers or "cloudfront" in resp.headers.get("via", "").lower():
                result.cdn_detected = "AWS CloudFront"
            elif "fastly" in resp.headers.get("via", "").lower():
                result.cdn_detected = "Fastly"

            # Check TTFB Thresholds
            if result.ttfb_ms < 300:
                result.ttfb_rating = "Good"
            elif result.ttfb_ms <= 800:
                result.ttfb_rating = "Needs Improvement"
            else:
                result.ttfb_rating = "Poor"
                result.issues.append(AuditIssue(
                    category="Performance",
                    item_number=12,
                    title="Slow Server Response Time (High TTFB)",
                    description=f"Server took {result.ttfb_ms}ms to deliver the first byte of HTML. Google recommends < 800ms (ideal < 300ms).",
                    severity=Severity.WARNING,
                    recommendation="Enable server-level page caching, upgrade hosting compute, or configure Cloudflare edge caching.",
                    proof={"ttfb_ms": result.ttfb_ms, "rating": result.ttfb_rating}
                ))

            # Status code evaluation
            if resp.status_code != 200:
                result.issues.append(AuditIssue(
                    category="Technical",
                    item_number=1,
                    title=f"Site Returned Non-200 Status Code ({resp.status_code})",
                    description=f"Target URL returned HTTP status {resp.status_code}.",
                    severity=Severity.CRITICAL,
                    recommendation="Investigate server routing, error logs, or firewall restrictions to ensure 200 OK responses.",
                    proof={"status_code": resp.status_code}
                ))

        except httpx.TimeoutException:
            result.is_live = False
            result.issues.append(AuditIssue(
                category="Technical",
                item_number=1,
                title="Connection Timeout (Server Down or Unresponsive)",
                description="The server failed to respond within 10 seconds.",
                severity=Severity.CRITICAL,
                recommendation="Check DNS settings and verify hosting server health.",
                proof={"timeout": True}
            ))
        except Exception as e:
            result.is_live = False
            result.issues.append(AuditIssue(
                category="Technical",
                item_number=1,
                title="Site Failed to Load",
                description=f"Connection error: {str(e)}",
                severity=Severity.CRITICAL,
                recommendation="Verify domain resolution and server status.",
                proof={"error": str(e)}
            ))

    return result
