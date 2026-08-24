"""
STUB — owned by Person 4 (Simulation & Data Lead).

Real implementation: dry-run "what-if" simulation, recoverability checks
(backup status, git-tracked, reversibility level).
"""


def dry_run(execution_tree: dict) -> dict:
    return {
        "would_affect": execution_tree.get("sub_commands", []),
        "reversible": "unknown",
        "backup_detected": False,
        "note": "Simulation module stub — replace with real dry-run logic.",
    }
