import unittest

from configs.sfft_fields import SFFT_FIELDS
from voice_helper.schema import FieldSpec, FieldType
from voice_helper.session import SessionStatus, VoiceSession


class VoiceSessionTests(unittest.TestCase):
    def test_full_pass(self) -> None:
        session = VoiceSession(SFFT_FIELDS)
        session.start()
        self.assertEqual(session.status, SessionStatus.PROMPT)

        expected = [
            ("ph", 0),
            ("ktr1", 52),
            ("ktr2", 48),
            ("pi2", 1),
            ("tvp_gt3", 0),
        ]
        for key, value in expected:
            field = session.current_field()
            self.assertIsNotNone(field)
            assert field is not None
            self.assertEqual(field.key, key)
            session.record_value(key, value)
            session.advance()

        self.assertTrue(session.is_done())
        self.assertEqual(session.get_values(), dict(expected))

    def test_retry_keeps_index(self) -> None:
        fields = [
            FieldSpec("a", "A", FieldType.BOOLEAN, "prompt"),
            FieldSpec("b", "B", FieldType.NUMBER, "prompt"),
            FieldSpec("c", "C", FieldType.BOOLEAN, "prompt"),
        ]
        session = VoiceSession(fields)
        session.start()
        session.mark_listening()

        session.retry("Не удалось распознать")
        self.assertEqual(session.index, 0)
        self.assertEqual(session.status, SessionStatus.PROMPT)
        self.assertEqual(session.last_error, "Не удалось распознать")
        self.assertIs(session.current_field(), fields[0])

        session.record_value("a", 1)
        session.advance()
        self.assertEqual(session.index, 1)

    def test_wrong_key_raises(self) -> None:
        session = VoiceSession(SFFT_FIELDS)
        session.start()
        with self.assertRaises(ValueError):
            session.record_value("ktr1", 50)


if __name__ == "__main__":
    unittest.main()
