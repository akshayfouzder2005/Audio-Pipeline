import os
import torch
import tempfile
from pyannote.audio import Pipeline

# Patch torch.load for PyTorch 2.6 compatibility
original_torch_load = torch.load
def patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return original_torch_load(*args, **kwargs)
torch.load = patched_torch_load

_pipeline = None

def get_pipeline():
    global _pipeline
    if _pipeline is None:
        print("Loading pyannote diarization pipeline...")
        _pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=os.environ.get("HF_TOKEN")
        )
        _pipeline = _pipeline.to(torch.device("cpu"))
        print("Diarization pipeline loaded.")
    return _pipeline

def convert_to_wav(file_path: str) -> str:
    import subprocess
    wav_path = file_path.rsplit(".", 1)[0] + "_converted.wav"
    subprocess.run([
        "ffmpeg", "-y", "-i", file_path,
        "-ar", "16000",   # 16kHz sample rate
        "-ac", "1",       # mono
        "-f", "wav",
        wav_path
    ], capture_output=True)
    return wav_path

def diarize(file_path: str) -> list:
    pipeline = get_pipeline()
    wav_path = convert_to_wav(file_path)

    try:
        print("Running diarization inference...")
        diarization = pipeline(wav_path, min_speakers=1, max_speakers=5)
        print("Diarization inference complete.")
    except Exception as e:
        print(f"Diarization inference failed: {e}")
        return []
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

    speakers = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speakers.append({
            "speaker": speaker,
            "start": round(turn.start, 3),
            "end": round(turn.end, 3)
        })

    return speakers