"""
STUB — owned by Person 3 (Risk & Policy Engine Lead).

Real implementation: deterministic scoring across destructiveness, scope,
reversibility, privilege, persistence, network exposure, plus impact map /
blast-radius logic and threat detection for obfuscated/chained commands.

Consumes: Intent (from Person 2's intent_engine) + GoalAlignment (drift).
Produces: risk_score (0-1), risk_level (LOW/MEDIUM/HIGH/CRITICAL), factors[].
"""

from intent_engine.schema import Intent, GoalAlignment, IntentCategory, DriftFlag

HIGH_RISK_CATEGORIES = {
    IntentCategory.DESTRUCTIVE_ADMIN,
    IntentCategory.PRIVILEGE_ESCALATION,
}


def score_risk(intent: Intent, goal_alignment: GoalAlignment, execution_tree: dict) -> dict:
    """Naive placeholder scoring — replace with real deterministic engine."""
    score = 0.1
    factors = []

    if intent.category in HIGH_RISK_CATEGORIES:
        score += 0.5
        factors.append(f"category={intent.category}")

    if execution_tree.get("obfuscation_detected"):
        score += 0.3
        factors.append("obfuscation_detected")

    if goal_alignment.drift_flag == DriftFlag.MAJOR_DRIFT:
        score += 0.3
        factors.append("major_goal_drift")
    elif goal_alignment.drift_flag == DriftFlag.MINOR_DEVIATION:
        score += 0.1
        factors.append("minor_goal_deviation")

    score = min(score, 1.0)

    if score >= 0.75:
        level = "CRITICAL"
    elif score >= 0.5:
        level = "HIGH"
    elif score >= 0.25:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_score": round(score, 2),
        "risk_level": level,
        "factors": factors,
        "summary": f"{level} ({score:.2f}) — {', '.join(factors) if factors else 'no elevated risk factors'}",
    }
