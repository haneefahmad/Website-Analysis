import re
from datetime import datetime
from bs4 import BeautifulSoup
from models import SaudiConversionResult, AuditIssue, Severity

async def scan_saudi_conversion(target_url: str, html_content: str, rendered_html: str = "") -> SaudiConversionResult:
    result = SaudiConversionResult()
    combined_html = f"{html_content}\n{rendered_html}" if rendered_html else html_content
    soup = BeautifulSoup(combined_html, "lxml")
    current_year = datetime.now().year

    # 1. WhatsApp Button / Direct Link
    wa_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if "wa.me/" in href or "api.whatsapp.com/send" in href or "whatsapp://" in href:
            wa_links.append(a["href"])
    if wa_links:
        result.has_whatsapp = True
        result.whatsapp_links = wa_links
    else:
        result.has_whatsapp = False
        result.issues.append(AuditIssue(
            category="Conversion",
            item_number=17,
            title="Missing Direct WhatsApp Contact Button",
            description="No WhatsApp click-to-chat link detected. Over 80% of direct commercial inquiries in Saudi Arabia occur through WhatsApp.",
            severity=Severity.CRITICAL,
            recommendation="Add a floating WhatsApp click-to-chat button prominently on mobile and desktop.",
            proof={"whatsapp_detected": False}
        ))

    # 2. Click-to-Call (tel:)
    phone_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("tel:"):
            phone_links.append(href.replace("tel:", "").strip())
            
    # Search for phone numbers in visible page text
    body_text_full = soup.get_text()
    raw_phones = re.findall(r"(?:\+?\d{1,3}[- ]?)?\(?\d{2,4}\)?[- ]?\d{3,4}[- ]?\d{3,4}", body_text_full)
    detected_plain_phones = list(set([p.strip() for p in raw_phones if len(re.sub(r'\D', '', p)) >= 8]))[:3]

    if phone_links:
        result.has_click_to_call = True
        result.phone_numbers = phone_links
    elif detected_plain_phones:
        result.has_click_to_call = False
        result.phone_numbers = detected_plain_phones
        result.issues.append(AuditIssue(
            category="Conversion",
            item_number=18,
            title="Phone Number Present But Not Clickable (tel:)",
            description=f"Found phone number ({', '.join(detected_plain_phones)}) in plain text, but it is not wrapped in a clickable <a href='tel:...'> link. Mobile visitors cannot tap to call directly.",
            severity=Severity.WARNING,
            recommendation=f"Wrap {detected_plain_phones[0]} in an <a href='tel:{re.sub(r'[^0-9+]', '', detected_plain_phones[0])}'> tag to allow one-tap dialing.",
            proof={"plain_text_numbers": detected_plain_phones, "tel_links_count": 0}
        ))
    else:
        result.has_click_to_call = False
        result.issues.append(AuditIssue(
            category="Conversion",
            item_number=18,
            title="No Direct Click-to-Call (tel:) Link",
            description="No phone numbers or click-to-call links were detected on the page.",
            severity=Severity.WARNING,
            recommendation="Add your phone number wrapped in a clickable <a href='tel:+966...'> link.",
            proof={"click_to_call": False}
        ))

    # 3. Arabic Language & RTL Direction
    html_tag = soup.find("html")
    lang_attr = (html_tag.get("lang") or "").lower() if html_tag else ""
    dir_attr = (html_tag.get("dir") or "").lower() if html_tag else ""

    # Check for Arabic text in page body
    body_text = soup.get_text()
    arabic_char_count = len(re.findall(r"[\u0600-\u06FF]", body_text))

    # Check for alternate Arabic hreflang or navigation language switchers
    has_ar_hreflang = bool(soup.find("link", rel="alternate", attrs={"hreflang": re.compile(r"^ar", re.I)}))
    has_ar_switcher = bool(re.search(r"عربي|arabic|/ar[\"\'/]", html_content, re.I))

    if "ar" in lang_attr or arabic_char_count > 100 or has_ar_hreflang or has_ar_switcher:
        result.has_arabic = True
        if has_ar_hreflang:
            # Verified bilingual site
            pass
    else:
        result.issues.append(AuditIssue(
            category="Localization",
            item_number=25,
            title="Missing Arabic Version or Arabic Content",
            description="The website does not offer an Arabic version. In the Saudi market, Arabic parity is essential for consumer trust and search volume.",
            severity=Severity.CRITICAL,
            recommendation="Implement a localized Arabic version with native copy and proper hreflang tagging.",
            proof={"lang": lang_attr, "arabic_char_count": arabic_char_count}
        ))

    if dir_attr == "rtl" or 'direction: rtl' in str(soup).lower():
        result.is_rtl = True
    elif result.has_arabic:
        result.issues.append(AuditIssue(
            category="Localization",
            item_number=26,
            title="Arabic Content Present Without RTL Layout",
            description="Arabic text was detected but the root <html> tag lacks dir='rtl', causing flipped punctuation and unnatural alignment.",
            severity=Severity.WARNING,
            recommendation="Set dir='rtl' on the <html> or body tag for Arabic page views.",
            proof={"dir": dir_attr}
        ))

    # 4. Local Saudi Payment Options (mada, Apple Pay, STC Pay, Tabby, Tamara)
    full_html_lower = html_content.lower()
    
    if "mada" in full_html_lower or "مدى" in full_html_lower:
        result.has_mada = True
    if "apple pay" in full_html_lower or "apple-pay" in full_html_lower or "applepay" in full_html_lower:
        result.has_apple_pay = True
    if "stc pay" in full_html_lower or "stcpay" in full_html_lower or "stc bank" in full_html_lower:
        result.has_stc_pay = True
    if "tabby" in full_html_lower or "تابي" in full_html_lower:
        result.has_tabby = True
    if "tamara" in full_html_lower or "تمارا" in full_html_lower:
        result.has_tamara = True

    # If it looks like an e-commerce or booking store, verify mada and Apple Pay
    is_ecommerce = any(token in full_html_lower for token in ["cart", "checkout", "سلة", "الدفع", "add to cart", "buy now", "price", "ر.س", "sar"])
    if is_ecommerce and not (result.has_mada or result.has_apple_pay):
        result.issues.append(AuditIssue(
            category="Conversion",
            item_number=23,
            title="E-commerce Store Missing mada or Apple Pay",
            description="Checkout/pricing tokens detected, but neither mada nor Apple Pay was found. In Saudi Arabia, mada and Apple Pay account for over 85% of online card transactions.",
            severity=Severity.CRITICAL,
            recommendation="Integrate a local payment gateway supporting mada, Apple Pay, and BNPL (Tabby/Tamara).",
            proof={"is_ecommerce": True, "mada": result.has_mada, "apple_pay": result.has_apple_pay}
        ))

    # 5. Developer Abandonment & Placeholder Content
    placeholder_matches = []
    if "lorem ipsum" in full_html_lower:
        placeholder_matches.append("Lorem ipsum placeholder text")
    if "just another wordpress site" in full_html_lower or "موقع ووردبريس جديد" in full_html_lower:
        placeholder_matches.append("Default WordPress tagline")
    if "hello world!" in full_html_lower or "أهلاً بالعالم!" in full_html_lower:
        placeholder_matches.append("Default 'Hello World' sample post")

    if placeholder_matches:
        result.placeholder_text_found = True
        result.placeholder_snippets = placeholder_matches
        result.issues.append(AuditIssue(
            category="Branding",
            item_number=21,
            title="Developer Placeholder Text Discovered",
            description=f"Found default template placeholder text ({', '.join(placeholder_matches)}) left in production.",
            severity=Severity.WARNING,
            recommendation="Replace all template placeholder text with verified company copy.",
            proof={"matches": placeholder_matches}
        ))

    # 6. Outdated Copyright Year
    copyright_match = re.search(r"©\s*(?:20\d{2}\s*[-–]\s*)?(20\d{2})", body_text)
    if copyright_match:
        year_found = int(copyright_match.group(1))
        result.copyright_year = year_found
        if year_found < current_year:
            result.outdated_copyright = True
            result.issues.append(AuditIssue(
                category="Branding",
                item_number=20,
                title=f"Outdated Footer Copyright Year (© {year_found})",
                description=f"Footer copyright displays {year_found} instead of {current_year}. This signals an unmaintained or abandoned website to visitors.",
                severity=Severity.INFO,
                recommendation=f"Update the copyright year to {current_year} (or use dynamic JavaScript to keep it current automatically).",
                proof={"year_found": year_found, "current_year": current_year}
            ))

    return result
