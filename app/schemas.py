import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class JobResponse(BaseModel):
    id: uuid.UUID
    filename: str
    status: str
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SegmentResponse(BaseModel):
    id: uuid.UUID
    speaker_label: str
    start_time: float
    end_time: float
    text: str

    class Config:
        from_attributes = True

class TranscriptResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    full_text: str
    language: str
    duration_seconds: float
    segments: List[SegmentResponse] = []

    class Config:
        from_attributes = True