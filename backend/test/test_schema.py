"""Tests for the shared intent engine schema — the team's core contract."""

import pytest
from pydantic import ValidationError
from intent_engine.schema import (
    Intent, IntentCategory, GoalAlignment, DriftFlag,
    Explanation, GoalContract, EXAMPLE_OUTPUT, IntentEngineOutput
)


def test_intent_valid():
    intent = Intent(
        summary="Deletes log files",
        category=IntentCategory.CLEANUP,
        confidence=0.9,
        resources=["/var/log"],
    )
    assert intent.category == IntentCategory.CLEANUP
    assert 0.0 <= intent.confidence <= 1.0


def test_intent_confidence_out_of_range_rejected():
    with pytest.raises(ValidationError):
        Intent(summary="x", category=IntentCategory.UNKNOWN, confidence=1.5, resources=[])


def test_intent_invalid_category_rejected():
    with pytest.raises(ValidationError):
        Intent(summary="x", category="not_a_real_category", confidence=0.5, resources=[])


def test_goal_alignment_valid():
    ga = GoalAlignment(drift_flag=DriftFlag.MAJOR_DRIFT, drift_score=0.9, explanation="off scope")
    assert ga.drift_flag == DriftFlag.MAJOR_DRIFT


def test_example_output_matches_schema():
    """The EXAMPLE_OUTPUT teammates stub against must always validate."""
    parsed = IntentEngineOutput(**EXAMPLE_OUTPUT)
    assert parsed.intent.category == IntentCategory.DESTRUCTIVE_ADMIN
    assert parsed.goal_alignment.drift_flag == DriftFlag.ALIGNED


def test_goal_contract_defaults():
    gc = GoalContract(session_id="s1", stated_goal="clean logs")
    assert gc.scope_boundaries == []
    assert gc.expected_resource_types == []
