#!/usr/bin/env python3
"""CLI check: WAV file -> STT -> normalize for a single field."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from configs.sfft_fields import SFFT_FIELDS
from voice_helper.normalize import normalize
from voice_helper.stt import transcribe


def _find_field(field_key: str):
    for field in SFFT_FIELDS:
        if field.key == field_key:
            return field
    available = ", ".join(field.key for field in SFFT_FIELDS)
    raise SystemExit(f"Unknown field {field_key!r}. Available: {available}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test STT + normalize pipeline")
    parser.add_argument("wav_path", type=Path, help="Path to a WAV recording")
    parser.add_argument(
        "--field",
        default="ktr1",
        help="Target field key from configs/sfft_fields.py",
    )
    args = parser.parse_args()

    if not args.wav_path.is_file():
        raise SystemExit(f"File not found: {args.wav_path}")

    field = _find_field(args.field)
    audio_bytes = args.wav_path.read_bytes()
    heard = transcribe(audio_bytes, language="ru")
    value = normalize(heard, field)

    print(f"Field:  {field.key} ({field.label})")
    print(f"Heard:  {heard!r}")
    print(f"Value:  {value!r}")


if __name__ == "__main__":
    main()
