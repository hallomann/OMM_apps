from __future__ import annotations

import asyncio

import edge_tts

from voice_helper.schema import FieldSpec

DEFAULT_VOICE = "ru-RU-SvetlanaNeural"


def build_listen_message(field: FieldSpec) -> str:
    """Return the spoken prompt for the current field."""
    return field.tts_prompt


async def async_speak(text: str, *, voice: str = DEFAULT_VOICE) -> bytes:
    communicate = edge_tts.Communicate(text, voice)
    chunks: list[bytes] = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)


def speak(text: str, *, voice: str = DEFAULT_VOICE) -> bytes:
    return asyncio.run(async_speak(text, voice=voice))
