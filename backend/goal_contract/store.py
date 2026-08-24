"""
In-memory Goal Contract store, keyed by session_id.

For the hackathon demo this is intentionally simple (dict in process memory).
Swap for Redis/SQLite if the demo needs persistence across backend restarts —
Person 4's audit DB is the natural place to also persist this if time allows.
"""

from intent_engine.schema import GoalContract

_contracts: dict[str, GoalContract] = {}


def set_goal_contract(contract: GoalContract) -> None:
    _contracts[contract.session_id] = contract


def get_goal_contract(session_id: str) -> GoalContract | None:
    return _contracts.get(session_id)


def clear_goal_contract(session_id: str) -> None:
    _contracts.pop(session_id, None)


def has_goal_contract(session_id: str) -> bool:
    return session_id in _contracts
