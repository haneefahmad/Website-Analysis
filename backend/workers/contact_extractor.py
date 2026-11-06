import re
import json
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Any, Optional, Set, Tuple
import httpx
from bs4 import BeautifulSoup
from models import CompanyContactInfo, SocialProfile

# Regex patterns
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# Blacklist of domain/file extensions and dummy strings for emails
INVALID_EMAIL_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico",
    ".css", ".js", ".jsx", ".ts", ".tsx", ".map", ".woff", ".woff2", ".ttf", ".eot"
}

DUMMY_EMAIL_PATTERNS = {
    "example.com", "domain.com", "yoursite.com", "sample.com", "email.com",
    "test.com", "placeholder.com", "company.com", "wixpress.com", "sentry.io",
    "schema.org", "wordpress.org", "cloudflare.com", "googletagmanager.com",
    "google-analytics.com", "gravatar.com", "mysite.com", "yourdomain.com"
}

SOCIAL_PLATFORMS = {
    "linkedin": {
        "domains": ["linkedin.com"],
        "path_prefixes": ["/company/", "/in/", "/school/", "/pub/"],
        "excludes": ["/sharearticle", "/sharing", "/share", "/post", "/learning"]
    },
    "twitter": {
        "domains": ["twitter.com", "x.com"],
        "path_prefixes": [],
        "excludes": ["/intent", "/share", "/home", "/explore", "/search", "/hashtag", "/login", "/signup", "/tos", "/privacy", "/i/"]
    },
    "instagram": {
        "domains": ["instagram.com"],
        "path_prefixes": [],
        "excludes": ["/p/", "/reel/", "/reels/", "/explore/", "/direct/", "/accounts/", "/stories/", "/legal/"]
    },
    "facebook": {
        "domains": ["facebook.com", "fb.com"],
        "path_prefixes": [],
        "excludes": ["/sharer", "/share", "/plugins", "/tr", "/dialog", "/policies", "/legal", "/login", "/recover"]
    },
    "youtube": {
        "domains": ["youtube.com", "youtu.be"],
        "path_prefixes": ["/@", "/channel/", "/c/", "/user/"],
        "excludes": ["/watch", "/embed", "/playlist", "/feed", "/premium", "/shorts"]
    },
    "tiktok": {
        "domains": ["tiktok.com"],
        "path_prefixes": ["/@"],
        "excludes": ["/share", "/embed", "/legal", "/privacy"]
    },
    "github": {
        "domains": ["github.com"],
        "path_prefixes": [],
        "excludes": ["/features", "/pricing", "/marketplace", "/topics", "/collections", "/login", "/signup", "/about", "/security"]
    },
    "snapchat": {
        "domains": ["snapchat.com"],
        "path_prefixes": ["/add/"],
        "excludes": []
    },
    "telegram": {
        "domains": ["t.me", "telegram.me"],
        "path_prefixes": [],
        "excludes": ["/share"]
    },
    "threads": {
        "domains": ["threads.net"],
        "path_prefixes": ["/@"],
        "excludes": ["/terms", "/privacy"]
    },
    "pinterest": {
        "domains": ["pinterest.com"],
        "path_prefixes": [],
        "excludes": ["/pin/create", "/pin/", "/search/"]
    },
    "whatsapp": {
        "domains": ["wa.me", "api.whatsapp.com"],
        "path_prefixes": [],
        "excludes": []
    }
}


def is_valid_email(email: str) -> bool:
    email_clean = email.strip().lower()
    if len(email_clean) < 6 or len(email_clean) > 100:
        return False
    
    # Check extension
    for ext in INVALID_EMAIL_EXTENSIONS:
        if email_clean.endswith(ext):
            return False
            
    # Check dummy domains
    domain_part = email_clean.split("@")[-1]
    if domain_part in DUMMY_EMAIL_PATTERNS:
        return False
        
    local_part = email_clean.split("@")[0]
    if local_part in {"user", "name", "yourname", "test", "email", "username", "info@example"}:
        return False
        
    return True


def clean_phone_number(raw_phone: str) -> Optional[str]:
    # Remove excessive whitespace, trailing periods
    cleaned = raw_phone.strip().rstrip(".,;")
    digits = re.sub(r"\D", "", cleaned)
    
    # Valid phone numbers usually have between 8 and 15 digits
    if len(digits) < 8 or len(digits) > 15:
        return None
        
    # Exclude dummy sequences like 12345678 or 00000000
    if len(set(digits)) <= 2:
        return None
    if digits in {"12345678", "123456789", "1234567890", "0123456789"}:
        return None
        
    # Keep leading + if present
    if cleaned.startswith("+"):
        return f"+{cleaned[1:].strip()}"
    return cleaned


