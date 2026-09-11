from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_owned_project
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.platform import RegressionHistory
from app.models.user import User

router = APIRouter()


class RegressionCreate(BaseModel):
    project_id: int
    baseline_execution_id: Optional[int] = None
    comparison_execution_id: Optional[int] = None
    summary: Optional[dict] = None


class RegressionResponse(BaseModel):
    id: int
    project_id: int
    baseline_execution_id: Optional[int] = None
    comparison_execution_id: Optional[int] = None
    summary: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=RegressionResponse, status_code=status.HTTP_201_CREATED)
def create_regression_record(
    payload: RegressionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_project(db, payload.project_id, current_user)
    record = RegressionHistory(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/project/{project_id}", response_model=list[RegressionResponse])
def list_regression_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_project(db, project_id, current_user)
    return db.query(RegressionHistory).filter(RegressionHistory.project_id == project_id).all()
