import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ─── Auth Schemas ────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Job Schemas ─────────────────────────────────────

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