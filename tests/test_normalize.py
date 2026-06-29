import unittest

from configs.sfft_fields import SFFT_FIELDS
from voice_helper.normalize import (
    is_ambiguous_round_tens,
    normalize,
    normalize_boolean,
    normalize_number,
)
from voice_helper.schema import FieldSpec, FieldType


class NormalizeBooleanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.field = SFFT_FIELDS[0]

    def test_true_variants(self) -> None:
        for phrase in ("да", "есть", "имеется", "Да, есть", "Есть!"):
            with self.subTest(phrase=phrase):
                self.assertEqual(normalize_boolean(phrase, self.field), 1)

    def test_false_variants(self) -> None:
        for phrase in ("нет", "отсутствует", "Нет", "Нет."):
            with self.subTest(phrase=phrase):
                self.assertEqual(normalize_boolean(phrase, self.field), 0)

    def test_unknown(self) -> None:
        self.assertIsNone(normalize_boolean("может быть", self.field))
        self.assertIsNone(normalize_boolean("", self.field))


class NormalizeNumberTests(unittest.TestCase):
    def test_digits(self) -> None:
        self.assertEqual(normalize_number("52"), 52.0)
        self.assertEqual(normalize_number("52.5"), 52.5)
        self.assertEqual(normalize_number("52,5"), 52.5)

    def test_spoken(self) -> None:
        self.assertEqual(normalize_number("пятьдесят два"), 52.0)
        self.assertEqual(normalize_number("сорок один"), 41.0)
        self.assertEqual(normalize_number("сорок, один"), 41.0)
        self.assertEqual(normalize_number("сорок один."), 41.0)
        self.assertEqual(normalize_number("четыре один"), 41.0)
        self.assertEqual(normalize_number("сто"), 100.0)
        self.assertEqual(normalize_number("ноль"), 0.0)

    def test_invalid(self) -> None:
        self.assertIsNone(normalize_number(""))
        self.assertIsNone(normalize_number("abc"))
        self.assertIsNone(normalize_number("может пятьдесят"))

    def test_ambiguous_round_tens(self) -> None:
        self.assertTrue(is_ambiguous_round_tens("сорок"))
        self.assertTrue(is_ambiguous_round_tens("сорок."))
        self.assertFalse(is_ambiguous_round_tens("сорок пять"))
        self.assertFalse(is_ambiguous_round_tens("четыре ноль"))
        self.assertFalse(is_ambiguous_round_tens("40"))


class NormalizeDispatcherTests(unittest.TestCase):
    def test_boolean_field(self) -> None:
        self.assertEqual(normalize("да", SFFT_FIELDS[3]), 1)

    def test_number_field(self) -> None:
        self.assertEqual(normalize("пятьдесят два", SFFT_FIELDS[1]), 52)

    def test_number_out_of_range(self) -> None:
        negative_field = FieldSpec(
            key="test",
            label="test",
            field_type=FieldType.NUMBER,
            tts_prompt="test",
            min_value=0.0,
        )
        self.assertIsNone(normalize("-5", negative_field))


if __name__ == "__main__":
    unittest.main()
