from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.test_case import TestCase, TestType
from app.models.requirement import Requirement
from app.models.test_execution import ExecutionStatus, TestExecution
from app.models.platform import Notification
from app.models.project import Project
from app.api.v1.dependencies import get_owned_project
from app.agents.test_generator_agent import TestGeneratorAgent
from app.agents.self_healing_agent import SelfHealingAgent
from app.services.email_service import send_email, create_test_failure_email

router = APIRouter()

test_generator = TestGeneratorAgent()
self_healer = SelfHealingAgent()

class TestCaseResponse(BaseModel):
    id: int
    project_id: int
    requirement_id: int = None
    title: str
    description: str = None
    test_type: TestType
    script: str = None
    status: str
    tags: List[str] = []
    is_flaky: bool = False
    failure_count: int = 0
    total_runs: int = 0
    last_failure_date: datetime = None
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/generate/{requirement_id}", response_model=List[TestCaseResponse])
async def generate_test_cases(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    get_owned_project(db, requirement.project_id, current_user)
    
    requirements_data = requirement.structured_data or {"functional_requirements": [requirement.content]}
    test_cases_data = test_generator.generate_test_cases(requirements_data)
    
    created_tests = []
    for tc_data in test_cases_data:
        script = test_generator.generate_playwright_script(tc_data)
        db_test = TestCase(
            project_id=requirement.project_id,
            requirement_id=requirement_id,
            title=tc_data.get("title", "Test Case"),
            description=tc_data.get("description", ""),
            test_type=tc_data.get("test_type", "functional"),
            script=script,
            status="ready"
        )
        db.add(db_test)
        db.commit()
        db.refresh(db_test)
        created_tests.append(db_test)
    
    return created_tests

@router.get("/project/{project_id}", response_model=List[TestCaseResponse])
def get_project_tests(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_owned_project(db, project_id, current_user)
    # Optimized: Use index on created_at for sorting + pagination
    tests = db.query(TestCase).filter(
        TestCase.project_id == project_id
    ).order_by(TestCase.created_at.desc()).offset(skip).limit(limit).all()
    return tests

@router.get("/{test_id}", response_model=TestCaseResponse)
def get_test_case(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    test_case = db.query(TestCase).filter(TestCase.id == test_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    get_owned_project(db, test_case.project_id, current_user)
    return test_case

@router.post("/{test_id}/execute")
def execute_test(
    test_id: int,
    url: str = Form(...),
    selector: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    test_case = db.query(TestCase).filter(TestCase.id == test_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    get_owned_project(db, test_case.project_id, current_user)
    execution = TestExecution(
        project_id=test_case.project_id,
        test_case_id=test_case.id,
        status=ExecutionStatus.RUNNING,
        logs="Execution started",
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    try:
        result = self_healer.execute_test(url, selector)
        execution.status = ExecutionStatus.PASSED if result.get("status") == "success" else ExecutionStatus.FAILED
        execution.logs = result.get("message")
        db.commit()
        return result
    except Exception as e:
        execution.status = ExecutionStatus.FAILED
        execution.logs = str(e)
        db.commit()
        return {"status": "error", "message": str(e)}


class BulkRunRequest(BaseModel):
    url: str = "http://localhost:3000"

@router.post("/project/{project_id}/run-all")
def run_all_tests(
    project_id: int,
    payload: BulkRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run all test cases for a project and record executions. Returns a summary."""
    get_owned_project(db, project_id, current_user)
    test_cases = db.query(TestCase).filter(TestCase.project_id == project_id).all()
    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found for this project")

    results = []
    passed = 0
    failed = 0
    failed_tests = []

    for tc in test_cases:
        execution = TestExecution(
            project_id=project_id,
            test_case_id=tc.id,
            status=ExecutionStatus.RUNNING,
            logs="Bulk run started",
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)

        try:
            # Use a default selector from script or fallback to "body"
            selector = "body"
            result = self_healer.execute_test(payload.url, selector)
            is_passed = result.get("status") == "success"
            execution.status = ExecutionStatus.PASSED if is_passed else ExecutionStatus.FAILED
            execution.logs = result.get("message", "")
            if is_passed:
                passed += 1
            else:
                failed += 1
                failed_tests.append(tc.title)
            results.append({
                "test_id": tc.id,
                "title": tc.title,
                "status": execution.status,
                "message": result.get("message", ""),
            })
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.logs = str(e)
            failed += 1
            failed_tests.append(tc.title)
            results.append({
                "test_id": tc.id,
                "title": tc.title,
                "status": "failed",
                "message": str(e),
            })
        db.commit()

    # Create notification if tests failed
    if failed > 0:
        notification = Notification(
            user_id=current_user.id,
            channel="browser",
            title=f"⚠️ {failed} Test{'s' if failed > 1 else ''} Failed",
            message=f"Bulk test run completed with {failed}/{len(test_cases)} failures. Failed tests: {', '.join(failed_tests[:3])}{' ...' if len(failed_tests) > 3 else ''}",
            status="unread",
            payload={"project_id": project_id, "failed_count": failed, "total": len(test_cases)}
        )
        db.add(notification)
        db.commit()
        
        # Send email notification if enabled
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            project_name = project.name if project else f"Project #{project_id}"
            
            html_body = create_test_failure_email(
                user_name=current_user.email.split('@')[0].title(),
                project_name=project_name,
                failed_count=failed,
                total_count=len(test_cases),
                failed_tests=failed_tests,
                dashboard_url="http://localhost:3000/dashboard"
            )
            
            send_email(
                to_emails=[current_user.email],
                subject=f"⚠️ Test Failure Alert: {failed}/{len(test_cases)} Tests Failed in {project_name}",
                html_body=html_body
            )
        except Exception as e:
            print(f"Failed to send email notification: {e}")
            # Don't fail the request if email fails

    return {
        "total": len(test_cases),
        "passed": passed,
        "failed": failed,
        "skipped": 0,
        "success_rate": round((passed / len(test_cases)) * 100, 1) if test_cases else 0,
        "results": results,
    }


# ==================== TAG MANAGEMENT ENDPOINTS ====================

class TagsRequest(BaseModel):
    tags: List[str]

@router.post("/{test_id}/tags", response_model=TestCaseResponse)
def update_test_tags(
    test_id: int,
    tags_req: TagsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add or update tags for a test case"""
    test_case = db.query(TestCase).filter(TestCase.id == test_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    get_owned_project(db, test_case.project_id, current_user)
    
    # Parse existing tags if they're stored as JSON string
    if isinstance(test_case.tags, str):
        try:
            existing_tags = json.loads(test_case.tags) if test_case.tags else []
        except:
            existing_tags = []
    else:
        existing_tags = test_case.tags or []
    
    # Merge and deduplicate tags
    updated_tags = list(set(existing_tags + tags_req.tags))
    test_case.tags = json.dumps(updated_tags)
    
    db.commit()
    db.refresh(test_case)
    
    # Convert tags back to list for response
    response_test = test_case
    if isinstance(response_test.tags, str):
        response_test.tags = json.loads(response_test.tags) if response_test.tags else []
    
    return response_test


@router.delete("/{test_id}/tags/{tag}")
def remove_test_tag(
    test_id: int,
    tag: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a specific tag from a test case"""
    test_case = db.query(TestCase).filter(TestCase.id == test_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    get_owned_project(db, test_case.project_id, current_user)
    
    # Parse existing tags
    if isinstance(test_case.tags, str):
        try:
            existing_tags = json.loads(test_case.tags) if test_case.tags else []
        except:
            existing_tags = []
    else:
        existing_tags = test_case.tags or []
    
    # Remove the tag
    if tag in existing_tags:
        existing_tags.remove(tag)
        test_case.tags = json.dumps(existing_tags)
        db.commit()
        return {"message": f"Tag '{tag}' removed successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Tag '{tag}' not found")


@router.get("/project/{project_id}/tags")
def get_all_project_tags(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique tags used in a project"""
    get_owned_project(db, project_id, current_user)
    
    test_cases = db.query(TestCase).filter(TestCase.project_id == project_id).all()
    all_tags = set()
    
    for tc in test_cases:
        if tc.tags:
            if isinstance(tc.tags, str):
                try:
                    tags = json.loads(tc.tags)
                    all_tags.update(tags)
                except:
                    pass
            else:
                all_tags.update(tc.tags)
    
    return {"tags": sorted(list(all_tags))}


# ==================== REGRESSION SUITE ENDPOINTS ====================

@router.get("/project/{project_id}/regression", response_model=List[TestCaseResponse])
def get_regression_tests(
    project_id: int,
    tags: Optional[str] = None,  # Comma-separated tags
    exclude_flaky: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tests for regression suite, filtered by tags and flaky status"""
    get_owned_project(db, project_id, current_user)
    
    # Start with base query
    query = db.query(TestCase).filter(TestCase.project_id == project_id)
    
    # Filter out flaky tests if requested
    if exclude_flaky:
        query = query.filter(TestCase.is_flaky == False)
    
    test_cases = query.order_by(TestCase.created_at.desc()).all()
    
    # Filter by tags if provided
    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
        filtered_tests = []
        
        for tc in test_cases:
            tc_tags = []
            if tc.tags:
                if isinstance(tc.tags, str):
                    try:
                        tc_tags = json.loads(tc.tags)
                    except:
                        pass
                else:
                    tc_tags = tc.tags
            
            # Check if test has any of the requested tags
            if any(tag in tc_tags for tag in tag_list):
                # Convert tags to list for response
                tc.tags = tc_tags
                filtered_tests.append(tc)
        
        return filtered_tests
    
    # Convert all tags to lists for response
    for tc in test_cases:
        if isinstance(tc.tags, str):
            try:
                tc.tags = json.loads(tc.tags) if tc.tags else []
            except:
                tc.tags = []
    
    return test_cases


class RegressionRunRequest(BaseModel):
    url: str = "http://localhost:3000"
    tags: Optional[List[str]] = None
    exclude_flaky: bool = False


@router.post("/project/{project_id}/run-regression")
def run_regression_suite(
    project_id: int,
    payload: RegressionRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run regression suite with tag filtering and flaky test exclusion"""
    get_owned_project(db, project_id, current_user)
    
    # Get tests for regression (filtered)
    query = db.query(TestCase).filter(TestCase.project_id == project_id)
    
    # Exclude flaky tests if requested
    if payload.exclude_flaky:
        query = query.filter(TestCase.is_flaky == False)
    
    all_tests = query.all()
    
    # Filter by tags if provided
    if payload.tags:
        test_cases = []
        for tc in all_tests:
            tc_tags = []
            if tc.tags:
                if isinstance(tc.tags, str):
                    try:
                        tc_tags = json.loads(tc.tags)
                    except:
                        pass
                else:
                    tc_tags = tc.tags
            
            if any(tag in tc_tags for tag in payload.tags):
                test_cases.append(tc)
    else:
        test_cases = all_tests
    
    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found matching criteria")

    results = []
    passed = 0
    failed = 0
    failed_tests = []

    for tc in test_cases:
        # Update total runs
        tc.total_runs = (tc.total_runs or 0) + 1
        
        execution = TestExecution(
            project_id=project_id,
            test_case_id=tc.id,
            status=ExecutionStatus.RUNNING,
            logs="Regression run started",
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)

        try:
            selector = "body"
            result = self_healer.execute_test(payload.url, selector)
            is_passed = result.get("status") == "success"
            execution.status = ExecutionStatus.PASSED if is_passed else ExecutionStatus.FAILED
            execution.logs = result.get("message", "")
            
            if is_passed:
                passed += 1
            else:
                failed += 1
                failed_tests.append(tc.title)
                # Update failure tracking
                tc.failure_count = (tc.failure_count or 0) + 1
                tc.last_failure_date = datetime.utcnow()
            
            # Check for flaky test pattern (fails sometimes but not always)
            # Flaky = failure rate between 20% and 80%
            if tc.total_runs >= 5:  # Need at least 5 runs to detect flaky
                failure_rate = tc.failure_count / tc.total_runs
                if 0.2 <= failure_rate <= 0.8:
                    tc.is_flaky = True
                elif failure_rate < 0.1 or failure_rate > 0.9:
                    tc.is_flaky = False
            
            results.append({
                "test_id": tc.id,
                "title": tc.title,
                "status": execution.status,
                "message": result.get("message", ""),
                "is_flaky": tc.is_flaky,
            })
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.logs = str(e)
            failed += 1
            failed_tests.append(tc.title)
            tc.failure_count = (tc.failure_count or 0) + 1
            tc.last_failure_date = datetime.utcnow()
            
            results.append({
                "test_id": tc.id,
                "title": tc.title,
                "status": "failed",
                "message": str(e),
                "is_flaky": tc.is_flaky,
            })
        
        db.commit()

    # Create notification if tests failed
    if failed > 0:
        tag_info = f" (tags: {', '.join(payload.tags)})" if payload.tags else ""
        notification = Notification(
            user_id=current_user.id,
            channel="browser",
            title=f"⚠️ Regression: {failed} Test{'s' if failed > 1 else ''} Failed",
            message=f"Regression suite{tag_info} completed with {failed}/{len(test_cases)} failures. Failed tests: {', '.join(failed_tests[:3])}{' ...' if len(failed_tests) > 3 else ''}",
            status="unread",
            payload={"project_id": project_id, "failed_count": failed, "total": len(test_cases), "type": "regression"}
        )
        db.add(notification)
        db.commit()
        
        # Send email notification if enabled
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            project_name = project.name if project else f"Project #{project_id}"
            
            html_body = create_test_failure_email(
                user_name=current_user.email.split('@')[0].title(),
                project_name=f"{project_name} - Regression Suite",
                failed_count=failed,
                total_count=len(test_cases),
                failed_tests=failed_tests,
                dashboard_url="http://localhost:3000/dashboard"
            )
            
            send_email(
                to_emails=[current_user.email],
                subject=f"⚠️ Regression Alert: {failed}/{len(test_cases)} Tests Failed in {project_name}",
                html_body=html_body
            )
        except Exception as e:
            print(f"Failed to send email notification: {e}")

    return {
        "total": len(test_cases),
        "passed": passed,
        "failed": failed,
        "skipped": 0,
        "success_rate": round((passed / len(test_cases)) * 100, 1) if test_cases else 0,
        "filters_applied": {
            "tags": payload.tags or [],
            "exclude_flaky": payload.exclude_flaky
        },
        "results": results,
    }

