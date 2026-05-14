# only schemas
from __future__ import annotations
import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime,
    Enum as SAEnum, ForeignKey, JSON, Boolean, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# Enums
class JobStatus(str, enum.Enum):
    PENDING   = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED    = "failed"


class Recommendation(str, enum.Enum):
    HIRE    = "Hire"
    IMPROVE = "Improve"
    REJECT  = "Reject"


# Tables 
class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    username   = Column(String(80),  unique=True, nullable=False, index=True)
    email      = Column(String(120), unique=True, nullable=False, index=True)
    password   = Column(String(255), nullable=False)
    is_active  = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resumes     = relationship("Resume",     back_populates="user", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    original_name   = Column(String(255), nullable=False)
    stored_path     = Column(String(512), nullable=False)
    file_type       = Column(String(10),  nullable=False)   # pdf | docx
    parsed_text     = Column(Text,        nullable=True)
    parse_status    = Column(SAEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    parse_task_id   = Column(String(64),  nullable=True)
    skills_found    = Column(JSON,        nullable=True)     # list[str]
    word_count      = Column(Integer,     nullable=True)
    uploaded_at     = Column(DateTime,    default=datetime.utcnow, nullable=False)

    user        = relationship("User",       back_populates="resumes")
    evaluations = relationship("Evaluation", back_populates="resume", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_resumes_user_status", "user_id", "parse_status"),
    )


class Job(Base):
    """A job posting that resumes are evaluated against."""
    __tablename__ = "jobs"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    title       = Column(String(200), nullable=False)
    company     = Column(String(200), nullable=True)
    description = Column(Text,        nullable=False)
    required_skills = Column(JSON,    nullable=True)   # list[str] extracted from JD
    created_by  = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)

    evaluations = relationship("Evaluation", back_populates="job")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    resume_id        = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id           = Column(Integer, ForeignKey("jobs.id",    ondelete="CASCADE"), nullable=False, index=True)
    user_id          = Column(Integer, ForeignKey("users.id",   ondelete="SET NULL"), nullable=True)

    # Scores (0–100 each)
    total_score         = Column(Float, nullable=True)
    skills_score        = Column(Float, nullable=True)
    experience_score    = Column(Float, nullable=True)
    keyword_score       = Column(Float, nullable=True)

    matched_skills  = Column(JSON, nullable=True)    # list[str]
    missing_skills  = Column(JSON, nullable=True)    # list[str]
    recommendation  = Column(SAEnum(Recommendation), nullable=True)
    reasoning       = Column(Text, nullable=True)
    ai_feedback     = Column(Text, nullable=True)

    status       = Column(SAEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    task_id      = Column(String(64),  nullable=True)
    error_detail = Column(Text,        nullable=True)

    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    resume = relationship("Resume",     back_populates="evaluations")
    job    = relationship("Job",        back_populates="evaluations")
    user   = relationship("User",       back_populates="evaluations")

    __table_args__ = (
        Index("ix_evaluations_resume_job", "resume_id", "job_id"),
        Index("ix_evaluations_status",     "status"),
    )