"""
Thin wrapper around the Anthropic SDK so every module in intent_engine/ and
goal_contract/ calls the LLM the same way, with the same error handling and
JSON-extraction logic.
"""

import os
import json
import logging
from anthropic import Anthropic

logger = logging.getLogger("sentinelos.llm_client")

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5")

_client: Anthropic | None = None


def get_client() -> Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
            )
        _client = Anthropic(api_key=api_key)
    return _client


def call_structured(system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> dict:
    """
    Calls the model with a system prompt that demands JSON-only output,
    then parses and returns the dict. Raises ValueError if parsing fails.
    """
    client = get_client()

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw_text = "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()

    # Strip markdown code fences if the model wraps its JSON anyway
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {raw_text[:500]}")
        raise ValueError(f"LLM did not return valid JSON: {e}") from e
