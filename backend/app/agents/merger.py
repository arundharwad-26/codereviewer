from loguru import logger
from app.models.enums import Severity


# Severity ranking for comparison
SEVERITY_RANK = {
    Severity.low.value: 1,
    Severity.medium.value: 2,
    Severity.high.value: 3,
    Severity.critical.value: 4,
}


def get_highest_severity(severities: list[str]) -> str:
    """
    Compare a list of severity strings and return the highest one.
    Returns 'low' if the list is empty.
    """
    if not severities:
        return Severity.low.value

    return max(severities, key=lambda s: SEVERITY_RANK.get(s, 0))


def merge_results(
    code_review_output: dict,
    security_output: dict
) -> dict:
    """
    Merge code review and security agent outputs into one report.
    Pure Python only — no DB calls, no AI calls, no HTTP calls.
    Returns a single merged report dict.
    """
    logger.info("Merging agent results")

    # Extract issues from code review
    code_issues = code_review_output.get("issues", [])
    code_score = code_review_output.get("overall_score", 0)
    code_summary = code_review_output.get("summary", "")

    # Extract vulnerabilities from security
    vulnerabilities = security_output.get("vulnerabilities", [])
    security_severity = security_output.get("severity", Severity.low.value)
    security_summary = security_output.get("summary", "")

    # Count total issues
    total_issues = len(code_issues) + len(vulnerabilities)

    # Collect all severities
    all_severities = []

    for issue in code_issues:
        severity = issue.get("severity", Severity.low.value)
        all_severities.append(severity)

    for vuln in vulnerabilities:
        severity = vuln.get("severity", security_severity)
        all_severities.append(severity)

    # Get highest severity across all issues
    highest_severity = get_highest_severity(all_severities)

    # Calculate overall score
    # Security penalty based on severity
    security_penalty = {
        Severity.low.value: 0,
        Severity.medium.value: 5,
        Severity.high.value: 15,
        Severity.critical.value: 30,
    }

    penalty = security_penalty.get(security_severity, 0)
    overall_score = max(0, code_score - penalty)

    # Build merged report
    report = {
        "overall_score": overall_score,
        "highest_severity": highest_severity,
        "total_issues": total_issues,
        "code_review": {
            "score": code_score,
            "summary": code_summary,
            "issues": code_issues,
            "issues_count": len(code_issues),
        },
        "security": {
            "severity": security_severity,
            "summary": security_summary,
            "vulnerabilities": vulnerabilities,
            "vulnerabilities_count": len(vulnerabilities),
        }
    }

    logger.info(
        f"Merge complete — score: {overall_score}, "
        f"total issues: {total_issues}, "
        f"highest severity: {highest_severity}"
    )

    return report