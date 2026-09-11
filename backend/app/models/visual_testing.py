"""
Visual Regression Testing Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class VisualTest(Base):
    """Visual test configuration"""
    __tablename__ = "visual_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=True, index=True)
    
    # Test details
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=False)
    selector = Column(String, nullable=True)  # CSS selector for element screenshot
    
    # Configuration
    viewport_width = Column(Integer, default=1920)
    viewport_height = Column(Integer, default=1080)
    browser = Column(String, default="chromium")  # chromium, firefox, webkit
    device = Column(String, nullable=True)  # Mobile device name
    full_page = Column(Boolean, default=False)
    
    # Comparison settings
    threshold = Column(Float, default=0.1)  # Difference threshold (0-1)
    ignore_regions = Column(JSON, nullable=True)  # Areas to ignore [{x, y, width, height}]
    
    # Status
    is_active = Column(Boolean, default=True)
    has_baseline = Column(Boolean, default=False)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project")
    test_case = relationship("TestCase")
    creator = relationship("User")
    baselines = relationship("VisualBaseline", back_populates="visual_test", cascade="all, delete-orphan")
    comparisons = relationship("VisualComparison", back_populates="visual_test", cascade="all, delete-orphan")


class VisualBaseline(Base):
    """Baseline screenshots for visual comparison"""
    __tablename__ = "visual_baselines"
    
    id = Column(Integer, primary_key=True, index=True)
    visual_test_id = Column(Integer, ForeignKey("visual_tests.id"), index=True)
    
    # Baseline details
    version = Column(String, nullable=True)  # Version tag
    screenshot_path = Column(String, nullable=False)
    
    # Metadata
    width = Column(Integer)
    height = Column(Integer)
    file_size = Column(Integer)  # bytes
    hash = Column(String, nullable=True)  # Image hash for quick comparison
    
    # Status
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    
    # Approval
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    
    # Relationships
    visual_test = relationship("VisualTest", back_populates="baselines")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])


class VisualComparison(Base):
    """Visual comparison results"""
    __tablename__ = "visual_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    visual_test_id = Column(Integer, ForeignKey("visual_tests.id"), index=True)
    baseline_id = Column(Integer, ForeignKey("visual_baselines.id"), nullable=True, index=True)
    execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=True, index=True)
    
    # Comparison images
    screenshot_path = Column(String, nullable=False)  # Current screenshot
    diff_path = Column(String, nullable=True)  # Diff image highlighting changes
    
    # Comparison metrics
    difference_percentage = Column(Float, default=0.0)  # 0-100
    pixel_difference_count = Column(Integer, default=0)
    mismatch_percentage = Column(Float, default=0.0)
    
    # Structural similarity metrics
    ssim_score = Column(Float, nullable=True)  # Structural Similarity Index (-1 to 1)
    mse_score = Column(Float, nullable=True)  # Mean Squared Error
    
    # Status
    status = Column(String, default="pending")  # pending, passed, failed, approved, rejected
    passed = Column(Boolean, default=False)
    
    # Resolution
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Actions taken
    action = Column(String, nullable=True)  # approve_change, update_baseline, reject, ignore
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    browser = Column(String, nullable=True)
    viewport = Column(String, nullable=True)
    
    # Additional info
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    visual_test = relationship("VisualTest", back_populates="comparisons")
    baseline = relationship("VisualBaseline")
    execution = relationship("TestExecution")
    reviewer = relationship("User")


class VisualTestRun(Base):
    """Visual test run history"""
    __tablename__ = "visual_test_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), index=True)
    
    # Run details
    run_name = Column(String, nullable=True)
    total_tests = Column(Integer, default=0)
    passed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    new_baselines = Column(Integer, default=0)
    
    # Status
    status = Column(String, default="running")  # running, completed, failed
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Metadata
    triggered_by = Column(Integer, ForeignKey("users.id"))
    trigger_type = Column(String, nullable=True)  # manual, scheduled, ci_cd
    
    # Configuration
    browser = Column(String, nullable=True)
    viewport = Column(String, nullable=True)
    
    # Relationships
    project = relationship("Project")
    user = relationship("User")
