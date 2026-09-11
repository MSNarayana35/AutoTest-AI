from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_owned_project
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.platform import BugReport, BugStatus, Severity
from app.models.test_execution import TestExecution
from app.models.test_case import TestCase
from app.models.user import User

router = APIRouter()


class BugCreate(BaseModel):
    project_id: int
    test_case_id: Optional[int] = None
    execution_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    severity: Severity = Severity.MEDIUM
    evidence: Optional[dict] = None


class BugUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[Severity] = None
    status: Optional[BugStatus] = None


class BugResponse(BaseModel):
    id: int
    project_id: int
    test_case_id: Optional[int] = None
    execution_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    severity: Severity
    status: BugStatus
    evidence: Optional[dict] = None
    suggested_fix: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    test_case_title: Optional[str] = None

    class Config:
        from_attributes = True


@router.post("/", response_model=BugResponse, status_code=status.HTTP_201_CREATED)
def create_bug(
    payload: BugCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_project(db, payload.project_id, current_user)
    bug = BugReport(**payload.model_dump())
    if payload.evidence:
        bug.suggested_fix = "Review the captured error, failing assertion, and related recent changes."
    db.add(bug)
    db.commit()
    db.refresh(bug)
    return bug


@router.get("/project/{project_id}", response_model=list[BugResponse])
def list_bugs(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_project(db, project_id, current_user)
    bugs = (
        db.query(BugReport)
        .filter(BugReport.project_id == project_id)
        .order_by(BugReport.created_at.desc())
        .all()
    )
    # Add test case title if linked
    for bug in bugs:
        if bug.test_case_id:
            test_case = db.query(TestCase).filter(TestCase.id == bug.test_case_id).first()
            if test_case:
                bug.test_case_title = test_case.title
    return bugs


@router.put("/{bug_id}", response_model=BugResponse)
def update_bug(
    bug_id: int,
    payload: BugUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bug = db.query(BugReport).filter(BugReport.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    get_owned_project(db, bug.project_id, current_user)
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bug, field, value)
    
    db.commit()
    db.refresh(bug)
    return bug


@router.delete("/{bug_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bug(
    bug_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bug = db.query(BugReport).filter(BugReport.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    get_owned_project(db, bug.project_id, current_user)
    
    db.delete(bug)
    db.commit()
    return None
