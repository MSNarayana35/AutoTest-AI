from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_owned_project
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.test_case import TestCase
from app.models.test_execution import ExecutionStatus, TestExecution
from app.models.user import User

router = APIRouter()


class ExecutionCreate(BaseModel):
    test_case_id: int
    mode: str = "sequential"


class ExecutionResponse(BaseModel):
    id: int
    project_id: int
    test_case_id: int
    status: ExecutionStatus
    logs: Optional[str] = None
    screenshots: Optional[dict] = None
    execution_time: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
def queue_execution(
    payload: ExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    test_case = db.query(TestCase).filter(TestCase.id == payload.test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    get_owned_project(db, test_case.project_id, current_user)

    execution = TestExecution(
        project_id=test_case.project_id,
        test_case_id=test_case.id,
        status=ExecutionStatus.PENDING,
        logs=f"Queued for {payload.mode} execution",
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    return execution


@router.get("/project/{project_id}", response_model=list[ExecutionResponse])
def list_executions(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_project(db, project_id, current_user)
    # Optimized: Use index on created_at for sorting + pagination
    return db.query(TestExecution).filter(
        TestExecution.project_id == project_id
    ).order_by(TestExecution.created_at.desc()).offset(skip).limit(limit).all()
