"""
Intent Engine — infers what a command is actually trying to do.

Input: execution tree from Person 1's parser module.
Output: Intent object (see schema.py) consumed by Goal Alignment Check
        and the Risk Engine.
"""

import logging
from .llm_client import call_structured
from .prompts import INTENT_SYSTEM_PROMPT, INTENT_USER_PROMPT_TEMPLATE
from .schema import Intent, IntentCategory

logger = logging.getLogger("sentinelos.intent_engine")


def infer_intent(execution_tree: dict, cwd: str = "/", history: list[str] | None = None) -> Intent:
    """
    execution_tree: dict produced by backend/parser (tokenized, chain-resolved,
                    alias-expanded, de-obfuscated). Expected to at minimum have
                    a 'raw' or 'normalized' command string — see parser/README.
    cwd: current working directory context, improves resource inference.
    history: last few commands in the session, improves intent disambiguation.
    """
    history = history or []

    user_prompt = INTENT_USER_PROMPT_TEMPLATE.format(
        execution_tree=execution_tree,
        cwd=cwd,
        history=", ".join(history) if history else "(none)",
    )

    try:
        raw = call_structured(INTENT_SYSTEM_PROMPT, user_prompt)
        return Intent(
            summary=raw.get("summary", "Unable to determine intent"),
            category=_safe_category(raw.get("category")),
            confidence=float(raw.get("confidence", 0.0)),
            resources=raw.get("resources", []),
        )
    except Exception as e:
        logger.error(f"Intent inference failed, falling back to UNKNOWN: {e}")
        return Intent(
            summary="Intent could not be determined due to an internal error.",
            category=IntentCategory.UNKNOWN,
            confidence=0.0,
            resources=[],
        )


def _safe_category(value: str | None) -> IntentCategory:
    try:
        return IntentCategory(value)
    except (ValueError, TypeError):
        return IntentCategory.UNKNOWN
