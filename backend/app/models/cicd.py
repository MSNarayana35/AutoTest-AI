"""
CI/CD Configuration and Workflow Run Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class CICDConfig(Base):
    """CI/CD configuration for a project"""
    __tablename__ = "cicd_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True, index=True)
    
    # GitHub integration
    github_token_encrypted = Column(Text, nullable=True)  # Encrypted token
    repository_name = Column(String, nullable=True)  # Format: owner/repo
    default_branch = Column(String, default="main")
    
    # Workflow configuration
    workflows_enabled = Column(Boolean, default=False)
    auto_trigger = Column(Boolean, default=True)
    
    # Webhook configuration
    webhook_url = Column(String, nullable=True)
    webhook_secret = Column(String, nullable=True)
    webhook_enabled = Column(Boolean, default=False)
    
    # Additional settings
    python_version = Column(String, default="3.10")
    node_version = Column(String, default="20")
    test_command = Column(String, default="pytest")
    deployment_command = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="cicd_config")
    workflow_runs = relationship("WorkflowRun", back_populates="config", cascade="all, delete-orphan")


class WorkflowRun(Base):
    """Record of a workflow run"""
    __tablename__ = "workflow_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    config_id = Column(Integer, ForeignKey("cicd_configs.id"), index=True)
    
    # GitHub workflow info
    github_run_id = Column(String, unique=True, index=True)
    workflow_name = Column(String)
    workflow_path = Column(String, nullable=True)
    
    # Run details
    run_number = Column(Integer)
    event = Column(String)  # push, pull_request, schedule, workflow_dispatch
    status = Column(String, index=True)  # queued, in_progress, completed
    conclusion = Column(String, nullable=True, index=True)  # success, failure, cancelled, skipped
    
    # Branch and commit info
    branch = Column(String)
    commit_sha = Column(String)
    commit_message = Column(Text, nullable=True)
    author = Column(String, nullable=True)
    
    # Test results (if available)
    total_tests = Column(Integer, nullable=True)
    passed_tests = Column(Integer, nullable=True)
    failed_tests = Column(Integer, nullable=True)
    success_rate = Column(Integer, nullable=True)
    
    # URLs
    run_url = Column(String, nullable=True)
    logs_url = Column(String, nullable=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Additional data
    payload = Column(JSON, nullable=True)  # Full webhook payload
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    config = relationship("CICDConfig", back_populates="workflow_runs")


class WorkflowTemplate(Base):
    """Saved workflow templates for reuse"""
    __tablename__ = "workflow_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Template info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    template_type = Column(String, index=True)  # test, regression, deploy, etc.
    
    # Template content
    yaml_content = Column(Text, nullable=False)
    
    # Configuration
    is_public = Column(Boolean, default=False)
    is_official = Column(Boolean, default=False)
    
    # Usage stats
    usage_count = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
