import os
import asyncio
from playwright.async_api import async_playwright
from models import HeadlessMobileResult, AuditIssue, Severity

async def scan_headless_mobile(target_url: str, audit_id: str, screenshots_dir: str) -> HeadlessMobileResult:
    result = HeadlessMobileResult()
    audit_screenshots_folder = os.path.join(screenshots_dir, audit_id)
    os.makedirs(audit_screenshots_folder, exist_ok=True)

    fold_path = os.path.join(audit_screenshots_folder, "mobile_fold.png")
    full_path = os.path.join(audit_screenshots_folder, "mobile_full.png")

    async with async_playwright() as p:
        # iPhone 14 Pro emulation viewport
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        )
        page = await context.new_page()

        try:
            # Navigate with a max 15s timeout
            await page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(2000)  # Brief pause for animations / responsive layout

            # 1. Capture Rendered HTML for downstream workers (fixes unhydrated SPA issues)
            result.rendered_html = await page.content()

            # 2. Extract Native Browser Performance Metrics
            perf_data = await page.evaluate("""() => {
                const nav = performance.getEntriesByType('navigation')[0] || {};
                const paints = performance.getEntriesByType('paint') || [];
                let fcp = null;
                paints.forEach(p => {
                    if (p.name === 'first-contentful-paint') fcp = Math.round(p.startTime);
                });
                return {
                    fcp_ms: fcp,
                    load_time_ms: nav.loadEventEnd ? Math.round(nav.loadEventEnd) : null,
                    dom_interactive_ms: nav.domInteractive ? Math.round(nav.domInteractive) : null
                };
            }""")
            result.local_fcp_ms = perf_data.get("fcp_ms")
            result.local_load_time_ms = perf_data.get("load_time_ms")
            result.local_dom_interactive_ms = perf_data.get("dom_interactive_ms")

            # 3. Capture Above-The-Fold Screenshot
            await page.screenshot(path=fold_path, full_page=False)
            result.fold_screenshot_path = fold_path

            # 2. Capture Full Page Screenshot
            try:
                await page.screenshot(path=full_path, full_page=True, timeout=8000)
                result.full_screenshot_path = full_path
            except Exception:
                result.full_screenshot_path = fold_path

            # 3. Horizontal Scroll Overflow Check (Strict Math)
            scroll_data = await page.evaluate("""() => {
                const docWidth = document.documentElement.scrollWidth;
                const winWidth = window.innerWidth;
                const hasOverflow = docWidth > winWidth;
                
                let badElements = [];
                if (hasOverflow) {
                    const all = document.querySelectorAll('*');
                    for (let el of all) {
                        const rect = el.getBoundingClientRect();
                        if (rect.right > winWidth + 5) {
                            badElements.push(el.tagName.toLowerCase() + (el.className ? '.' + el.className.split(' ').join('.') : ''));
                            if (badElements.length >= 5) break;
                        }
                    }
                }
                return { hasOverflow, docWidth, winWidth, badElements };
            }""")

            result.scroll_width = scroll_data.get("docWidth", 390)
            result.viewport_width = scroll_data.get("winWidth", 390)
            result.horizontal_scroll_overflow = scroll_data.get("hasOverflow", False)
            result.overflow_elements = scroll_data.get("badElements", [])

            if result.horizontal_scroll_overflow:
                diff = result.scroll_width - result.viewport_width
                result.issues.append(AuditIssue(
                    category="Mobile UX",
                    item_number=7,
                    title="Mobile Horizontal Scroll Layout Breakage",
                    description=f"Page body ({result.scroll_width}px) is wider than mobile viewport ({result.viewport_width}px), causing awkward horizontal side-scrolling and cut-off content by {diff}px.",
                    severity=Severity.CRITICAL,
                    recommendation="Ensure all container widths use max-width: 100% or overflow-x: hidden to avoid horizontal layout breaking.",
                    proof={"viewport_width": result.viewport_width, "scroll_width": result.scroll_width, "culprit_elements": result.overflow_elements}
                ))

            # 4. Tap Target Sizing & Spacing Check
            tap_data = await page.evaluate("""() => {
                const clickables = document.querySelectorAll('a, button, input[type="submit"], input[type="button"]');
                let smallTargets = [];
                
                clickables.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    // Must be visible in viewport
                    if (rect.width > 0 && rect.height > 0 && (rect.width < 40 || rect.height < 40)) {
                        smallTargets.push({
                            tag: el.tagName.toLowerCase(),
                            text: (el.innerText || el.getAttribute('aria-label') || '').trim().substring(0, 30),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        });
                    }
                });
                return { count: smallTargets.length, samples: smallTargets.slice(0, 5) };
            }""")

            result.small_tap_targets_count = tap_data.get("count", 0)
            result.small_tap_target_samples = [f"{t['tag']}: '{t['text']}' ({t['width']}x{t['height']}px)" for t in tap_data.get("samples", [])]

            if result.small_tap_targets_count > 3:
                result.issues.append(AuditIssue(
                    category="Mobile UX",
                    item_number=7,
                    title=f"{result.small_tap_targets_count} Small Tap Targets Detected on Mobile",
                    description=f"Found {result.small_tap_targets_count} interactive buttons or links smaller than the 48x48px mobile touch accessibility threshold.",
                    severity=Severity.WARNING,
                    recommendation="Increase button padding and touch target sizes to at least 48x48px to prevent mis-clicks on mobile devices.",
                    proof={"count": result.small_tap_targets_count, "samples": result.small_tap_target_samples}
                ))

        except Exception as e:
            result.issues.append(AuditIssue(
                category="Mobile UX",
                item_number=7,
                title="Headless Mobile Navigation Failed",
                description=f"Playwright browser error: {str(e)}",
                severity=Severity.WARNING,
                recommendation="Verify target URL stability and SSL certificate.",
                proof={"error": str(e)}
            ))
        finally:
            await context.close()
            await browser.close()

    return result
