from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Requirement(Base):
    __tablename__ = "requirements"
    __table_args__ = (
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)  # Index for filtering by project
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)
    structured_data = Column(JSON, nullable=True)
    status = Column(String, default="pending", index=True)  # Index for status filtering
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # Index for sorting
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="requirements")
