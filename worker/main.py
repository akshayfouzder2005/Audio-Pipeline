import os
import sys
import time
import tempfile
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import redis
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Job, Transcript, Segment
from app.config import settings
from worker.groq_client import transcribe_and_diarize

Base.metadata.create_all(bind=engine)

r = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

STREAM_NAME = "audio:jobs"
GROUP_NAME  = "workers"
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


def download_audio(job_id: str, filename: str) -> str:
    """
    Download audio file from the API and save to a temp file.
    Returns the local temp file path.
    """
    api_url = f"{settings.API_BASE_URL}/api/audio/{job_id}"
    print(f"Downloading audio from {api_url}...")

    response = requests.get(api_url, timeout=120)
    response.raise_for_status()

    # Preserve original extension for Groq
    ext = os.path.splitext(filename)[-1].lower() or ".mp3"
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    tmp.write(response.content)
    tmp.close()

    print(f"Audio downloaded to {tmp.name} ({len(response.content) / 1024:.1f} KB)")
    return tmp.name


def process_job(job_id: str, file_path: str, filename: str):
    db = SessionLocal()
    local_path = None
    try:
        print(f"\nProcessing job {job_id} — {filename}")
        update_job_status(db, job_id, "processing")

        # Download audio from API (works whether worker is local or on Render)
        local_path = download_audio(job_id, filename)

        # Transcribe
        result = transcribe_and_diarize(local_path)

        print(f"Done. Language: {result['language']} | "
              f"Duration: {result['duration_seconds']:.1f}s | "
              f"Segments: {len(result['segments'])}")

        # Save Transcript
        transcript = Transcript(
            job_id=job_id,
            full_text=result["text"],
            language=result["language"],
            duration_seconds=result["duration_seconds"]
        )
        db.add(transcript)
        db.flush()

        # Save Segments
        for seg in result["segments"]:
            segment = Segment(
                transcript_id=transcript.id,
                speaker_label=seg["speaker"],
                start_time=float(seg["start"]),
                end_time=float(seg["end"]),
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
        # Clean up temp file
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
            print(f"Cleaned up {local_path}")


def main():
    print("Worker started. Waiting for jobs...")
    print(f"API base URL: {settings.API_BASE_URL}")
    create_consumer_group()

    while True:
        try:
            messages = r.xreadgroup(
                GROUP_NAME,
                CONSUMER_NAME,
                {STREAM_NAME: ">"},
                count=1,
                block=5000
            )

            if not messages:
                continue

            for stream, entries in messages:
                for message_id, data in entries:
                    job_id   = data.get("job_id")
                    file_path = data.get("file_path")
                    filename  = data.get("filename")

                    try:
                        process_job(job_id, file_path, filename)
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