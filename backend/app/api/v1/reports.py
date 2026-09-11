from datetime import datetime
from typing import Optional
import pytz

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_owned_project
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.platform import ArtifactStatus, Report, BugReport
from app.models.test_execution import TestExecution
from app.models.test_case import TestCase
from app.models.requirement import Requirement
from app.models.project import Project
from app.models.user import User
from app.services.pdf_generator import pdf_generator

# Indian Standard Time
IST = pytz.timezone('Asia/Kolkata')

router = APIRouter()


class ReportCreate(BaseModel):
    project_id: int
    execution_id: Optional[int] = None
    report_type: str = "json"


class ReportResponse(BaseModel):
    id: int
    project_id: int
    execution_id: Optional[int] = None
    report_type: str
    status: ArtifactStatus
    payload: Optional[dict] = None
    file_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    payload: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_project(db, payload.project_id, current_user)
    executions = db.query(TestExecution).filter(TestExecution.project_id == payload.project_id).all()
    total = len(executions)
    passed = len([item for item in executions if item.status.value == "passed"])
    failed = len([item for item in executions if item.status.value == "failed"])
    report = Report(
        project_id=payload.project_id,
        execution_id=payload.execution_id,
        report_type=payload.report_type,
        payload={
            "total_executions": total,
            "passed": passed,
            "failed": failed,
            "success_rate": round((passed / total) * 100, 2) if total else 0,
            "ai_summary": "Report generated from recorded execution data.",
            "recommendations": ["Prioritize failed and flaky tests before the next release."],
        },
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/project/{project_id}", response_model=list[ReportResponse])
def list_reports(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_project(db, project_id, current_user)
    return db.query(Report).filter(Report.project_id == project_id).all()


@router.get("/project/{project_id}/pdf")
def generate_pdf_report(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate and download detailed PDF report for a project"""
    project = get_owned_project(db, project_id, current_user)
    
    # Fetch all related data
    requirements = db.query(Requirement).filter(
        Requirement.project_id == project_id
    ).order_by(Requirement.created_at.desc()).all()
    
    test_cases = db.query(TestCase).filter(
        TestCase.project_id == project_id
    ).order_by(TestCase.created_at.desc()).all()
    
    executions = db.query(TestExecution).filter(
        TestExecution.project_id == project_id
    ).order_by(TestExecution.created_at.desc()).all()
    
    bugs = db.query(BugReport).filter(
        BugReport.project_id == project_id
    ).order_by(BugReport.created_at.desc()).all()
    
    # Convert to dicts
    project_data = {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'repository_url': project.repository_url,
        'deployment_url': project.deployment_url,
        'created_at': project.created_at,
    }
    
    requirements_data = [
        {
            'id': r.id,
            'title': r.title,
            'content': r.content,
            'status': r.status,
            'created_at': r.created_at,
        }
        for r in requirements
    ]
    
    test_cases_data = [
        {
            'id': tc.id,
            'title': tc.title,
            'description': tc.description,
            'test_type': tc.test_type.value if hasattr(tc.test_type, 'value') else tc.test_type,
            'status': tc.status,
            'created_at': tc.created_at,
        }
        for tc in test_cases
    ]
    
    executions_data = [
        {
            'id': e.id,
            'test_case_id': e.test_case_id,
            'status': e.status.value if hasattr(e.status, 'value') else e.status,
            'logs': e.logs,
            'execution_time': e.execution_time,
            'created_at': e.created_at,
        }
        for e in executions
    ]
    
    bugs_data = [
        {
            'id': b.id,
            'title': b.title,
            'description': b.description,
            'severity': b.severity,
            'status': b.status,
            'created_at': b.created_at,
        }
        for b in bugs
    ]
    
    # Generate PDF
    pdf_buffer = pdf_generator.generate_report(
        project_data,
        requirements_data,
        test_cases_data,
        executions_data,
        bugs_data
    )
    
    # Return as downloadable file
    now_ist = datetime.now(IST)
    filename = f"TestReport_{project.name.replace(' ', '_')}_{now_ist.strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
