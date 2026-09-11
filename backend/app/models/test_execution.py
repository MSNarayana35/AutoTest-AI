from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class ExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

class TestExecution(Base):
    __tablename__ = "test_executions"
    __table_args__ = (
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)  # Index for filtering by project
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), index=True)  # Index for test case lookups
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, index=True)  # Index for status filtering
    logs = Column(Text)
    screenshots = Column(JSON, nullable=True)
    execution_time = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # Index for sorting
    
    project = relationship("Project", back_populates="executions")
