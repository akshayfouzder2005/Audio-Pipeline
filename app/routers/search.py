import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Segment, Transcript

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search")
def search_segments(
    job_id: uuid.UUID,
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    transcript = db.query(Transcript).filter(
        Transcript.job_id == job_id
    ).first()

    if not transcript:
        return {"results": [], "query": q}

    # Simple keyword search — we'll upgrade to semantic later
    segments = db.query(Segment).filter(
        Segment.transcript_id == transcript.id,
        Segment.text.ilike(f"%{q}%")
    ).all()

    return {
        "query": q,
        "job_id": str(job_id),
        "results": [
            {
                "speaker": s.speaker_label,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "text": s.text
            }
            for s in segments
        ]
    }