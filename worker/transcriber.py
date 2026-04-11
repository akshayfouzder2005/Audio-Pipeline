import whisper
import os

# Load model once at startup — not on every request
# "base" is fast and good enough for demo
# Options: tiny, base, small, medium, large
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading Whisper model...")
        _model = whisper.load_model("base")
        print("Whisper model loaded.")
    return _model

def transcribe(file_path: str) -> dict:
    model = get_model()

    result = model.transcribe(
        file_path,
        verbose=False,
        word_timestamps=True   # needed for speaker alignment later
    )

    return {
        "text": result["text"].strip(),
        "language": result["language"],
        "segments": [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            }
            for seg in result["segments"]
        ]
    }