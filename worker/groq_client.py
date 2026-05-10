import os
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

SUPPORTED_EXTENSIONS = ('.mp3', '.wav', '.flac', '.m4a', '.ogg', '.mp4', '.webm')


def transcribe_and_diarize(file_path: str) -> dict:
    """
    Transcribe audio using Groq Whisper Large v3.
    Returns same structure as assemblyai_client for drop-in compatibility:
    {
        "text": str,
        "language": str,
        "duration_seconds": float,
        "segments": [
            {"speaker": str, "start": float, "end": float, "text": str}
        ]
    }
    """
    print(f"Sending {file_path} to Groq Whisper...")

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    with open(file_path, "rb") as f:
        response = client.audio.transcriptions.create(
            file=(os.path.basename(file_path), f),
            model="whisper-large-v3",
            response_format="verbose_json",  # gives us segments with timestamps
            language="en",                   # remove this line for auto-detect
            temperature=0.0
        )

    print(f"Groq transcription complete. Language: {response.language}")

    # verbose_json returns segments with start/end timestamps
    raw_segments = response.segments or []

    segments = []
    for seg in raw_segments:
        # Groq returns segments as dicts
        start = seg["start"] if isinstance(seg, dict) else seg.start
        end = seg["end"] if isinstance(seg, dict) else seg.end
        text = seg["text"] if isinstance(seg, dict) else seg.text
        segments.append({
            "speaker": "SPEAKER_00",
            "start": float(start),
            "end": float(end),
            "text": text.strip()
        })

    # duration: use last segment end, or fallback to response.duration if available
    duration = 0.0
    if segments:
        duration = segments[-1]["end"]
    elif hasattr(response, "duration") and response.duration:
        duration = float(response.duration)

    return {
        "text":             response.text.strip(),
        "language":         response.language or "en",
        "duration_seconds": duration,
        "segments":         segments
    }