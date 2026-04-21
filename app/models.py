import uuid
from sqlalchemy import Column, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path = Column(String(500), nullable=True)
    filename = Column(String(255))
    status = Column(String(50), default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    transcript = relationship("Transcript", back_populates="job", uselist=False)

class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    full_text = Column(Text)
    language = Column(String(10))
    duration_seconds = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("Job", back_populates="transcript")
    segments = relationship("Segment", back_populates="transcript")

class Segment(Base):
    __tablename__ = "segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcripts.id"))
    speaker_label = Column(String(50))
    start_time = Column(Float)
    end_time = Column(Float)
    text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transcript = relationship("Transcript", back_populates="segments")