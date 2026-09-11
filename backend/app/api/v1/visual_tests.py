"""
Visual Regression Testing API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from PIL import Image
import io
import os

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.visual_testing import VisualTest, VisualBaseline, VisualComparison, VisualTestRun
from app.api.v1.dependencies import get_owned_project
from app.services.visual_testing_service import VisualTestingService

router = APIRouter()
visual_service = VisualTestingService()


# ==================== REQUEST/RESPONSE MODELS ====================

class VisualTestCreate(BaseModel):
    name: str
    description: Optional[str] = None
    url: str
    selector: Optional[str] = None
    viewport_width: int = 1920
    viewport_height: int = 1080
    browser: str = "chromium"
    device: Optional[str] = None
    full_page: bool = False
    threshold: float = 0.1
    ignore_regions: Optional[List[Dict]] = None


class VisualTestUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    selector: Optional[str] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    browser: Optional[str] = None
    threshold: Optional[float] = None
    ignore_regions: Optional[List[Dict]] = None
    is_active: Optional[bool] = None


class BaselineApproval(BaseModel):
    notes: Optional[str] = None


class ComparisonReview(BaseModel):
    action: str  # approve_change, update_baseline, reject, ignore
    notes: Optional[str] = None


class VisualTestResponse(BaseModel):
    id: int
    project_id: int
    name: str
    description: Optional[str]
    url: str
    viewport_width: int
    viewport_height: int
    browser: str
    threshold: float
    is_active: bool
    has_baseline: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ComparisonResponse(BaseModel):
    id: int
    visual_test_id: int
    difference_percentage: float
    passed: bool
    status: str
    screenshot_path: str
    diff_path: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== VISUAL TEST CRUD ====================

@router.post("/projects/{project_id}/visual-tests", response_model=VisualTestResponse)
async def create_visual_test(
    project_id: int,
    test_data: VisualTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new visual test"""
    # Verify project ownership
    get_owned_project(db, project_id, current_user)
    
    visual_test = VisualTest(
        project_id=project_id,
        created_by=current_user.id,
        **test_data.dict()
    )
    
    db.add(visual_test)
    db.commit()
    db.refresh(visual_test)
    
    return visual_test