def deduplicate_phone_numbers(phone_list: List[str]) -> List[str]:
    """
    Deduplicates phone numbers by matching their digit sequence,
    preferring international format (+...) and clean formatting.
    """
    by_digits: Dict[str, str] = {}
    for p in phone_list:
        if not p:
            continue
        digits = re.sub(r"\D", "", p)
        if not digits:
            continue
        if digits not in by_digits:
            by_digits[digits] = p
        else:
            current = by_digits[digits]
            # Prefer + notation
            if p.startswith("+") and not current.startswith("+"):
                by_digits[digits] = p
            elif len(p) > len(current) and " " in p:
                by_digits[digits] = p
    return sorted(list(by_digits.values()))



def extract_social_from_url(url_str: str) -> Optional[Tuple[str, str, Optional[str]]]:
    """
    Returns (platform, normalized_url, handle) if matched, else None.
    """
    if not url_str or not isinstance(url_str, str):
        return None
    url_str = url_str.strip()
    if not (url_str.startswith("http://") or url_str.startswith("https://") or url_str.startswith("//")):
        return None

    try:
        parsed = urlparse(url_str)
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        path = parsed.path
        
        for platform, config in SOCIAL_PLATFORMS.items():
            if any(netloc == d or netloc.endswith("." + d) for d in config["domains"]):
                # Check excludes
                path_lower = path.lower()
                if any(ex in path_lower for ex in config["excludes"]):
                    return None
                    
                # Check required prefixes if any
                required_prefixes = config.get("path_prefixes", [])
                if required_prefixes:
                    if not any(path.startswith(p) or path_lower.startswith(p.lower()) for p in required_prefixes):
                        # Some platforms (like YouTube/LinkedIn) might have specific profile formats
                        if platform in ["linkedin", "youtube", "tiktok", "snapchat"]:
                            return None
                            
                # Exclude root domain with no handle
                clean_path = path.strip("/")
                if not clean_path and platform != "whatsapp":
                    return None
                    
                # Clean URL (remove tracking queries)
                clean_url = f"https://{netloc}/{clean_path}"
                
                # Deduce handle
                handle = None
                segments = [s for s in clean_path.split("/") if s]
                if segments:
                    handle = segments[-1].lstrip("@")
                    
                return platform, clean_url, handle
    except Exception:
        pass
    return None


def extract_contacts_from_html(html: str, base_url: str) -> Dict[str, Any]:
    emails: Set[str] = set()
    phones: Set[str] = set()
    whatsapp_numbers: Set[str] = set()
    social_dict: Dict[str, SocialProfile] = {}  # key by url
    contact_page_links: Set[str] = set()
    
    if not html:
        return {
            "emails": [],
            "phone_numbers": [],
            "whatsapp_numbers": [],
            "social_profiles": [],
            "contact_page_links": []
        }

    soup = BeautifulSoup(html, "lxml")

    # 1. <a> tags inspection
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        href_lower = href.lower()
        text = a.get_text().strip()
        text_lower = text.lower()

        # Email via mailto:
        if href_lower.startswith("mailto:"):
            raw_email = href[7:].split("?")[0].strip()
            if is_valid_email(raw_email):
                emails.add(raw_email.lower())

        # Phone via tel:
        elif href_lower.startswith("tel:"):
            raw_tel = href[4:].split("?")[0].strip()
            cleaned_tel = clean_phone_number(raw_tel)
            if cleaned_tel:
                phones.add(cleaned_tel)

        # WhatsApp via wa.me / api.whatsapp.com
        elif "wa.me/" in href_lower or "api.whatsapp.com/send" in href_lower:
            m = re.search(r"(?:wa\.me/|phone=)(\+?\d{8,15})", href)
            if m:
                wa_clean = clean_phone_number(m.group(1))
                if wa_clean:
                    whatsapp_numbers.add(wa_clean)
                    phones.add(wa_clean)
            social_dict[href] = SocialProfile(platform="whatsapp", url=href, handle=None)

        # Social profiles
        social_match = extract_social_from_url(href)
        if social_match:
            plat, clean_url, handle = social_match
            if plat != "whatsapp":
                social_dict[clean_url] = SocialProfile(platform=plat, url=clean_url, handle=handle)

        # Potential Contact / About Page link for secondary discovery
        contact_keywords = ["contact", "contact-us", "contactus", "about-us", "about", "connect", "get-in-touch", "تواصل", "اتصل", "من نحن"]
        is_contact_href = any(kw in href_lower for kw in ["contact", "contact-us", "contactus", "get-in-touch", "reach-us", "about-us"])
        is_contact_text = any(kw in text_lower for kw in contact_keywords)
        
        if (is_contact_href or is_contact_text) and not href.startswith("#") and not href_lower.startswith("javascript:"):
            resolved = urljoin(base_url, href)
            # Ensure it is on the same host
            try:
                if urlparse(resolved).netloc == urlparse(base_url).netloc:
                    contact_page_links.add(resolved)
            except Exception:
                pass

    # 2. Text regex search for emails
    # Search whole page text as well as attributes
    full_text = soup.get_text(separator=" ")
    raw_emails = EMAIL_REGEX.findall(full_text)
    for em in raw_emails:
        if is_valid_email(em):
            emails.add(em.lower())

    # 3. Text regex search for phones
    # International & regional formats
    phone_matches = re.findall(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}", full_text)
    for p in phone_matches:
        cleaned_p = clean_phone_number(p)
        if cleaned_p:
            phones.add(cleaned_p)

    # 4. JSON-LD Schema.org analysis
    schema_tags = soup.find_all("script", attrs={"type": re.compile(r"^application/ld\+json$", re.I)})
    for tag in schema_tags:
        try:
            content = tag.string or ""
            data = json.loads(content)

            def inspect_schema(node):
                if not isinstance(node, dict):
                    return
                # Check email
                if "email" in node and isinstance(node["email"], str):
                    if is_valid_email(node["email"]):
                        emails.add(node["email"].lower())
                # Check telephone
                if "telephone" in node and isinstance(node["telephone"], str):
                    cleaned_tel = clean_phone_number(node["telephone"])
                    if cleaned_tel:
                        phones.add(cleaned_tel)
                # Check sameAs for social profiles
                same_as = node.get("sameAs", [])
                if isinstance(same_as, str):
                    same_as = [same_as]
                if isinstance(same_as, list):
                    for link in same_as:
                        if isinstance(link, str):
                            sm = extract_social_from_url(link)
                            if sm:
                                plat, clean_url, handle = sm
                                social_dict[clean_url] = SocialProfile(platform=plat, url=clean_url, handle=handle)

                # Recursive walk
                for v in node.values():
                    if isinstance(v, dict):
                        inspect_schema(v)
                    elif isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                inspect_schema(item)

            if isinstance(data, list):
                for item in data:
                    inspect_schema(item)
            elif isinstance(data, dict):
                inspect_schema(data)
        except Exception:
            pass

    return {
        "emails": list(emails),
        "phone_numbers": list(phones),
        "whatsapp_numbers": list(whatsapp_numbers),
        "social_profiles": list(social_dict.values()),
        "contact_page_links": list(contact_page_links)
    }


