from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class Severity(str, Enum):
    CRITICAL = "critical"  # 🔴
    WARNING = "warning"    # 🟡
    INFO = "info"          # 🟢

class AuditIssue(BaseModel):
    category: str
    item_number: int
    title: str
    description: str
    severity: Severity
    recommendation: str
    proof: Optional[Dict[str, Any]] = None

class NetworkSecurityResult(BaseModel):
    is_live: bool = False
    status_code: Optional[int] = None
    ssl_valid: bool = False
    ssl_issuer: Optional[str] = None
    ssl_days_remaining: Optional[int] = None
    ssl_expired: bool = False
    http_to_https_redirect: bool = False
    ttfb_ms: Optional[float] = None
    ttfb_rating: str = "Unknown"  # Good (<300ms), Needs Improvement (300-800ms), Poor (>800ms)
    server_header: Optional[str] = None
    cdn_detected: Optional[str] = None
    issues: List[AuditIssue] = []

class DOMSEOResult(BaseModel):
    title: Optional[str] = None
    title_length: int = 0
    meta_description: Optional[str] = None
    h1_count: int = 0
    h1_tags: List[str] = []
    total_images: int = 0
    images_missing_alt: int = 0
    sitemap_exists: bool = False
    robots_exists: bool = False
    robots_blocking_site: bool = False
    canonical_url: Optional[str] = None
    canonical_valid: bool = False
    mixed_content_found: bool = False
    mixed_content_urls: List[str] = []
    ga4_detected: bool = False
    ga4_id: Optional[str] = None
    gtm_detected: bool = False
    gtm_id: Optional[str] = None
    meta_pixel_detected: bool = False
    snap_pixel_detected: bool = False
    tiktok_pixel_detected: bool = False
    privacy_policy_found: bool = False
    terms_found: bool = False
    cookie_banner_found: bool = False
    issues: List[AuditIssue] = []

class SaudiConversionResult(BaseModel):
    has_whatsapp: bool = False
    whatsapp_links: List[str] = []
    has_click_to_call: bool = False
    phone_numbers: List[str] = []
    has_arabic: bool = False
    is_rtl: bool = False
    has_mada: bool = False
    has_apple_pay: bool = False
    has_stc_pay: bool = False
    has_tabby: bool = False
    has_tamara: bool = False
    outdated_copyright: bool = False
    copyright_year: Optional[int] = None
    placeholder_text_found: bool = False
    placeholder_snippets: List[str] = []
    issues: List[AuditIssue] = []

class HeadlessMobileResult(BaseModel):
    horizontal_scroll_overflow: bool = False
    viewport_width: int = 390
    scroll_width: int = 390
    overflow_elements: List[str] = []
    small_tap_targets_count: int = 0
    small_tap_target_samples: List[str] = []
    fold_screenshot_path: Optional[str] = None
    full_screenshot_path: Optional[str] = None
    local_fcp_ms: Optional[int] = None
    local_load_time_ms: Optional[int] = None
    local_dom_interactive_ms: Optional[int] = None
    rendered_html: Optional[str] = None
    issues: List[AuditIssue] = []

class ExternalIntelResult(BaseModel):
    mobile_performance_score: Optional[int] = None  # 0 - 100
    lcp_seconds: Optional[float] = None
    cls_score: Optional[float] = None
    inp_ms: Optional[float] = None
    image_savings_mb: Optional[float] = None
    gbp_claimed: Optional[bool] = None
    gbp_rating: Optional[float] = None
    gbp_reviews_count: Optional[int] = None
    issues: List[AuditIssue] = []

class AEOGEOResult(BaseModel):
    ai_bots_permissions: Dict[str, bool] = {}  # e.g. {"GPTBot": True, "PerplexityBot": False}
    ai_bots_blocked: List[str] = []
    has_sameas_schema: bool = False
    sameas_urls: List[str] = []
    has_localbusiness_schema: bool = False
    has_faq_schema: bool = False
    direct_qa_pairs_count: int = 0
    direct_qa_samples: List[Dict[str, str]] = []
    tables_count: int = 0
    semantic_lists_count: int = 0
    issues: List[AuditIssue] = []

class AIPitchResult(BaseModel):
    mobile_fold_review: Optional[str] = None
    whatsapp_script_arabic: Optional[str] = None
    cold_email_english: Optional[str] = None
    cold_email_arabic: Optional[str] = None
    discovery_questions: List[str] = []

class FullAuditResponse(BaseModel):
    audit_id: str
    target_url: str
    scanned_at: datetime = Field(default_factory=datetime.utcnow)
    overall_score: int = 0
    scores_by_category: Dict[str, int] = {}
    total_critical_issues: int = 0
    total_warning_issues: int = 0
    total_info_issues: int = 0
    network: Optional[NetworkSecurityResult] = None
    dom_seo: Optional[DOMSEOResult] = None
    saudi_conversion: Optional[SaudiConversionResult] = None
    mobile: Optional[HeadlessMobileResult] = None
    external: Optional[ExternalIntelResult] = None
    aeo_geo: Optional[AEOGEOResult] = None
    ai_pitch: Optional[AIPitchResult] = None
    all_issues: List[AuditIssue] = []
