import os
import uuid
import json
import asyncio
from typing import AsyncGenerator
import httpx
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from database import init_db, save_audit, get_audit, list_recent_audits
from models import FullAuditResponse
from workers.network_scanner import scan_network_and_security
from workers.dom_seo_scanner import scan_dom_and_seo
from workers.saudi_scanner import scan_saudi_conversion
from workers.mobile_browser import scan_headless_mobile
from workers.external_intel import scan_external_intel
from workers.aeo_scanner import scan_aeo_and_geo
from services.scoring_engine import calculate_audit_scores
from services.ai_pitch_engine import generate_ai_pitch

app = FastAPI(title="Website Analysis & Lead Gen Engine", version="1.0.0")

# Enable CORS for local React/Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure screenshots folder exists and mount static endpoint
os.makedirs(settings.SCREENSHOTS_DIR, exist_ok=True)
app.mount("/screenshots", StaticFiles(directory=settings.SCREENSHOTS_DIR), name="screenshots")

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/api/audits/recent")
async def get_recent():
    return await list_recent_audits(limit=25)

@app.get("/api/audit/stream")
async def stream_audit(url: str = Query(..., description="Target website URL")):
    """
    Server-Sent Events (SSE) endpoint:
    Streams progress updates from each of the 6 parallel workers as they complete,
    ending with the full synthesized report.
    """
    target_url = url.strip()
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "https://" + target_url

    audit_id = str(uuid.uuid4())

    async def event_generator() -> AsyncGenerator[str, None]:
        yield f"data: {json.dumps({'event': 'start', 'audit_id': audit_id, 'url': target_url, 'message': 'Starting multi-worker diagnostic scan...'})}\n\n"

        # 1. Fetch raw HTML once for workers 2, 3, 6 to share
        html_content = ""
        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False, follow_redirects=True) as client:
                resp = await client.get(target_url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
                html_content = resp.text
        except Exception:
            pass

        # 2. Parallel Workers Definition
        # Launch mobile browser and network concurrently first
        yield f"data: {json.dumps({'event': 'worker_start', 'worker': 'mobile', 'message': 'Launching Headless Mobile Browser & Layout Analysis...'})}\n\n"
        
        mobile_task = asyncio.create_task(scan_headless_mobile(target_url, audit_id, settings.SCREENSHOTS_DIR))
        network_task = asyncio.create_task(scan_network_and_security(target_url))
        external_task = asyncio.create_task(scan_external_intel(target_url, settings.PAGESPEED_API_KEY, settings.GOOGLE_PLACES_API_KEY))

        # Await mobile and network
        mobile_res = await mobile_task
        yield f"data: {json.dumps({'event': 'worker_done', 'worker': 'mobile', 'message': 'Mobile viewport and layout completed'})}\n\n"

        net_res = await network_task
        yield f"data: {json.dumps({'event': 'worker_done', 'worker': 'network', 'message': 'Network & protocol completed'})}\n\n"

        # Now pass both raw HTML and Playwright rendered HTML to DOM, Saudi, and AEO scanners
        rendered_html = mobile_res.rendered_html or ""

        dom_task = asyncio.create_task(scan_dom_and_seo(target_url, html_content, rendered_html))
        saudi_task = asyncio.create_task(scan_saudi_conversion(target_url, html_content, rendered_html))
        aeo_task = asyncio.create_task(scan_aeo_and_geo(target_url, rendered_html or html_content))

        dom_res = await dom_task
        yield f"data: {json.dumps({'event': 'worker_done', 'worker': 'dom_seo', 'message': 'DOM & SEO completed'})}\n\n"

        saudi_res = await saudi_task
        yield f"data: {json.dumps({'event': 'worker_done', 'worker': 'saudi', 'message': 'Saudi conversion completed'})}\n\n"

        aeo_res = await aeo_task
        yield f"data: {json.dumps({'event': 'worker_done', 'worker': 'aeo_geo', 'message': 'AEO & GEO completed'})}\n\n"

        ext_res = await external_task
        yield f"data: {json.dumps({'event': 'worker_done', 'worker': 'external', 'message': 'External intelligence completed'})}\n\n"

        worker_results = {
            "network": net_res,
            "dom_seo": dom_res,
            "saudi": saudi_res,
            "mobile": mobile_res,
            "external": ext_res,
            "aeo_geo": aeo_res
        }

        # 3. Aggregate Issues & Scoring
        all_issues = []
        for res in worker_results.values():
            if hasattr(res, "issues"):
                all_issues.extend(res.issues)

        score_data = calculate_audit_scores(all_issues)

        # 4. AI Pitch & Vision Engine
        mobile_res = worker_results.get("mobile")
        fold_path = mobile_res.fold_screenshot_path if mobile_res else None
        
        yield f"data: {json.dumps({'event': 'ai_pitch_start', 'message': 'Generating bilingual sales outreach pitches...'})}\n\n"
        
        ai_pitch = await generate_ai_pitch(
            target_url=target_url,
            top_issues=all_issues,
            screenshot_path=fold_path,
            gemini_api_key=settings.GEMINI_API_KEY
        )

        # 5. Build Final Response Object
        final_response = FullAuditResponse(
            audit_id=audit_id,
            target_url=target_url,
            overall_score=score_data["overall_score"],
            scores_by_category=score_data["scores_by_category"],
            total_critical_issues=score_data["critical_count"],
            total_warning_issues=score_data["warning_count"],
            total_info_issues=score_data["info_count"],
            network=worker_results.get("network"),
            dom_seo=worker_results.get("dom_seo"),
            saudi_conversion=worker_results.get("saudi"),
            mobile=worker_results.get("mobile"),
            external=worker_results.get("external"),
            aeo_geo=worker_results.get("aeo_geo"),
            ai_pitch=ai_pitch,
            all_issues=all_issues
        )

        # Save into SQLite
        await save_audit(audit_id, target_url, final_response.overall_score, final_response.model_dump())

        yield f"data: {json.dumps({'event': 'complete', 'data': final_response.model_dump(mode='json')})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/audit/{audit_id}")
async def get_single_audit(audit_id: str):
    data = await get_audit(audit_id)
    if not data:
        raise HTTPException(status_code=404, detail="Audit not found")
    return data

# Mount built React frontend at root after all API routes are defined
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
