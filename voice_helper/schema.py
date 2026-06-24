from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Tuple


class FieldType(Enum):
    NUMBER = "number"
    BOOLEAN = "boolean"


@dataclass(frozen=True)
class FieldSpec:
    """Description of a single form field for the voice-guided input flow."""

    key: str
    label: str
    field_type: FieldType
    tts_prompt: str
    min_value: float | None = None
    max_value: float | None = None
    true_labels: Tuple[str, ...] = ("да", "есть", "имеется", "положительно")
    false_labels: Tuple[str, ...] = ("нет", "отсутствует", "не", "отрицательно")

    def validate_number(self, value: float) -> bool:
        if self.field_type is not FieldType.NUMBER:
            return False
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True
