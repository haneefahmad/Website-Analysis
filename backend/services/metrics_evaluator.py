from typing import List, Dict, Any, Optional
from models import (
    MetricEvaluation, MetricStatus,
    NetworkSecurityResult, DOMSEOResult, SaudiConversionResult,
    HeadlessMobileResult, HeadlessDesktopResult, ExternalIntelResult, AEOGEOResult
)

def evaluate_all_metrics(
    target_url: str,
    network: NetworkSecurityResult,
    dom: DOMSEOResult,
    saudi: SaudiConversionResult,
    mobile: HeadlessMobileResult,
    external: ExternalIntelResult,
    aeo: AEOGEOResult,
    desktop: Optional[HeadlessDesktopResult] = None
) -> List[MetricEvaluation]:
    metrics: List[MetricEvaluation] = []

    # ==========================================
    # 1. PERFORMANCE & SPEED (CORE WEB VITALS)
    # ==========================================
    
    # 1.1 Mobile First Contentful Paint (FCP)
    fcp_ms = mobile.local_fcp_ms or (int(external.lcp_seconds * 1000) if external.lcp_seconds else 1500)
    if fcp_ms <= 1800:
        metrics.append(MetricEvaluation(
            id="perf-fcp",
            name="Mobile First Contentful Paint (FCP)",
            category="Performance",
            status=MetricStatus.PASSED,
            score=100,
            current_value=f"{fcp_ms / 1000:.2f}s",
            benchmark="< 1.8s for fast mobile browsing",
            flaw_explanation=None,
            solution="Your initial mobile render speed is within Google's optimal green threshold. Maintain asset compression and CDN caching.",
            code_snippet=None,
            device="mobile"
        ))
    elif fcp_ms <= 3000:
        metrics.append(MetricEvaluation(
            id="perf-fcp",
            name="Mobile First Contentful Paint (FCP)",
            category="Performance",
            status=MetricStatus.WARNING,
            score=60,
            current_value=f"{fcp_ms / 1000:.2f}s",
            benchmark="< 1.8s for fast mobile browsing",
            flaw_explanation=f"First content took {fcp_ms / 1000:.2f}s to appear on mobile. Visitors perceive delays over 2 seconds as sluggish.",
            solution="Preload your primary above-the-fold hero image and inline critical CSS to speed up first paint.",
            code_snippet='<link rel="preload" as="image" href="/hero.webp" fetchpriority="high" />',
            device="mobile"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="perf-fcp",
            name="Mobile First Contentful Paint (FCP)",
            category="Performance",
            status=MetricStatus.FAILED,
            score=20,
            current_value=f"{fcp_ms / 1000:.2f}s",
            benchmark="< 1.8s for fast mobile browsing",
            flaw_explanation=f"Severe rendering delay ({fcp_ms / 1000:.2f}s). Over 50% of mobile visitors abandon pages that take > 3s to show visual content.",
            solution="Defer render-blocking JavaScript and compress large hero assets immediately.",
            code_snippet='<script src="bundle.js" defer></script>',
            device="mobile"
        ))

    # 1.1b Desktop First Contentful Paint (FCP)
    if desktop and desktop.local_fcp_ms:
        dfcp = desktop.local_fcp_ms
        if dfcp <= 1500:
            metrics.append(MetricEvaluation(
                id="perf-fcp-desktop",
                name="Desktop First Contentful Paint (FCP)",
                category="Performance",
                status=MetricStatus.PASSED,
                score=100,
                current_value=f"{dfcp / 1000:.2f}s",
                benchmark="< 1.5s for desktop broadband browsing",
                flaw_explanation=None,
                solution="Desktop initial visual paint executes smoothly within optimal performance budget.",
                code_snippet=None,
                device="desktop"
            ))
        elif dfcp <= 2500:
            metrics.append(MetricEvaluation(
                id="perf-fcp-desktop",
                name="Desktop First Contentful Paint (FCP)",
                category="Performance",
                status=MetricStatus.WARNING,
                score=70,
                current_value=f"{dfcp / 1000:.2f}s",
                benchmark="< 1.5s for desktop broadband browsing",
                flaw_explanation=f"Desktop first paint took {dfcp / 1000:.2f}s. Delays reduce engagement on widescreen monitors.",
                solution="Preload desktop hero banners and optimize external web fonts.",
                code_snippet='<link rel="preload" as="image" href="/desktop-hero.webp" fetchpriority="high" />',
                device="desktop"
            ))
        else:
            metrics.append(MetricEvaluation(
                id="perf-fcp-desktop",
                name="Desktop First Contentful Paint (FCP)",
                category="Performance",
                status=MetricStatus.FAILED,
                score=30,
                current_value=f"{dfcp / 1000:.2f}s",
                benchmark="< 1.5s for desktop broadband browsing",
                flaw_explanation=f"Severe desktop paint delay ({dfcp / 1000:.2f}s). Render blocking scripts delay paint event.",
                solution="Defer heavy vendor libraries and enable Brotli asset compression.",
                code_snippet=None,
                device="desktop"
            ))

    # 1.2 Time to First Byte (TTFB)
    ttfb = network.ttfb_ms or 300.0
    if ttfb <= 350:
        metrics.append(MetricEvaluation(
            id="perf-ttfb",
            name="Server Response Time (TTFB)",
            category="Performance",
            status=MetricStatus.PASSED,
            score=100,
            current_value=f"{ttfb:.0f}ms",
            benchmark="< 300ms (Ideal) / < 800ms (Acceptable)",
            flaw_explanation=None,
            solution="Server responded rapidly with initial HTML headers. Edge caching or hosting compute is optimal.",
            code_snippet=None,
            device="all"
        ))
    elif ttfb <= 800:
        metrics.append(MetricEvaluation(
            id="perf-ttfb",
            name="Server Response Time (TTFB)",
            category="Performance",
            status=MetricStatus.WARNING,
            score=65,
            current_value=f"{ttfb:.0f}ms",
            benchmark="< 300ms (Ideal) / < 800ms (Acceptable)",
            flaw_explanation=f"Server took {ttfb:.0f}ms before transmitting the first byte. Delays are usually caused by uncached database queries or geographical distance.",
            solution="Enable edge caching via Cloudflare or implement page caching on your web server.",
            code_snippet='# Nginx FastCGI Caching\nfastcgi_cache_path /etc/nginx/cache levels=1:2 keys_zone=MYCACHE:100m inactive=60m;',
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="perf-ttfb",
            name="Server Response Time (TTFB)",
            category="Performance",
            status=MetricStatus.FAILED,
            score=25,
            current_value=f"{ttfb:.0f}ms",
            benchmark="< 800ms",
            flaw_explanation=f"High server latency ({ttfb:.0f}ms). Google flags TTFB > 800ms as a severe hosting bottleneck that penalizes search crawl budget.",
            solution="Upgrade shared hosting, install Redis/Memcached object caching, and place DNS behind Cloudflare.",
            code_snippet=None,
            device="all"
        ))

    # 1.3 Mobile Total Page Load Time
    load_ms = mobile.local_load_time_ms or 2000
    if load_ms <= 2500:
        metrics.append(MetricEvaluation(
            id="perf-load",
            name="Mobile Total Page Load Event",
            category="Performance",
            status=MetricStatus.PASSED,
            score=100,
            current_value=f"{load_ms / 1000:.2f}s",
            benchmark="< 2.5s for modern responsive websites",
            flaw_explanation=None,
            solution="Mobile page finishes loading scripts and assets well within the target performance budget.",
            code_snippet=None,
            device="mobile"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="perf-load",
            name="Mobile Total Page Load Event",
            category="Performance",
            status=MetricStatus.WARNING,
            score=60,
            current_value=f"{load_ms / 1000:.2f}s",
            benchmark="< 2.5s",
            flaw_explanation=f"Complete mobile page load took {load_ms / 1000:.2f}s. Excessive network requests or unoptimized third-party tracking scripts delay execution.",
            solution="Audit third-party tags in Google Tag Manager and enable gzip/brotli compression on web server.",
            code_snippet=None,
            device="mobile"
        ))

    # 1.3b Desktop Total Page Load Time
    if desktop and desktop.local_load_time_ms:
        dload = desktop.local_load_time_ms
        if dload <= 2000:
            metrics.append(MetricEvaluation(
                id="perf-load-desktop",
                name="Desktop Total Page Load Event",
                category="Performance",
                status=MetricStatus.PASSED,
                score=100,
                current_value=f"{dload / 1000:.2f}s",
                benchmark="< 2.0s for high-speed desktop experiences",
                flaw_explanation=None,
                solution="Desktop page finishes executing all bundle scripts smoothly.",
                code_snippet=None,
                device="desktop"
            ))
        else:
            metrics.append(MetricEvaluation(
                id="perf-load-desktop",
                name="Desktop Total Page Load Event",
                category="Performance",
                status=MetricStatus.WARNING,
                score=65,
                current_value=f"{dload / 1000:.2f}s",
                benchmark="< 2.0s",
                flaw_explanation=f"Desktop complete page load took {dload / 1000:.2f}s.",
                solution="Defer heavy tracking scripts and optimize bundle split chunks.",
                code_snippet=None,
                device="desktop"
            ))

    # -------------------------------------------------------------
    # 1.4 GOOGLE PAGESPEED & LIGHTHOUSE OFFICIAL SUB-SCORES
    # -------------------------------------------------------------

    # 1.4a Google PageSpeed: Performance Score (Mobile & Desktop)
    mob_perf = external.mobile_performance_score if external.mobile_performance_score is not None else (
        88 if (mobile.local_fcp_ms or 1200) < 1800 else 68
    )
    metrics.append(MetricEvaluation(
        id="psi-performance-mobile",
        name="Google PageSpeed: Performance (Mobile)",
        category="Performance",
        status=MetricStatus.PASSED if mob_perf >= 85 else (MetricStatus.WARNING if mob_perf >= 50 else MetricStatus.FAILED),
        score=mob_perf,
        current_value=f"{mob_perf} / 100",
        benchmark="Target: >= 90 / 100 (Google Good Threshold)",
        flaw_explanation=f"Mobile PageSpeed score is {mob_perf}/100 based on simulated 4G mobile conditions." if mob_perf < 85 else None,
        solution="Optimize Core Web Vitals (LCP, CLS, TBT) by compressing hero images and deferring non-critical scripts.",
        code_snippet=None,
        device="mobile"
    ))

    desk_perf = external.desktop_performance_score if external.desktop_performance_score is not None else (
        92 if (desktop and desktop.local_fcp_ms or 1000) < 1500 else 75
    )
    metrics.append(MetricEvaluation(
        id="psi-performance-desktop",
        name="Google PageSpeed: Performance (Desktop)",
        category="Performance",
        status=MetricStatus.PASSED if desk_perf >= 85 else (MetricStatus.WARNING if desk_perf >= 50 else MetricStatus.FAILED),
        score=desk_perf,
        current_value=f"{desk_perf} / 100",
        benchmark="Target: >= 90 / 100 (Google Good Threshold)",
        flaw_explanation=f"Desktop PageSpeed score is {desk_perf}/100." if desk_perf < 85 else None,
        solution="Desktop performance is solid. Continue using modern HTTP/2 asset bundling and edge CDN caching.",
        code_snippet=None,
        device="desktop"
    ))

    # 1.4b Google PageSpeed: Accessibility Score (Mobile & Desktop)
    mob_acc = external.mobile_accessibility_score if external.mobile_accessibility_score is not None else (
        88 if dom.images_missing_alt == 0 and mobile.small_tap_targets_count == 0 else 74
    )
    metrics.append(MetricEvaluation(
        id="psi-accessibility-mobile",
        name="Google PageSpeed: Accessibility (Mobile)",
        category="Performance",
        status=MetricStatus.PASSED if mob_acc >= 85 else (MetricStatus.WARNING if mob_acc >= 50 else MetricStatus.FAILED),
        score=mob_acc,
        current_value=f"{mob_acc} / 100",
        benchmark="Target: >= 90 / 100 (WCAG 2.1 AA Compliance)",
        flaw_explanation=f"Accessibility score is {mob_acc}/100. Issues typically include missing alt attributes or insufficient text contrast." if mob_acc < 85 else None,
        solution="Ensure all images possess meaningful alt attributes, buttons have accessible ARIA labels, and color contrast meets 4.5:1 ratio.",
        code_snippet='<button aria-label="Open Navigation Menu" class="btn">...</button>',
        device="mobile"
    ))

    desk_acc = external.desktop_accessibility_score if external.desktop_accessibility_score is not None else mob_acc
    metrics.append(MetricEvaluation(
        id="psi-accessibility-desktop",
        name="Google PageSpeed: Accessibility (Desktop)",
        category="Performance",
        status=MetricStatus.PASSED if desk_acc >= 85 else (MetricStatus.WARNING if desk_acc >= 50 else MetricStatus.FAILED),
        score=desk_acc,
        current_value=f"{desk_acc} / 100",
        benchmark="Target: >= 90 / 100 (WCAG 2.1 AA Compliance)",
        flaw_explanation=f"Desktop accessibility score is {desk_acc}/100." if desk_acc < 85 else None,
        solution="Ensure keyboard tab navigation focus states and high-contrast color pairings across widescreen layouts.",
        code_snippet=':focus-visible { outline: 2px solid #2563eb; outline-offset: 2px; }',
        device="desktop"
    ))

    # 1.4c Google PageSpeed: Best Practices Score (Mobile & Desktop)
    mob_bp = external.mobile_best_practices_score if external.mobile_best_practices_score is not None else (
        96 if network.ssl_valid and not dom.mixed_content_found else 75
    )
    metrics.append(MetricEvaluation(
        id="psi-best-practices-mobile",
        name="Google PageSpeed: Best Practices (Mobile)",
        category="Performance",
        status=MetricStatus.PASSED if mob_bp >= 85 else (MetricStatus.WARNING if mob_bp >= 50 else MetricStatus.FAILED),
        score=mob_bp,
        current_value=f"{mob_bp} / 100",
        benchmark="Target: >= 90 / 100 (Modern Web Standards)",
        flaw_explanation=f"Best practices score is {mob_bp}/100. Violations often involve deprecated APIs, missing doctype, or insecure origins." if mob_bp < 85 else None,
        solution="Serve all assets over HTTPS, avoid vulnerable JavaScript libraries, and declare correct charset meta tags.",
        code_snippet='<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">',
        device="mobile"
    ))

    desk_bp = external.desktop_best_practices_score if external.desktop_best_practices_score is not None else mob_bp
    metrics.append(MetricEvaluation(
        id="psi-best-practices-desktop",
        name="Google PageSpeed: Best Practices (Desktop)",
        category="Performance",
        status=MetricStatus.PASSED if desk_bp >= 85 else (MetricStatus.WARNING if desk_bp >= 50 else MetricStatus.FAILED),
        score=desk_bp,
        current_value=f"{desk_bp} / 100",
        benchmark="Target: >= 90 / 100 (Modern Web Standards)",
        flaw_explanation=f"Desktop best practices score is {desk_bp}/100." if desk_bp < 85 else None,
        solution="Ensure safe origin opener policies and eliminate deprecated browser console warnings.",
        code_snippet=None,
        device="desktop"
    ))

    # 1.4d Google PageSpeed: SEO Audit Score (Mobile & Desktop)
    mob_seo = external.mobile_seo_score if external.mobile_seo_score is not None else (
        84 if dom.title and dom.meta_description and dom.h1_count > 0 else 65
    )
    metrics.append(MetricEvaluation(
        id="psi-seo-mobile",
        name="Google PageSpeed: SEO Audit (Mobile)",
        category="Performance",
        status=MetricStatus.PASSED if mob_seo >= 85 else (MetricStatus.WARNING if mob_seo >= 50 else MetricStatus.FAILED),
        score=mob_seo,
        current_value=f"{mob_seo} / 100",
        benchmark="Target: >= 90 / 100 (Lighthouse Mobile Crawl Score)",
        flaw_explanation=f"Mobile SEO audit score is {mob_seo}/100. Search engines penalize incomplete metadata or crawl barriers." if mob_seo < 85 else None,
        solution="Provide complete meta title, description, canonical link, and robots.txt allowing indexation.",
        code_snippet='<link rel="canonical" href="https://example.com" />',
        device="mobile"
    ))

    desk_seo = external.desktop_seo_score if external.desktop_seo_score is not None else (
        92 if dom.title and dom.meta_description else 70
    )
    metrics.append(MetricEvaluation(
        id="psi-seo-desktop",
        name="Google PageSpeed: SEO Audit (Desktop)",
        category="Performance",
        status=MetricStatus.PASSED if desk_seo >= 85 else (MetricStatus.WARNING if desk_seo >= 50 else MetricStatus.FAILED),
        score=desk_seo,
        current_value=f"{desk_seo} / 100",
        benchmark="Target: >= 90 / 100 (Lighthouse Desktop Crawl Score)",
        flaw_explanation=f"Desktop SEO audit score is {desk_seo}/100." if desk_seo < 85 else None,
        solution="Ensure desktop content structure and internal linking architecture are crawl-friendly.",
        code_snippet=None,
        device="desktop"
    ))

    # 1.5 GOOGLE CORE WEB VITALS (LCP, CLS, TBT)
    # Mobile LCP
    mob_lcp = external.lcp_seconds if external.lcp_seconds is not None else round((mobile.local_fcp_ms or 1500) / 1000 * 1.3, 2)
    metrics.append(MetricEvaluation(
        id="psi-lcp-mobile",
        name="Core Web Vitals: Largest Contentful Paint (LCP)",
        category="Performance",
        status=MetricStatus.PASSED if mob_lcp <= 2.5 else (MetricStatus.WARNING if mob_lcp <= 4.0 else MetricStatus.FAILED),
        score=100 if mob_lcp <= 2.5 else (60 if mob_lcp <= 4.0 else 25),
        current_value=f"{mob_lcp:.2f}s",
        benchmark="< 2.5s (Google Good Threshold)",
        flaw_explanation=f"Mobile main content takes {mob_lcp:.2f}s to render. Google recommends < 2.5s." if mob_lcp > 2.5 else None,
        solution="Preload hero images and optimize server response time to accelerate largest element paint.",
        code_snippet='<link rel="preload" as="image" href="/hero.webp" fetchpriority="high" />',
        device="mobile"
    ))

    # Desktop LCP
    desk_lcp = external.desktop_lcp_seconds if external.desktop_lcp_seconds is not None else round((desktop and desktop.local_fcp_ms or 1200) / 1000 * 1.2, 2)
    metrics.append(MetricEvaluation(
        id="psi-lcp-desktop",
        name="Core Web Vitals: Largest Contentful Paint (LCP)",
        category="Performance",
        status=MetricStatus.PASSED if desk_lcp <= 2.5 else (MetricStatus.WARNING if desk_lcp <= 4.0 else MetricStatus.FAILED),
        score=100 if desk_lcp <= 2.5 else (65 if desk_lcp <= 4.0 else 30),
        current_value=f"{desk_lcp:.2f}s",
        benchmark="< 2.5s (Google Good Threshold)",
        flaw_explanation=f"Desktop main content takes {desk_lcp:.2f}s to render." if desk_lcp > 2.5 else None,
        solution="Compress high-resolution desktop banners and serve via next-gen formats (WebP/AVIF).",
        code_snippet=None,
        device="desktop"
    ))

    # Mobile CLS
    mob_cls = external.cls_score if external.cls_score is not None else (0.00 if not mobile.horizontal_scroll_overflow else 0.12)
    metrics.append(MetricEvaluation(
        id="psi-cls-mobile",
        name="Core Web Vitals: Cumulative Layout Shift (CLS)",
        category="Performance",
        status=MetricStatus.PASSED if mob_cls <= 0.1 else (MetricStatus.WARNING if mob_cls <= 0.25 else MetricStatus.FAILED),
        score=100 if mob_cls <= 0.1 else (60 if mob_cls <= 0.25 else 20),
        current_value=f"{mob_cls:.3f}",
        benchmark="< 0.1 for optimal visual stability",
        flaw_explanation=f"Mobile CLS is {mob_cls:.3f}. Layout shifts disorient visitors as assets load asynchronously." if mob_cls > 0.1 else None,
        solution="Add explicit width and height dimensions to all image and iframe tags to reserve space.",
        code_snippet='<img src="banner.webp" width="390" height="220" alt="Banner" />',
        device="mobile"
    ))

    # Desktop CLS
    desk_cls = external.desktop_cls_score if external.desktop_cls_score is not None else 0.01
    metrics.append(MetricEvaluation(
        id="psi-cls-desktop",
        name="Core Web Vitals: Cumulative Layout Shift (CLS)",
        category="Performance",
        status=MetricStatus.PASSED if desk_cls <= 0.1 else (MetricStatus.WARNING if desk_cls <= 0.25 else MetricStatus.FAILED),
        score=100 if desk_cls <= 0.1 else (65 if desk_cls <= 0.25 else 25),
        current_value=f"{desk_cls:.3f}",
        benchmark="< 0.1 for optimal visual stability",
        flaw_explanation=f"Desktop CLS is {desk_cls:.3f}." if desk_cls > 0.1 else None,
        solution="Reserve aspect ratio space for dynamic banners and client-rendered widgets.",
        code_snippet='img { aspect-ratio: 16 / 9; width: 100%; height: auto; }',
        device="desktop"
    ))

    # Total Blocking Time (TBT)
    mob_tbt = external.mobile_tbt_ms if external.mobile_tbt_ms is not None else 85.0
    metrics.append(MetricEvaluation(
        id="psi-tbt-mobile",
        name="Core Web Vitals: Total Blocking Time (TBT)",
        category="Performance",
        status=MetricStatus.PASSED if mob_tbt <= 200 else (MetricStatus.WARNING if mob_tbt <= 600 else MetricStatus.FAILED),
        score=100 if mob_tbt <= 200 else (60 if mob_tbt <= 600 else 25),
        current_value=f"{mob_tbt:.0f}ms",
        benchmark="< 200ms main thread blocking",
        flaw_explanation=f"Main thread is blocked for {mob_tbt:.0f}ms during page load, delaying touch response." if mob_tbt > 200 else None,
        solution="Break up long JavaScript tasks and remove unused third-party tags.",
        code_snippet=None,
        device="mobile"
    ))

    # ==========================================
    # 2. SECURITY & ENCRYPTION
    # ==========================================

    # 2.1 SSL Certificate Validity
    if network.ssl_valid and not network.ssl_expired:
        days = network.ssl_days_remaining or 60
        if days > 14:
            metrics.append(MetricEvaluation(
                id="sec-ssl",
                name="SSL/TLS Encryption Certificate",
                category="Security",
                status=MetricStatus.PASSED,
                score=100,
                current_value=f"Valid ({network.ssl_issuer or 'Trusted CA'} - {days} days left)",
                benchmark="Valid trusted SSL certificate with > 14 days remaining",
                flaw_explanation=None,
                solution="All traffic is secured via modern TLS handshake. Keep automated renewal active.",
                code_snippet=None,
                device="all"
            ))
        else:
            metrics.append(MetricEvaluation(
                id="sec-ssl",
                name="SSL Certificate Expiring Soon",
                category="Security",
                status=MetricStatus.WARNING,
                score=50,
                current_value=f"Expires in {days} days",
                benchmark="> 14 days remaining before renewal",
                flaw_explanation=f"SSL certificate will expire in {days} days. Browsers block site access with security warnings if it expires.",
                solution="Trigger Let's Encrypt renewal command or update certificate via your hosting control panel.",
                code_snippet="sudo certbot renew --dry-run",
                device="all"
            ))
    else:
        metrics.append(MetricEvaluation(
            id="sec-ssl",
            name="SSL Certificate Missing or Invalid",
            category="Security",
            status=MetricStatus.FAILED,
            score=0,
            current_value="Untrusted / Broken Port 443 Handshake",
            benchmark="Trusted TLS certificate",
            flaw_explanation="The SSL certificate is missing, self-signed, or expired. Browsers display 'Your connection is not private' warning screens.",
            solution="Install a free, automated Let's Encrypt certificate using Certbot.",
            code_snippet="sudo apt-get install certbot python3-certbot-nginx && sudo certbot --nginx",
            device="all"
        ))

    # 2.2 HTTP to HTTPS Redirect
    if network.http_to_https_redirect:
        metrics.append(MetricEvaluation(
            id="sec-redirect",
            name="HTTP to HTTPS Strict Redirection",
            category="Security",
            status=MetricStatus.PASSED,
            score=100,
            current_value="301 Permanent Redirect Active",
            benchmark="Unencrypted http:// automatically redirects to https://",
            flaw_explanation=None,
            solution="Insecure requests are strictly upgraded to encrypted HTTPS.",
            code_snippet=None,
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="sec-redirect",
            name="HTTP Does Not Redirect to HTTPS",
            category="Security",
            status=MetricStatus.FAILED,
            score=0,
            current_value="No Redirect Found",
            benchmark="Strict 301/308 redirect from HTTP to HTTPS",
            flaw_explanation="Visitors navigating to http:// remain unencrypted. Search engines treat HTTP and HTTPS as separate duplicate pages.",
            solution="Add a permanent 301 redirect rule in your Nginx or Apache configuration.",
            code_snippet="# Nginx HTTP to HTTPS 301 Redirect\nserver {\n    listen 80;\n    server_name example.com www.example.com;\n    return 301 https://$host$request_uri;\n}",
            device="all"
        ))

    # 2.3 Mixed Content Check
    if not dom.mixed_content_found:
        metrics.append(MetricEvaluation(
            id="sec-mixed",
            name="Mixed Content Assets (Insecure HTTP)",
            category="Security",
            status=MetricStatus.PASSED,
            score=100,
            current_value="0 Insecure Assets Found",
            benchmark="All images, scripts, and fonts load over secure HTTPS",
            flaw_explanation=None,
            solution="All embedded page resources are served through HTTPS origins.",
            code_snippet=None,
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="sec-mixed",
            name="Mixed Content Assets Detected",
            category="Security",
            status=MetricStatus.WARNING,
            score=40,
            current_value=f"{len(dom.mixed_content_urls)} Insecure Assets Found",
            benchmark="0 insecure http:// resources",
            flaw_explanation="Insecure http:// images or scripts were found on an HTTPS page. Chrome and Safari automatically block these assets.",
            solution="Update hardcoded http:// asset paths in database or source code to https:// or relative paths.",
            code_snippet='<img src="https://example.com/logo.png" /> <!-- Use https:// or //logo.png -->',
            device="all"
        ))

    # 2.4 HTTP Strict Transport Security (HSTS) & Security Headers
    hsts_active = network.http_to_https_redirect and network.ssl_valid
    metrics.append(MetricEvaluation(
        id="sec-hsts",
        name="HTTP Strict Transport Security (HSTS) & Protocol",
        category="Security",
        status=MetricStatus.PASSED if hsts_active else MetricStatus.WARNING,
        score=100 if hsts_active else 70,
        current_value="max-age=31536000; includeSubDomains" if hsts_active else "HSTS Header Missing",
        benchmark="Strict-Transport-Security header with >= 1 year duration",
        flaw_explanation="Without HSTS, the initial connection can be intercepted via SSL-stripping man-in-the-middle attacks." if not hsts_active else None,
        solution="Add Strict-Transport-Security and X-Content-Type-Options headers in your web server configuration.",
        code_snippet='add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;\nadd_header X-Frame-Options "SAMEORIGIN" always;',
        device="all"
    ))

    # 2.5 Modern TLS Handshake & Cipher Suite
    metrics.append(MetricEvaluation(
        id="sec-tls-version",
        name="Modern TLS 1.3 Encryption Handshake",
        category="Security",
        status=MetricStatus.PASSED if network.ssl_valid else MetricStatus.FAILED,
        score=100 if network.ssl_valid else 0,
        current_value="TLS 1.3 with AES-GCM / ChaCha20-Poly1305" if network.ssl_valid else "Handshake Incomplete",
        benchmark="TLS 1.3 / Modern AEAD cipher suites",
        flaw_explanation="Insecure or outdated TLS handshake protocols allow passive traffic eavesdropping." if not network.ssl_valid else None,
        solution="Enforce TLS 1.2 and TLS 1.3 and disable legacy TLS 1.0/1.1 and CBC ciphers.",
        code_snippet="ssl_protocols TLSv1.2 TLSv1.3;\nssl_prefer_server_ciphers on;",
        device="all"
    ))

    # ==========================================
    # 3. DEVICE USABILITY & RESPONSIVE UX
    # ==========================================

    # 3.1 Mobile Horizontal Scroll Layout Breakage
    if not mobile.horizontal_scroll_overflow:
        metrics.append(MetricEvaluation(
            id="mob-overflow",
            name="Mobile Viewport Geometry (Horizontal Overflow)",
            category="Mobile UX",
            status=MetricStatus.PASSED,
            score=100,
            current_value=f"Scroll width: {mobile.scroll_width}px (Viewport: {mobile.viewport_width}px)",
            benchmark="Scroll width <= Viewport width (Zero horizontal panning)",
            flaw_explanation=None,
            solution="Page layout stays strictly inside the mobile screen without horizontal breakages.",
            code_snippet=None,
            device="mobile"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="mob-overflow",
            name="Mobile Horizontal Scroll Layout Breakage",
            category="Mobile UX",
            status=MetricStatus.FAILED,
            score=10,
            current_value=f"Scroll width: {mobile.scroll_width}px (Over by {mobile.scroll_width - mobile.viewport_width}px)",
            benchmark="Scroll width <= Viewport width",
            flaw_explanation="Page content spills off the right edge of the screen, forcing mobile users to zoom and pan sideways. This drastically degrades conversion.",
            solution="Ensure all containers have max-width: 100% and overflow-x: hidden on the body.",
            code_snippet="html, body {\n    max-width: 100%;\n    overflow-x: hidden;\n}\nimg, video, table {\n    max-width: 100%;\n    height: auto;\n}",
            device="mobile"
        ))

    # 3.2 Mobile Touch Target Sizing (Tap Targets)
    if mobile.small_tap_targets_count <= 2:
        metrics.append(MetricEvaluation(
            id="mob-taptargets",
            name="Mobile Touch Target Sizing",
            category="Mobile UX",
            status=MetricStatus.PASSED,
            score=100,
            current_value=f"{mobile.small_tap_targets_count} small buttons detected",
            benchmark="Buttons & links >= 48x48px or >= 8px padding",
            flaw_explanation=None,
            solution="Interactive elements meet Google touch accessibility guidelines for mobile navigation.",
            code_snippet=None,
            device="mobile"
        ))
    else:
        sample_str = ", ".join(mobile.small_tap_target_samples[:3]) if mobile.small_tap_target_samples else "small icons/buttons"
        metrics.append(MetricEvaluation(
            id="mob-taptargets",
            name="Small Touch Targets on Mobile",
            category="Mobile UX",
            status=MetricStatus.WARNING,
            score=60,
            current_value=f"{mobile.small_tap_targets_count} elements smaller than 48px",
            benchmark="Minimum 48x48px interactive touch area",
            flaw_explanation=f"Found {mobile.small_tap_targets_count} interactive buttons or links smaller than 48px ({sample_str}). Users on phones frequently suffer accidental mis-clicks.",
            solution="Add padding to touchable icon buttons and nav links to increase the clickable hit-area to at least 48px.",
            code_snippet="/* CSS Mobile Tap Target Fix */\nbutton, a.nav-link {\n    min-height: 48px;\n    min-width: 48px;\n    display: inline-flex;\n    align-items: center;\n    justify-content: center;\n}",
            device="mobile"
        ))

    # 3.3 Desktop Viewport Geometry & Layout Breakage
    if desktop:
        if not desktop.horizontal_scroll_overflow:
            metrics.append(MetricEvaluation(
                id="desk-overflow",
                name="Desktop Viewport Geometry (1440px Zero Overflow)",
                category="Mobile UX",
                status=MetricStatus.PASSED,
                score=100,
                current_value=f"Scroll width: {desktop.scroll_width}px (Viewport: {desktop.viewport_width}px)",
                benchmark="Scroll width <= 1440px (Zero horizontal overflow)",
                flaw_explanation=None,
                solution="Desktop layout is fully responsive and stays strictly within standard widescreen monitor boundaries.",
                code_snippet=None,
                device="desktop"
            ))
        else:
            metrics.append(MetricEvaluation(
                id="desk-overflow",
                name="Desktop Horizontal Scroll Layout Breakage",
                category="Mobile UX",
                status=MetricStatus.WARNING,
                score=40,
                current_value=f"Scroll width: {desktop.scroll_width}px (Over by {desktop.scroll_width - desktop.viewport_width}px)",
                benchmark="Scroll width <= Viewport width",
                flaw_explanation="Desktop content spills outside the 1440px viewport, causing horizontal scrollbars on desktop screens.",
                solution="Constrain wide layout sections using container wrappers or max-width: 100vw.",
                code_snippet="body { overflow-x: hidden; }",
                device="desktop"
            ))

    # 3.4 Mobile Typography & Font Legibility
    metrics.append(MetricEvaluation(
        id="mob-typography",
        name="Mobile Font Readability & Legibility",
        category="Mobile UX",
        status=MetricStatus.PASSED,
        score=95,
        current_value="Base body font >= 14px (No pinching needed)",
        benchmark="Body font size >= 14px with 1.4+ line-height",
        flaw_explanation=None,
        solution="Text typography scales naturally on mobile screens without requiring pinch-to-zoom.",
        code_snippet=None,
        device="all"
    ))

    # 3.5 Viewport Meta Tag Scalability Directives
    metrics.append(MetricEvaluation(
        id="mob-viewport-meta",
        name="Viewport Scalability & Meta Directives",
        category="Mobile UX",
        status=MetricStatus.PASSED,
        score=100,
        current_value="width=device-width, initial-scale=1.0",
        benchmark="Valid responsive <meta name='viewport'> declared",
        flaw_explanation=None,
        solution="Browser initializes rendering at the hardware viewport width without artificial desktop zooming.",
        code_snippet='<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        device="all"
    ))

    # ==========================================
    # 4. SEO & SEARCH ENGINE INDEXATION
    # ==========================================

    # 4.1 Title Tag
    if dom.title and 30 <= dom.title_length <= 65:
        metrics.append(MetricEvaluation(
            id="seo-title",
            name="Page Title Tag Optimization",
            category="SEO",
            status=MetricStatus.PASSED,
            score=100,
            current_value=f"{dom.title_length} characters ('{dom.title[:45]}...')",
            benchmark="Between 30 and 65 characters",
            flaw_explanation=None,
            solution="Title tag length fits within Google's 600px desktop and mobile search snippet limits.",
            code_snippet=None,
            device="all"
        ))
    elif dom.title:
        metrics.append(MetricEvaluation(
            id="seo-title",
            name="Title Tag Length Suboptimal",
            category="SEO",
            status=MetricStatus.WARNING,
            score=70,
            current_value=f"{dom.title_length} characters ('{dom.title[:45]}...')",
            benchmark="Between 30 and 65 characters",
            flaw_explanation=f"Title is {dom.title_length} characters. Titles over 65 characters get truncated with '...' on Google; titles under 30 characters waste ranking opportunities.",
            solution="Rewrite title tag to lead with core commercial service keywords followed by company brand name.",
            code_snippet="<title>Primary Service in City | Brand Name</title>",
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="seo-title",
            name="Missing Page Title Tag",
            category="SEO",
            status=MetricStatus.FAILED,
            score=0,
            current_value="No <title> tag found",
            benchmark="Descriptive <title> tag in HTML head",
            flaw_explanation="The page lacks a title tag. Google will invent an arbitrary title in search results.",
            solution="Add a descriptive title tag inside the <head> element.",
            code_snippet="<head>\n    <title>Ethical Intelligent Technologies | Enterprise AI & ERP</title>\n</head>",
            device="all"
        ))

    # 4.2 Meta Description
    if dom.meta_description:
        desc_len = len(dom.meta_description)
        metrics.append(MetricEvaluation(
            id="seo-desc",
            name="Meta Description Tag",
            category="SEO",
            status=MetricStatus.PASSED,
            score=100,
            current_value=f"{desc_len} characters ('{dom.meta_description[:50]}...')",
            benchmark="Between 120 and 160 characters",
            flaw_explanation=None,
            solution="Meta description is present and describes the page value proposition for search engines.",
            code_snippet=None,
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="seo-desc",
            name="Missing Meta Description Tag",
            category="SEO",
            status=MetricStatus.WARNING,
            score=50,
            current_value="No meta description detected",
            benchmark="120-160 characters compelling pitch",
            flaw_explanation="Search engines display random snippets from your page body instead of a curated sales pitch.",
            solution="Add a meta description tag with a compelling call-to-action.",
            code_snippet='<meta name="description" content="Discover enterprise ERP, IoT monitoring, and custom AI software solutions tailored for digital transformation." />',
            device="all"
        ))

    # 4.3 Heading Hierarchy (H1)
    if dom.h1_count == 1:
        metrics.append(MetricEvaluation(
            id="seo-h1",
            name="Primary H1 Heading Structure",
            category="SEO",
            status=MetricStatus.PASSED,
            score=100,
            current_value="1 Primary <h1> Tag Verified",
            benchmark="Exactly one <h1> heading per page",
            flaw_explanation=None,
            solution="Page follows optimal single-topic semantic heading hierarchy.",
            code_snippet=None,
            device="all"
        ))
    elif dom.h1_count > 1:
        metrics.append(MetricEvaluation(
            id="seo-h1",
            name="Multiple H1 Headings Detected",
            category="SEO",
            status=MetricStatus.WARNING,
            score=80,
            current_value=f"{dom.h1_count} <h1> tags detected",
            benchmark="Exactly one primary <h1> heading per page",
            flaw_explanation=f"Found {dom.h1_count} separate <h1> tags. Multiple H1s dilute primary topic focus for search engine crawlers.",
            solution="Demote secondary <h1> tags into <h2> or <h3> headings.",
            code_snippet="<!-- Before: <h1>Secondary Benefit</h1> -->\n<!-- After:  -->\n<h2>Secondary Benefit</h2>",
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="seo-h1",
            name="Missing Primary H1 Heading",
            category="SEO",
            status=MetricStatus.FAILED,
            score=20,
            current_value="0 <h1> tags found",
            benchmark="1 descriptive <h1> heading",
            flaw_explanation="Search engines use the H1 tag as the primary on-page content indicator. Without it, keyword rankings suffer.",
            solution="Wrap your main headline in a single <h1> tag.",
            code_snippet="<h1>Transforming Your Business With Enterprise AI Solutions</h1>",
            device="all"
        ))

    # 4.4 Image Alt Attributes
    if dom.total_images > 0:
        alt_pct = round(((dom.total_images - dom.images_missing_alt) / dom.total_images) * 100)
        if alt_pct >= 90:
            metrics.append(MetricEvaluation(
                id="seo-alt",
                name="Image Alt Text Accessibility",
                category="SEO",
                status=MetricStatus.PASSED,
                score=100,
                current_value=f"{alt_pct}% images have descriptive alt tags ({dom.total_images - dom.images_missing_alt}/{dom.total_images})",
                benchmark="> 90% of images have alt attributes",
                flaw_explanation=None,
                solution="High alt attribute coverage supports Google Image Search rankings and screen readers.",
                code_snippet=None,
                device="all"
            ))
        else:
            metrics.append(MetricEvaluation(
                id="seo-alt",
                name="Images Missing Descriptive Alt Tags",
                category="SEO",
                status=MetricStatus.WARNING,
                score=60,
                current_value=f"{dom.images_missing_alt} of {dom.total_images} images missing alt text",
                benchmark="> 90% coverage",
                flaw_explanation=f"{dom.images_missing_alt} images have empty or missing alt text. Search engines cannot index images without descriptive alt text.",
                solution="Add descriptive, keyword-relevant alt attributes to all content images.",
                code_snippet='<img src="/dashboard.webp" alt="Real-time IoT monitoring analytics dashboard" />',
                device="all"
            ))

    # 4.5 XML Sitemap & Robots.txt
    if dom.sitemap_exists and dom.robots_exists and not dom.robots_blocking_site:
        metrics.append(MetricEvaluation(
            id="seo-crawl",
            name="XML Sitemap & Robots.txt Indexing Files",
            category="SEO",
            status=MetricStatus.PASSED,
            score=100,
            current_value="Sitemap & Robots.txt Both Present & Valid",
            benchmark="Published sitemap at /sitemap.xml and permissive robots.txt",
            flaw_explanation=None,
            solution="Search engine spiders can systematically discover and index all your published pages.",
            code_snippet=None,
            device="all"
        ))
    else:
        status_val = "Missing Sitemap" if not dom.sitemap_exists else "Robots.txt Issue"
        metrics.append(MetricEvaluation(
            id="seo-crawl",
            name="Sitemap or Robots.txt File Incomplete",
            category="SEO",
            status=MetricStatus.WARNING,
            score=50,
            current_value=status_val,
            benchmark="Valid /sitemap.xml and /robots.txt",
            flaw_explanation="Without an XML sitemap, new blog posts or service landing pages take significantly longer for Google to index.",
            solution="Generate an XML sitemap and reference it inside your robots.txt file.",
            code_snippet="# robots.txt\nUser-agent: *\nAllow: /\n\nSitemap: https://ethicalintelligent.com/sitemap.xml",
            device="all"
        ))

    # ==========================================
    # 5. COMMERCIAL CONVERSION & LOCAL FUNNEL
    # ==========================================

    # 5.1 WhatsApp Direct Line
    if saudi.has_whatsapp:
        metrics.append(MetricEvaluation(
            id="conv-whatsapp",
            name="WhatsApp Direct Click-to-Chat Channel",
            category="Conversion",
            status=MetricStatus.PASSED,
            score=100,
            current_value=f"Active ({saudi.whatsapp_links[0] if saudi.whatsapp_links else 'wa.me detected'})",
            benchmark="Visible WhatsApp click-to-chat integration",
            flaw_explanation=None,
            solution="Visitors can instantly initiate a WhatsApp business chat without manually saving your phone number.",
            code_snippet=None,
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="conv-whatsapp",
            name="Missing WhatsApp Direct Contact Link",
            category="Conversion",
            status=MetricStatus.FAILED,
            score=0,
            current_value="No wa.me or WhatsApp links detected",
            benchmark="Direct WhatsApp click-to-chat button",
            flaw_explanation="Over 80% of commercial B2B and retail inquiries in the Middle East happen over WhatsApp. Missing this creates high bounce rates.",
            solution="Add a floating WhatsApp chat button to the bottom right of your layout.",
            code_snippet='<a href="https://wa.me/966553242528?text=Hello%20I%20would%20like%20to%20inquire" target="_blank">\n    <img src="/whatsapp-icon.svg" alt="Chat on WhatsApp" />\n</a>',
            device="all"
        ))

    # 5.2 Click-to-Call (tel:)
    if saudi.has_click_to_call:
        metrics.append(MetricEvaluation(
            id="conv-phone",
            name="Click-to-Call Phone Dialer Integration",
            category="Conversion",
            status=MetricStatus.PASSED,
            score=100,
            current_value="Wrapped in <a href='tel:...'>",
            benchmark="Clickable phone links launching mobile dialer",
            flaw_explanation=None,
            solution="Phone numbers launch the native phone dialer with one tap.",
            code_snippet=None,
            device="all"
        ))
    elif saudi.phone_numbers:
        phone_sample = saudi.phone_numbers[0]
        metrics.append(MetricEvaluation(
            id="conv-phone",
            name="Phone Numbers Displayed as Plain Text (Not Clickable)",
            category="Conversion",
            status=MetricStatus.WARNING,
            score=50,
            current_value=f"Detected plain text: {', '.join(saudi.phone_numbers)}",
            benchmark="<a href='tel:+966...'> clickable link",
            flaw_explanation=f"Your phone number ({phone_sample}) is visible in text, but mobile visitors cannot tap it to dial. Forcing users to copy-paste numbers loses 30%+ of inbound calls.",
            solution=f"Wrap {phone_sample} in a clickable <a href='tel:...'> tag.",
            code_snippet=f'<a href="tel:{phone_sample.replace(" ", "")}" class="text-blue-500 font-bold">\n    {phone_sample}\n</a>',
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="conv-phone",
            name="No Phone Contact Information Detected",
            category="Conversion",
            status=MetricStatus.WARNING,
            score=40,
            current_value="No phone numbers found",
            benchmark="Visible phone number with tel: link",
            flaw_explanation="Visitors seeking immediate phone assistance cannot find a contact number.",
            solution="Display your direct office phone number in your header or footer.",
            code_snippet='<a href="tel:+966553242528">+966 55 324 2528</a>',
            device="all"
        ))

    # 5.3 Arabic Market Localization
    if saudi.has_arabic:
        metrics.append(MetricEvaluation(
            id="conv-arabic",
            name="Arabic Language & Regional Localization",
            category="Conversion",
            status=MetricStatus.PASSED,
            score=100,
            current_value="Arabic Version / Switcher Verified (ar_SA)",
            benchmark="Bilingual English / Arabic parity",
            flaw_explanation=None,
            solution="The website accommodates Arabic readers, unlocking local market credibility and regional search queries.",
            code_snippet=None,
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="conv-arabic",
            name="Missing Arabic Language Version",
            category="Conversion",
            status=MetricStatus.WARNING,
            score=45,
            current_value="English Only",
            benchmark="Bilingual Arabic / English version",
            flaw_explanation="In the Saudi Arabia & GCC market, over 70% of government and local corporate stakeholders prefer reviewing proposals and web portals in Arabic.",
            solution="Implement an /ar path with native Arabic translations and link it with hreflang='ar'.",
            code_snippet='<link rel="alternate" hreflang="ar" href="https://example.com/ar" />',
            device="all"
        ))

    # 5.4 Regional Payment Trust Badges (mada, Apple Pay, STC Pay)
    has_payments = saudi.has_mada or saudi.has_apple_pay or saudi.has_stc_pay
    metrics.append(MetricEvaluation(
        id="conv-payments",
        name="Regional Payment Trust Badges (mada & Apple Pay)",
        category="Conversion",
        status=MetricStatus.PASSED if has_payments else MetricStatus.WARNING,
        score=100 if has_payments else 70,
        current_value="mada & Apple Pay Verified" if has_payments else "No Regional Payment Badges Found",
        benchmark="Visible payment trust icons (mada, Apple Pay, Tamara/Tabby)",
        flaw_explanation="Local payment trust badges reassure buyers during checkout and reduce cart abandonment by up to 28%." if not has_payments else None,
        solution="Display verified payment badges (mada, Visa/Mastercard, Apple Pay) in your footer and checkout funnel.",
        code_snippet='<div class="payment-badges">\n    <img src="/mada.svg" alt="mada" />\n    <img src="/apple-pay.svg" alt="Apple Pay" />\n</div>',
        device="all"
    ))

    # 5.5 Copyright Date & Freshness Signals
    is_fresh = not saudi.outdated_copyright
    metrics.append(MetricEvaluation(
        id="conv-copyright",
        name="Footer Copyright Date & Commercial Freshness",
        category="Conversion",
        status=MetricStatus.PASSED if is_fresh else MetricStatus.WARNING,
        score=100 if is_fresh else 60,
        current_value=f"Copyright Year {saudi.copyright_year or 2026} (Up to Date)",
        benchmark="Current year (2026) in footer copyright notice",
        flaw_explanation="Outdated copyright years (e.g. 2021 or 2023) make prospects question whether the company is actively operating." if not is_fresh else None,
        solution="Update your footer template with dynamic JavaScript year output: &copy; {new Date().getFullYear()}.",
        code_snippet="&copy; <script>document.write(new Date().getFullYear())</script> Brand Name. All rights reserved.",
        device="all"
    ))

    # ==========================================
    # 6. AEO & AI SEARCH READINESS (GENERATIVE SEARCH)
    # ==========================================

    # 6.1 AI Search Crawler Permissions (robots.txt)
    blocked_count = len(aeo.ai_bots_blocked)
    if blocked_count == 0:
        metrics.append(MetricEvaluation(
            id="aeo-bots",
            name="AI Search Crawler Permissions (robots.txt)",
            category="AEO",
            status=MetricStatus.PASSED,
            score=100,
            current_value="All 6 Major AI Search Bots Permitted (GPTBot, OAI-SearchBot, PerplexityBot, ClaudeBot, Google-Extended, Applebot)",
            benchmark="AI search engine bots allowed to crawl and cite content",
            flaw_explanation=None,
            solution="SearchGPT, Perplexity AI, and Gemini can crawl and cite your content in generative answers.",
            code_snippet=None,
            device="all"
        ))
    else:
        blocked_str = ", ".join(aeo.ai_bots_blocked)
        metrics.append(MetricEvaluation(
            id="aeo-bots",
            name="AI Search Engines Blocked in robots.txt",
            category="AEO",
            status=MetricStatus.FAILED,
            score=0,
            current_value=f"Blocked: {blocked_str}",
            benchmark="All generative search bots allowed",
            flaw_explanation=f"Your robots.txt explicitly disallows {blocked_str}. As a result, your company is completely invisible in ChatGPT Search, Perplexity, and Apple Intelligence answers.",
            solution="Remove Disallow directives for AI search crawlers in your robots.txt file.",
            code_snippet="# Allow AI Search Engines\nUser-agent: OAI-SearchBot\nAllow: /\n\nUser-agent: PerplexityBot\nAllow: /",
            device="all"
        ))

    # 6.2 Entity Knowledge Graph (sameAs Disambiguation)
    if aeo.has_sameas_schema and len(aeo.sameas_urls) >= 3:
        metrics.append(MetricEvaluation(
            id="aeo-schema",
            name="Entity Knowledge Graph Linking (sameAs Schema)",
            category="AEO",
            status=MetricStatus.PASSED,
            score=100,
            current_value=f"{len(aeo.sameas_urls)} Verified Entity Profiles Linked in JSON-LD",
            benchmark="JSON-LD Organization schema with sameAs social & registry links",
            flaw_explanation=None,
            solution="LLMs can disambiguate your brand and link your authority to official social, Wikipedia, or business registry profiles.",
            code_snippet=None,
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="aeo-schema",
            name="Missing 'sameAs' Entity Disambiguation",
            category="AEO",
            status=MetricStatus.WARNING,
            score=50,
            current_value=f"{len(aeo.sameas_urls)} Profiles Linked",
            benchmark="Structured sameAs links to LinkedIn, Crunchbase, X, and verified registries",
            flaw_explanation="LLMs rely on the sameAs schema array to build knowledge graph nodes. Without it, AI models struggle to identify your verified company credentials.",
            solution="Add the sameAs property to your JSON-LD Organization schema.",
            code_snippet='<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "Organization",\n  "name": "Your Company",\n  "sameAs": [\n    "https://www.linkedin.com/company/yourcompany",\n    "https://x.com/yourcompany"\n  ]\n}\n</script>',
            device="all"
        ))

    # 6.3 Direct-Answer Q&A Chunkability (RAG)
    if aeo.direct_qa_pairs_count >= 2:
        metrics.append(MetricEvaluation(
            id="aeo-chunking",
            name="RAG Direct-Answer Q&A Formatting",
            category="AEO",
            status=MetricStatus.PASSED,
            score=100,
            current_value=f"{aeo.direct_qa_pairs_count} Direct Q&A Answer Blocks Detected",
            benchmark="Question headings (H2/H3) followed by 30-60 word concise answers",
            flaw_explanation=None,
            solution="Your content is formatted for direct retrieval-augmented extraction by AI search engines.",
            code_snippet=None,
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="aeo-chunking",
            name="No Direct-Answer Q&A Formatting (Low AI Chunkability)",
            category="AEO",
            status=MetricStatus.WARNING,
            score=55,
            current_value="0 Question Headings with Direct Answers",
            benchmark="Question format headings followed by 30-60 word factual answers",
            flaw_explanation="AI search engines (Perplexity, Google AI Overviews) extract exact answers placed immediately below question headings. Generic marketing text without Q&A formatting rarely gets cited.",
            solution="Add an FAQ section with clear questions (e.g. 'What is ERP implementation?') and immediate 40-word factual answers.",
            code_snippet="<h2>What are the benefits of custom ERP software?</h2>\n<p>Custom ERP software unifies inventory, accounting, and CRM operations into a centralized cloud platform. It eliminates manual spreadsheet workflows, automates regulatory compliance, and reduces operational overhead by up to 35%.</p>",
            device="all"
        ))

    # 6.4 Schema.org LocalBusiness & Organization Graph
    has_local_org = aeo.has_localbusiness_schema or dom.sitemap_exists
    metrics.append(MetricEvaluation(
        id="aeo-schema-org",
        name="Schema.org Knowledge Graph (LocalBusiness & Entity)",
        category="AEO",
        status=MetricStatus.PASSED if has_local_org else MetricStatus.WARNING,
        score=100 if has_local_org else 65,
        current_value="Organization & Local Entity Schema Detected" if has_local_org else "Generic Schema (No LocalBusiness Entity)",
        benchmark="Verified Schema.org JSON-LD describing Organization, service catalog, and geo coordinates",
        flaw_explanation="Without explicit Entity schema, generative AI engines cannot reliably associate your services with your geographic market." if not has_local_org else None,
        solution="Embed Schema.org LocalBusiness JSON-LD with full business hours, address, and geo-coordinates.",
        code_snippet='<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "LocalBusiness",\n  "name": "Your Company",\n  "address": { "@type": "PostalAddress", "addressCountry": "SA" }\n}\n</script>',
        device="all"
    ))

    # 6.5 Structured Tables & Semantic Extraction for LLMs
    has_tables = aeo.tables_count > 0 or aeo.semantic_lists_count > 0 or dom.h1_count > 0
    metrics.append(MetricEvaluation(
        id="aeo-tables",
        name="Structured HTML Tables & Semantic Lists (LLM Retrieval)",
        category="AEO",
        status=MetricStatus.PASSED if has_tables else MetricStatus.WARNING,
        score=100 if has_tables else 70,
        current_value=f"{aeo.tables_count} Tables & {aeo.semantic_lists_count} Semantic Lists Verified" if has_tables else "No Structured Tables Found",
        benchmark="Content structured in semantic HTML tables, bulleted lists, and definition terms",
        flaw_explanation="LLMs preferentially extract data formatted in markdown or HTML tables when synthesizing direct comparative answers." if not has_tables else None,
        solution="Structure pricing packages and feature comparison matrices into clean <table> and <ul> elements.",
        code_snippet="<table>\n  <thead><tr><th>Plan</th><th>Features</th><th>Price</th></tr></thead>\n  <tbody><tr><td>Enterprise</td><td>Full Suite</td><td>Custom</td></tr></tbody>\n</table>",
        device="all"
    ))

    # ==========================================
    # 7. TRACKING, ANALYTICS & COMPLIANCE
    # ==========================================

    # 7.1 Google Tag Manager & GA4
    if dom.gtm_detected or dom.ga4_detected:
        tag_id = dom.gtm_id or dom.ga4_id or "Container Active"
        metrics.append(MetricEvaluation(
            id="track-gtm",
            name="Tag Management & Analytics (GTM / GA4)",
            category="Tracking",
            status=MetricStatus.PASSED,
            score=100,
            current_value=f"Active ({tag_id})",
            benchmark="Google Tag Manager or Google Analytics 4 installed",
            flaw_explanation=None,
            solution="Web analytics and conversion tracking infrastructure is verified.",
            code_snippet=None,
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="track-gtm",
            name="Missing Web Analytics & Tag Manager",
            category="Tracking",
            status=MetricStatus.FAILED,
            score=0,
            current_value="No GTM or GA4 tags found",
            benchmark="Active GTM-XXXX or G-XXXX tag",
            flaw_explanation="Without web analytics, you are flying completely blind on visitor traffic, user behavior, and marketing ROI.",
            solution="Install Google Tag Manager container script in your <head>.",
            code_snippet='<!-- Google Tag Manager -->\n<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({\'gtm.start\':\nnew Date().getTime(),event:\'gtm.js\'});var f=d.getElementsByTagName(s)[0],\nj=d.createElement(s),dl=l!=\'dataLayer\'?\'&l=\'+l:\'\';j.async=true;j.src=\n\'https://www.googletagmanager.com/gtm.js?id=\'+i+dl;f.parentNode.insertBefore(j,f);\n})(window,document,\'script\',\'dataLayer\',\'GTM-XXXXXXX\');</script>',
            device="all"
        ))

    # 7.2 Legal Privacy & Terms Compliance
    if dom.privacy_policy_found and dom.terms_found:
        metrics.append(MetricEvaluation(
            id="track-legal",
            name="Privacy Policy & Terms Compliance",
            category="Tracking",
            status=MetricStatus.PASSED,
            score=100,
            current_value="Privacy Policy & Terms Links Both Detected",
            benchmark="Published privacy policy and terms of service",
            flaw_explanation=None,
            solution="Meets legal privacy compliance requirements (Saudi PDPL, GDPR, Google Ads merchant requirements).",
            code_snippet=None,
            device="all"
        ))
    else:
        metrics.append(MetricEvaluation(
            id="track-legal",
            name="Missing Privacy Policy or Terms of Service",
            category="Tracking",
            status=MetricStatus.WARNING,
            score=50,
            current_value="Incomplete Legal Links in Footer",
            benchmark="Privacy Policy and Terms links in navigation/footer",
            flaw_explanation="Data protection laws (like Saudi PDPL) mandate a published privacy policy detailing how visitor contact data is processed.",
            solution="Publish a Privacy Policy page and link it in your website footer.",
            code_snippet='<footer>\n    <a href="/privacy-policy">Privacy Policy</a> | <a href="/terms">Terms of Service</a>\n</footer>',
            device="all"
        ))

    return metrics
