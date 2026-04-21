import os
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job, Transcript
from app.schemas import JobResponse, TranscriptResponse
from fastapi.responses import FileResponse
from app.models import Job, Transcript, Segment
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["jobs"])

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/jobs/{job_id}/transcript", response_model=TranscriptResponse)
def get_transcript(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Transcript not ready. Job status: {job.status}"
        )
    transcript = db.query(Transcript).filter(
        Transcript.job_id == job_id
    ).first()
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript

@router.get("/jobs")
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(20).all()
    return jobs


@router.get("/audio/{job_id}")
def serve_audio(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job.file_path or not os.path.exists(job.file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(job.file_path, media_type="audio/mpeg")



class SegmentUpdate(BaseModel):
    text: str

@router.patch("/segments/{segment_id}")
def update_segment(segment_id: uuid.UUID, body: SegmentUpdate, db: Session = Depends(get_db)):
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    segment.text = body.text
    db.commit()
    db.refresh(segment)
    return {"id": str(segment.id), "text": segment.text}

