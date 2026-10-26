import re
from urllib.parse import urlparse, urljoin
import httpx
from bs4 import BeautifulSoup
from models import DOMSEOResult, AuditIssue, Severity

async def scan_dom_and_seo(target_url: str, html_content: str = None, rendered_html: str = "") -> DOMSEOResult:
    result = DOMSEOResult()
    parsed_target = urlparse(target_url)
    base_url = f"{parsed_target.scheme}://{parsed_target.netloc}"

    if rendered_html:
        html_content = f"{html_content or ''}\n{rendered_html}"

    # Fetch HTML if not already provided
    if not html_content:
        async with httpx.AsyncClient(timeout=10.0, verify=False, follow_redirects=True) as client:
            try:
                resp = await client.get(
                    target_url, 
                    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                )
                html_content = resp.text
            except Exception as e:
                result.issues.append(AuditIssue(
                    category="SEO",
                    item_number=38,
                    title="Could not fetch HTML for DOM Analysis",
                    description=f"Error retrieving page source: {str(e)}",
                    severity=Severity.CRITICAL,
                    recommendation="Ensure target URL is publicly accessible."
                ))
                return result

    soup = BeautifulSoup(html_content, "lxml")

    # 1. Title Tag
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        result.title = title_tag.string.strip()
        result.title_length = len(result.title)
        if result.title_length < 25 or result.title_length > 65:
            result.issues.append(AuditIssue(
                category="SEO",
                item_number=38,
                title="Title Tag Length Unoptimized",
                description=f"Title tag is {result.title_length} characters (Recommended: 30–60 characters for clean Google search snippets).",
                severity=Severity.WARNING,
                recommendation="Adjust title tag to be between 30 and 60 characters with core service keywords and brand name.",
                proof={"title": result.title, "length": result.title_length}
            ))
    else:
        result.issues.append(AuditIssue(
            category="SEO",
            item_number=38,
            title="Missing Title Tag",
            description="Page does not have a <title> tag in the HTML head.",
            severity=Severity.CRITICAL,
            recommendation="Add a descriptive <title> tag to specify the page topic for search engines.",
            proof={"title": None}
        ))

    # 2. Meta Description
    meta_desc = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    if meta_desc and meta_desc.get("content"):
        result.meta_description = meta_desc["content"].strip()
    else:
        result.issues.append(AuditIssue(
            category="SEO",
            item_number=39,
            title="Missing Meta Description",
            description="Page lacks a meta description tag.",
            severity=Severity.WARNING,
            recommendation="Add an engaging 120-160 character meta description summarizing your service value proposition.",
            proof={"meta_description": None}
        ))

    # 3. H1 Headings Hierarchy
    h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all("h1") if h1.get_text(strip=True)]
    result.h1_count = len(h1_tags)
    result.h1_tags = h1_tags
    if result.h1_count == 0:
        result.issues.append(AuditIssue(
            category="SEO",
            item_number=40,
            title="Missing H1 Heading",
            description="The page has no <h1> heading tag, weakening semantic topic clarity for Google.",
            severity=Severity.WARNING,
            recommendation="Include exactly one primary <h1> tag containing your primary service keyword.",
            proof={"h1_count": 0}
        ))
    elif result.h1_count > 1:
        result.issues.append(AuditIssue(
            category="SEO",
            item_number=40,
            title="Multiple H1 Headings Detected",
            description=f"The page contains {result.h1_count} <h1> headings. Best practice is to have a single primary <h1> per page.",
            severity=Severity.INFO,
            recommendation="Consolidate secondary <h1> tags into <h2> or <h3> headings.",
            proof={"h1_count": result.h1_count, "h1_samples": h1_tags[:3]}
        ))

    # 4. Images and Alt Attributes
    images = soup.find_all("img")
    result.total_images = len(images)
    missing_alt = [img for img in images if not img.get("alt") or not img["alt"].strip()]
    result.images_missing_alt = len(missing_alt)
    if result.total_images > 0 and result.images_missing_alt > 0:
        pct = round((result.images_missing_alt / result.total_images) * 100, 1)
        if pct > 20:
            result.issues.append(AuditIssue(
                category="SEO",
                item_number=41,
                title=f"{result.images_missing_alt} Images Missing Alt Text ({pct}%)",
                description=f"Out of {result.total_images} images found on the page, {result.images_missing_alt} are missing descriptive alt attributes.",
                severity=Severity.WARNING if pct > 50 else Severity.INFO,
                recommendation="Add descriptive alt tags to images to improve image search ranking and accessibility.",
                proof={"total_images": result.total_images, "missing_alt_count": result.images_missing_alt, "percentage": pct}
            ))

    # 5. Canonical Tag
    canonical = soup.find("link", rel=re.compile(r"^canonical$", re.I))
    if canonical and canonical.get("href"):
        result.canonical_url = canonical["href"].strip()
        result.canonical_valid = True
    else:
        result.issues.append(AuditIssue(
            category="SEO",
            item_number=45,
            title="Missing Canonical Tag",
            description="The page does not specify a canonical URL tag (<link rel='canonical'>).",
            severity=Severity.INFO,
            recommendation="Add a canonical tag to prevent duplicate content indexing across different URL parameters.",
            proof={"canonical": None}
        ))

    # 6. Mixed Content Check (if HTTPS target)
    if target_url.startswith("https://"):
        insecure_assets = []
        for tag, attr in [("img", "src"), ("script", "src"), ("link", "href"), ("iframe", "src")]:
            for el in soup.find_all(tag):
                val = el.get(attr, "")
                if val.startswith("http://"):
                    insecure_assets.append(val)
        if insecure_assets:
            result.mixed_content_found = True
            result.mixed_content_urls = insecure_assets[:10]
            result.issues.append(AuditIssue(
                category="Security",
                item_number=5,
                title="Mixed Content Detected (Insecure HTTP Assets)",
                description=f"Found {len(insecure_assets)} asset(s) loading over insecure http:// on an HTTPS page. Modern browsers block these assets.",
                severity=Severity.WARNING,
                recommendation="Update asset URLs to use https:// or relative paths to prevent browser security warnings.",
                proof={"sample_insecure_urls": insecure_assets[:5]}
            ))

    # 7. Tracking Pixels & Analytics (GA4, GTM, Meta, TikTok, Snap)
    # Search entire HTML (including <noscript>, <iframe>, data attributes, inline JS)
    full_html = html_content or ""
    scripts_text = " ".join([s.get_text() for s in soup.find_all("script")])
    script_srcs = " ".join([s.get("src", "") for s in soup.find_all("script") if s.get("src")])
    search_corpus = f"{full_html} {scripts_text} {script_srcs}"

    ga4_match = re.search(r"\b(G-[A-Z0-9]{8,14})\b", search_corpus)
    if ga4_match:
        result.ga4_detected = True
        result.ga4_id = ga4_match.group(1)

    gtm_match = re.search(r"\b(GTM-[A-Z0-9]{6,12})\b", search_corpus, re.I)
    if gtm_match or "googletagmanager.com" in search_corpus:
        result.gtm_detected = True
        result.gtm_id = gtm_match.group(1) if gtm_match else "Detected via Tag Manager Container"

    if not result.ga4_detected and not result.gtm_detected:
        result.issues.append(AuditIssue(
            category="Tracking",
            item_number=67,
            title="No Google Analytics 4 (GA4) or GTM Detected",
            description="No Google Analytics 4 tag or Google Tag Manager container was found in the page code.",
            severity=Severity.CRITICAL,
            recommendation="Install Google Analytics 4 via GTM immediately to measure traffic, user behavior, and conversions.",
            proof={"ga4": False, "gtm": False}
        ))

    if "fbq(" in scripts_text or "connect.facebook.net" in script_srcs:
        result.meta_pixel_detected = True
    if "snaptr(" in scripts_text or "sc-static.net/scevent.min.js" in script_srcs:
        result.snap_pixel_detected = True
    if "ttq." in scripts_text or "analytics.tiktok.com" in script_srcs:
        result.tiktok_pixel_detected = True

    # 8. Legal Compliance Pages
    links = soup.find_all("a", href=True)
    for a in links:
        href_lower = a["href"].lower()
        text_lower = a.get_text().lower()
        if any(w in href_lower or w in text_lower for w in ["privacy", "خصوصي"]):
            result.privacy_policy_found = True
        if any(w in href_lower or w in text_lower for w in ["terms", "conditions", "شروط"]):
            result.terms_found = True

    if not result.privacy_policy_found:
        result.issues.append(AuditIssue(
            category="Compliance",
            item_number=69,
            title="Missing Privacy Policy Link",
            description="No link to a Privacy Policy page was detected in the navigation or footer.",
            severity=Severity.WARNING,
            recommendation="Add a clear Privacy Policy link in the footer to comply with local privacy regulations (Saudi PDPL).",
            proof={"privacy_policy": False}
        ))

    # 9. Asynchronous Sitemap & Robots.txt Probes
    async with httpx.AsyncClient(timeout=6.0, verify=False) as client:
        try:
            sitemap_url = urljoin(base_url, "/sitemap.xml")
            resp_sm = await client.get(sitemap_url)
            if resp_sm.status_code == 200 and ("xml" in resp_sm.headers.get("content-type", "").lower() or "<urlset" in resp_sm.text):
                result.sitemap_exists = True
            else:
                result.sitemap_exists = False
                result.issues.append(AuditIssue(
                    category="SEO",
                    item_number=42,
                    title="Missing or Inaccessible XML Sitemap",
                    description=f"HTTP GET /sitemap.xml returned status {resp_sm.status_code}.",
                    severity=Severity.WARNING,
                    recommendation="Generate and publish an XML sitemap at /sitemap.xml and submit it to search engines.",
                    proof={"url": sitemap_url, "status_code": resp_sm.status_code}
                ))
        except Exception:
            result.sitemap_exists = False

        try:
            robots_url = urljoin(base_url, "/robots.txt")
            resp_rb = await client.get(robots_url)
            if resp_rb.status_code == 200:
                result.robots_exists = True
                # Check for accidental total disallow
                if re.search(r"User-agent:\s*\*\s*\nDisallow:\s*/\s*$", resp_rb.text, re.MULTILINE):
                    result.robots_blocking_site = True
                    result.issues.append(AuditIssue(
                        category="SEO",
                        item_number=43,
                        title="Robots.txt is Disallowing All Search Engines",
                        description="Robots.txt contains 'Disallow: /' for all User-agents, actively de-indexing the entire site from Google.",
                        severity=Severity.CRITICAL,
                        recommendation="Remove the universal 'Disallow: /' directive in robots.txt immediately.",
                        proof={"robots_txt": resp_rb.text[:300]}
                    ))
            else:
                result.robots_exists = False
        except Exception:
            result.robots_exists = False

    return result
