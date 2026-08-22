"""
STUB — owned by Person 3 (Risk & Policy Engine Lead).

Real implementation: loads /policies/default_rules.yaml, applies allow/confirm/
block decision logic with override support.
"""

import yaml
import os

DEFAULT_POLICY_PATH = os.environ.get("POLICY_PATH", "/app/policies/default_rules.yaml")


def load_policy(path: str = DEFAULT_POLICY_PATH) -> dict:
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {"thresholds": {"block": 0.75, "confirm": 0.4}}


def decide(risk_result: dict, policy: dict | None = None) -> dict:
    policy = policy or load_policy()
    thresholds = policy.get("thresholds", {"block": 0.75, "confirm": 0.4})
    score = risk_result["risk_score"]

    if score >= thresholds["block"]:
        decision = "block"
    elif score >= thresholds["confirm"]:
        decision = "confirm"
    else:
        decision = "allow"

    return {"decision": decision, "risk_score": score, "risk_level": risk_result["risk_level"]}
