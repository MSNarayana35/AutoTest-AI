from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_owned_project
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.platform import AgentLog, ArtifactStatus
from app.models.user import User

# Import agents
from app.agents import (
    RootCauseAnalysisAgent,
    BugDetectionAgent,
    TestExecutionAgent
)

router = APIRouter()

AGENT_REGISTRY = [
    "requirement_agent",
    "planner_agent",
    "test_generator_agent",
    "execution_agent",
    "bug_detection_agent",
    "regression_agent",
    "root_cause_agent",
    "self_healing_agent",
    "report_agent",
    "coordinator_agent",
    "memory_agent",
]


class AgentRunRequest(BaseModel):
    agent_name: str
    project_id: Optional[int] = None
    input_payload: dict = {}


class AgentLogResponse(BaseModel):
    id: int
    project_id: Optional[int] = None
    agent_name: str
    event: str
    status: ArtifactStatus
    input_payload: Optional[dict] = None
    output_payload: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/")
def list_agents():
    return {"agents": AGENT_REGISTRY}


@router.post("/run", response_model=AgentLogResponse, status_code=status.HTTP_201_CREATED)
def run_agent(
    payload: AgentRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.project_id is not None:
        get_owned_project(db, payload.project_id, current_user)
    output = {
        "agent": payload.agent_name,
        "status": "accepted",
        "message": "Agent run recorded for orchestration.",
    }
    log = AgentLog(
        project_id=payload.project_id,
        agent_name=payload.agent_name,
        event="manual_run",
        input_payload=payload.input_payload,
        output_payload=output,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/logs", response_model=list[AgentLogResponse])
def list_agent_logs(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AgentLog)
    if project_id is not None:
        get_owned_project(db, project_id, current_user)
        query = query.filter(AgentLog.project_id == project_id)
    return query.order_by(AgentLog.created_at.desc()).limit(100).all()


# ─── ROOT CAUSE ANALYSIS ENDPOINT ─────────────────────────────────────────────

class RootCauseRequest(BaseModel):
    test_case: dict
    execution: dict


@router.post("/root-cause-analysis", status_code=status.HTTP_200_OK)
def analyze_root_cause(
    payload: RootCauseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze the root cause of a test failure.
    """
    try:
        agent = RootCauseAnalysisAgent()
        result = agent.run({
            "test_case": payload.test_case,
            "execution": payload.execution
        })
        
        # Log the analysis
        log = AgentLog(
            project_id=payload.test_case.get("project_id"),
            agent_name="root_cause_agent",
            event="root_cause_analysis",
            input_payload={"test_case_id": payload.test_case.get("id")},
            output_payload=result,
        )
        db.add(log)
        db.commit()
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


class BatchRootCauseRequest(BaseModel):
    failed_executions: list


@router.post("/root-cause-analysis/batch", status_code=status.HTTP_200_OK)
def analyze_batch_root_cause(
    payload: BatchRootCauseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze multiple test failures to identify patterns.
    """
    try:
        agent = RootCauseAnalysisAgent()
        result = agent.batch_analyze(payload.failed_executions)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ─── BUG DETECTION ENDPOINT ───────────────────────────────────────────────────

class BugDetectionRequest(BaseModel):
    executions: list


@router.post("/bug-detection", status_code=status.HTTP_200_OK)
def detect_bugs(
    payload: BugDetectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Automatically detect bugs from test execution results.
    """
    try:
        agent = BugDetectionAgent()
        result = agent.run({"executions": payload.executions})
        
        # Log the detection
        log = AgentLog(
            project_id=payload.executions[0].get("project_id") if payload.executions else None,
            agent_name="bug_detection_agent",
            event="bug_detection",
            input_payload={"execution_count": len(payload.executions)},
            output_payload=result,
        )
        db.add(log)
        db.commit()
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/bug-detection/patterns", status_code=status.HTTP_200_OK)
def analyze_bug_patterns(
    payload: BaseModel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze patterns in detected bugs.
    """
    try:
        bugs = payload.dict().get("bugs", [])
        agent = BugDetectionAgent()
        result = agent.analyze_bug_patterns(bugs)
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ─── TEST EXECUTION ENDPOINT ──────────────────────────────────────────────────

class ExecutionRequest(BaseModel):
    mode: str = "single"  # single, bulk, tags
    test_cases: list
    options: Optional[dict] = {}
    tags: Optional[list] = []


@router.post("/execute", status_code=status.HTTP_200_OK)
def execute_tests(
    payload: ExecutionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Execute test cases using the execution agent.
    Supports single, bulk, and tag-based execution.
    """
    try:
        agent = TestExecutionAgent(config=payload.options)
        result = agent.run({
            "mode": payload.mode,
            "test_cases": payload.test_cases,
            "options": payload.options,
            "tags": payload.tags
        })
        
        # Log the execution
        log = AgentLog(
            project_id=payload.test_cases[0].get("project_id") if payload.test_cases else None,
            agent_name="execution_agent",
            event=f"test_execution_{payload.mode}",
            input_payload={"test_count": len(payload.test_cases), "mode": payload.mode},
            output_payload=result,
        )
        db.add(log)
        db.commit()
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
