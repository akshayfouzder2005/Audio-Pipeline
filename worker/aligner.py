def align(whisper_segments: list, diarization: list) -> list:
    aligned = []

    for seg in whisper_segments:
        seg_start = seg["start"]
        seg_end = seg["end"]
        seg_mid = (seg_start + seg_end) / 2

        # Find which speaker was talking at the midpoint of this segment
        speaker = "UNKNOWN"
        best_overlap = 0

        for d in diarization:
            # Calculate overlap between whisper segment and diarization turn
            overlap_start = max(seg_start, d["start"])
            overlap_end = min(seg_end, d["end"])
            overlap = max(0, overlap_end - overlap_start)

            if overlap > best_overlap:
                best_overlap = overlap
                speaker = d["speaker"]

        aligned.append({
            "speaker": speaker,
            "start": seg_start,
            "end": seg_end,
            "text": seg["text"]
        })

    return aligned