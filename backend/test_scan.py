import asyncio
import json
from workers.network_scanner import scan_network_and_security
from workers.dom_seo_scanner import scan_dom_and_seo
from workers.saudi_scanner import scan_saudi_conversion
from workers.mobile_browser import scan_headless_devices, scan_headless_mobile
from workers.aeo_scanner import scan_aeo_and_geo
from services.scoring_engine import calculate_audit_scores
from services.ai_pitch_engine import generate_ai_pitch

async def main():
    target = "https://example.com"
    print(f"Testing local audit pipeline on {target}...")

    # Run network & security
    print("Running Worker 1 (Network & Security)...")
    net = await scan_network_and_security(target)
    print(f"  Live: {net.is_live}, Status: {net.status_code}, SSL: {net.ssl_valid}, Days Left: {net.ssl_days_remaining}, TTFB: {net.ttfb_ms}ms")

    # Run DOM & SEO
    print("Running Worker 2 (DOM & SEO)...")
    dom = await scan_dom_and_seo(target)
    print(f"  Title: '{dom.title}', H1s: {dom.h1_count}, Sitemap: {dom.sitemap_exists}, Robots: {dom.robots_exists}")

    # Run Saudi Conversion
    print("Running Worker 3 (Saudi & GCC Conversion)...")
    saudi = await scan_saudi_conversion(target, "<html><body>Example Domain</body></html>")
    print(f"  WhatsApp: {saudi.has_whatsapp}, Arabic: {saudi.has_arabic}, mada: {saudi.has_mada}")

    # Run AEO / GEO
    print("Running Worker 6 (AEO & GEO)...")
    aeo = await scan_aeo_and_geo(target, "<html><body>Example Domain</body></html>")
    print(f"  AI Bots Checked: {len(aeo.ai_bots_permissions)}, Blocked: {aeo.ai_bots_blocked}, Schema: {aeo.has_localbusiness_schema}")

    # Run Dual Headless Browsers (Mobile & Desktop)
    print("Running Worker 4 & 5 (Playwright Mobile & Desktop Headless)...")
    mobile, desktop = await scan_headless_devices(target, "test-audit-123", "./screenshots")
    print(f"  Mobile Overflow: {mobile.horizontal_scroll_overflow}, Scroll Width: {mobile.scroll_width}px, Fold: {mobile.fold_screenshot_path}")
    print(f"  Desktop Overflow: {desktop.horizontal_scroll_overflow}, Scroll Width: {desktop.scroll_width}px, Fold: {desktop.fold_screenshot_path}")

    # Aggregate Scoring
    all_issues = net.issues + dom.issues + saudi.issues + mobile.issues + desktop.issues + aeo.issues
    scores = calculate_audit_scores(all_issues)
    print(f"\nFinal Overall Score: {scores['overall_score']} / 100")
    print(f"Mobile Overall Score: {scores['mobile_overall_score']} / 100")
    print(f"Desktop Overall Score: {scores['desktop_overall_score']} / 100")
    print(f"Critical Issues: {scores['critical_count']}, Warnings: {scores['warning_count']}, Info: {scores['info_count']}")

    # Pitch Generation
    pitch = await generate_ai_pitch(target, all_issues)
    print("\nGenerated Arabic WhatsApp Outreach:")
    print(pitch.whatsapp_script_arabic)

if __name__ == "__main__":
    asyncio.run(main())
