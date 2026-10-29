import asyncio
from typing import Optional
from urllib.parse import quote_plus
import httpx
from models import ExternalIntelResult, AuditIssue, Severity

async def scan_external_intel(
    target_url: str, 
    pagespeed_api_key: Optional[str] = None
) -> ExternalIntelResult:
    """
    Worker 5: External Intelligence & Core Web Vitals
    Queries Google PageSpeed Insights REST API for Mobile & Desktop Lighthouse scores:
    Performance, Accessibility, Best Practices, and SEO.
    Falls back gracefully if key is omitted or rate-limited.
    """
    result = ExternalIntelResult()

    # Google PageSpeed Insights API (Mobile & Desktop Strategies in Parallel)
    async def fetch_pagespeed(strategy: str):
        endpoint = (
            f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={quote_plus(target_url)}"
            f"&strategy={strategy}"
            f"&category=performance&category=accessibility&category=best-practices&category=seo"
        )
        if pagespeed_api_key:
            endpoint += f"&key={pagespeed_api_key}"
        try:
            async with httpx.AsyncClient(timeout=35.0) as client:
                resp = await client.get(endpoint)
                if resp.status_code == 200:
                    return resp.json()
        except Exception:
            return None
        return None

    try:
        mobile_data, desktop_data = await asyncio.gather(
            fetch_pagespeed("mobile"),
            fetch_pagespeed("desktop")
        )

        # Process Mobile PSI
        if mobile_data:
            lighthouse = mobile_data.get("lighthouseResult", {})
            categories = lighthouse.get("categories", {})
            
            perf = categories.get("performance", {})
            if "score" in perf and perf["score"] is not None:
                result.mobile_performance_score = int(perf["score"] * 100)

            acc = categories.get("accessibility", {})
            if "score" in acc and acc["score"] is not None:
                result.mobile_accessibility_score = int(acc["score"] * 100)

            bp = categories.get("best-practices", {})
            if "score" in bp and bp["score"] is not None:
                result.mobile_best_practices_score = int(bp["score"] * 100)

            seo = categories.get("seo", {})
            if "score" in seo and seo["score"] is not None:
                result.mobile_seo_score = int(seo["score"] * 100)

            audits = lighthouse.get("audits", {})
            
            fcp_audit = audits.get("first-contentful-paint", {})
            if "numericValue" in fcp_audit:
                result.mobile_fcp_seconds = round(fcp_audit["numericValue"] / 1000, 2)

            si_audit = audits.get("speed-index", {})
            if "numericValue" in si_audit:
                result.mobile_speed_index_seconds = round(si_audit["numericValue"] / 1000, 2)

            tbt_audit = audits.get("total-blocking-time", {})
            if "numericValue" in tbt_audit:
                result.mobile_tbt_ms = round(tbt_audit["numericValue"], 1)

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
                        proof={"lcp_seconds": result.lcp_seconds, "device": "mobile"}
                    ))
                elif result.lcp_seconds > 2.5:
                    result.issues.append(AuditIssue(
                        category="Performance",
                        item_number=8,
                        title="Mobile LCP Needs Improvement",
                        description=f"Mobile LCP is {result.lcp_seconds}s (Target: < 2.5s).",
                        severity=Severity.WARNING,
                        recommendation="Compress above-the-fold media and enable preloading on primary hero assets.",
                        proof={"lcp_seconds": result.lcp_seconds, "device": "mobile"}
                    ))

            cls_audit = audits.get("cumulative-layout-shift", {})
            if "numericValue" in cls_audit:
                result.cls_score = round(cls_audit["numericValue"], 3)
                if result.cls_score > 0.25:
                    result.issues.append(AuditIssue(
                        category="Performance",
                        item_number=8,
                        title="High Mobile Cumulative Layout Shift (CLS)",
                        description=f"Mobile CLS score is {result.cls_score} (Poor threshold > 0.25). Elements jump around as the page loads, frustrating mobile visitors.",
                        severity=Severity.WARNING,
                        recommendation="Add explicit width and height attributes to all images, banners, and iframes.",
                        proof={"cls_score": result.cls_score, "device": "mobile"}
                    ))

            inp_audit = audits.get("interaction-to-next-paint", {})
            if "numericValue" in inp_audit:
                result.inp_ms = round(inp_audit["numericValue"], 1)

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

        # Process Desktop PSI
        if desktop_data:
            dlighthouse = desktop_data.get("lighthouseResult", {})
            dcategories = dlighthouse.get("categories", {})
            
            dperf = dcategories.get("performance", {})
            if "score" in dperf and dperf["score"] is not None:
                result.desktop_performance_score = int(dperf["score"] * 100)

            dacc = dcategories.get("accessibility", {})
            if "score" in dacc and dacc["score"] is not None:
                result.desktop_accessibility_score = int(dacc["score"] * 100)

            dbp = dcategories.get("best-practices", {})
            if "score" in dbp and dbp["score"] is not None:
                result.desktop_best_practices_score = int(dbp["score"] * 100)

            dseo = dcategories.get("seo", {})
            if "score" in dseo and dseo["score"] is not None:
                result.desktop_seo_score = int(dseo["score"] * 100)

            daudits = dlighthouse.get("audits", {})

            dfcp = daudits.get("first-contentful-paint", {})
            if "numericValue" in dfcp:
                result.desktop_fcp_seconds = round(dfcp["numericValue"] / 1000, 2)

            dsi = daudits.get("speed-index", {})
            if "numericValue" in dsi:
                result.desktop_speed_index_seconds = round(dsi["numericValue"] / 1000, 2)

            dtbt = daudits.get("total-blocking-time", {})
            if "numericValue" in dtbt:
                result.desktop_tbt_ms = round(dtbt["numericValue"], 1)

            dlcp = daudits.get("largest-contentful-paint", {})
            if "numericValue" in dlcp:
                result.desktop_lcp_seconds = round(dlcp["numericValue"] / 1000, 2)
                if result.desktop_lcp_seconds > 4.0:
                    result.issues.append(AuditIssue(
                        category="Performance",
                        item_number=8,
                        title="Poor Desktop Largest Contentful Paint (LCP)",
                        description=f"Main content takes {result.desktop_lcp_seconds}s to render on desktop screens.",
                        severity=Severity.WARNING,
                        recommendation="Optimize desktop hero media and inline critical CSS.",
                        proof={"desktop_lcp_seconds": result.desktop_lcp_seconds, "device": "desktop"}
                    ))

            dcls = daudits.get("cumulative-layout-shift", {})
            if "numericValue" in dcls:
                result.desktop_cls_score = round(dcls["numericValue"], 3)

            dinp = daudits.get("interaction-to-next-paint", {})
            if "numericValue" in dinp:
                result.desktop_inp_ms = round(dinp["numericValue"], 1)

    except Exception:
        pass

    return result
