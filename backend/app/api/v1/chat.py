from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.dependencies import get_owned_project
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.platform import ChatMessage
from app.models.user import User

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    project_id: Optional[int] = None


class ChatMessageResponse(BaseModel):
    id: int
    project_id: Optional[int] = None
    user_id: int
    role: str
    content: str
    metadata_json: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=list[ChatMessageResponse], status_code=status.HTTP_201_CREATED)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.project_id is not None:
        get_owned_project(db, payload.project_id, current_user)
    user_message = ChatMessage(
        project_id=payload.project_id,
        user_id=current_user.id,
        role="user",
        content=payload.message,
    )
    assistant_message = ChatMessage(
        project_id=payload.project_id,
        user_id=current_user.id,
        role="assistant",
        content="I can help analyze requirements, failures, reports, bugs, and test generation data recorded in AutoTest AI.",
        metadata_json={"source": "local_assistant"},
    )
    db.add_all([user_message, assistant_message])
    db.commit()
    db.refresh(user_message)
    db.refresh(assistant_message)
    return [user_message, assistant_message]


@router.get("/", response_model=list[ChatMessageResponse])
def list_chat_history(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id)
    if project_id is not None:
        get_owned_project(db, project_id, current_user)
        query = query.filter(ChatMessage.project_id == project_id)
    return query.order_by(ChatMessage.created_at.desc()).limit(100).all()
