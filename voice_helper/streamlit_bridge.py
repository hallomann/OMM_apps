from __future__ import annotations

import base64
import uuid
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from voice_helper.normalize import is_ambiguous_round_tens, normalize
from voice_helper.schema import FieldSpec, FieldType
from voice_helper.session import SessionStatus, VoiceSession
from voice_helper.stt import transcribe
from voice_helper.tts import build_listen_message, speak


def _session_key(state_prefix: str) -> str:
    return f"{state_prefix}vh_session"


def _auto_calculate_key(state_prefix: str) -> str:
    return f"{state_prefix}vh_auto_calculate"


def _completed_rows_key(state_prefix: str) -> str:
    return f"{state_prefix}vh_completed_rows"


def _attempt_rows_key(state_prefix: str) -> str:
    return f"{state_prefix}vh_attempt_rows"


def _audio_attempt_key(state_prefix: str, index: int) -> str:
    return f"{state_prefix}vh_audio_attempt_{index}"


def _tts_played_key(state_prefix: str, index: int) -> str:
    return f"{state_prefix}vh_tts_played_{index}"


def _tts_processing_key(state_prefix: str, index: int) -> str:
    return f"{state_prefix}vh_tts_processing_{index}"


def _pending_audio_key(state_prefix: str, index: int) -> str:
    return f"{state_prefix}vh_pending_audio_{index}"


def _init_voice_state(state_prefix: str) -> None:
    st.session_state.setdefault(_auto_calculate_key(state_prefix), False)


def _get_session(state_prefix: str) -> VoiceSession | None:
    session = st.session_state.get(_session_key(state_prefix))
    return session if isinstance(session, VoiceSession) else None


def is_voice_session_active(*, state_prefix: str = "") -> bool:
    session = _get_session(state_prefix)
    return session is not None and session.status is not SessionStatus.IDLE


def _clear_voice_keys(state_prefix: str, *, keep_completed: bool = False) -> None:
    prefix = f"{state_prefix}vh_"
    protected = {
        _completed_rows_key(state_prefix),
    }
    for key in list(st.session_state.keys()):
        if key.startswith(prefix) and not (keep_completed and key in protected):
            del st.session_state[key]


def _format_value(field: FieldSpec, value: Any) -> str:
    if field.field_type is FieldType.BOOLEAN:
        return "Да" if value else "Нет"
    return str(value)


