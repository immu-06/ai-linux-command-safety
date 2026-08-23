"""
Tests for the Goal Contract + Alignment Check (Intent Drift feature).
LLM calls are mocked so tests run without an API key / network access.
"""

from unittest.mock import patch
from intent_engine.schema import Intent, IntentCategory, GoalContract, DriftFlag
from goal_contract.alignment import check_alignment, NO_CONTRACT_ALIGNMENT
from goal_contract.store import set_goal_contract, get_goal_contract, clear_goal_contract, has_goal_contract


def test_no_contract_returns_aligned_by_default():
    intent = Intent(summary="does something", category=IntentCategory.CLEANUP, confidence=0.8, resources=[])
    result = check_alignment(None, intent)
    assert result == NO_CONTRACT_ALIGNMENT
    assert result.drift_flag == DriftFlag.ALIGNED


@patch("goal_contract.alignment.call_structured")
def test_aligned_command_within_scope(mock_call):
    mock_call.return_value = {
        "drift_flag": "aligned",
        "drift_score": 0.05,
        "explanation": "Matches the stated cleanup goal.",
    }
    contract = GoalContract(
        session_id="s1",
        stated_goal="clean up temp files",
        scope_boundaries=["/tmp/*"],
        expected_resource_types=["temp files"],
    )
    intent = Intent(summary="deletes tmp files", category=IntentCategory.CLEANUP, confidence=0.9, resources=["/tmp/foo"])

    result = check_alignment(contract, intent)
    assert result.drift_flag == DriftFlag.ALIGNED
    assert result.drift_score < 0.2


@patch("goal_contract.alignment.call_structured")
def test_major_drift_detected_for_scope_creep(mock_call):
    """Core scenario for the demo: agent told to clean logs, tries to escalate privileges."""
    mock_call.return_value = {
        "drift_flag": "major_drift",
        "drift_score": 0.95,
        "explanation": "Command modifies user permissions, unrelated to the stated log-cleanup goal.",
    }
    contract = GoalContract(
        session_id="agent-session",
        stated_goal="clean up old log files",
        scope_boundaries=["/var/log/*"],
        expected_resource_types=["log files"],
    )
    intent = Intent(
        summary="adds current user to sudoers group",
        category=IntentCategory.PRIVILEGE_ESCALATION,
        confidence=0.92,
        resources=["/etc/sudoers"],
    )

    result = check_alignment(contract, intent)
    assert result.drift_flag == DriftFlag.MAJOR_DRIFT
    assert result.drift_score > 0.8


@patch("goal_contract.alignment.call_structured")
def test_llm_failure_fails_safe_to_major_drift(mock_call):
    """If the drift-check LLM call errors, we must NOT silently allow — fail safe."""
    mock_call.side_effect = Exception("network error")
    contract = GoalContract(session_id="s1", stated_goal="deploy service")
    intent = Intent(summary="unknown", category=IntentCategory.UNKNOWN, confidence=0.0, resources=[])

    result = check_alignment(contract, intent)
    assert result.drift_flag == DriftFlag.MAJOR_DRIFT
    assert result.drift_score == 1.0


def test_goal_contract_store_roundtrip():
    contract = GoalContract(session_id="store-test", stated_goal="test goal")
    set_goal_contract(contract)
    assert has_goal_contract("store-test")
    fetched = get_goal_contract("store-test")
    assert fetched.stated_goal == "test goal"
    clear_goal_contract("store-test")
    assert not has_goal_contract("store-test")
