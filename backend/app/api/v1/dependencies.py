from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User


def get_owned_project(db: Session, project_id: int, current_user: User) -> Project:
    query = db.query(Project).filter(Project.id == project_id)
    if current_user.role.value != "admin":
        query = query.filter(Project.owner_id == current_user.id)

    project = query.first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project