def _show_center_loader(message: str):
    placeholder = st.empty()
    placeholder.markdown(
        f"""
        <style>
        .vh-loader {{
            display: flex;
            align-items: center;
            justify-content: center;
            position: fixed;
            inset: 0;
            z-index: 999999;
            background: rgba(8, 13, 24, 0.74);
            backdrop-filter: blur(5px);
        }}
        .vh-loader-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 14px;
            min-width: 280px;
            padding: 28px 34px;
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(31, 111, 235, 0.28), rgba(47, 179, 255, 0.12));
            border: 1px solid rgba(147, 197, 253, 0.34);
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
            color: #dbeafe;
            font-weight: 600;
            text-align: center;
        }}
        .vh-spinner {{
            width: 44px;
            height: 44px;
            border-radius: 50%;
            border: 4px solid rgba(147, 197, 253, 0.28);
            border-top-color: #38bdf8;
            animation: vh-spin 0.9s linear infinite;
        }}
        @keyframes vh-spin {{
            to {{ transform: rotate(360deg); }}
        }}
        </style>
        <div class="vh-loader">
            <div class="vh-loader-card">
                <div class="vh-spinner"></div>
                <div>{message}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    return placeholder


def _render_autoplay_audio(audio_bytes: bytes) -> None:
    encoded = base64.b64encode(audio_bytes).decode("ascii")
    audio_id = f"vh_audio_{uuid.uuid4().hex}"
    components.html(
        f"""
        <audio id="{audio_id}" autoplay controls style="width: 100%;">
            <source src="data:audio/mpeg;base64,{encoded}" type="audio/mpeg">
        </audio>
        <script>
        const audio = document.getElementById("{audio_id}");
        if (audio) {{
            audio.play().catch(() => {{}});
        }}
        </script>
        """,
        height=56,
    )


def _append_attempt_row(
    field: FieldSpec,
    *,
    state_prefix: str,
    heard: str,
    value: Any,
    status: str,
) -> None:
    rows = st.session_state.setdefault(_attempt_rows_key(state_prefix), [])
    rows.append(
        {
            "Поле": field.label,
            "Услышано": heard or "—",
            "Значение": _format_value(field, value) if value is not None else "—",
            "Статус": status,
        }
    )


def _render_attempt_rows(state_prefix: str) -> None:
    rows = st.session_state.get(_attempt_rows_key(state_prefix))
    if not rows:
        return
    st.markdown("**Текущий голосовой ввод**")
    st.table(rows)


def _render_prompt_step(
    session: VoiceSession,
    field: FieldSpec,
    *,
    state_prefix: str,
) -> None:
    prompt = build_listen_message(field)
    st.info(prompt)

    played_key = _tts_played_key(state_prefix, session.index)
    processing_key = _tts_processing_key(state_prefix, session.index)
    if st.session_state.get(played_key):
        if session.status is SessionStatus.PROMPT:
            session.mark_listening()
        return

    if not st.session_state.get(processing_key):
        st.session_state[processing_key] = True
        st.rerun()

    loader = _show_center_loader("Готовлю голосовую подсказку...")
    try:
        audio_bytes = speak(prompt)
        _render_autoplay_audio(audio_bytes)
    except Exception as exc:
        st.warning(f"Озвучка недоступна: {exc}. Прочитайте текст выше.")
    finally:
        loader.empty()

    st.session_state.pop(processing_key, None)
    st.session_state[played_key] = True
    session.mark_listening()


def _render_listen_step(
    session: VoiceSession,
    field: FieldSpec,
    fields: list[FieldSpec],
    *,
    state_prefix: str,
) -> None:
    attempt = st.session_state.setdefault(_audio_attempt_key(state_prefix, session.index), 0)
    pending_key = _pending_audio_key(state_prefix, session.index)
    pending_audio = st.session_state.get(pending_key)
    if pending_audio is not None:
        loader = _show_center_loader("Распознаю ответ и подготавливаю следующий шаг...")
        try:
            _process_audio_bytes(
                pending_audio,
                session,
                field,
                fields,
                state_prefix=state_prefix,
                attempt=attempt,
            )
        finally:
            loader.empty()
        return

    audio_data = st.audio_input(
        "Скажите значение",
        key=f"{state_prefix}vh_audio_{session.index}_{attempt}",
    )

    if audio_data is None:
        st.caption("После записи ответ будет обработан автоматически.")
        return

    st.session_state[pending_key] = audio_data.getvalue()
    st.rerun()


def _process_audio_bytes(
    audio_bytes: bytes,
    session: VoiceSession,
    field: FieldSpec,
    fields: list[FieldSpec],
    *,
    state_prefix: str,
    attempt: int,
) -> None:
    pending_key = _pending_audio_key(state_prefix, session.index)
    heard = transcribe(audio_bytes, language="ru")
    st.session_state.pop(pending_key, None)

    value = normalize(heard, field)
    if value is not None and field.field_type is FieldType.NUMBER and is_ambiguous_round_tens(heard):
        session.retry(
            "Услышано только круглое десятковое число. "
            "Повторите значение полностью, например «сорок пять»."
        )
        _append_attempt_row(
            field,
            state_prefix=state_prefix,
            heard=heard,
            value=value,
            status="Нужно повторить",
        )
        if _tts_played_key(state_prefix, session.index) in st.session_state:
            del st.session_state[_tts_played_key(state_prefix, session.index)]
        st.session_state[_audio_attempt_key(state_prefix, session.index)] = attempt + 1
        st.rerun()
        return

    if value is None:
        session.retry(f"Не удалось распознать значение. Услышано: «{heard}».")
        _append_attempt_row(
            field,
            state_prefix=state_prefix,
            heard=heard,
            value=None,
            status="Ошибка",
        )
        if _tts_played_key(state_prefix, session.index) in st.session_state:
            del st.session_state[_tts_played_key(state_prefix, session.index)]
        st.session_state[_audio_attempt_key(state_prefix, session.index)] = attempt + 1
        st.rerun()
        return

    _append_attempt_row(
        field,
        state_prefix=state_prefix,
        heard=heard,
        value=value,
        status="Принято",
    )
    session.record_value(field.key, value)
    session.advance()

    if session.is_done():
        _finish_session(fields, state_prefix=state_prefix)
        st.rerun()
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
            "Значение": _format_value(field, session.get_values().get(field.key)),
        }
        for field in fields
    ]
    for field in fields:
        st.session_state[field.key] = session.get_values().get(field.key)
    st.session_state[_completed_rows_key(state_prefix)] = rows
    st.session_state[_auto_calculate_key(state_prefix)] = True
    del st.session_state[_session_key(state_prefix)]


def _render_completed_rows(state_prefix: str) -> None:
    rows = st.session_state.get(_completed_rows_key(state_prefix))
    if not rows:
        return
    st.subheader("Голосовой ввод завершён")
    st.table(rows)


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
            _clear_voice_keys(state_prefix, keep_completed=True)
            _init_voice_state(state_prefix)
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
            _clear_voice_keys(state_prefix, keep_completed=True)
            _init_voice_state(state_prefix)
            st.info("Голосовой ввод прерван. Можно продолжить ручной ввод.")
            st.rerun()

    session = _get_session(state_prefix)
    if session is None or session.status is SessionStatus.IDLE:
        _render_completed_rows(state_prefix)
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

    _render_attempt_rows(state_prefix)

    if session.status is SessionStatus.PROMPT:
        _render_prompt_step(session, field, state_prefix=state_prefix)

    if session.status is SessionStatus.LISTEN:
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
