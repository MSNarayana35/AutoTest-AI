from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.cache import Cache, cache_key
from app.models.platform import AgentLog, BugReport, Notification
from app.models.project import Project
from app.models.requirement import Requirement
from app.models.test_case import TestCase
from app.models.test_execution import ExecutionStatus, TestExecution
from app.models.user import User

router = APIRouter()

@router.get("/")
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check cache first
    cache_key_str = f"dashboard:user:{current_user.id}"
    cached_result = Cache.get(cache_key_str)
    if cached_result:
        return cached_result
    
    # Optimized: Get project IDs in one query
    project_ids = [
        item.id for item in db.query(Project.id).filter(Project.owner_id == current_user.id).all()
    ]
    
    # Initialize defaults
    total_tests = 0
    total_executions = 0
    passed_executions = 0
    failed_executions = 0
    bug_count = 0
    requirement_count = 0

    if project_ids:
        # Optimized: Use a single query with conditional aggregation instead of multiple count queries
        from sqlalchemy import func, case
        
        # Aggregate all counts in one query
        counts = db.query(
            func.count(TestCase.id).label('tests'),
            func.count(Requirement.id).label('requirements'),
        ).select_from(Project).outerjoin(TestCase, TestCase.project_id == Project.id).outerjoin(
            Requirement, Requirement.project_id == Project.id
        ).filter(Project.id.in_(project_ids)).first()
        
        total_tests = counts.tests if counts else 0
        requirement_count = counts.requirements if counts else 0
        
        # Execution stats with single query
        exec_stats = db.query(
            func.count(TestExecution.id).label('total'),
            func.sum(case((TestExecution.status == ExecutionStatus.PASSED, 1), else_=0)).label('passed'),
            func.sum(case((TestExecution.status == ExecutionStatus.FAILED, 1), else_=0)).label('failed'),
        ).filter(TestExecution.project_id.in_(project_ids)).first()
        
        if exec_stats:
            total_executions = exec_stats.total or 0
            passed_executions = exec_stats.passed or 0
            failed_executions = exec_stats.failed or 0
        
        bug_count = db.query(func.count(BugReport.id)).filter(BugReport.project_id.in_(project_ids)).scalar() or 0

    # Optimized: Get recent projects with a single query
    recent_projects = (
        db.query(Project)
        .filter(Project.owner_id == current_user.id)
        .order_by(Project.created_at.desc())
        .limit(5)
        .all()
    )
    
    # Optimized: Get agent activity with a single query
    agent_activity = (
        db.query(AgentLog)
        .filter(AgentLog.project_id.in_(project_ids))
        .order_by(AgentLog.created_at.desc())
        .limit(10)
        .all()
        if project_ids
        else []
    )
    
    unread_notifications = (
        db.query(func.count(Notification.id))
        .filter(Notification.user_id == current_user.id, Notification.status == "unread")
        .scalar() or 0
    )

    result = {
        "analytics": {
            "projects": len(project_ids),
            "requirements": requirement_count,
            "test_cases": total_tests,
            "executions": total_executions,
            "passed_executions": passed_executions,
            "failed_executions": failed_executions,
            "success_rate": round((passed_executions / total_executions) * 100, 2)
            if total_executions
            else 0,
            "bugs": bug_count,
            "unread_notifications": unread_notifications,
        },
        "recent_projects": [
            {"id": project.id, "name": project.name, "created_at": project.created_at}
            for project in recent_projects
        ],
        "agent_activity": [
            {
                "id": log.id,
                "agent_name": log.agent_name,
                "event": log.event,
                "status": log.status,
                "created_at": log.created_at,
            }
            for log in agent_activity
        ],
    }
    
    # Cache for 2 minutes
    Cache.set(cache_key_str, result, ttl=120)
    return result
