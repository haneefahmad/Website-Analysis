# 🏛️ WebAudit Pro — System Architecture Document

**Version:** 2.0.0  
**Status:** Production Ready  
**Architecture Type:** Dual-Device (Mobile + Desktop), Local-First, Zero-Cloud-Cost 7-Worker Diagnostic Platform  
**Author:** WebAudit Pro Engineering Team  
**Last Updated:** October 2026  

---

## 📑 Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [High-Level System Topology](#2-high-level-system-topology)
3. [Component Architecture by Tier](#3-component-architecture-by-tier)
   * 3.1 [Presentation Tier (React + Vite + Device Filter)](#31-presentation-tier-react--vite--device-filter)
   * 3.2 [API Orchestration Tier (FastAPI + Asyncio)](#32-api-orchestration-tier-fastapi--asyncio)
   * 3.3 [The 7 Diagnostic Worker Streams Matrix](#33-the-7-diagnostic-worker-streams-matrix)
   * 3.4 [Dual-Device Scoring & AI Outreach Services](#34-dual-device-scoring--ai-outreach-services)
   * 3.5 [Persistence & Asset Storage (SQLite & Dual Screenshots)](#35-persistence--asset-storage-sqlite--dual-screenshots)
4. [Asynchronous Data Flow & SSE Pipeline](#4-asynchronous-data-flow--sse-pipeline)
5. [Database Schema & Data Models](#5-database-schema--data-models)
6. [External Integrations & Fallback Mechanics](#6-external-integrations--fallback-mechanics)
7. [Fault Isolation & Resilience Design](#7-fault-isolation--resilience-design)
8. [Deployment & Local Operational Profile](#8-deployment--local-operational-profile)

---

## 1. Executive Summary

**WebAudit Pro** is an asynchronous, dual-device website diagnostic and automated sales lead generation platform. Engineered for digital agencies and conversion consultants targeting enterprise clients (with dedicated localization for Saudi Arabia and the GCC), the platform executes parallel technical, UX, and conversion audits simultaneously across both **Mobile (390px iPhone 14 Pro)** and **Desktop (1440px)** viewports:

1. **Network & Security Protocol** (TLS socket handshake, SSL validity, TTFB, 301/308 redirect enforcement).
2. **DOM & Technical SEO** (Headings hierarchy, meta descriptions, image alts, tracking scripts, and technical stack).
3. **Saudi & GCC Conversion Optimization** (WhatsApp links, click-to-call, Saudi gateways like Mada/STC Pay/Tabby/Tamara, Arabic RTL orientation).
4. **Headless Mobile Viewport Simulation** (Playwright iPhone 14 Pro emulation, touch target ergonomics < 48px, horizontal layout overflow, mobile hero screenshot).
5. **Headless Desktop Viewport Simulation** (Playwright 1440px desktop viewport, desktop layout overflow, desktop hero screenshot, rendered dynamic DOM extraction).
6. **Dual PageSpeed Core Web Vitals** (Google PageSpeed Insights v5 REST API for both Mobile & Desktop Core Web Vitals: FCP, Speed Index, TBT, LCP, CLS, INP).
7. **AI Search Engine Optimization (AEO & GEO)** (AI bot crawl permissions, Schema.org entity linking, RAG direct-answer chunkability).

---

## 2. High-Level System Topology

```mermaid
flowchart TD
    %% Styling Definitions
    classDef clientLayer fill:#0284c7,stroke:#0369a1,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef gatewayLayer fill:#4f46e5,stroke:#4338ca,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef wNet fill:#059669,stroke:#047857,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef wDom fill:#0891b2,stroke:#0e7490,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef wSau fill:#d97706,stroke:#b45309,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef wMob fill:#e11d48,stroke:#be123c,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef wDesk fill:#2563eb,stroke:#1d4ed8,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef wExt fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef wAeo fill:#db2777,stroke:#be185d,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef serviceLayer fill:#9333ea,stroke:#7e22ce,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef storageLayer fill:#ea580c,stroke:#c2410c,stroke-width:2px,color:#ffffff,font-weight:bold
    classDef extNode fill:#334155,stroke:#1e293b,stroke-width:2px,color:#ffffff,font-weight:bold

    subgraph Tier1["🖥️ TIER 1: Presentation Layer (Client & Device Filter)"]
        UI["React 18 + Vite UI (App.tsx)<br/>(Device Filter: All | Mobile | Desktop)"]:::clientLayer
        SSEConsumer["SSE EventSource Stream Consumer<br/>(/api/audit/stream)"]:::clientLayer
        Views["Checklist | Dual Radar Gauges | Outreach | Viewport Switcher"]:::clientLayer
    end

    subgraph Tier2["⚡ TIER 2: Gateway & Orchestration (FastAPI Core)"]
        FastAPI["FastAPI Orchestrator (Uvicorn ASGI :8000)<br/>Static Routes /screenshots & /dist"]:::gatewayLayer
        AsyncEngine["Two-Phase Asyncio Concurrency Engine<br/>(Live SSE Stream Pipeline)"]:::gatewayLayer
    end

    subgraph Tier3["🛠️ TIER 3: The 7 Diagnostic Worker Streams (Two-Phase Execution)"]
        subgraph Phase1["Phase 1: Concurrent Device & Network Launch"]
            W1["Worker 1: Network & Security (network_scanner.py)"]:::wNet
            W4["Worker 4: Playwright Mobile (iPhone 14 Pro, 390px)"]:::wMob
            W5["Worker 5: Playwright Desktop (1440x900px Viewport)"]:::wDesk
            W6["Worker 6: Dual PageSpeed (Mobile + Desktop CWV)"]:::wExt
        end
        subgraph Phase2["Phase 2: Rendered DOM Fan-Out"]
            W2["Worker 2: DOM & Technical SEO (dom_seo_scanner.py)"]:::wDom
            W3["Worker 3: Saudi Conversion (saudi_scanner.py)"]:::wSau
            W7["Worker 7: Generative AEO & GEO (aeo_scanner.py)"]:::wAeo
        end
    end

    subgraph Tier4["🧠 TIER 4: Dual-Device Scoring & AI Outreach Services"]
        Scorer["Dual-Device Scoring Engine<br/>(Overall, Mobile & Desktop Scores)"]:::serviceLayer
        Evaluator["Metrics Evaluator<br/>(20+ Rules tagged with Device: all/mob/desk)"]:::serviceLayer
        GeminiService["Google Gemini AI Engine<br/>(Multimodal Vision + Arabic WhatsApp & Email)"]:::serviceLayer
    end

    subgraph Tier5["💾 TIER 5: Persistence & Artifacts"]
        SQLite[("aiosqlite Database<br/>audits.db (audits & leads tables)")]:::storageLayer
        Screenshots["Screenshots Repository<br/>backend/screenshots/*.png (Mobile + Desktop)"]:::storageLayer
    end

    subgraph Tier6["🌐 External Targets & Third-Party APIs"]
        TargetHost["Target Website Infrastructure<br/>(HTTP Sockets & Playwright Chromium)"]:::extNode
        GoogleCloud["Google Cloud APIs<br/>(Gemini 2.0/1.5/2.5 Flash & PageSpeed Insights v5)"]:::extNode
    end

    %% Wiring
    UI --> SSEConsumer
    SSEConsumer <== "HTTP SSE (data: chunked)" ==> FastAPI
    FastAPI --> AsyncEngine

    AsyncEngine -->|"Phase 1 Launch"| W1 & W4 & W5 & W6

    W4 & W5 -.->|"Pass Rendered Dynamic DOM"| W2 & W3 & W7

    W1 & W2 & W3 & W4 & W5 & W7 <===> TargetHost
    W6 <===> GoogleCloud

    W1 & W2 & W3 & W4 & W5 & W6 & W7 --> Scorer
    W1 & W2 & W3 & W4 & W5 & W6 & W7 --> Evaluator

    W4 & W5 -->|"Save Mobile & Desktop PNGs"| Screenshots
    Screenshots --> GeminiService
    GeminiService <===> GoogleCloud

    Scorer & Evaluator & GeminiService --> SQLite
    SQLite -.->|"Load Audit History"| FastAPI
    AsyncEngine -.->|"SSE event: complete (Full JSON)"| SSEConsumer
```

---

## 3. Component Architecture by Tier

### 3.1 Presentation Tier (React + Vite + Device Filter)
Located in `frontend/src/`:
* **Device Filter System:** Users can filter the entire checklist and analytics radar by `deviceFilter: 'all' | 'mobile' | 'desktop'`.
* **Dual Viewport Switcher:** Interactive device mock container switching between iPhone 14 Pro (390px) and Desktop (1440px) with interactive tap target and layout overflow overlays.
* **Dual Scorecards:** Displays `overall_score`, `mobile_overall_score`, and `desktop_overall_score` side-by-side.

### 3.2 API Orchestration Tier (FastAPI + Asyncio)
Located in `backend/main.py`:
* Concurrently fires `scan_headless_devices(target_url, audit_id, screenshots_dir)` which launches both mobile and desktop browser contexts inside an incognito Chromium instance.
* Streams SSE events for all workers (`mobile`, `desktop`, `network`, `external`, `dom_seo`, `saudi`, `aeo_geo`).

### 3.3 The 7 Diagnostic Worker Streams Matrix

| # | Worker Stream | Module File | Inspection Scope & Diagnostics | Device Relevancy |
|---|---|---|---|---|
| **1** | **Network & Security** | `network_scanner.py` | Direct TLS 1.2/1.3 socket handshake on port 443; SSL expiration days countdown; HTTP $\to$ HTTPS permanent redirect (301/308); TTFB latency; CDN identification. | All Devices |
| **2** | **DOM & Technical SEO** | `dom_seo_scanner.py` | Meta title & description length; H1 single hierarchy; image alt text coverage; robots.txt & sitemap.xml presence; pixels (GA4, GTM, Meta, Snapchat, TikTok). | All Devices |
| **3** | **Saudi Conversion** | `saudi_scanner.py` | Direct WhatsApp lead triggers (`wa.me`); click-to-call phone tags (`tel:`); Saudi payment gateways (Mada, Apple Pay, STC Pay, Tabby, Tamara); Arabic RTL orientation. | All Devices |
| **4** | **Playwright Mobile** | `mobile_browser.py` | Emulates iPhone 14 Pro (390×844px, DPR 3.0); touch targets < 48px; mobile layout overflow (`scrollWidth > clientWidth`); mobile fold & full PNGs. | Mobile |
| **5** | **Playwright Desktop** | `mobile_browser.py` | Emulates Desktop Viewport (1440×900px); desktop horizontal scroll overflow; desktop fold & full PNGs; extracts rendered SPA DOM. | Desktop |
| **6** | **Dual PageSpeed Vitals** | `external_intel.py` | Google PageSpeed Insights REST API querying both Mobile and Desktop Lighthouse: FCP, Speed Index, TBT, LCP, CLS, INP, and WebP compression savings. | Mobile & Desktop |
| **7** | **Generative AEO & GEO** | `aeo_scanner.py` | AI crawler directives in robots.txt (GPTBot, PerplexityBot, ClaudeBot); Schema.org JSON-LD structured data with `sameAs` entity links; RAG chunkability. | All Devices |

### 3.4 Dual-Device Scoring & AI Outreach Services
* **Device-Aware Deductions (`scoring_engine.py`):**
  * Mobile score ignores Desktop UX issues.
  * Desktop score ignores Mobile UX issues (tap targets, mobile overflow).
* **Multi-Model Gemini Fallback (`ai_pitch_engine.py`):**
  * Tries `gemini-2.0-flash`, `gemini-1.5-flash`, and `gemini-2.5-flash` with the mobile or desktop fold hero screenshot.
  * Instant fallback to high-converting deterministic Arabic WhatsApp, English cold email, and sales discovery scripts.

---
*Updated for WebAudit Pro Dual-Device Architecture.*
