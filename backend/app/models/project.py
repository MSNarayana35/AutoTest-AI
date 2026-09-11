from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    repository_url = Column(String, nullable=True)
    deployment_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User", back_populates="projects")
    requirements = relationship("Requirement", back_populates="project")
    test_cases = relationship("TestCase", back_populates="project")
    executions = relationship("TestExecution", back_populates="project")
    cicd_config = relationship("CICDConfig", back_populates="project", uselist=False)
