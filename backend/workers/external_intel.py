from typing import Optional
from urllib.parse import quote_plus
import httpx
from models import ExternalIntelResult, AuditIssue, Severity

async def scan_external_intel(
    target_url: str, 
    pagespeed_api_key: Optional[str] = None, 
    google_places_api_key: Optional[str] = None, 
    business_name: Optional[str] = None
) -> ExternalIntelResult:
    result = ExternalIntelResult()

    # 1. Google PageSpeed Insights API (Mobile Strategy)
    try:
        pagespeed_endpoint = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={quote_plus(target_url)}&strategy=mobile"
        if pagespeed_api_key:
            pagespeed_endpoint += f"&key={pagespeed_api_key}"

        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.get(pagespeed_endpoint)
            if resp.status_code == 200:
                data = resp.json()
                lighthouse = data.get("lighthouseResult", {})
                categories = lighthouse.get("categories", {})
                perf = categories.get("performance", {})
                
                # Overall Performance Score (0-100)
                if "score" in perf and perf["score"] is not None:
                    result.mobile_performance_score = int(perf["score"] * 100)

                # Core Web Vitals Audits
                audits = lighthouse.get("audits", {})
                
                # LCP (Largest Contentful Paint)
                lcp_audit = audits.get("largest-contentful-paint", {})
                if "numericValue" in lcp_audit:
                    result.lcp_seconds = round(lcp_audit["numericValue"] / 1000, 2)
                    if result.lcp_seconds > 4.0:
                        result.issues.append(AuditIssue(
                            category="Performance",
                            item_number=8,
                            title="Poor Mobile Largest Contentful Paint (LCP)",
                            description=f"Main content takes {result.lcp_seconds}s to render on mobile. Google classifies anything > 4.0s as Poor (Target: < 2.5s).",
                            severity=Severity.CRITICAL,
                            recommendation="Optimize hero images, defer non-critical JavaScript, and eliminate render-blocking resources.",
                            proof={"lcp_seconds": result.lcp_seconds}
                        ))
                    elif result.lcp_seconds > 2.5:
                        result.issues.append(AuditIssue(
                            category="Performance",
                            item_number=8,
                            title="LCP Needs Improvement",
                            description=f"Mobile LCP is {result.lcp_seconds}s (Target: < 2.5s).",
                            severity=Severity.WARNING,
                            recommendation="Compress above-the-fold media and enable preloading on primary hero assets.",
                            proof={"lcp_seconds": result.lcp_seconds}
                        ))

                # CLS (Cumulative Layout Shift)
                cls_audit = audits.get("cumulative-layout-shift", {})
                if "numericValue" in cls_audit:
                    result.cls_score = round(cls_audit["numericValue"], 3)
                    if result.cls_score > 0.25:
                        result.issues.append(AuditIssue(
                            category="Performance",
                            item_number=8,
                            title="High Cumulative Layout Shift (CLS)",
                            description=f"CLS score is {result.cls_score} (Poor threshold > 0.25). Elements jump around as the page loads, frustrating visitors.",
                            severity=Severity.WARNING,
                            recommendation="Add explicit width and height attributes to all images, banners, and iframes.",
                            proof={"cls_score": result.cls_score}
                        ))

                # Image Optimization Opportunities
                modern_img = audits.get("modern-image-formats", {})
                if "numericValue" in modern_img and modern_img["numericValue"] > 300000:
                    savings_mb = round(modern_img["numericValue"] / (1024 * 1024), 2)
                    result.image_savings_mb = savings_mb
                    result.issues.append(AuditIssue(
                        category="Performance",
                        item_number=9,
                        title=f"Unoptimized Images Wasting {savings_mb} MB Bandwidth",
                        description=f"Serving modern image formats (WebP/AVIF) instead of legacy JPEG/PNG would save approximately {savings_mb} MB on mobile loads.",
                        severity=Severity.WARNING,
                        recommendation="Convert uploaded PNG/JPEG images into compressed WebP or AVIF formats.",
                        proof={"savings_mb": savings_mb}
                    ))
            elif resp.status_code == 429:
                # Quota exceeded on Google anonymous IP pool
                result.mobile_performance_score = None
    except Exception:
        pass

    # 2. Google Places API (Google Business Profile & Reviews)
    if google_places_api_key and business_name:
        try:
            places_url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={quote_plus(business_name)}&inputtype=textquery&fields=place_id,name,rating,user_ratings_total,business_status&key={google_places_api_key}"
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(places_url)
                if resp.status_code == 200:
                    pdata = resp.json()
                    candidates = pdata.get("candidates", [])
                    if candidates:
                        cand = candidates[0]
                        result.gbp_claimed = True
                        result.gbp_rating = cand.get("rating")
                        result.gbp_reviews_count = cand.get("user_ratings_total")

                        if result.gbp_rating and result.gbp_rating < 4.0:
                            result.issues.append(AuditIssue(
                                category="Reputation",
                                item_number=50,
                                title=f"Low Google Review Rating ({result.gbp_rating} / 5.0)",
                                description=f"Business has an average rating of {result.gbp_rating} across {result.gbp_reviews_count or 0} reviews on Google.",
                                severity=Severity.WARNING,
                                recommendation="Implement a post-service automated review request system to generate positive 5-star ratings.",
                                proof={"rating": result.gbp_rating, "reviews_count": result.gbp_reviews_count}
                            ))
                    else:
                        result.gbp_claimed = False
                        result.issues.append(AuditIssue(
                            category="Reputation",
                            item_number=49,
                            title="Unclaimed or Missing Google Business Profile",
                            description="Could not find a claimed Google Business Profile matching the business name in local search.",
                            severity=Severity.CRITICAL,
                            recommendation="Claim and optimize your Google Business Profile to capture local Google Maps and 'near me' searches.",
                            proof={"found": False}
                        ))
        except Exception:
            pass

    return result
