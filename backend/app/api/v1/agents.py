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
