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
    cleaned = re.sub(r"[^\w\s.\-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_boolean(text: str, field: FieldSpec) -> int | None:
    cleaned = _prepare_text(text)
    if not cleaned:
        return None
    tokens = set(re.findall(r"\w+", cleaned))

    for label in field.true_labels:
        if label in tokens:
            return 1
    for label in field.false_labels:
        if label in tokens:
            return 0
    return None


_NUMBER_WORDS = set(_ONES) | set(_TENS) | set(_HUNDREDS)


def _parse_spoken_integer_from_tokens(tokens: list[str]) -> int | None:
    if not tokens:
        return None

    if len(tokens) > 1 and all(token in _ONES for token in tokens):
        return int("".join(str(_ONES[token]) for token in tokens))

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


def _parse_spoken_integer(cleaned: str) -> int | None:
    tokens = [token.strip(".") for token in cleaned.split()]
    return _parse_spoken_integer_from_tokens(tokens)


def _parse_spoken_integer_sequence(cleaned: str) -> int | None:
    tokens = [token.strip(".") for token in cleaned.split()]
    sequences: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token in _NUMBER_WORDS:
            current.append(token)
        elif current:
            sequences.append(current)
            current = []
    if current:
        sequences.append(current)

    for sequence in reversed(sequences):
        parsed = _parse_spoken_integer_from_tokens(sequence)
        if parsed is not None:
            return parsed
    return None


def _parse_joined_digit_sequence(cleaned: str) -> float | None:
    hyphen_match = re.search(r"(?<!\d)(\d)\s*-\s*(\d)(?!\d)", cleaned)
    if hyphen_match:
        return float(f"{hyphen_match.group(1)}{hyphen_match.group(2)}")

    spaced_match = re.search(r"(?<!\d)(\d)\s+(\d)(?!\d)", cleaned)
    if spaced_match:
        return float(f"{spaced_match.group(1)}{spaced_match.group(2)}")
    return None


def normalize_number(text: str, *, join_digit_sequence: bool = False) -> float | None:
    cleaned = _prepare_text(text)
    if not cleaned:
        return None

    if join_digit_sequence:
        joined = _parse_joined_digit_sequence(cleaned)
        if joined is not None:
            return joined

    digit_match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if digit_match:
        return float(digit_match.group(0))

    sequence_integer = _parse_spoken_integer_sequence(cleaned)
    if sequence_integer is not None:
        return float(sequence_integer)

    integer = _parse_spoken_integer(cleaned)
    if integer is not None:
        return float(integer)
    return None


def is_ambiguous_round_tens(text: str) -> bool:
    """Return True when STT heard only a tens word, e.g. "сорок".

    In voice input this is risky: "сорок пять" can be truncated by STT to
    "сорок", silently changing 45 to 40. The UI can ask the user to repeat
    such values as a full number.
    """
    cleaned = _prepare_text(text)
    tokens = [token.strip(".") for token in cleaned.split()]
    return len(tokens) == 1 and tokens[0] in _TENS


def normalize(text: str, field: FieldSpec) -> Any | None:
    if field.field_type is FieldType.BOOLEAN:
        return normalize_boolean(text, field)

    value = normalize_number(text, join_digit_sequence=field.join_digit_sequence)
    if value is None:
        return None
    if not field.validate_number(value):
        return None
    if value.is_integer():
        return int(value)
    return value
