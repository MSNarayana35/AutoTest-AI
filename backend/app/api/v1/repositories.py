from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_owned_project
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.platform import Repository
from app.models.user import User

router = APIRouter()


class RepositoryCreate(BaseModel):
    project_id: int
    provider: str = "github"
    url: HttpUrl
    default_branch: str = "main"


class RepositoryResponse(BaseModel):
    id: int
    project_id: int
    provider: str
    url: str
    default_branch: str
    current_branch: Optional[str] = None
    scan_summary: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
def connect_repository(
    payload: RepositoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_project(db, payload.project_id, current_user)
    repository = Repository(
        project_id=payload.project_id,
        provider=payload.provider,
        url=str(payload.url),
        default_branch=payload.default_branch,
        current_branch=payload.default_branch,
        scan_summary={"status": "connected", "message": "Repository metadata recorded"},
    )
    db.add(repository)
    db.commit()
    db.refresh(repository)
    return repository


@router.get("/project/{project_id}", response_model=list[RepositoryResponse])
def list_repositories(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_owned_project(db, project_id, current_user)
    return db.query(Repository).filter(Repository.project_id == project_id).all()
