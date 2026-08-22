"""
SHARED OUTPUT CONTRACT — owned by AI/Intent Engine Lead (Person 2)

This is the schema every downstream module (Risk Engine, Policy Engine,
Simulation/Audit, Frontend) consumes. Freeze this early (Phase 1) so nobody
downstream is blocked.

Pydantic models double as:
  1. Runtime validation of LLM output
  2. Auto-generated JSON schema we hand to the LLM for structured output
  3. The typed contract other teammates import directly
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class IntentCategory(str, Enum):
    CLEANUP = "cleanup"
    DEPLOY = "deploy"
    DEBUG = "debug"
    DATA_MIGRATION = "data_migration"
    DESTRUCTIVE_ADMIN = "destructive_admin"
    NETWORK = "network"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    FILE_MANAGEMENT = "file_management"
    UNKNOWN = "unknown"


class DriftFlag(str, Enum):
    ALIGNED = "aligned"
    MINOR_DEVIATION = "minor_deviation"
    MAJOR_DRIFT = "major_drift"


class Intent(BaseModel):
    summary: str = Field(..., description="Plain-English description of what this command actually does")
    category: IntentCategory = Field(default=IntentCategory.UNKNOWN)
    confidence: float = Field(..., ge=0.0, le=1.0, description="LLM confidence in this intent classification")
    resources: list[str] = Field(default_factory=list, description="Files, services, paths, ports, processes touched")


class GoalAlignment(BaseModel):
    drift_flag: DriftFlag = Field(default=DriftFlag.ALIGNED)
    drift_score: float = Field(..., ge=0.0, le=1.0, description="0 = fully aligned, 1 = complete drift")
    explanation: str = Field(..., description="Why this command does or doesn't match the stated goal")


class Explanation(BaseModel):
    reasoning: str = Field(..., description="Human-readable explanation of the flag/risk")
    safer_alternative: Optional[str] = Field(default=None, description="A safer command achieving similar intent, if one exists")


class IntentEngineOutput(BaseModel):
    """The full object returned to Risk Engine / Policy Engine / Frontend."""
    intent: Intent
    goal_alignment: GoalAlignment
    explanation: Explanation

    model_config = ConfigDict(use_enum_values=True)


class GoalContract(BaseModel):
    """Captured once per session/task. Everything after this is checked against it."""
    session_id: str
    stated_goal: str
    scope_boundaries: list[str] = Field(default_factory=list, description="e.g. ['/var/log/*', 'no privilege changes']")
    expected_resource_types: list[str] = Field(default_factory=list, description="e.g. ['log files', 'temp files']")


# Example payload, useful for teammates stubbing against this before the
# real LLM call is wired up (Phase 1 mock).
EXAMPLE_OUTPUT = {
    "intent": {
        "summary": "Recursively deletes all files under /var/log without confirmation",
        "category": "destructive_admin",
        "confidence": 0.94,
        "resources": ["/var/log/*"]
    },
    "goal_alignment": {
        "drift_flag": "aligned",
        "drift_score": 0.05,
        "explanation": "Matches stated goal of clearing old log files."
    },
    "explanation": {
        "reasoning": "This command is irreversible and affects system logs used for diagnostics.",
        "safer_alternative": "mv /var/log/*.log /var/log/archive/ && logrotate -f"
    }
}
