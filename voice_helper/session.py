from __future__ import annotations

from enum import Enum
from typing import Any

from voice_helper.schema import FieldSpec


class SessionStatus(Enum):
    IDLE = "idle"
    PROMPT = "prompt"
    LISTEN = "listen"
    DONE = "done"


class VoiceSession:
    """Step-by-step voice input scenario (pure Python, no Streamlit)."""

    def __init__(self, fields: list[FieldSpec]) -> None:
        if not fields:
            raise ValueError("fields cannot be empty")
        self.fields = fields
        self.status = SessionStatus.IDLE
        self.index = 0
        self.values: dict[str, Any] = {}
        self.last_error: str | None = None

    def start(self) -> None:
        self.status = SessionStatus.PROMPT
        self.index = 0
        self.values = {}
        self.last_error = None

    def current_field(self) -> FieldSpec | None:
        if self.status in (SessionStatus.IDLE, SessionStatus.DONE):
            return None
        if self.index >= len(self.fields):
            return None
        return self.fields[self.index]

    def mark_listening(self) -> None:
        if self.status is SessionStatus.PROMPT:
            self.status = SessionStatus.LISTEN

    def record_value(self, key: str, value: Any) -> None:
        field = self.current_field()
        if field is None:
            raise RuntimeError("No active field to record value for")
        if field.key != key:
            raise ValueError(f"Expected field {field.key!r}, got {key!r}")
        self.values[key] = value
        self.last_error = None

    def advance(self) -> None:
        if self.status is SessionStatus.DONE:
            return
        self.index += 1
        if self.index >= len(self.fields):
            self.status = SessionStatus.DONE
        else:
            self.status = SessionStatus.PROMPT

    def retry(self, message: str | None = None) -> None:
        self.last_error = message
        if self.status is not SessionStatus.DONE:
            self.status = SessionStatus.PROMPT

    def is_done(self) -> bool:
        return self.status is SessionStatus.DONE

    def get_values(self) -> dict[str, Any]:
        return dict(self.values)
