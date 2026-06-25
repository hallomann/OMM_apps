from __future__ import annotations

from typing import Any

import streamlit as st

from voice_helper.normalize import normalize
from voice_helper.schema import FieldSpec
from voice_helper.session import SessionStatus, VoiceSession
from voice_helper.stt import transcribe
from voice_helper.tts import build_listen_message, speak


def _session_key(state_prefix: str) -> str:
    return f"{state_prefix}vh_session"


def _auto_calculate_key(state_prefix: str) -> str:
    return f"{state_prefix}vh_auto_calculate"


def _tts_played_key(state_prefix: str, index: int) -> str:
    return f"{state_prefix}vh_tts_played_{index}"


def _init_voice_state(state_prefix: str) -> None:
    st.session_state.setdefault(_auto_calculate_key(state_prefix), False)


def _get_session(state_prefix: str) -> VoiceSession | None:
    session = st.session_state.get(_session_key(state_prefix))
    return session if isinstance(session, VoiceSession) else None


def _clear_voice_keys(state_prefix: str) -> None:
    prefix = f"{state_prefix}vh_"
    for key in list(st.session_state.keys()):
        if key.startswith(prefix):
            del st.session_state[key]


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "Да" if value else "Нет"
    if value in (0, 1) and not isinstance(value, bool):
        return "Да" if value == 1 else "Нет"
    return str(value)


def _render_prompt_step(
    session: VoiceSession,
    field: FieldSpec,
    *,
    state_prefix: str,
) -> None:
    prompt = build_listen_message(field)
    st.info(prompt)

    played_key = _tts_played_key(state_prefix, session.index)
    if st.session_state.get(played_key):
        if session.status is SessionStatus.PROMPT:
            session.mark_listening()
            st.rerun()
        return

    try:
        audio_bytes = speak(prompt)
        st.audio(audio_bytes, format="audio/mp3")
    except Exception as exc:
        st.warning(f"Озвучка недоступна: {exc}. Прочитайте текст выше.")

    st.session_state[played_key] = True
    session.mark_listening()
    st.rerun()


def _render_listen_step(
    session: VoiceSession,
    field: FieldSpec,
    fields: list[FieldSpec],
    *,
    state_prefix: str,
) -> None:
    audio_data = st.audio_input(
        "Скажите значение",
        key=f"{state_prefix}vh_audio_{session.index}",
    )

    if not st.button(
        "Продолжить",
        key=f"{state_prefix}vh_submit_{session.index}",
        type="primary",
    ):
        return

    if audio_data is None:
        session.retry("Сначала запишите ответ.")
        st.rerun()
        return

    heard = transcribe(audio_data.getvalue(), language="ru")
    value = normalize(heard, field)
    if value is None:
        session.retry(f"Не удалось распознать значение. Услышано: «{heard}».")
        if _tts_played_key(state_prefix, session.index) in st.session_state:
            del st.session_state[_tts_played_key(state_prefix, session.index)]
        st.rerun()
        return

    session.record_value(field.key, value)
    st.session_state[field.key] = value
    session.advance()

    if session.is_done():
        _finish_session(fields, state_prefix=state_prefix)
    else:
        st.rerun()


def _finish_session(fields: list[FieldSpec], *, state_prefix: str) -> None:
    session = _get_session(state_prefix)
    if session is None:
        return

    rows = [
        {
            "Поле": field.label,
            "Ключ": field.key,
            "Значение": _format_value(session.get_values().get(field.key)),
        }
        for field in fields
    ]
    st.subheader("Голосовой ввод завершён")
    st.table(rows)
    st.session_state[_auto_calculate_key(state_prefix)] = True
    del st.session_state[_session_key(state_prefix)]


def render_voice_session(
    fields: list[FieldSpec],
    *,
    state_prefix: str = "",
) -> None:
    """Render the voice-guided input UI and update ``st.session_state``."""
    _init_voice_state(state_prefix)

    session = _get_session(state_prefix)
    is_active = session is not None and session.status is not SessionStatus.IDLE

    start_col, cancel_col = st.columns(2)
    with start_col:
        start_disabled = is_active
        if st.button(
            "Голосовой ввод",
            type="primary",
            icon="🎤",
            disabled=start_disabled,
            use_container_width=True,
            key=f"{state_prefix}vh_start",
        ):
            new_session = VoiceSession(fields)
            new_session.start()
            st.session_state[_session_key(state_prefix)] = new_session
            st.rerun()

    with cancel_col:
        if st.button(
            "Прервать голосовой ввод",
            disabled=not is_active,
            use_container_width=True,
            key=f"{state_prefix}vh_cancel",
        ):
            _clear_voice_keys(state_prefix)
            _init_voice_state(state_prefix)
            st.info("Голосовой ввод прерван. Можно продолжить ручной ввод.")
            st.rerun()

    session = _get_session(state_prefix)
    if session is None or session.status is SessionStatus.IDLE:
        return

    if session.is_done():
        _finish_session(fields, state_prefix=state_prefix)
        return

    field = session.current_field()
    if field is None:
        return

    st.progress((session.index + 1) / len(fields))
    st.caption(f"Поле {session.index + 1} из {len(fields)}: {field.label}")

    if session.last_error:
        st.warning(session.last_error)

    if session.status is SessionStatus.PROMPT:
        _render_prompt_step(session, field, state_prefix=state_prefix)
    elif session.status is SessionStatus.LISTEN:
        _render_listen_step(
            session,
            field,
            fields,
            state_prefix=state_prefix,
        )


def consume_auto_calculate(*, state_prefix: str = "") -> bool:
    """Return True once after voice flow completes; resets the flag."""
    key = _auto_calculate_key(state_prefix)
    if st.session_state.get(key):
        st.session_state[key] = False
        return True
    return False
