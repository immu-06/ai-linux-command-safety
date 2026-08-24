"""
Explanation & Safer-Alternative Generator.

Runs AFTER the Risk Engine (Person 3) and Goal Alignment Check have produced
their outputs, and packages a human-readable explanation + safer command for
the frontend's risk card.
"""

import logging
from .llm_client import call_structured
from .prompts import EXPLANATION_SYSTEM_PROMPT, EXPLANATION_USER_PROMPT_TEMPLATE
from .schema import Explanation, GoalAlignment, Intent

logger = logging.getLogger("sentinelos.explainer")


def generate_explanation(
    command: str,
    intent: Intent,
    risk_summary: str,
    goal_alignment: GoalAlignment,
) -> Explanation:
    """
    risk_summary: a short string handed to us by Person 3's Risk Engine,
                  e.g. "HIGH (0.87) — destructive, irreversible, root-owned files"
    """
    user_prompt = EXPLANATION_USER_PROMPT_TEMPLATE.format(
        command=command,
        intent_summary=intent.summary,
        intent_category=intent.category,
        risk_summary=risk_summary,
        drift_flag=goal_alignment.drift_flag,
        drift_explanation=goal_alignment.explanation,
    )

    try:
        raw = call_structured(EXPLANATION_SYSTEM_PROMPT, user_prompt)
        return Explanation(
            reasoning=raw.get("reasoning", "No explanation available."),
            safer_alternative=raw.get("safer_alternative"),
        )
    except Exception as e:
        logger.error(f"Explanation generation failed: {e}")
        return Explanation(
            reasoning="Explanation could not be generated due to an internal error.",
            safer_alternative=None,
        )
