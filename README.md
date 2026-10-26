# WebAudit Pro: 6-Worker Website Audit & Lead Gen Platform

A local-first, zero-cost, high-accuracy website auditing and cold outreach generation engine. Built for agency founders and sales teams targeting high-ticket clients (with dedicated localization for Saudi Arabia and the GCC).

---

## Architecture Overview

* **Backend:** FastAPI (Python 3.14) orchestrating 6 parallel diagnostic workers via `asyncio.gather`.
* **Frontend:** React + Vite + TypeScript + Tailwind CSS (served directly by FastAPI or via Vite dev server).
* **AI Engine:** Google Gemini 2.5 Flash via official `google-genai` SDK for mobile fold inspection and bilingual cold outreach pitch generation.
* **Database:** Local SQLite (`backend/audits.db`) using `aiosqlite`.
* **Total Cost:** **$0.00** running locally on your Mac.

---

## The 6 Diagnostic Workers

1. **Worker 1 (`network_scanner.py`):** TLS socket handshake, SSL expiration countdown, HTTP $\to$ HTTPS permanent redirect, Time to First Byte (TTFB).
2. **Worker 2 (`dom_seo_scanner.py`):** Title tag, meta description, H1 hierarchy, image alt coverage, sitemap.xml, robots.txt disallow rules, canonical tags, mixed content, and GA4/GTM/Meta tracking scripts.
3. **Worker 3 (`saudi_scanner.py`):** Direct WhatsApp links (`wa.me`), click-to-call (`tel:`), Saudi payment gateways (mada, Apple Pay, STC Pay, Tabby, Tamara), Arabic language and RTL orientation, developer placeholder detection (`Lorem ipsum`).
4. **Worker 4 (`mobile_browser.py`):** Headless Chromium (Playwright) emulating iPhone 14 Pro, calculates horizontal layout overflow (`scrollWidth > clientWidth`), tap target sizes (< 48px), and captures mobile fold and full screenshots.
5. **Worker 5 (`external_intel.py`):** Google PageSpeed Insights REST API (Core Web Vitals: LCP, INP, CLS, modern WebP/AVIF compression savings) + Google Places API (profile claim status and star rating).
6. **Worker 6 (`aeo_scanner.py`):** AI search bot permissions in `robots.txt` (`GPTBot`, `OAI-SearchBot`, `PerplexityBot`, `Google-Extended`, `ClaudeBot`), Schema `sameAs` entity links, and RAG direct-answer Q&A chunkability.

---

## Quick Start (One Command)

Simply run:
```bash
./run.sh
```

Then open your browser at:
👉 **`http://127.0.0.1:8000`**

---

## Development Mode (Live Hot-Reloading Frontend)

If you are modifying the React UI and want instant Vite Hot-Module-Replacement:

1. **Terminal 1 (Backend API):**
   ```bash
   cd backend
   source .venv/bin/activate
   python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Terminal 2 (Frontend UI):**
   ```bash
   cd frontend
   npm run dev
   ```
   Open `http://localhost:3000`.

---

## API Keys Configuration (Optional)

Copy `backend/.env.example` to `backend/.env`:
```bash
cp backend/.env.example backend/.env
```
* `GEMINI_API_KEY`: For automated Gemini Vision screenshot reviews (Get free key at [Google AI Studio](https://aistudio.google.com)).
* `PAGESPEED_API_KEY`: Optional key for higher PageSpeed quota (Google developer console).
* `GOOGLE_PLACES_API_KEY`: For Google Business Profile star rating and review count.