async def extract_company_contacts(
    target_url: str,
    html_content: str = "",
    rendered_html: str = ""
) -> CompanyContactInfo:
    """
    Orchestrates extraction of emails, phone numbers, WhatsApp, and social media profiles.
    Searches both raw and Playwright-rendered HTML, and if contact info is sparse,
    proactively crawls discovered /contact or /about pages.
    """
    parsed = urlparse(target_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # Step 1: Extract from homepage (raw + rendered)
    combined_home_html = f"{html_content}\n{rendered_html}" if rendered_html else html_content
    home_data = extract_contacts_from_html(combined_home_html, base_url)

    all_emails: Set[str] = set(home_data["emails"])
    all_phones: Set[str] = set(home_data["phone_numbers"])
    all_whatsapp: Set[str] = set(home_data["whatsapp_numbers"])
    social_map: Dict[str, SocialProfile] = {p.url: p for p in home_data["social_profiles"]}
    visited_pages: List[str] = []

    # Step 2: If no email or phone found, or to discover more complete contacts,
    # inspect candidate contact / about pages
    candidate_links = [
        link for link in home_data["contact_page_links"] 
        if link.rstrip("/") != target_url.rstrip("/")
    ]

    # Prioritize contact pages over generic about pages
    candidate_links.sort(key=lambda u: (
        0 if any(k in u.lower() for k in ["contact", "اتصل", "تواصل"]) else 1
    ))

    # Fetch top 1-2 candidate pages with strict timeout to keep audit blazing fast
    if candidate_links:
        pages_to_crawl = candidate_links[:2]
        async with httpx.AsyncClient(timeout=5.0, verify=False, follow_redirects=True) as client:
            for page_url in pages_to_crawl:
                try:
                    resp = await client.get(
                        page_url,
                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
                    )
                    if resp.status_code == 200 and resp.text:
                        visited_pages.append(page_url)
                        sec_data = extract_contacts_from_html(resp.text, base_url)
                        all_emails.update(sec_data["emails"])
                        all_phones.update(sec_data["phone_numbers"])
                        all_whatsapp.update(sec_data["whatsapp_numbers"])
                        for sp in sec_data["social_profiles"]:
                            social_map[sp.url] = sp
                except Exception:
                    pass

    # Sort social profiles in standard order
    platform_order = {
        "linkedin": 1, "twitter": 2, "instagram": 3, "facebook": 4,
        "youtube": 5, "tiktok": 6, "github": 7, "whatsapp": 8,
        "telegram": 9, "threads": 10, "snapchat": 11, "pinterest": 12
    }
    sorted_socials = sorted(
        social_map.values(),
        key=lambda x: (platform_order.get(x.platform, 99), x.platform)
    )

    return CompanyContactInfo(
        emails=sorted(list(all_emails)),
        phone_numbers=deduplicate_phone_numbers(list(all_phones)),
        whatsapp_numbers=deduplicate_phone_numbers(list(all_whatsapp)),
        social_profiles=sorted_socials,
        contact_pages=visited_pages or candidate_links[:2]
    )
