from typing import List, Dict, Any
from models import AuditIssue, Severity

def _score_category_subset(issues: List[AuditIssue], device: str) -> Dict[str, Any]:
    categories = {
        "Technical": {"base": 100, "weight": 0.20},
        "Security": {"base": 100, "weight": 0.20},
        "Mobile UX": {"base": 100, "weight": 0.20},
        "SEO": {"base": 100, "weight": 0.15},
        "Conversion": {"base": 100, "weight": 0.15},
        "AEO & GEO": {"base": 100, "weight": 0.10}
    }

    deductions = {
        Severity.CRITICAL: 25,
        Severity.WARNING: 12,
        Severity.INFO: 4
    }

    category_scores = {cat: 100 for cat in categories}

    for issue in issues:
        # Check device relevancy:
        # If calculating for desktop, skip Mobile UX specific issues (tap targets, mobile overflow)
        if device == "desktop" and issue.category == "Mobile UX":
            continue
        # If calculating for mobile, skip Desktop UX specific issues
        if device == "mobile" and issue.category == "Desktop UX":
            continue

        target_cat = issue.category
        if target_cat not in category_scores:
            if "Localization" in target_cat or "Branding" in target_cat:
                target_cat = "Conversion"
            elif "Performance" in target_cat:
                target_cat = "Technical"
            elif "Compliance" in target_cat or "Tracking" in target_cat:
                target_cat = "SEO"
            elif "Desktop UX" in target_cat:
                target_cat = "Mobile UX"
            else:
                target_cat = "Technical"

        penalty = deductions.get(issue.severity, 5)
        category_scores[target_cat] = max(0, category_scores[target_cat] - penalty)

    overall = 0.0
    for cat, meta in categories.items():
        score = category_scores.get(cat, 100)
        overall += score * meta["weight"]

    return {
        "overall_score": max(5, min(100, round(overall))),
        "scores_by_category": category_scores
    }

def calculate_audit_scores(all_issues: List[AuditIssue]) -> Dict[str, Any]:
    categories = {
        "Technical": {"base": 100, "weight": 0.20},
        "Security": {"base": 100, "weight": 0.20},
        "Mobile UX": {"base": 100, "weight": 0.20},
        "SEO": {"base": 100, "weight": 0.15},
        "Conversion": {"base": 100, "weight": 0.15},
        "AEO & GEO": {"base": 100, "weight": 0.10}
    }

    deductions = {
        Severity.CRITICAL: 25,
        Severity.WARNING: 12,
        Severity.INFO: 4
    }

    category_scores = {cat: 100 for cat in categories}
    crit_count = 0
    warn_count = 0
    info_count = 0

    for issue in all_issues:
        if issue.severity == Severity.CRITICAL:
            crit_count += 1
        elif issue.severity == Severity.WARNING:
            warn_count += 1
        else:
            info_count += 1

        target_cat = issue.category
        if target_cat not in category_scores:
            if "Localization" in target_cat or "Branding" in target_cat:
                target_cat = "Conversion"
            elif "Performance" in target_cat:
                target_cat = "Technical"
            elif "Compliance" in target_cat or "Tracking" in target_cat:
                target_cat = "SEO"
            elif "Desktop UX" in target_cat:
                target_cat = "Mobile UX"
            else:
                target_cat = "Technical"

        penalty = deductions.get(issue.severity, 5)
        category_scores[target_cat] = max(0, category_scores[target_cat] - penalty)

    # Weighted overall score
    overall = 0.0
    for cat, meta in categories.items():
        score = category_scores.get(cat, 100)
        overall += score * meta["weight"]

    mobile_data = _score_category_subset(all_issues, "mobile")
    desktop_data = _score_category_subset(all_issues, "desktop")

    return {
        "overall_score": max(5, min(100, round(overall))),
        "scores_by_category": category_scores,
        "mobile_overall_score": mobile_data["overall_score"],
        "desktop_overall_score": desktop_data["overall_score"],
        "mobile_scores_by_category": mobile_data["scores_by_category"],
        "desktop_scores_by_category": desktop_data["scores_by_category"],
        "critical_count": crit_count,
        "warning_count": warn_count,
        "info_count": info_count
    }
