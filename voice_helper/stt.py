from __future__ import annotations

import tempfile
from functools import lru_cache
from pathlib import Path

from faster_whisper import WhisperModel

DEFAULT_MODEL_SIZE = "base"


@lru_cache(maxsize=1)
def _load_model(model_size: str = DEFAULT_MODEL_SIZE) -> WhisperModel:
    return WhisperModel(model_size, device="cpu", compute_type="int8")


def transcribe(audio_bytes: bytes, language: str = "ru", *, model_size: str = DEFAULT_MODEL_SIZE) -> str:
    """Convert recorded audio bytes (WAV) to text."""
    if not audio_bytes:
        return ""

    model = _load_model(model_size)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.write(audio_bytes)

    try:
        segments, _info = model.transcribe(str(temp_path), language=language)
        parts = [segment.text.strip() for segment in segments if segment.text.strip()]
        return " ".join(parts).strip()
    finally:
        temp_path.unlink(missing_ok=True)
