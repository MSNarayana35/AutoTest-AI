from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.cache import invalidate_dashboard_cache, Cache
from app.models.user import User
from app.models.requirement import Requirement
from app.models.test_case import TestCase
from app.api.v1.dependencies import get_owned_project
from app.agents.requirement_agent import RequirementAgent
from app.agents.test_generator_agent import TestGeneratorAgent
import os
from app.core.config import settings

router = APIRouter()

requirement_agent = RequirementAgent()
test_generator_agent = TestGeneratorAgent()

class RequirementCreate(BaseModel):
    project_id: int
    title: str
    content: str

class RequirementResponse(BaseModel):
    id: int
    project_id: int
    title: str
    content: str
    structured_data: Optional[dict] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
async def create_requirement(
    background_tasks: BackgroundTasks,
    project_id: int = Form(...),
    title: str = Form(...),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_owned_project(db, project_id, current_user)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    file_path = None
    if file:
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content_bytes = await file.read()
            buffer.write(content_bytes)
        
        if not content:
            content = f"Uploaded file: {file.filename}"

    # Ensure content is never None before storing
    if not content:
        content = ""

    db_requirement = Requirement(
        project_id=project_id,
        title=title,
        content=content,
        file_path=file_path,
        status="analyzing"
    )
    db.add(db_requirement)
    db.commit()
    db.refresh(db_requirement)
    
    # Optimized: Process analysis in background
    def analyze_and_generate_tests():
        from app.core.database import SessionLocal
        bg_db = SessionLocal()
        try:
            req = bg_db.query(Requirement).filter(Requirement.id == db_requirement.id).first()
            if not req:
                return
            
            structured_data = None
            try:
                structured_data = requirement_agent.analyze_requirement(content)
                req.structured_data = structured_data
                req.status = "analyzed"
            except Exception as e:
                print(f"Error analyzing requirement: {e}")
                req.structured_data = {"error": str(e)}
                req.status = "error"
            
            bg_db.commit()
            
            # Auto-generate test cases if analysis succeeded
            if req.status == "analyzed" and structured_data:
                try:
                    test_cases = test_generator_agent.generate_test_cases(structured_data)
                    
                    for idx, test_case_data in enumerate(test_cases):
                        db_test_case = TestCase(
                            project_id=project_id,
                            requirement_id=req.id,
                            title=test_case_data.get("title", f"Test Case {idx + 1}"),
                            description=test_case_data.get("description", ""),
                            test_type=test_case_data.get("test_type", "functional"),
                            status="ready",
                            script=test_case_data.get("script", ""),
                        )
                        bg_db.add(db_test_case)
                    bg_db.commit()
                except Exception as e:
                    print(f"Error auto-generating test cases: {e}")
            
            # Invalidate cache
            invalidate_dashboard_cache()
            Cache.delete_pattern(f"project:{project_id}")
        finally:
            bg_db.close()
    
    background_tasks.add_task(analyze_and_generate_tests)
    
    return db_requirement

@router.get("/project/{project_id}", response_model=List[RequirementResponse])
def get_project_requirements(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    get_owned_project(db, project_id, current_user)
    # Optimized: Use index on created_at for sorting + pagination
    requirements = db.query(Requirement).filter(
        Requirement.project_id == project_id
    ).order_by(Requirement.created_at.desc()).offset(skip).limit(limit).all()
    return requirements
