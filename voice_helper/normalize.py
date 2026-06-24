from __future__ import annotations

import re
from typing import Any

from voice_helper.schema import FieldSpec, FieldType

_ONES: dict[str, int] = {
    "ноль": 0,
    "один": 1,
    "одна": 1,
    "одно": 1,
    "два": 2,
    "две": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "девять": 9,
    "десять": 10,
    "одиннадцать": 11,
    "двенадцать": 12,
    "тринадцать": 13,
    "четырнадцать": 14,
    "пятнадцать": 15,
    "шестнадцать": 16,
    "семнадцать": 17,
    "восемнадцать": 18,
    "девятнадцать": 19,
}

_TENS: dict[str, int] = {
    "двадцать": 20,
    "тридцать": 30,
    "сорок": 40,
    "пятьдесят": 50,
    "шестьдесят": 60,
    "семьдесят": 70,
    "восемьдесят": 80,
    "девяносто": 90,
}

_HUNDREDS: dict[str, int] = {
    "сто": 100,
}


def _prepare_text(text: str) -> str:
    cleaned = text.strip().lower().replace("ё", "е")
    cleaned = cleaned.replace(",", ".")
    return cleaned


def normalize_boolean(text: str, field: FieldSpec) -> int | None:
    cleaned = _prepare_text(text)
    if not cleaned:
        return None

    for label in field.true_labels:
        if label in cleaned:
            return 1
    for label in field.false_labels:
        if label in cleaned:
            return 0
    return None


def _parse_spoken_integer(cleaned: str) -> int | None:
    tokens = cleaned.split()
    if not tokens:
        return None

    total = 0
    for token in tokens:
        if token in _HUNDREDS:
            total += _HUNDREDS[token]
        elif token in _TENS:
            total += _TENS[token]
        elif token in _ONES:
            total += _ONES[token]
        else:
            return None
    return total


def normalize_number(text: str) -> float | None:
    cleaned = _prepare_text(text)
    if not cleaned:
        return None

    digit_match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if digit_match:
        return float(digit_match.group(0))

    integer = _parse_spoken_integer(cleaned)
    if integer is not None:
        return float(integer)
    return None


def normalize(text: str, field: FieldSpec) -> Any | None:
    if field.field_type is FieldType.BOOLEAN:
        return normalize_boolean(text, field)

    value = normalize_number(text)
    if value is None:
        return None
    if not field.validate_number(value):
        return None
    if value.is_integer():
        return int(value)
    return value
