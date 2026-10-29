import os
import sys
from PIL import Image, ImageDraw, ImageFont

def build_professional_pdf(output_path: str):
    # Standard A4 Portrait at 300 DPI: 2480 x 3508
    WIDTH = 2480
    HEIGHT = 3508
    
    # macOS TrueType fonts
    font_path_helvetica = '/System/Library/Fonts/Helvetica.ttc'
    font_path_menlo = '/System/Library/Fonts/Menlo.ttc'
    
    # Font scales
    f_hero = ImageFont.truetype(font_path_helvetica, 44, index=1)       # Bold
    f_h1 = ImageFont.truetype(font_path_helvetica, 32, index=1)         # Bold
    f_h2 = ImageFont.truetype(font_path_helvetica, 24, index=1)         # Bold
    f_h3 = ImageFont.truetype(font_path_helvetica, 20, index=1)         # Bold
    f_body = ImageFont.truetype(font_path_helvetica, 16, index=0)       # Regular
    f_body_bold = ImageFont.truetype(font_path_helvetica, 16, index=1)  # Bold
    f_small = ImageFont.truetype(font_path_helvetica, 13, index=0)      # Regular
    f_small_bold = ImageFont.truetype(font_path_helvetica, 13, index=1) # Bold
    f_meta = ImageFont.truetype(font_path_helvetica, 13, index=1)       # Bold uppercase
    f_mono = ImageFont.truetype(font_path_menlo, 14, index=0)           # Regular
    f_mono_bold = ImageFont.truetype(font_path_menlo, 14, index=1)      # Bold
    f_table_header = ImageFont.truetype(font_path_helvetica, 15, index=1)
    f_table_cell = ImageFont.truetype(font_path_helvetica, 14, index=0)

    # -------------------------------------------------------------
    # HELPER FUNCTIONS
    # -------------------------------------------------------------
    def create_base_page():
        page = Image.new('RGB', (WIDTH, HEIGHT), '#f8fafc')
        draw = ImageDraw.Draw(page)
        return page, draw

    def draw_page_header(draw, title_text, section_subtitle, page_num):
        draw.rectangle([0, 0, WIDTH, 16], fill='#1e1b4b')
        draw.text((100, 48), "WEBAUDIT PRO • SYSTEMS ARCHITECTURE WHITE PAPER (V2.0 DUAL-DEVICE)", font=f_meta, fill='#6366f1')
        draw.text((1680, 48), "DOC ID: WAP-ARCH-2026-V2.0  |  STATUS: PRODUCTION", font=f_meta, fill='#64748b')

        draw.text((100, 78), title_text, font=f_hero, fill='#0f172a')
        draw.text((100, 134), section_subtitle, font=f_body, fill='#475569')

        draw.line([(100, 175), (WIDTH - 100, 175)], fill='#e2e8f0', width=2)
        draw.line([(100, 175), (460, 175)], fill='#6366f1', width=3)

    def draw_page_footer(draw, page_num, total_pages=3):
        foot_y = HEIGHT - 85
        draw.line([(100, foot_y - 20), (WIDTH - 100, foot_y - 20)], fill='#e2e8f0', width=1)
        draw.text((100, foot_y - 5), "WebAudit Pro • Dual-Device (Mobile + Desktop) 7-Worker Architecture", font=f_small, fill='#64748b')
        draw.text((1150, foot_y - 5), "Confidential & Proprietary • Systems Engineering Blueprint", font=f_small, fill='#94a3b8')
        
        page_str = f"Page {page_num} of {total_pages}"
        bbox = f_small_bold.getbbox(page_str)
        w = bbox[2] - bbox[0]
        draw.text((WIDTH - 100 - w, foot_y - 5), page_str, font=f_small_bold, fill='#0f172a')

    def draw_pill(draw, cx, cy, text, text_color, bg_color, border_color, font=f_small_bold, px=14, py=5):
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        w = tw + px * 2
        h = th + py * 2
        x1 = cx - w // 2
        y1 = cy - h // 2
        x2 = cx + w // 2
        y2 = cy + h // 2
        draw.rounded_rectangle([x1, y1, x2, y2], radius=h // 2, fill=bg_color, outline=border_color, width=1)
        draw.text((x1 + px, y1 + py - 2), text, font=font, fill=text_color)
        return (x1, y1, x2, y2)

    def draw_card(draw, x1, y1, x2, y2, bg='#ffffff', border='#e2e8f0', radius=14, border_w=1, shadow=True):
        if shadow:
            draw.rounded_rectangle([x1 + 2, y1 + 3, x2 + 2, y2 + 4], radius=radius, fill='#eef2f6')
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=bg, outline=border, width=border_w)

    def draw_down_arrow(draw, x, y1, y2, color='#6366f1', label=None, label_bg='#ffffff', label_border='#cbd5e1'):
        draw.line([(x, y1), (x, y2)], fill=color, width=3)
        arrow_sz = 10
        draw.polygon([(x, y2 + 6), (x - arrow_sz, y2 - arrow_sz), (x + arrow_sz, y2 - arrow_sz)], fill=color)
        if label:
            mid_y = (y1 + y2) // 2
            draw_pill(draw, x, mid_y, label, color, label_bg, label_border, font=f_mono_bold, px=18, py=6)

    # =========================================================================
    # PAGE 1: NEW DUAL-DEVICE ARCHITECTURE FLOWCHART
    # =========================================================================
    p1, d1 = create_base_page()
    draw_page_header(d1, "Dual-Device System Architecture Flowchart", 
                     "Dual-Viewport Inspection (Mobile 390px + Desktop 1440px), 7-Stream Concurrency & Device-Aware Scoring", 1)

    # Top Metadata Pills
    chips = [
        ("Architecture:", "Dual-Device Local-First"),
        ("Viewports:", "Mobile 390px & Desktop 1440px"),
        ("Diagnostic Streams:", "7 Parallel Workers across 2 Phases"),
        ("Dual Vitals:", "PageSpeed v5 Mobile + Desktop"),
        ("Scoring:", "Separate Mobile & Desktop Health")
    ]
    cur_chip_x = 100
    for title, val in chips:
        txt = f"{title} {val}"
        bbox = f_small.getbbox(txt)
        w = bbox[2] - bbox[0] + 24
        d1.rounded_rectangle([cur_chip_x, 195, cur_chip_x + w, 227], radius=6, fill='#ffffff', outline='#cbd5e1', width=1)
        d1.text((cur_chip_x + 10, 203), title, font=f_small_bold, fill='#64748b')
        d1.text((cur_chip_x + 10 + f_small_bold.getbbox(title)[2] + 4, 203), val, font=f_small_bold, fill='#0284c7')
        cur_chip_x += w + 16

    # --- STEP 1: PRESENTATION TIER ---
    s1_y = 250
    d1.ellipse([100, s1_y, 136, s1_y + 36], fill='#0284c7')
    d1.text((112, s1_y + 8), "1", font=f_body_bold, fill='#ffffff')
    d1.text((150, s1_y + 6), "STEP 1: PRESENTATION TIER & DEVICE FILTER INTERFACE", font=f_h2, fill='#0284c7')

    draw_card(d1, 100, s1_y + 45, WIDTH - 100, s1_y + 205, bg='#ffffff', border='#bae6fd', radius=14)
    d1.rounded_rectangle([101, s1_y + 46, WIDTH - 101, s1_y + 88], radius=14, fill='#f0f9ff')
    d1.rectangle([101, s1_y + 75, WIDTH - 101, s1_y + 88], fill='#f0f9ff')
    d1.text((130, s1_y + 55), "🖥️ React 18 + Vite Dashboard with Device Filter System", font=f_h3, fill='#0369a1')
    d1.text((870, s1_y + 58), "(frontend/src/App.tsx)", font=f_mono, fill='#0284c7')
    draw_pill(d1, WIDTH - 220, s1_y + 67, "Device: All | Mobile | Desktop", "#0284c7", "#ffffff", "#bae6fd", px=12, py=4)

    s1_bullets = [
        "• User inputs target website URL and clicks 'Run Diagnostic Audit'. Features real-time Device Filtering ('all', 'mobile', 'desktop').",
        "• Establishes reactive HTTP EventSource connection to SSE endpoint: /api/audit/stream?url=<target>.",
        "• Tracks 7 active workers concurrently: network, dom_seo, saudi, mobile (390px), desktop (1440px), external (vitals), aeo_geo."
    ]
    cur_y = s1_y + 102
    for b in s1_bullets:
        d1.text((130, cur_y), b, font=f_body, fill='#334155')
        cur_y += 28

    # Arrow 1 -> 2
    draw_down_arrow(d1, WIDTH // 2, s1_y + 205, s1_y + 295, color='#0284c7', 
                    label="HTTP GET /api/audit/stream (StreamingResponse)", 
                    label_bg='#f0f9ff', label_border='#7dd3fc')

    # --- STEP 2: GATEWAY & DUAL-DEVICE LAUNCH ---
    s2_y = s1_y + 315
    d1.ellipse([100, s2_y, 136, s2_y + 36], fill='#4f46e5')
    d1.text((111, s2_y + 8), "2", font=f_body_bold, fill='#ffffff')
    d1.text((150, s2_y + 6), "STEP 2: GATEWAY & DUAL-DEVICE ASYNC LAUNCH", font=f_h2, fill='#4338ca')

    draw_card(d1, 100, s2_y + 45, WIDTH - 100, s2_y + 215, bg='#ffffff', border='#c7d2fe', radius=14)
    d1.rounded_rectangle([101, s2_y + 46, WIDTH - 101, s2_y + 88], radius=14, fill='#eef2ff')
    d1.rectangle([101, s2_y + 75, WIDTH - 101, s2_y + 88], fill='#eef2ff')
    d1.text((130, s2_y + 55), "⚡ FastAPI ASGI Core & scan_headless_devices Orchestrator", font=f_h3, fill='#3730a3')
    d1.text((920, s2_y + 58), "(backend/main.py • Uvicorn :8000)", font=f_mono, fill='#4f46e5')
    draw_pill(d1, WIDTH - 220, s2_y + 67, "Concurrent Browser Contexts", "#4338ca", "#ffffff", "#c7d2fe", px=12, py=4)

    s2_bullets = [
        "• Generates audit_id UUID. Executes pre-flight raw HTML fetch via httpx.AsyncClient with desktop User-Agent.",
        "• Dispatches Phase 1 tasks: scan_headless_devices (spawns mobile 390px + desktop 1440px), network_scanner, and dual PageSpeed.",
        "• Streams atomic milestone updates ('worker_start': mobile, desktop, network, external) to client EventSource."
    ]
    cur_y = s2_y + 102
    for b in s2_bullets:
        d1.text((130, cur_y), b, font=f_body, fill='#334155')
        cur_y += 28

    # Arrow 2 -> 3
    draw_down_arrow(d1, WIDTH // 2, s2_y + 215, s2_y + 305, color='#4f46e5', 
                    label="Phase 1 Launch: scan_headless_devices + network + external intel", 
                    label_bg='#eef2ff', label_border='#a5b4fc')

    # --- STEP 3: THE 7 DIAGNOSTIC WORKERS MATRIX ---
    s3_y = s2_y + 325
    d1.ellipse([100, s3_y, 136, s3_y + 36], fill='#059669')
    d1.text((111, s3_y + 8), "3", font=f_body_bold, fill='#ffffff')
    d1.text((150, s3_y + 6), "STEP 3: THE 7 DIAGNOSTIC WORKER STREAMS (TWO-PHASE MATRIX)", font=f_h2, fill='#047857')
    draw_pill(d1, WIDTH - 220, s3_y + 18, "Dual Viewports & Dual Vitals", "#047857", "#ecfdf5", "#a7f3d0")

    # Phase 1: 4 Cards (Col 1 to Col 4)
    p1_cols = 4
    col_w4 = (WIDTH - 200 - 30 * 3) // 4
    gap4 = 30
    p1_card_h = 300
    p1_y = s3_y + 45

    p1_cards_data = [
        ("Worker 1: Network & SSL", "network_scanner.py", [
            "• TLS 1.2/1.3 socket handshake",
            "• SSL expiry countdown days",
            "• HTTP ➔ HTTPS 301/308 redirect",
            "• TTFB latency rating (ms)",
            "• Server header & CDN detection"
        ], "#059669", "#ecfdf5", "#a7f3d0", "Phase 1"),

        ("Worker 4: Playwright Mobile", "mobile_browser.py (390px)", [
            "• iPhone 14 Pro emulation (390px)",
            "• Tap targets < 48px touch audit",
            "• Mobile scroll overflow check",
            "• Captures mobile fold & full PNG",
            "• Local FCP & load time metrics"
        ], "#e11d48", "#fff1f2", "#fecdd3", "Mobile UX"),

        ("Worker 5: Playwright Desktop", "mobile_browser.py (1440px)", [
            "• Desktop Viewport (1440x900px)",
            "• Desktop horizontal layout overflow",
            "• Captures desktop fold & full PNG",
            "• Extracts rendered dynamic DOM",
            "• Identifies overflow DOM elements"
        ], "#2563eb", "#eff6ff", "#bfdbfe", "Desktop UX"),

        ("Worker 6: Dual PageSpeed", "external_intel.py (v5 API)", [
            "• Mobile Lighthouse Scores (0-100)",
            "• Desktop Lighthouse Scores (0-100)",
            "• Core Web Vitals: LCP, CLS, INP",
            "• Speed Index & Total Blocking Time",
            "• Next-Gen image format savings"
        ], "#7c3aed", "#faf5ff", "#e9d5ff", "Dual Vitals")
    ]

    for idx, (title, sub, pts, color, bg, border, badge) in enumerate(p1_cards_data):
        cx1 = 100 + idx * (col_w4 + gap4)
        cx2 = cx1 + col_w4
        draw_card(d1, cx1, p1_y, cx2, p1_y + p1_card_h, border=border)
        d1.rounded_rectangle([cx1 + 1, p1_y + 1, cx2 - 1, p1_y + 42], radius=14, fill=bg)
        d1.text((cx1 + 14, p1_y + 10), title, font=f_table_header, fill=color)
        d1.text((cx1 + 14, p1_y + 48), sub, font=f_mono, fill='#64748b')
        draw_pill(d1, cx2 - 55, p1_y + 21, badge, color, "#ffffff", border, px=8, py=2)
        cur_y = p1_y + 78
        for pt in pts:
            d1.text((cx1 + 14, cur_y), pt, font=f_small, fill='#334155')
            cur_y += 38

    # Handoff Banner between Phase 1 and Phase 2
    trans_y = p1_y + p1_card_h + 12
    draw_card(d1, 100, trans_y, WIDTH - 100, trans_y + 42, bg='#f0f9ff', border='#bae6fd', radius=8, shadow=False)
    d1.text((120, trans_y + 12), "⚡ Phase 2 Handoff:", font=f_body_bold, fill='#0284c7')
    d1.text((290, trans_y + 12), "Playwright yields rendered dynamic DOM (mobile or desktop) ➔ passed concurrently to Workers 2, 3, and 7", font=f_body, fill='#334155')
    draw_pill(d1, WIDTH - 220, trans_y + 21, "Hydrated DOM Feed", "#0284c7", "#ffffff", "#bae6fd", px=10, py=3)

    # Phase 2: 3 Cards (Col 1 to Col 3)
    p2_cols = 3
    col_w3 = (WIDTH - 200 - 32 * 2) // 3
    gap3 = 32
    p2_card_h = 290
    p2_y = trans_y + 54

    p2_cards_data = [
        ("Worker 2: DOM & Technical SEO", "dom_seo_scanner.py • BeautifulSoup4", [
            "• Title tag length (30-60 chars) & Meta Description",
            "• Single H1 semantic heading hierarchy validation",
            "• Image alt text accessibility ratio & total count",
            "• robots.txt rules & sitemap.xml presence check",
            "• Pixels: GA4, GTM, Meta, Snapchat, TikTok"
        ], "#0369a1", "#f0f9ff", "#bae6fd", "Technical SEO"),

        ("Worker 3: Saudi Conversion", "saudi_scanner.py • Localization RegEx", [
            "• Direct WhatsApp link detection (wa.me)",
            "• Click-to-call mobile phone tags (tel:)",
            "• Saudi Gateways: Mada, Apple Pay, STC Pay",
            "• Buy-Now-Pay-Later gateways: Tabby & Tamara",
            "• Arabic RTL direction & Lorem ipsum placeholders"
        ], "#b45309", "#fffbeb", "#fde68a", "GCC Conversion"),

        ("Worker 7: Generative AEO & GEO", "aeo_scanner.py • Schema.org & LLM SEO", [
            "• AI crawler permissions: GPTBot, PerplexityBot",
            "• ClaudeBot & Google-Extended robots directives",
            "• Schema.org JSON-LD structured data parser",
            "• sameAs Knowledge Graph entity authority links",
            "• RAG direct-answer chunkability & FAQ structures"
        ], "#be185d", "#fdf2f8", "#fbcfe8", "AEO / AI Search")
    ]

    for idx, (title, sub, pts, color, bg, border, badge) in enumerate(p2_cards_data):
        cx1 = 100 + idx * (col_w3 + gap3)
        cx2 = cx1 + col_w3
        draw_card(d1, cx1, p2_y, cx2, p2_y + p2_card_h, border=border)
        d1.rounded_rectangle([cx1 + 1, p2_y + 1, cx2 - 1, p2_y + 42], radius=14, fill=bg)
        d1.text((cx1 + 18, p2_y + 10), title, font=f_h3, fill=color)
        d1.text((cx1 + 18, p2_y + 48), sub, font=f_mono, fill='#64748b')
        draw_pill(d1, cx2 - 65, p2_y + 21, badge, color, "#ffffff", border, px=8, py=2)
        cur_y = p2_y + 80
        for pt in pts:
            d1.text((cx1 + 18, cur_y), pt, font=f_body, fill='#334155')
            cur_y += 36

    # Arrow 3 -> 4
    c3_y1 = p2_y + p2_card_h
    c3_y2 = c3_y1 + 75
    draw_down_arrow(d1, WIDTH // 2, c3_y1, c3_y2, color='#9333ea', 
                    label="Aggregate Device-Specific Issue Sets, Scores & Dual PNG Artifacts", 
                    label_bg='#f5f3ff', label_border='#d8b4fe')

    # --- STEP 4: INTELLIGENCE & DUAL SCORING ---
    s4_y = c3_y2 + 20
    d1.ellipse([100, s4_y, 136, s4_y + 36], fill='#9333ea')
    d1.text((111, s4_y + 8), "4", font=f_body_bold, fill='#ffffff')
    d1.text((150, s4_y + 6), "STEP 4: DUAL-DEVICE SCORING & MULTIMODAL GEMINI AI", font=f_h2, fill='#6d28d9')

    s4_w = (WIDTH - 200 - 32) // 2
    s4_h = 280
    s4_x1 = 100
    s4_x2 = s4_x1 + s4_w + 32

    # Left: Dual-Device Scoring & Evaluator
    draw_card(d1, s4_x1, s4_y + 45, s4_x1 + s4_w, s4_y + 45 + s4_h, border='#ddd6fe')
    d1.rounded_rectangle([s4_x1 + 1, s4_y + 46, s4_x1 + s4_w - 1, s4_y + 88], radius=14, fill='#f5f3ff')
    d1.text((s4_x1 + 20, s4_y + 55), "🎯 Dual-Device Scoring & Metrics Evaluator", font=f_h3, fill='#6d28d9')
    d1.text((s4_x1 + 470, s4_y + 58), "(services/scoring_engine.py)", font=f_mono, fill='#9333ea')
    s4_left_pts = [
        "• Calculates overall_score, mobile_overall_score, and desktop_overall_score.",
        "• Device-Aware Filtering: Desktop score skips Mobile UX tap targets; Mobile score skips Desktop UX overflow.",
        "• Evaluates 20+ checks tagged with device='all', 'mobile', or 'desktop' against W3C benchmarks.",
        "• Synthesizes actionable remediation explanations and copy-paste code snippets for engineers."
    ]
    cur_y = s4_y + 102
    for p in s4_left_pts:
        d1.text((s4_x1 + 20, cur_y), p, font=f_body, fill='#334155')
        cur_y += 34

    # Right: Multimodal Gemini AI
    draw_card(d1, s4_x2, s4_y + 45, s4_x2 + s4_w, s4_y + 45 + s4_h, border='#fecdd3')
    d1.rounded_rectangle([s4_x2 + 1, s4_y + 46, s4_x2 + s4_w - 1, s4_y + 88], radius=14, fill='#fff1f2')
    d1.text((s4_x2 + 20, s4_y + 55), "🤖 Google Gemini Multimodal Sales Pitch Engine", font=f_h3, fill='#be123c')
    d1.text((s4_x2 + 480, s4_y + 58), "(services/ai_pitch_engine.py)", font=f_mono, fill='#e11d48')
    s4_right_pts = [
        "• Multimodal Vision: Inspects captured mobile or desktop fold screenshot for visual hierarchy and CTA clarity.",
        "• Model Fallbacks: Tries gemini-2.0-flash, gemini-1.5-flash, gemini-2.5-flash for personalized outreach copy.",
        "• Deterministic Baseline: Instant fallback to high-converting Arabic WhatsApp scripts and bilingual cold emails.",
        "• Discovery Questions: 4 qualification questions uncovering bottlenecks in client lead routing."
    ]
    cur_y = s4_y + 102
    for p in s4_right_pts:
        d1.text((s4_x2 + 20, cur_y), p, font=f_body, fill='#334155')
        cur_y += 34

    # Arrow 4 -> 5
    c4_y1 = s4_y + 45 + s4_h
    c4_y2 = c4_y1 + 75
    draw_down_arrow(d1, WIDTH // 2, c4_y1, c4_y2, color='#ea580c', 
                    label="Save Dual Scores to SQLite & Dispatch SSE 'event: complete'", 
                    label_bg='#fff7ed', label_border='#fdba74')

    # --- STEP 5: PERSISTENCE & CLIENT PRESENTATION ---
    s5_y = c4_y2 + 20
    d1.ellipse([100, s5_y, 136, s5_y + 36], fill='#ea580c')
    d1.text((111, s5_y + 8), "5", font=f_body_bold, fill='#ffffff')
    d1.text((150, s5_y + 6), "STEP 5: PERSISTENCE & DEVICE-FILTERABLE DASHBOARD DELIVERY", font=f_h2, fill='#c2410c')

    s5_h = 240
    # Left: Database & Dual Screenshots
    draw_card(d1, s4_x1, s5_y + 45, s4_x1 + s4_w, s5_y + 45 + s5_h, border='#fed7aa')
    d1.rounded_rectangle([s4_x1 + 1, s5_y + 46, s4_x1 + s4_w - 1, s5_y + 88], radius=14, fill='#fff7ed')
    d1.text((s4_x1 + 20, s5_y + 55), "💾 Local SQLite & Dual Screenshots Storage", font=f_h3, fill='#c2410c')
    d1.text((s4_x1 + 450, s5_y + 58), "(audits.db • /screenshots/)", font=f_mono, fill='#ea580c')
    s5_left_pts = [
        "• audits table (aiosqlite): Stores audit UUID, target URL, overall/mobile/desktop scores, and full JSON.",
        "• leads table: Built-in CRM tracking prospective clients, outreach status, decision-makers, and notes.",
        "• Dual Screenshots: Saves both {id}_mobile_fold.png and {id}_desktop_fold.png for interactive review."
    ]
    cur_y = s5_y + 102
    for p in s5_left_pts:
        d1.text((s4_x1 + 20, cur_y), p, font=f_body, fill='#334155')
        cur_y += 34

    # Right: Presentation Dashboard with Device Toggles
    draw_card(d1, s4_x2, s5_y + 45, s4_x2 + s4_w, s5_y + 45 + s5_h, border='#a7f3d0')
    d1.rounded_rectangle([s4_x2 + 1, s5_y + 46, s4_x2 + s4_w - 1, s5_y + 88], radius=14, fill='#ecfdf5')
    d1.text((s4_x2 + 20, s5_y + 55), "🏁 Interactive Presentation & Viewport Switcher", font=f_h3, fill='#047857')
    d1.text((s4_x2 + 480, s5_y + 58), "(event: complete received)", font=f_mono, fill='#059669')
    s5_right_pts = [
        "• Device Filter Tabs: Toggle checklist and analytics between 'All', 'Mobile', and 'Desktop'.",
        "• Dual Scorecards: Side-by-side radar scorecards and progress gauges for mobile vs desktop.",
        "• Dual Viewport Mock: Switch between iPhone 14 Pro mock and Desktop 1440px viewport.",
        "• AI Outreach Center: One-click copy for Arabic WhatsApp script and bilingual sales pitches."
    ]
    cur_y = s5_y + 102
    for p in s5_right_pts:
        d1.text((s4_x2 + 20, cur_y), p, font=f_body, fill='#334155')
        cur_y += 34

    draw_page_footer(d1, 1, 3)

    # =========================================================================
    # PAGE 2: THE 7 DIAGNOSTIC WORKERS SPECIFICATION & TIMELINE
    # =========================================================================
    p2, d2 = create_base_page()
    draw_page_header(d2, "Diagnostic Workers Specification Matrix (Dual-Device)", 
                     "Detailed technical breakdown of inputs, diagnostic routines, target benchmarks, and latency budgets", 2)

    d2.text((100, 205), "1. THE 7 DIAGNOSTIC WORKER STREAMS SPECIFICATION TABLE", font=f_h2, fill='#0f172a')
    
    tbl_x1 = 100
    tbl_x2 = WIDTH - 100
    tbl_y = 250
    headers = [
        ("#", 70),
        ("Worker & Module", 360),
        ("Engine / Library", 250),
        ("Targeted Inspections & Attributes", 780),
        ("Benchmark Standards", 400),
        ("Device", 220),
        ("Phase", 200)
    ]

    d2.rounded_rectangle([tbl_x1, tbl_y, tbl_x2, tbl_y + 48], radius=8, fill='#1e1b4b')
    cur_x = tbl_x1
    for h_text, w in headers:
        d2.text((cur_x + 14, tbl_y + 15), h_text, font=f_table_header, fill='#ffffff')
        cur_x += w

    worker_rows = [
        (
            "01", "Worker 1: Network & Security\nworkers/network_scanner.py", "socket, ssl, httpx",
            "Direct TLS 1.2/1.3 socket handshake on port 443; SSL expiration days countdown; CA issuer chain; HTTP ➔ HTTPS redirect codes (301/308); TTFB latency; CDN header identification.",
            "SSL > 30 days\nHTTP ➔ HTTPS: 301\nTTFB < 300ms", "All Devices\n(General)", "Phase 1\n(Initial)"
        ),
        (
            "02", "Worker 2: DOM & SEO Scanner\nworkers/dom_seo_scanner.py", "BeautifulSoup4, re",
            "Title length & meta description presence; single H1 hierarchy; image alt text coverage ratio; robots.txt disallow rules & sitemap.xml presence; GA4, GTM, Meta Pixel, Snap & TikTok tracking.",
            "Title: 30-60 chars\nH1 count == 1\nAlt coverage: 100%", "All Devices\n(General)", "Phase 2\n(Hydrated)"
        ),
        (
            "03", "Worker 3: Saudi Conversion\nworkers/saudi_scanner.py", "Localization RegEx",
            "Direct WhatsApp lead channels (wa.me); click-to-call phone links (tel:); Saudi payment gateways (Mada, Apple Pay, STC Pay, Tabby, Tamara); Arabic RTL orientation; placeholder text.",
            "WhatsApp & tel: present\nMada & Apple Pay enabled\nRTL dir attribute", "All Devices\n(General)", "Phase 2\n(Hydrated)"
        ),
        (
            "04", "Worker 4: Playwright Mobile\nworkers/mobile_browser.py", "Playwright (390px)",
            "Emulates iPhone 14 Pro (390×844, DPR 3.0); measures layout overflow (scrollWidth > clientWidth); calculates tap target bounding boxes (< 48px); captures fold and full screenshots.",
            "scrollWidth == clientWidth\nTap targets >= 48px\nHero fold capture", "Mobile\n(Viewport)", "Phase 1\n(Initial)"
        ),
        (
            "05", "Worker 5: Playwright Desktop\nworkers/mobile_browser.py", "Playwright (1440px)",
            "Emulates Desktop Viewport (1440×900); measures desktop layout horizontal overflow; captures desktop fold and full screenshots; extracts rendered dynamic SPA DOM for Phase 2.",
            "scrollWidth == 1440px\nDesktop fold capture\nDynamic DOM yield", "Desktop\n(Viewport)", "Phase 1\n(Initial)"
        ),
        (
            "06", "Worker 6: Dual PageSpeed\nworkers/external_intel.py", "Google Cloud REST (v5)",
            "Queries Google PageSpeed Insights REST API for both Mobile and Desktop Lighthouse audits: FCP, Speed Index, TBT, LCP, CLS, INP, and next-gen image compression savings.",
            "LCP < 2.5s, CLS < 0.1\nINP < 200ms\nDesktop Score >= 90", "Mobile &\nDesktop", "Phase 1\n(Initial)"
        ),
        (
            "07", "Worker 7: Generative AEO & GEO\nworkers/aeo_scanner.py", "Schema.org, JSON-LD",
            "AI search crawler permissions in robots.txt (GPTBot, PerplexityBot, ClaudeBot, Google-Extended); Schema.org JSON-LD structured data; sameAs authority links; RAG direct-answer chunkability.",
            "AI Bots: Allowed\nsameAs links > 0\nFAQ schema present", "All Devices\n(General)", "Phase 2\n(Hydrated)"
        )
    ]

    cur_row_y = tbl_y + 52
    for r_idx, (w_num, w_name, w_eng, w_insp, w_bm, w_dev, w_phase) in enumerate(worker_rows):
        bg_color = '#ffffff' if r_idx % 2 == 0 else '#f1f5f9'
        row_height = 118
        d2.rounded_rectangle([tbl_x1, cur_row_y, tbl_x2, cur_row_y + row_height], radius=6, fill=bg_color, outline='#e2e8f0', width=1)
        
        cur_x = tbl_x1
        d2.text((cur_x + 14, cur_row_y + 14), w_num, font=f_h3, fill='#0284c7')
        cur_x += headers[0][1]

        name_parts = w_name.split('\n')
        d2.text((cur_x + 14, cur_row_y + 12), name_parts[0], font=f_body_bold, fill='#0f172a')
        d2.text((cur_x + 14, cur_row_y + 34), name_parts[1], font=f_mono, fill='#6366f1')
        cur_x += headers[1][1]

        d2.text((cur_x + 14, cur_row_y + 14), w_eng, font=f_mono, fill='#047857')
        cur_x += headers[2][1]

        words = w_insp.split(' ')
        lines = []
        cur_line = []
        for word in words:
            if len(" ".join(cur_line + [word])) < 68:
                cur_line.append(word)
            else:
                lines.append(" ".join(cur_line))
                cur_line = [word]
        if cur_line:
            lines.append(" ".join(cur_line))
        
        c_y = cur_row_y + 10
        for l in lines[:3]:
            d2.text((cur_x + 14, c_y), l, font=f_table_cell, fill='#334155')
            c_y += 22
        cur_x += headers[3][1]

        bm_parts = w_bm.split('\n')
        b_y = cur_row_y + 12
        for bp in bm_parts:
            d2.text((cur_x + 14, b_y), bp, font=f_mono, fill='#b45309')
            b_y += 22
        cur_x += headers[4][1]

        dev_parts = w_dev.split('\n')
        d2.text((cur_x + 14, cur_row_y + 14), dev_parts[0], font=f_body_bold, fill='#0284c7')
        d2.text((cur_x + 14, cur_row_y + 36), dev_parts[1], font=f_small, fill='#64748b')
        cur_x += headers[5][1]

        ph_parts = w_phase.split('\n')
        d2.text((cur_x + 14, cur_row_y + 14), ph_parts[0], font=f_body_bold, fill='#6366f1')
        d2.text((cur_x + 14, cur_row_y + 36), ph_parts[1], font=f_small, fill='#64748b')

        cur_row_y += row_height + 6

    # Section 2: Concurrency Timeline Gantt Visualization
    gantt_top = cur_row_y + 25
    d2.text((100, gantt_top), "2. DUAL-DEVICE ASYNCHRONOUS TWO-PHASE TIMELINE (GANTT PROFILE)", font=f_h2, fill='#0f172a')
    
    gantt_box_y = gantt_top + 40
    draw_card(d2, 100, gantt_box_y, WIDTH - 100, gantt_box_y + 390, border='#cbd5e1')

    axis_y = gantt_box_y + 45
    d2.line([(420, axis_y), (WIDTH - 150, axis_y)], fill='#94a3b8', width=2)
    time_marks = [("0.0s", 420), ("1.0s", 740), ("2.0s", 1060), ("3.0s", 1380), ("4.0s", 1700), ("5.0s", 2020)]
    for tm_label, tm_x in time_marks:
        d2.line([(tm_x, axis_y - 6), (tm_x, axis_y + 6)], fill='#64748b', width=2)
        d2.text((tm_x - 18, axis_y - 26), tm_label, font=f_mono_bold, fill='#475569')

    tasks = [
        ("Pre-flight HTML (httpx)", 420, 620, "#0284c7", "Raw HTML Ready"),
        ("Worker 1: Network & SSL (Socket)", 420, 700, "#059669", "TLS & TTFB Evaluated"),
        ("Worker 4: Playwright Mobile (390px)", 420, 1180, "#e11d48", "Mobile Viewport, Fold PNG & Tap Targets"),
        ("Worker 5: Playwright Desktop (1440px)", 420, 1200, "#2563eb", "Desktop Viewport, Overflow & Dynamic DOM"),
        ("Worker 6: Dual PageSpeed (REST)", 420, 1100, "#7c3aed", "Mobile + Desktop Core Web Vitals"),
        ("Phase 2: Workers 2, 3, 7 (DOM/Saudi/AEO)", 1200, 1500, "#0891b2", "Hydrated Dynamic DOM Fully Scanned"),
        ("Synthesis: Dual-Device Scoring & Remedies", 1500, 1650, "#9333ea", "Mobile vs Desktop Deductions Computed"),
        ("AI Pitch: Gemini 2.0/1.5/2.5 Flash Vision", 1500, 2050, "#be123c", "Hero Contrast Review & Bilingual Scripts"),
        ("Persistence: SQLite Save & Final SSE Push", 2050, 2180, "#ea580c", "Dashboard Hydrated with Device Filter")
    ]

    t_y = axis_y + 18
    for t_name, x_start, x_end, bar_color, milestone in tasks:
        d2.text((120, t_y + 2), t_name, font=f_small_bold, fill='#0f172a')
        d2.rounded_rectangle([x_start, t_y, x_end, t_y + 20], radius=6, fill=bar_color)
        d2.text((x_end + 12, t_y + 2), milestone, font=f_small, fill='#475569')
        t_y += 34

    draw_page_footer(d2, 2, 3)

    # =========================================================================
    # PAGE 3: DATA ARCHITECTURE, MODELS & DEPLOYMENT BLUEPRINT
    # =========================================================================
    p3, d3 = create_base_page()
    draw_page_header(d3, "Data Architecture, Domain Models & Deployment", 
                     "SQLite database schemas, Pydantic domain models, security profile, and local deployment blueprint", 3)

    d3.text((100, 205), "1. ASYNCHRONOUS SQLITE DATABASE ARCHITECTURE (audits.db)", font=f_h2, fill='#0f172a')

    ddl_y = 250
    ddl_w = (WIDTH - 200 - 32) // 2
    ddl_h = 360

    draw_card(d3, 100, ddl_y, 100 + ddl_w, ddl_y + ddl_h, bg='#0f172a', border='#334155')
    d3.text((125, ddl_y + 20), "TABLE: audits (Dual-Device JSON & Scores)", font=f_h3, fill='#38bdf8')
    d3.text((125, ddl_y + 55), "Stores all synthesized dual-device audit payloads for instant recall", font=f_small, fill='#94a3b8')
    audits_ddl = [
        "CREATE TABLE IF NOT EXISTS audits (",
        "    id TEXT PRIMARY KEY,               -- UUID v4",
        "    target_url TEXT NOT NULL,          -- Normalized Target Domain",
        "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,",
        "    overall_score INTEGER NOT NULL,    -- 0-100 General Health",
        "    data_json TEXT NOT NULL            -- Serialized Dual Payload",
        ");"
    ]
    cur_y = ddl_y + 95
    for l in audits_ddl:
        d3.text((125, cur_y), l, font=f_mono, fill='#e2e8f0')
        cur_y += 30

    draw_card(d3, 100 + ddl_w + 32, ddl_y, WIDTH - 100, ddl_y + ddl_h, bg='#0f172a', border='#334155')
    d3.text((100 + ddl_w + 57, ddl_y + 20), "TABLE: leads (Built-in Sales CRM Pipeline)", font=f_h3, fill='#34d399')
    d3.text((100 + ddl_w + 57, ddl_y + 55), "Tracks prospective client outreach status, decision-makers, and notes", font=f_small, fill='#94a3b8')
    leads_ddl = [
        "CREATE TABLE IF NOT EXISTS leads (",
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
        "    audit_id TEXT REFERENCES audits(id),",
        "    company_name TEXT, contact_person TEXT,",
        "    phone TEXT, email TEXT,",
        "    status TEXT DEFAULT 'new',         -- new, contacted, closed",
        "    notes TEXT, updated_at TIMESTAMP",
        ");"
    ]
    cur_y = ddl_y + 95
    for l in leads_ddl:
        d3.text((100 + ddl_w + 57, cur_y), l, font=f_mono, fill='#e2e8f0')
        cur_y += 30

    mod_top = ddl_y + ddl_h + 35
    d3.text((100, mod_top), "2. PYDANTIC DOMAIN MODEL ARCHITECTURE (models.py)", font=f_h2, fill='#0f172a')

    mod_box_y = mod_top + 45
    draw_card(d3, 100, mod_box_y, WIDTH - 100, mod_box_y + 360, border='#cbd5e1')

    m_card_w = (WIDTH - 200 - 30 - 32 * 3) // 4
    m_card_h = 290
    m_card_y = mod_box_y + 40
    
    models_data = [
        ("FullAuditResponse", "Root Synthetic Model", [
            "• audit_id: str (UUID)",
            "• target_url: str",
            "• overall_score: int",
            "• mobile_overall_score: int",
            "• desktop_overall_score: int",
            "• mobile: HeadlessMobileResult",
            "• desktop: HeadlessDesktopResult",
            "• evaluated_metrics: List"
        ], "#0284c7", "#f0f9ff"),
        ("MetricEvaluation", "Device-Aware Check", [
            "• id: str (rule identifier)",
            "• name: str (human title)",
            "• category: str",
            "• status: MetricStatus",
            "• score: int (0 to 100)",
            "• device: 'all'|'mob'|'desk'",
            "• benchmark: str",
            "• code_snippet: Optional[str]"
        ], "#059669", "#ecfdf5"),
        ("HeadlessDesktopResult", "Playwright Desktop", [
            "• horizontal_overflow: bool",
            "• viewport_width: 1440",
            "• viewport_height: 900",
            "• scroll_width: int",
            "• overflow_elements: list",
            "• fold_screenshot_path: str",
            "• full_screenshot_path: str",
            "• rendered_html: str"
        ], "#2563eb", "#eff6ff"),
        ("ExternalIntelResult", "Dual PageSpeed Vitals", [
            "• mobile_performance_score",
            "• desktop_performance_score",
            "• lcp_seconds (mobile)",
            "• desktop_lcp_seconds",
            "• cls_score & desktop_cls",
            "• inp_ms & desktop_inp",
            "• image_savings_mb",
            "• issues: List[AuditIssue]"
        ], "#7c3aed", "#faf5ff")
    ]

    m_x = 125
    for m_name, m_sub, m_fields, m_color, m_bg in models_data:
        draw_card(d3, m_x, m_card_y, m_x + m_card_w, m_card_y + m_card_h, bg=m_bg, border=m_color)
        d3.text((m_x + 14, m_card_y + 16), m_name, font=f_h3, fill=m_color)
        d3.text((m_x + 14, m_card_y + 44), m_sub, font=f_small, fill='#64748b')
        f_y = m_card_y + 75
        for f in m_fields:
            d3.text((m_x + 14, f_y), f, font=f_small, fill='#1e293b')
            f_y += 24
        m_x += m_card_w + 32

    dep_top = mod_box_y + 400
    d3.text((100, dep_top), "3. OPERATIONAL PROFILE & PRODUCTION DEPLOYMENT BLUEPRINT", font=f_h2, fill='#0f172a')

    dep_card_y = dep_top + 45
    draw_card(d3, 100, dep_card_y, WIDTH - 100, dep_card_y + 320, border='#cbd5e1')

    d3.text((130, dep_card_y + 25), "🚀 One-Command Local Startup", font=f_h3, fill='#0f172a')
    d3.text((130, dep_card_y + 60), "Execute from the project repository root:", font=f_body, fill='#475569')

    draw_card(d3, 130, dep_card_y + 95, 1050, dep_card_y + 265, bg='#0f172a', border='#334155', radius=8)
    run_cmds = [
        "#!/usr/bin/env bash",
        "./run.sh",
        "",
        "# Automatically executes:",
        "# 1. Installs/verifies virtualenv dependencies",
        "# 2. Builds React 18 production bundle (Vite)",
        "# 3. Initializes local SQLite database",
        "# 4. Launches FastAPI on http://127.0.0.1:8000"
    ]
    c_y = dep_card_y + 110
    for cmd in run_cmds:
        color = '#38bdf8' if cmd.startswith("./") else ('#64748b' if cmd.startswith("#") else '#e2e8f0')
        d3.text((150, c_y), cmd, font=f_mono, fill=color)
        c_y += 20

    d3.text((1120, dep_card_y + 25), "🔒 Engineering Invariants & Security Guardrails", font=f_h3, fill='#0f172a')
    inv_pts = [
        "• Dual-Device Isolation: Playwright launches isolated mobile (390px) & desktop (1440px) contexts cleanly.",
        "• Zero Infrastructure Cost: $0.00/month recurring cost. Runs completely on developer localhost.",
        "• Complete Data Privacy: Target audit records and screenshot files remain local in audits.db and /screenshots.",
        "• Graceful AI Multi-Model Fallbacks: Tries gemini-2.0-flash, 1.5-flash, 2.5-flash with local copy fallbacks.",
        "• Network Timeout Controls: Strict 10-second request timeouts protect against slow, unresponsive targets."
    ]
    i_y = dep_card_y + 65
    for inv in inv_pts:
        d3.text((1120, i_y), inv, font=f_body, fill='#334155')
        i_y += 44

    draw_page_footer(d3, 3, 3)

    print(f"Compiling executive 3-page architecture PDF to {output_path}...")
    p1.save(output_path, "PDF", save_all=True, append_images=[p2, p3], resolution=300.0)
    print("Multi-page PDF generated successfully!")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "WebAudit_Pro_Architecture_Flowchart.pdf"
    build_professional_pdf(out_file)
