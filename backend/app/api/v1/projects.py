from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.cache import Cache, invalidate_dashboard_cache
from app.models.user import User
from app.models.project import Project
from app.api.v1.dependencies import get_owned_project

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    repository_url: Optional[str] = None
    deployment_url: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    repository_url: Optional[str] = None
    deployment_url: Optional[str] = None
    owner_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_project = Project(
        name=project.name,
        description=project.description,
        repository_url=project.repository_url,
        deployment_url=project.deployment_url,
        owner_id=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Invalidate dashboard cache
    invalidate_dashboard_cache()
    Cache.delete(f"projects:user:{current_user.id}")
    
    return db_project

@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check cache
    cache_key = f"projects:user:{current_user.id}"
    cached = Cache.get(cache_key)
    if cached:
        return cached
    
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    
    # Cache for 5 minutes
    Cache.set(cache_key, projects, ttl=300)
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_owned_project(db, project_id, current_user)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = get_owned_project(db, project_id, current_user)
    project.name = project_update.name
    project.description = project_update.description
    project.repository_url = project_update.repository_url
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = get_owned_project(db, project_id, current_user)
    db.delete(project)
    db.commit()
    
    # Invalidate caches
    invalidate_dashboard_cache()
    Cache.delete(f"projects:user:{current_user.id}")
    Cache.delete_pattern(f"project:{project_id}")
