import os
import sys
import time

# Add parent directory to path so worker can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import redis
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Job, Transcript, Segment
from app.config import settings
from worker.transcriber import transcribe
from worker.diarizer import diarize
from worker.aligner import align

# Create tables if not exist
Base.metadata.create_all(bind=engine)

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

STREAM_NAME = "audio:jobs"
GROUP_NAME = "workers"
CONSUMER_NAME = "worker-1"

def create_consumer_group():
    try:
        r.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
        print(f"Consumer group '{GROUP_NAME}' created.")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" in str(e):
            print(f"Consumer group '{GROUP_NAME}' already exists.")
        else:
            raise

def update_job_status(db: Session, job_id: str, status: str, error: str = None):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job:
        job.status = status
        if error:
            job.error_message = error
        db.commit()

def process_job(job_id: str, file_path: str, filename: str):
    db = SessionLocal()
    try:
        print(f"Processing job {job_id} — {filename}")
        update_job_status(db, job_id, "processing")

        # Step 1 — Transcribe with Whisper
        print(f"Transcribing {file_path}...")
        transcription = transcribe(file_path)
        print(f"Transcription done. Language: {transcription['language']}")

        # Step 2 — Diarize with pyannote
        print(f"Diarizing {file_path}...")
        diarization = diarize(file_path)
        print(f"Diarization done. Found {len(set(d['speaker'] for d in diarization))} speakers.")

        # Step 3 — Align speakers with transcript
        aligned_segments = align(transcription["segments"], diarization)

        # Step 4 — Store results in PostgreSQL
        # Get audio duration from last segment
        duration = float(transcription["segments"][-1]["end"]) if transcription["segments"] else 0.0

        transcript = Transcript(
            job_id=job_id,
            full_text=transcription["text"],
            language=transcription["language"],
            duration_seconds=duration
        )
        db.add(transcript)
        db.flush()

        for seg in aligned_segments:
            segment = Segment(
                transcript_id=transcript.id,
                speaker_label=seg["speaker"],
                start_time=float(seg["start"]),  # convert numpy float to Python float
                end_time=float(seg["end"]),  # convert numpy float to Python float
                text=seg["text"]
            )
            db.add(segment)

        db.commit()
        update_job_status(db, job_id, "completed")
        print(f"Job {job_id} completed successfully.")


    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        db.rollback()
        update_job_status(db, job_id, "failed", error=str(e))
    finally:
        db.close()

def main():
    print("Worker started. Waiting for jobs...")
    create_consumer_group()

    while True:
        try:
            # Read new messages from stream
            messages = r.xreadgroup(
                GROUP_NAME,
                CONSUMER_NAME,
                {STREAM_NAME: ">"},  # ">" means only new messages
                count=1,
                block=5000           # block for 5 seconds if no messages
            )

            if not messages:
                continue

            for stream, entries in messages:
                for message_id, data in entries:
                    job_id = data.get("job_id")
                    file_path = data.get("file_path")
                    filename = data.get("filename")

                    try:
                        process_job(job_id, file_path, filename)
                        # Acknowledge message — removes from pending list
                        r.xack(STREAM_NAME, GROUP_NAME, message_id)
                    except Exception as e:
                        print(f"Failed to process message {message_id}: {e}")

        except KeyboardInterrupt:
            print("Worker stopped.")
            break
        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()