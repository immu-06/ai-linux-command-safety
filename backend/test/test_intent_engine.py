"""Tests for Intent Engine — LLM calls mocked."""

from unittest.mock import patch
from intent_engine.engine import infer_intent
from intent_engine.schema import IntentCategory


@patch("intent_engine.engine.call_structured")
def test_infer_intent_happy_path(mock_call):
    mock_call.return_value = {
        "summary": "Recursively removes log directory",
        "category": "destructive_admin",
        "confidence": 0.91,
        "resources": ["/var/log"],
    }
    tree = {"raw": "rm -rf /var/log", "normalized": "rm -rf /var/log", "sub_commands": ["rm -rf /var/log"]}
    result = infer_intent(tree, cwd="/", history=[])

    assert result.category == IntentCategory.DESTRUCTIVE_ADMIN
    assert result.confidence == 0.91
    assert "/var/log" in result.resources


@patch("intent_engine.engine.call_structured")
def test_infer_intent_falls_back_on_error(mock_call):
    mock_call.side_effect = ValueError("bad json")
    tree = {"raw": "ls", "normalized": "ls", "sub_commands": ["ls"]}
    result = infer_intent(tree)

    assert result.category == IntentCategory.UNKNOWN
    assert result.confidence == 0.0


@patch("intent_engine.engine.call_structured")
def test_infer_intent_invalid_category_defaults_unknown(mock_call):
    mock_call.return_value = {
        "summary": "does something weird",
        "category": "not_a_valid_category",
        "confidence": 0.5,
        "resources": [],
    }
    tree = {"raw": "foo", "normalized": "foo", "sub_commands": ["foo"]}
    result = infer_intent(tree)
    assert result.category == IntentCategory.UNKNOWN
