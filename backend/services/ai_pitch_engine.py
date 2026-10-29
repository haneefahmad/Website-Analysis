import os
import json
from typing import List, Optional
from PIL import Image
from models import AIPitchResult, AuditIssue, Severity

async def generate_ai_pitch(
    target_url: str,
    top_issues: List[AuditIssue],
    screenshot_path: Optional[str] = None,
    gemini_api_key: Optional[str] = None
) -> AIPitchResult:
    result = AIPitchResult()

    # Prepare bullet points of the critical issues found
    critical_flaws = [f"• {iss.title}: {iss.description}" for iss in top_issues if iss.severity in (Severity.CRITICAL, Severity.WARNING)]
    flaws_text = "\n".join(critical_flaws[:5]) if critical_flaws else "• General performance and mobile optimizations needed."

    # Always initialize high-converting, battle-tested templates FIRST
    result.mobile_fold_review = "Visual inspection and mobile UX evaluation completed."
    result.whatsapp_script_arabic = f"""السلام عليكم ورحمة الله وبركاته،
لاحظت موقعكم ({target_url}) وحبيت أنبهكم على نقاط بسيطة تأثر بشكل مباشر على تحويل الزوار إلى عملاء:
{flaws_text}

نقاط بسيطة ولكن تعديلها يرفع نسبة الاتصالات والمبيعات بشكل ملحوظ. هل يناسبك نتناقش بدقيقة حول طريقة حلها؟"""

    result.cold_email_english = f"""Subject: Quick observation regarding {target_url}

Hi Team,

I came across {target_url} and ran a quick diagnostic audit on your mobile experience and technical speed. 

I noticed a few high-impact friction points that are likely causing potential clients to bounce before reaching out:
{flaws_text}

With over 70% of local traffic browsing on mobile, resolving these technical hurdles typically leads to an immediate increase in inquiries and booking conversions.

Would you be open to a brief 5-minute call this week to review the full diagnostic breakdown?

Best regards,"""

    result.cold_email_arabic = f"""الموضوع: ملاحظات سريعة حول تحسين أداء موقعكم {target_url}

مرحباً بكم،

أثناء تصفحي لموقعكم ({target_url}) وإجراء فحص تقني سريع لتجربة المستخدم على الجوال، لاحظت بعض النقاط الفنية التي قد تؤثر على سرعة التفاعل وثقة الزوار:
{flaws_text}

معظم العملاء اليوم يتصفحون عبر الجوال، ومعالجة هذه النقاط تنعكس فوراً على زيادة المبيعات والاتصالات الواردة.

هل يناسبكم اتصال سريع لمدة 5 دقائق لمناقشة التقرير الفني الكامل والحلول المقترحة؟

مع أطيب التحيات،"""

    result.discovery_questions = [
        "How do incoming inquiries from the website currently get routed to your sales or booking team?",
        "What percentage of your customers prefer contacting you directly over WhatsApp versus web forms?",
        "Have you noticed a drop-off in conversions from mobile visitors compared to desktop users?",
        "Who handles maintenance and speed updates for your current website infrastructure?"
    ]

    # If no Gemini API key, return the deterministic templates immediately
    if not gemini_api_key:
        return result

    # When Gemini API key is present: attempt AI-generated personalization
    try:
        from google import genai
        from google.genai import types

        keys_to_try = [gemini_api_key]
        from config import settings
        if settings.PAGESPEED_API_KEY and settings.PAGESPEED_API_KEY != gemini_api_key:
            keys_to_try.append(settings.PAGESPEED_API_KEY)

        prompt = f"""You are an elite digital transformation and web agency sales strategist.
Target Website: {target_url}
The automated diagnostic scan discovered these verified issues:
{flaws_text}

Generate a JSON response matching this schema:
{{
  "mobile_fold_review": "string (A sharp 2-sentence assessment of the above-the-fold mobile experience)",
  "whatsapp_script_arabic": "string (A friendly, respectful, high-converting Arabic WhatsApp outreach message to the business owner, highlighting 2-3 specific friction points without being insulting)",
  "cold_email_english": "string (A concise, value-first executive cold email pitch for the managing director or founder)",
  "cold_email_arabic": "string (The Arabic translation/adaptation of the executive cold email)",
  "discovery_questions": ["string", "string", "string", "string"] (4 tactical questions for a discovery sales call exploring manual operations, CRM, and WhatsApp workflows)
}}
Output ONLY valid JSON.
"""

        contents = []
        if screenshot_path and os.path.exists(screenshot_path):
            try:
                img = Image.open(screenshot_path)
                contents.append(img)
            except Exception:
                pass

        contents.append(prompt)

        response = None
        candidate_models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-flash"]
        
        for k in keys_to_try:
            try:
                client = genai.Client(api_key=k)
                for candidate_model in candidate_models:
                    try:
                        response = client.models.generate_content(
                            model=candidate_model,
                            contents=contents,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                temperature=0.2
                            )
                        )
                        if response and response.text:
                            break
                    except Exception:
                        continue
                if response and response.text:
                    break
            except Exception:
                continue

        if response and response.text:
            data = json.loads(response.text)
            if data.get("mobile_fold_review"):
                result.mobile_fold_review = data["mobile_fold_review"]
            if data.get("whatsapp_script_arabic"):
                result.whatsapp_script_arabic = data["whatsapp_script_arabic"]
            if data.get("cold_email_english"):
                result.cold_email_english = data["cold_email_english"]
            if data.get("cold_email_arabic"):
                result.cold_email_arabic = data["cold_email_arabic"]
            if data.get("discovery_questions") and isinstance(data["discovery_questions"], list) and len(data["discovery_questions"]) > 0:
                result.discovery_questions = data["discovery_questions"]

    except Exception:
        # Defaults are already in place
        pass

    return result
