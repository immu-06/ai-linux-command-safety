"""
SentinelOS backend orchestrator.

Wires: Parser -> Intent Engine -> Goal Alignment Check -> Risk Engine
       -> Policy Engine -> Simulation -> Explanation -> Audit Log

Exposes a REST API consumed by the frontend (Person 5).
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from parser import parse_command
from intent_engine import infer_intent, generate_explanation
from goal_contract import (
    set_goal_contract,
    get_goal_contract,
    check_alignment,
)
from intent_engine.schema import GoalContract
from risk_engine import score_risk
from policy_engine import decide
from simulation import dry_run
from audit import log_evaluation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinelos.main")

app = FastAPI(title="SentinelOS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
)


class EvaluateRequest(BaseModel):
    command: str
    session_id: str = "default"
    cwd: str = "/"
    history: list[str] = []


class GoalContractRequest(BaseModel):
    session_id: str
    stated_goal: str
    scope_boundaries: list[str] = []
    expected_resource_types: list[str] = []


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/goal-contract")
def create_goal_contract(req: GoalContractRequest):
    """Set the Goal Contract for a session — call this before evaluating commands
    if you want drift detection to be meaningful."""
    contract = GoalContract(
        session_id=req.session_id,
        stated_goal=req.stated_goal,
        scope_boundaries=req.scope_boundaries,
        expected_resource_types=req.expected_resource_types,
    )
    set_goal_contract(contract)
    return {"status": "set", "contract": contract.model_dump()}


@app.post("/api/evaluate")
def evaluate(req: EvaluateRequest):
    """
    Full pipeline for a single command:
    parse -> intent -> drift check -> risk score -> policy decision
    -> simulation -> explanation -> audit log
    """
    try:
        # 1. Parse (Person 1)
        execution_tree = parse_command(req.command)

        # 2. Intent (Person 2 — you)
        intent = infer_intent(execution_tree, cwd=req.cwd, history=req.history)

        # 3. Goal Alignment / Drift (Person 2 — you)
        contract = get_goal_contract(req.session_id)
        goal_alignment = check_alignment(contract, intent)

        # 4. Risk scoring (Person 3)
        risk_result = score_risk(intent, goal_alignment, execution_tree)

        # 5. Policy decision (Person 3)
        policy_decision = decide(risk_result)

        # 6. Simulation (Person 4)
        simulation_result = dry_run(execution_tree)

        # 7. Explanation + safer alternative (Person 2 — you)
        explanation = generate_explanation(
            command=req.command,
            intent=intent,
            risk_summary=risk_result["summary"],
            goal_alignment=goal_alignment,
        )

        result = {
            "command": req.command,
            "execution_tree": execution_tree,
            "intent": intent.model_dump(),
            "goal_alignment": goal_alignment.model_dump(),
            "risk": risk_result,
            "policy_decision": policy_decision,
            "simulation": simulation_result,
            "explanation": explanation.model_dump(),
        }

        # 8. Audit log (Person 4)
        log_evaluation(req.session_id, req.command, result)

        return result

    except Exception as e:
        logger.exception("Pipeline evaluation failed")
        raise HTTPException(status_code=500, detail=str(e))