@router.get("/projects/{project_id}/visual-tests", response_model=List[VisualTestResponse])
async def list_visual_tests(
    project_id: int,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all visual tests for a project"""
    get_owned_project(db, project_id, current_user)
    
    query = db.query(VisualTest).filter(VisualTest.project_id == project_id)
    
    if is_active is not None:
        query = query.filter(VisualTest.is_active == is_active)
    
    tests = query.order_by(VisualTest.created_at.desc()).all()
    return tests


@router.get("/visual-tests/{test_id}", response_model=VisualTestResponse)
async def get_visual_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get visual test details"""
    visual_test = db.query(VisualTest).filter(VisualTest.id == test_id).first()
    
    if not visual_test:
        raise HTTPException(status_code=404, detail="Visual test not found")
    
    # Verify project access
    get_owned_project(db, visual_test.project_id, current_user)
    
    return visual_test


@router.put("/visual-tests/{test_id}", response_model=VisualTestResponse)
async def update_visual_test(
    test_id: int,
    test_data: VisualTestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update visual test configuration"""
    visual_test = db.query(VisualTest).filter(VisualTest.id == test_id).first()
    
    if not visual_test:
        raise HTTPException(status_code=404, detail="Visual test not found")
    
    get_owned_project(db, visual_test.project_id, current_user)
    
    # Update fields
    for field, value in test_data.dict(exclude_unset=True).items():
        setattr(visual_test, field, value)
    
    visual_test.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(visual_test)
    
    return visual_test


@router.delete("/visual-tests/{test_id}")
async def delete_visual_test(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete visual test"""
    visual_test = db.query(VisualTest).filter(VisualTest.id == test_id).first()
    
    if not visual_test:
        raise HTTPException(status_code=404, detail="Visual test not found")
    
    get_owned_project(db, visual_test.project_id, current_user)
    
    db.delete(visual_test)
    db.commit()
    
    return {"message": "Visual test deleted successfully"}


# ==================== BASELINE MANAGEMENT ====================

@router.post("/visual-tests/{test_id}/baseline")
async def upload_baseline(
    test_id: int,
    file: UploadFile = File(...),
    version: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload baseline screenshot"""
    visual_test = db.query(VisualTest).filter(VisualTest.id == test_id).first()
    
    if not visual_test:
        raise HTTPException(status_code=404, detail="Visual test not found")
    
    get_owned_project(db, visual_test.project_id, current_user)
    
    # Read uploaded file
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # Save baseline
    baseline_path = visual_service.save_screenshot(image, test_id, "baseline")
    
    # Get image info
    full_path = os.path.join("uploads", baseline_path)
    image_info = visual_service.get_image_info(full_path)
    
    # Create baseline record
    baseline = VisualBaseline(
        visual_test_id=test_id,
        version=version,
        screenshot_path=baseline_path,
        width=image_info['width'],
        height=image_info['height'],
        file_size=image_info['file_size'],
        hash=image_info['hash'],
        created_by=current_user.id,
        notes=notes,
        is_active=True,
        is_approved=False
    )
    
    db.add(baseline)
    
    # Deactivate previous baselines
    db.query(VisualBaseline).filter(
        VisualBaseline.visual_test_id == test_id,
        VisualBaseline.id != baseline.id
    ).update({"is_active": False})
    
    # Update visual test
    visual_test.has_baseline = True
    
    db.commit()
    db.refresh(baseline)
    
    return {
        "id": baseline.id,
        "screenshot_path": baseline.screenshot_path,
        "width": baseline.width,
        "height": baseline.height,
        "hash": baseline.hash
    }


@router.post("/baselines/{baseline_id}/approve")
async def approve_baseline(
    baseline_id: int,
    approval: BaselineApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve baseline screenshot"""
    baseline = db.query(VisualBaseline).filter(VisualBaseline.id == baseline_id).first()
    
    if not baseline:
        raise HTTPException(status_code=404, detail="Baseline not found")
    
    visual_test = db.query(VisualTest).filter(VisualTest.id == baseline.visual_test_id).first()
    get_owned_project(db, visual_test.project_id, current_user)
    
    baseline.is_approved = True
    baseline.approved_by = current_user.id
    baseline.approved_at = datetime.utcnow()
    if approval.notes:
        baseline.notes = approval.notes
    
    db.commit()
    
    return {"message": "Baseline approved successfully"}


@router.get("/visual-tests/{test_id}/baselines")
async def list_baselines(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all baselines for a visual test"""
    visual_test = db.query(VisualTest).filter(VisualTest.id == test_id).first()
    
    if not visual_test:
        raise HTTPException(status_code=404, detail="Visual test not found")
    
    get_owned_project(db, visual_test.project_id, current_user)
    
    baselines = db.query(VisualBaseline).filter(
        VisualBaseline.visual_test_id == test_id
    ).order_by(VisualBaseline.created_at.desc()).all()
    
    return baselines


# ==================== SCREENSHOT COMPARISON ====================

@router.post("/visual-tests/{test_id}/compare")
async def compare_screenshot(
    test_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare screenshot against baseline"""
    visual_test = db.query(VisualTest).filter(VisualTest.id == test_id).first()
    
    if not visual_test:
        raise HTTPException(status_code=404, detail="Visual test not found")
    
    get_owned_project(db, visual_test.project_id, current_user)
    
    # Get active baseline
    baseline = db.query(VisualBaseline).filter(
        VisualBaseline.visual_test_id == test_id,
        VisualBaseline.is_active == True
    ).first()
    
    if not baseline:
        raise HTTPException(status_code=404, detail="No active baseline found. Please upload a baseline first.")
    
    # Read uploaded screenshot
    contents = await file.read()
    screenshot = Image.open(io.BytesIO(contents))
    
    # Save screenshot
    screenshot_path = visual_service.save_screenshot(screenshot, test_id, "screenshot")
    full_screenshot_path = os.path.join("uploads", screenshot_path)
    full_baseline_path = os.path.join("uploads", baseline.screenshot_path)
    
    # Perform comparison
    comparison_result = visual_service.compare_images(
        baseline_path=full_baseline_path,
        screenshot_path=full_screenshot_path,
        threshold=visual_test.threshold,
        ignore_regions=visual_test.ignore_regions
    )
    
    # Save diff images
    diff_image = comparison_result['diff_image']
    highlighted_diff = comparison_result['highlighted_diff']
    
    diff_path = visual_service.save_screenshot(diff_image, test_id, "diff")
    highlighted_path = visual_service.save_screenshot(highlighted_diff, test_id, "diff_highlighted")
    
    # Create comparison record
    comparison = VisualComparison(
        visual_test_id=test_id,
        baseline_id=baseline.id,
        screenshot_path=screenshot_path,
        diff_path=diff_path,
        difference_percentage=comparison_result['difference_percentage'],
        pixel_difference_count=comparison_result['pixel_difference_count'],
        mismatch_percentage=comparison_result['difference_percentage'],
        ssim_score=comparison_result['ssim_score'],
        mse_score=comparison_result['mse_score'],
        status="passed" if comparison_result['passed'] else "failed",
        passed=comparison_result['passed'],
        browser=visual_test.browser,
        viewport=f"{visual_test.viewport_width}x{visual_test.viewport_height}",
        extra_data={
            'histogram_similarity': comparison_result['histogram_similarity'],
            'hash_distance': comparison_result['hash_distance'],
            'highlighted_diff_path': highlighted_path
        }
    )
    
    db.add(comparison)
    db.commit()
    db.refresh(comparison)
    
    return {
        "id": comparison.id,
        "passed": comparison.passed,
        "difference_percentage": comparison.difference_percentage,
        "ssim_score": comparison.ssim_score,
        "screenshot_path": comparison.screenshot_path,
        "diff_path": comparison.diff_path,
        "highlighted_diff_path": highlighted_path,
        "status": comparison.status
    }


@router.get("/visual-tests/{test_id}/comparisons", response_model=List[ComparisonResponse])
async def list_comparisons(
    test_id: int,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List comparison history"""
    visual_test = db.query(VisualTest).filter(VisualTest.id == test_id).first()
    
    if not visual_test:
        raise HTTPException(status_code=404, detail="Visual test not found")
    
    get_owned_project(db, visual_test.project_id, current_user)
    
    query = db.query(VisualComparison).filter(VisualComparison.visual_test_id == test_id)
    
    if status:
        query = query.filter(VisualComparison.status == status)
    
    comparisons = query.order_by(VisualComparison.created_at.desc()).limit(limit).all()
    
    return comparisons


@router.post("/comparisons/{comparison_id}/review")
async def review_comparison(
    comparison_id: int,
    review: ComparisonReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Review and take action on comparison result"""
    comparison = db.query(VisualComparison).filter(VisualComparison.id == comparison_id).first()
    
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    visual_test = db.query(VisualTest).filter(VisualTest.id == comparison.visual_test_id).first()
    get_owned_project(db, visual_test.project_id, current_user)
    
    # Update comparison
    comparison.action = review.action
    comparison.reviewed_by = current_user.id
    comparison.reviewed_at = datetime.utcnow()
    comparison.review_notes = review.notes
    
    if review.action == "approve_change":
        comparison.status = "approved"
    elif review.action == "update_baseline":
        # Create new baseline from this screenshot
        screenshot_image = Image.open(os.path.join("uploads", comparison.screenshot_path))
        new_baseline_path = visual_service.save_screenshot(screenshot_image, visual_test.id, "baseline")
        
        image_info = visual_service.get_image_info(os.path.join("uploads", new_baseline_path))
        
        new_baseline = VisualBaseline(
            visual_test_id=visual_test.id,
            screenshot_path=new_baseline_path,
            width=image_info['width'],
            height=image_info['height'],
            file_size=image_info['file_size'],
            hash=image_info['hash'],
            created_by=current_user.id,
            is_active=True,
            is_approved=True,
            approved_by=current_user.id,
            approved_at=datetime.utcnow(),
            notes="Updated from comparison review"
        )
        
        db.add(new_baseline)
        
        # Deactivate old baselines
        db.query(VisualBaseline).filter(
            VisualBaseline.visual_test_id == visual_test.id,
            VisualBaseline.is_active == True
        ).update({"is_active": False})
        
        comparison.status = "approved"
    elif review.action == "reject":
        comparison.status = "rejected"
    elif review.action == "ignore":
        comparison.status = "ignored"
    
    db.commit()
    
    return {"message": f"Comparison {review.action} successfully"}


# ==================== BATCH OPERATIONS ====================

@router.post("/projects/{project_id}/visual-tests/run")
async def run_all_visual_tests(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run all visual tests for a project"""
    get_owned_project(db, project_id, current_user)
    
    # Create run record
    run = VisualTestRun(
        project_id=project_id,
        triggered_by=current_user.id,
        trigger_type="manual",
        status="running"
    )
    
    db.add(run)
    db.commit()
    db.refresh(run)
    
    # Queue background task
    # background_tasks.add_task(execute_visual_test_run, run.id, db)
    
    return {
        "run_id": run.id,
        "status": "queued",
        "message": "Visual test run started"
    }


# ==================== STATISTICS ====================

@router.get("/projects/{project_id}/visual-tests/stats")
async def get_visual_test_stats(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get visual testing statistics"""
    get_owned_project(db, project_id, current_user)
    
    # Count tests
    total_tests = db.query(VisualTest).filter(
        VisualTest.project_id == project_id
    ).count()
    
    active_tests = db.query(VisualTest).filter(
        VisualTest.project_id == project_id,
        VisualTest.is_active == True
    ).count()
    
    with_baseline = db.query(VisualTest).filter(
        VisualTest.project_id == project_id,
        VisualTest.has_baseline == True
    ).count()
    
    # Recent comparisons
    recent_comparisons = db.query(VisualComparison).join(VisualTest).filter(
        VisualTest.project_id == project_id
    ).order_by(VisualComparison.created_at.desc()).limit(10).all()
    
    passed = sum(1 for c in recent_comparisons if c.passed)
    failed = sum(1 for c in recent_comparisons if not c.passed)
    
    return {
        "total_tests": total_tests,
        "active_tests": active_tests,
        "with_baseline": with_baseline,
        "recent_comparisons": {
            "total": len(recent_comparisons),
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / len(recent_comparisons) * 100) if recent_comparisons else 0
        }
    }
