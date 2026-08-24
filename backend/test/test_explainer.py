"""Tests for Explanation & Safer-Alternative Generator — LLM calls mocked."""

from unittest.mock import patch
from intent_engine.explainer import generate_explanation
from intent_engine.schema import Intent, IntentCategory, GoalAlignment, DriftFlag


@patch("intent_engine.explainer.call_structured")
def test_generate_explanation_with_safer_alternative(mock_call):
    mock_call.return_value = {
        "reasoning": "This permanently deletes logs needed for diagnostics.",
        "safer_alternative": "mv /var/log/*.log /var/log/archive/",
    }
    intent = Intent(summary="deletes logs", category=IntentCategory.DESTRUCTIVE_ADMIN, confidence=0.9, resources=["/var/log"])
    alignment = GoalAlignment(drift_flag=DriftFlag.ALIGNED, drift_score=0.1, explanation="matches goal")

    result = generate_explanation("rm -rf /var/log", intent, "HIGH (0.8)", alignment)

    assert result.safer_alternative is not None
    assert "mv" in result.safer_alternative


@patch("intent_engine.explainer.call_structured")
def test_generate_explanation_low_risk_no_alternative(mock_call):
    mock_call.return_value = {"reasoning": "Low risk, read-only command.", "safer_alternative": None}
    intent = Intent(summary="lists files", category=IntentCategory.FILE_MANAGEMENT, confidence=0.95, resources=["."])
    alignment = GoalAlignment(drift_flag=DriftFlag.ALIGNED, drift_score=0.0, explanation="fine")

    result = generate_explanation("ls -la", intent, "LOW (0.05)", alignment)
    assert result.safer_alternative is None


@patch("intent_engine.explainer.call_structured")
def test_generate_explanation_fails_gracefully(mock_call):
    mock_call.side_effect = Exception("timeout")
    intent = Intent(summary="x", category=IntentCategory.UNKNOWN, confidence=0.0, resources=[])
    alignment = GoalAlignment(drift_flag=DriftFlag.ALIGNED, drift_score=0.0, explanation="n/a")

    result = generate_explanation("some command", intent, "LOW", alignment)
    assert "internal error" in result.reasoning
