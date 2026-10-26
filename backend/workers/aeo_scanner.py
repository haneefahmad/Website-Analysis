import re
import json
from urllib.parse import urlparse, urljoin
import urllib.robotparser
import httpx
from bs4 import BeautifulSoup
from models import AEOGEOResult, AuditIssue, Severity

async def scan_aeo_and_geo(target_url: str, html_content: str) -> AEOGEOResult:
    result = AEOGEOResult()
    parsed = urlparse(target_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    soup = BeautifulSoup(html_content, "lxml")

    # 1. AI Bots Crawlability & Permissions in robots.txt
    ai_bots = {
        "OAI-SearchBot": "OpenAI / SearchGPT Search Engine",
        "GPTBot": "ChatGPT Web Crawler",
        "PerplexityBot": "Perplexity AI Answer Engine",
        "Google-Extended": "Google Gemini & AI Overviews Training",
        "ClaudeBot": "Anthropic Claude AI Assistant",
        "Applebot-Extended": "Apple Intelligence Search"
    }

    async with httpx.AsyncClient(timeout=6.0, verify=False) as client:
        try:
            robots_url = urljoin(base_url, "/robots.txt")
            resp = await client.get(robots_url)
            if resp.status_code == 200:
                robots_content = resp.text
                
                # Check each bot's permission
                for bot, description in ai_bots.items():
                    rp = urllib.robotparser.RobotFileParser()
                    rp.parse(robots_content.splitlines())
                    is_allowed = rp.can_fetch(bot, target_url)
                    result.ai_bots_permissions[bot] = is_allowed

                    if not is_allowed:
                        result.ai_bots_blocked.append(bot)

                if "OAI-SearchBot" in result.ai_bots_blocked or "PerplexityBot" in result.ai_bots_blocked:
                    result.issues.append(AuditIssue(
                        category="AEO & GEO",
                        item_number=55,
                        title="AI Search Engines Blocked in robots.txt",
                        description=f"Your robots.txt explicitly blocks modern AI answer engines: {', '.join(result.ai_bots_blocked)}. This prevents your business from ever being cited or recommended in SearchGPT or Perplexity.",
                        severity=Severity.CRITICAL,
                        recommendation="Remove disallow rules for OAI-SearchBot and PerplexityBot to allow AI search citation indexing.",
                        proof={"blocked_bots": result.ai_bots_blocked}
                    ))
            else:
                # If robots.txt doesn't exist, bots are allowed by default
                for bot in ai_bots:
                    result.ai_bots_permissions[bot] = True
        except Exception:
            for bot in ai_bots:
                result.ai_bots_permissions[bot] = True

    # 2. Entity Disambiguation & JSON-LD Schema (sameAs, LocalBusiness)
    schema_tags = soup.find_all("script", attrs={"type": re.compile(r"^application/ld\+json$", re.I)})
    found_sameas = []
    has_localbusiness = False
    has_faq = False

    for tag in schema_tags:
        try:
            content = tag.string or ""
            data = json.loads(content)
            
            # Helper to inspect schema dicts
            def inspect_node(node):
                nonlocal has_localbusiness, has_faq, found_sameas
                if not isinstance(node, dict):
                    return
                ntype = str(node.get("@type", "")).lower()
                if any(x in ntype for x in ["localbusiness", "organization", "store", "medical", "clinic"]):
                    has_localbusiness = True
                if "faqpage" in ntype:
                    has_faq = True

                same_as = node.get("sameAs", [])
                if isinstance(same_as, str):
                    same_as = [same_as]
                if isinstance(same_as, list):
                    found_sameas.extend([str(s) for s in same_as if isinstance(s, str)])

                # Traverse children
                for v in node.values():
                    if isinstance(v, dict):
                        inspect_node(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                inspect_node(item)

            if isinstance(data, list):
                for item in data:
                    inspect_node(item)
            elif isinstance(data, dict):
                inspect_node(data)
        except Exception:
            continue

    result.has_localbusiness_schema = has_localbusiness
    result.has_faq_schema = has_faq
    result.has_sameas_schema = len(found_sameas) > 0
    result.sameas_urls = found_sameas

    if not result.has_localbusiness_schema:
        result.issues.append(AuditIssue(
            category="AEO & GEO",
            item_number=48,
            title="Missing LocalBusiness / Organization Schema",
            description="The site does not include structured JSON-LD schema defining the organization entity, contact, and geo-coordinates for search engines.",
            severity=Severity.WARNING,
            recommendation="Add Schema.org LocalBusiness JSON-LD markup with complete address, coordinates, and phone details.",
            proof={"schema_found": False}
        ))

    if not result.has_sameas_schema:
        result.issues.append(AuditIssue(
            category="AEO & GEO",
            item_number=55,
            title="Missing 'sameAs' Entity Disambiguation in Schema",
            description="Schema lacks 'sameAs' links to authoritative entity sources (Wikidata, Google Knowledge Graph, LinkedIn, official social channels). Without this, LLMs cannot reliably map your brand entity.",
            severity=Severity.INFO,
            recommendation="Include 'sameAs' array in your Organization schema linking to verified business registry, LinkedIn, and social profiles.",
            proof={"sameAs": []}
        ))

    # 3. Content Chunkability & Direct-Answer Q&A Formatting (RAG-Readiness)
    question_triggers = re.compile(r"\b(what|how|why|when|where|who|cost|price|كم|كيف|ما هو|ما هي|لماذا|أين|متى)\b", re.IGNORECASE)
    headings = soup.find_all(["h2", "h3"])
    direct_qa_list = []

    for h in headings:
        h_text = h.get_text(strip=True)
        if question_triggers.search(h_text) or "?" in h_text or "؟" in h_text:
            # Look for the immediate next paragraph
            sibling = h.find_next_sibling()
            while sibling and sibling.name not in ["p", "h1", "h2", "h3", "h4", "div"]:
                sibling = sibling.find_next_sibling()
            
            if sibling and sibling.name == "p":
                p_text = sibling.get_text(strip=True)
                words = p_text.split()
                # Check for 25-60 word concise direct answer pattern
                if 20 <= len(words) <= 75:
                    direct_qa_list.append({"question": h_text, "answer_preview": p_text[:120] + "..."})

    result.direct_qa_pairs_count = len(direct_qa_list)
    result.direct_qa_samples = direct_qa_list[:3]

    # Tables & Semantic Lists count
    result.tables_count = len(soup.find_all("table"))
    result.semantic_lists_count = len(soup.find_all(["ul", "ol"]))

    if result.direct_qa_pairs_count == 0:
        result.issues.append(AuditIssue(
            category="AEO & GEO",
            item_number=55,
            title="No Direct-Answer Q&A Formatting (Low AI Chunkability)",
            description="The page lacks direct question-and-answer formatted headings. LLM RAG pipelines specifically extract 30–60 word answer blocks immediately following question headings.",
            severity=Severity.WARNING,
            recommendation="Structure common customer questions as <h2> tags followed immediately by concise 40-word factual answers.",
            proof={"qa_pairs_found": 0}
        ))

    return result
