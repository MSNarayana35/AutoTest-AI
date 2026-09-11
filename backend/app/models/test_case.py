from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class TestType(str, enum.Enum):
    FUNCTIONAL = "functional"
    BOUNDARY = "boundary"
    NEGATIVE = "negative"
    EDGE_CASE = "edge_case"
    PERFORMANCE = "performance"
    SECURITY = "security"
    REGRESSION = "regression"
    ACCESSIBILITY = "accessibility"

class TestCase(Base):
    __tablename__ = "test_cases"
    __table_args__ = (
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)  # Index for filtering by project
    requirement_id = Column(Integer, ForeignKey("requirements.id"), nullable=True, index=True)  # Index for requirement lookups
    title = Column(String, nullable=False)
    description = Column(Text)
    test_type = Column(SQLEnum(TestType), default=TestType.FUNCTIONAL, index=True)  # Index for type filtering
    script = Column(Text)
    script_language = Column(String, default="playwright")
    status = Column(String, default="pending", index=True)  # Index for status filtering
    
    # Regression Suite Management Fields
    tags = Column(JSON, default=list)  # Tags for categorization (e.g., ["smoke", "critical", "regression"])
    is_flaky = Column(Boolean, default=False, index=True)  # Flaky test indicator
    failure_count = Column(Integer, default=0)  # Track number of failures
    total_runs = Column(Integer, default=0)  # Track total number of runs
    last_failure_date = Column(DateTime(timezone=True), nullable=True)  # Last time test failed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # Index for sorting
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="test_cases")
