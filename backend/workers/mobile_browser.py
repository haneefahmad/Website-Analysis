import os
import asyncio
from typing import Tuple
from playwright.async_api import async_playwright
from models import HeadlessMobileResult, HeadlessDesktopResult, AuditIssue, Severity

async def scan_headless_devices(
    target_url: str, 
    audit_id: str, 
    screenshots_dir: str
) -> Tuple[HeadlessMobileResult, HeadlessDesktopResult]:
    """
    Spins up Playwright Chromium once and audits BOTH Mobile and Desktop in parallel contexts.
    Captures above-the-fold and full-page screenshots for both form factors,
    measures real browser performance metrics (FCP, load time, DOM interactive),
    and checks for layout breakages / touch target issues.
    """
    mobile_res = HeadlessMobileResult()
    desktop_res = HeadlessDesktopResult()

    audit_screenshots_folder = os.path.join(screenshots_dir, audit_id)
    os.makedirs(audit_screenshots_folder, exist_ok=True)

    mobile_fold_path = os.path.join(audit_screenshots_folder, "mobile_fold.png")
    mobile_full_path = os.path.join(audit_screenshots_folder, "mobile_full.png")
    desktop_fold_path = os.path.join(audit_screenshots_folder, "desktop_fold.png")
    desktop_full_path = os.path.join(audit_screenshots_folder, "desktop_full.png")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Mobile Context (iPhone 14 Pro emulation)
        context_mobile = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1"
        )

        # 2. Desktop Context (Modern 1440x900 viewport)
        context_desktop = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        async def run_mobile_audit():
            page = None
            try:
                page = await context_mobile.new_page()
                await page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(2000)

                mobile_res.rendered_html = await page.content()

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
                mobile_res.local_fcp_ms = perf_data.get("fcp_ms")
                mobile_res.local_load_time_ms = perf_data.get("load_time_ms")
                mobile_res.local_dom_interactive_ms = perf_data.get("dom_interactive_ms")

                await page.screenshot(path=mobile_fold_path, full_page=False)
                mobile_res.fold_screenshot_path = mobile_fold_path

                try:
                    await page.screenshot(path=mobile_full_path, full_page=True, timeout=8000)
                    mobile_res.full_screenshot_path = mobile_full_path
                except Exception:
                    mobile_res.full_screenshot_path = mobile_fold_path

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
                mobile_res.scroll_width = scroll_data.get("docWidth", 390)
                mobile_res.viewport_width = scroll_data.get("winWidth", 390)
                mobile_res.horizontal_scroll_overflow = scroll_data.get("hasOverflow", False)
                mobile_res.overflow_elements = scroll_data.get("badElements", [])

                if mobile_res.horizontal_scroll_overflow:
                    diff = mobile_res.scroll_width - mobile_res.viewport_width
                    mobile_res.issues.append(AuditIssue(
                        category="Mobile UX",
                        item_number=7,
                        title="Mobile Horizontal Scroll Layout Breakage",
                        description=f"Page body ({mobile_res.scroll_width}px) is wider than mobile viewport ({mobile_res.viewport_width}px), causing awkward horizontal side-scrolling and cut-off content by {diff}px.",
                        severity=Severity.CRITICAL,
                        recommendation="Ensure all container widths use max-width: 100% or overflow-x: hidden to avoid horizontal layout breaking.",
                        proof={"viewport_width": mobile_res.viewport_width, "scroll_width": mobile_res.scroll_width, "culprit_elements": mobile_res.overflow_elements}
                    ))

                tap_data = await page.evaluate("""() => {
                    const clickables = document.querySelectorAll('a, button, input[type="submit"], input[type="button"]');
                    let smallTargets = [];
                    clickables.forEach(el => {
                        const rect = el.getBoundingClientRect();
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
                mobile_res.small_tap_targets_count = tap_data.get("count", 0)
                mobile_res.small_tap_target_samples = [f"{t['tag']}: '{t['text']}' ({t['width']}x{t['height']}px)" for t in tap_data.get("samples", [])]

                if mobile_res.small_tap_targets_count > 3:
                    mobile_res.issues.append(AuditIssue(
                        category="Mobile UX",
                        item_number=7,
                        title=f"{mobile_res.small_tap_targets_count} Small Tap Targets Detected on Mobile",
                        description=f"Found {mobile_res.small_tap_targets_count} interactive buttons or links smaller than the 48x48px mobile touch accessibility threshold.",
                        severity=Severity.WARNING,
                        recommendation="Increase button padding and touch target sizes to at least 48x48px to prevent mis-clicks on mobile devices.",
                        proof={"count": mobile_res.small_tap_targets_count, "samples": mobile_res.small_tap_target_samples}
                    ))
            except Exception as e:
                mobile_res.issues.append(AuditIssue(
                    category="Mobile UX",
                    item_number=7,
                    title="Headless Mobile Navigation Failed",
                    description=f"Playwright mobile browser error: {str(e)}",
                    severity=Severity.WARNING,
                    recommendation="Verify target URL stability and SSL certificate.",
                    proof={"error": str(e)}
                ))
            finally:
                if page:
                    await page.close()

        async def run_desktop_audit():
            page = None
            try:
                page = await context_desktop.new_page()
                await page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(2000)

                desktop_res.rendered_html = await page.content()

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
                desktop_res.local_fcp_ms = perf_data.get("fcp_ms")
                desktop_res.local_load_time_ms = perf_data.get("load_time_ms")
                desktop_res.local_dom_interactive_ms = perf_data.get("dom_interactive_ms")

                await page.screenshot(path=desktop_fold_path, full_page=False)
                desktop_res.fold_screenshot_path = desktop_fold_path

                try:
                    await page.screenshot(path=desktop_full_path, full_page=True, timeout=8000)
                    desktop_res.full_screenshot_path = desktop_full_path
                except Exception:
                    desktop_res.full_screenshot_path = desktop_fold_path

                scroll_data = await page.evaluate("""() => {
                    const docWidth = document.documentElement.scrollWidth;
                    const winWidth = window.innerWidth;
                    const hasOverflow = docWidth > winWidth + 5;
                    let badElements = [];
                    if (hasOverflow) {
                        const all = document.querySelectorAll('*');
                        for (let el of all) {
                            const rect = el.getBoundingClientRect();
                            if (rect.right > winWidth + 10) {
                                badElements.push(el.tagName.toLowerCase() + (el.className ? '.' + el.className.split(' ').join('.') : ''));
                                if (badElements.length >= 5) break;
                            }
                        }
                    }
                    return { hasOverflow, docWidth, winWidth, badElements };
                }""")
                desktop_res.scroll_width = scroll_data.get("docWidth", 1440)
                desktop_res.viewport_width = scroll_data.get("winWidth", 1440)
                desktop_res.horizontal_scroll_overflow = scroll_data.get("hasOverflow", False)
                desktop_res.overflow_elements = scroll_data.get("badElements", [])

                if desktop_res.horizontal_scroll_overflow:
                    diff = desktop_res.scroll_width - desktop_res.viewport_width
                    desktop_res.issues.append(AuditIssue(
                        category="Desktop UX",
                        item_number=7,
                        title="Desktop Horizontal Scroll Layout Breakage",
                        description=f"Desktop layout ({desktop_res.scroll_width}px) exceeds desktop viewport ({desktop_res.viewport_width}px) by {diff}px, causing unwanted horizontal scrollbars on desktop screens.",
                        severity=Severity.WARNING,
                        recommendation="Constrain wide layout sections using container classes or max-width: 100vw.",
                        proof={"viewport_width": desktop_res.viewport_width, "scroll_width": desktop_res.scroll_width, "culprit_elements": desktop_res.overflow_elements}
                    ))
            except Exception as e:
                desktop_res.issues.append(AuditIssue(
                    category="Desktop UX",
                    item_number=7,
                    title="Headless Desktop Navigation Failed",
                    description=f"Playwright desktop browser error: {str(e)}",
                    severity=Severity.WARNING,
                    recommendation="Verify target URL stability and SSL certificate.",
                    proof={"error": str(e)}
                ))
            finally:
                if page:
                    await page.close()

        # Run both mobile and desktop scans concurrently
        await asyncio.gather(run_mobile_audit(), run_desktop_audit())
        await context_mobile.close()
        await context_desktop.close()
        await browser.close()

    return mobile_res, desktop_res

async def scan_headless_mobile(target_url: str, audit_id: str, screenshots_dir: str) -> HeadlessMobileResult:
    """Backwards-compatible helper returning only the mobile result."""
    mobile_res, _ = await scan_headless_devices(target_url, audit_id, screenshots_dir)
    return mobile_res

async def scan_headless_desktop(target_url: str, audit_id: str, screenshots_dir: str) -> HeadlessDesktopResult:
    """Backwards-compatible helper returning only the desktop result."""
    _, desktop_res = await scan_headless_devices(target_url, audit_id, screenshots_dir)
    return desktop_res
