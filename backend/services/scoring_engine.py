from typing import List, Dict
from models import AuditIssue, Severity

def calculate_audit_scores(all_issues: List[AuditIssue]) -> Dict[str, any]:
    # Category base points
    categories = {
        "Technical": {"base": 100, "weight": 0.20},
        "Security": {"base": 100, "weight": 0.20},
        "Mobile UX": {"base": 100, "weight": 0.20},
        "SEO": {"base": 100, "weight": 0.15},
        "Conversion": {"base": 100, "weight": 0.15},
        "AEO & GEO": {"base": 100, "weight": 0.10}
    }

    # Deductions per issue severity
    deductions = {
        Severity.CRITICAL: 25,
        Severity.WARNING: 12,
        Severity.INFO: 4
    }

    category_scores = {}
    for cat in categories:
        category_scores[cat] = 100

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
            # Map miscellaneous to general
            if "Localization" in target_cat or "Branding" in target_cat:
                target_cat = "Conversion"
            elif "Performance" in target_cat:
                target_cat = "Technical"
            elif "Compliance" in target_cat or "Tracking" in target_cat:
                target_cat = "SEO"
            else:
                target_cat = "Technical"

        penalty = deductions.get(issue.severity, 5)
        category_scores[target_cat] = max(0, category_scores[target_cat] - penalty)

    # Weighted overall score
    overall = 0.0
    for cat, meta in categories.items():
        score = category_scores.get(cat, 100)
        overall += score * meta["weight"]

    return {
        "overall_score": max(5, min(100, round(overall))),
        "scores_by_category": category_scores,
        "critical_count": crit_count,
        "warning_count": warn_count,
        "info_count": info_count
    }
