"""
Third-party Integration Models (Slack, Discord, etc.)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Integration(Base):
    """Third-party integrations"""
    __tablename__ = "integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    
    # Integration details
    type = Column(String, nullable=False)  # slack, discord, teams, jira
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Configuration (encrypted webhook URLs, tokens, etc.)
    config = Column(JSON, nullable=False)
    
    # Notification settings
    notify_on_test_complete = Column(Boolean, default=True)
    notify_on_test_failure = Column(Boolean, default=True)
    notify_on_bug_created = Column(Boolean, default=True)
    notify_on_regression_failure = Column(Boolean, default=True)
    notify_on_ci_cd_status = Column(Boolean, default=False)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Statistics
    total_notifications_sent = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    
    # Relationships
    project = relationship("Project")
    creator = relationship("User")


class NotificationLog(Base):
    """Log of sent notifications"""
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(Integer, ForeignKey("integrations.id"), index=True)
    
    # Notification details
    event_type = Column(String, nullable=False)  # test_complete, bug_created, etc.
    message = Column(Text, nullable=False)
    status = Column(String, default="sent")  # sent, failed, pending
    
    # Context
    reference_type = Column(String, nullable=True)  # test, bug, execution
    reference_id = Column(Integer, nullable=True)
    
    # Response
    response_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    sent_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    integration = relationship("Integration")
