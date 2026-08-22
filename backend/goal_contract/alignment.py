"""
Goal Alignment Check — the Intent Drift feature.

Compares a command's inferred Intent against the session's Goal Contract
and returns a GoalAlignment verdict (aligned / minor_deviation / major_drift).

This is the module that catches an AI agent quietly expanding scope —
e.g. told to "clean up log files," then running a command that touches
/etc/passwd or opens a network port.
"""

import logging
from intent_engine.llm_client import call_structured
from intent_engine.prompts import DRIFT_SYSTEM_PROMPT, DRIFT_USER_PROMPT_TEMPLATE
from intent_engine.schema import GoalAlignment, GoalContract, Intent, DriftFlag

logger = logging.getLogger("sentinelos.goal_contract.alignment")

# If no Goal Contract exists for the session, we can't measure drift —
# treat as aligned but flag it so the frontend can show "no goal set" state.
NO_CONTRACT_ALIGNMENT = GoalAlignment(
    drift_flag=DriftFlag.ALIGNED,
    drift_score=0.0,
    explanation="No Goal Contract set for this session — drift cannot be evaluated.",
)


def check_alignment(contract: GoalContract | None, intent: Intent) -> GoalAlignment:
    if contract is None:
        return NO_CONTRACT_ALIGNMENT

    user_prompt = DRIFT_USER_PROMPT_TEMPLATE.format(
        stated_goal=contract.stated_goal,
        scope_boundaries=", ".join(contract.scope_boundaries) or "(none declared)",
        expected_resource_types=", ".join(contract.expected_resource_types) or "(none declared)",
        intent_summary=intent.summary,
        intent_category=intent.category,
        intent_resources=", ".join(intent.resources) or "(none identified)",
    )

    try:
        raw = call_structured(DRIFT_SYSTEM_PROMPT, user_prompt)
        return GoalAlignment(
            drift_flag=_safe_flag(raw.get("drift_flag")),
            drift_score=float(raw.get("drift_score", 0.5)),
            explanation=raw.get("explanation", "No explanation returned."),
        )
    except Exception as e:
        logger.error(f"Drift check failed, defaulting to major_drift for safety: {e}")
        # Fail SAFE: if we can't evaluate drift, treat it as suspicious rather
        # than silently letting it through.
        return GoalAlignment(
            drift_flag=DriftFlag.MAJOR_DRIFT,
            drift_score=1.0,
            explanation="Drift could not be evaluated due to an internal error; flagged for manual review.",
        )


def _safe_flag(value: str | None) -> DriftFlag:
    try:
        return DriftFlag(value)
    except (ValueError, TypeError):
        return DriftFlag.MAJOR_DRIFT
