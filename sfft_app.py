# app.py
import math
import streamlit as st

st.set_page_config(
    page_title="СФФТ: калькулятор риска", page_icon="🧮", layout="centered"
)

FIELD_LABELS = {
    "ph": "ПХ — предлежание хориона",
    "ktr1": "КТР1 (мм)",
    "ktr2": "КТР2 (мм)",
    "pi2": "ПИ 2-го плода более 95%",
    "tvp_gt3": "ТВП 1 или 2 плода > 3 мм",
}


def init_state():
    defaults = {
        "ph": 0,
        "ktr1": 50.0,
        "ktr2": 50.0,
        "pi2": 0,
        "tvp_gt3": 0,
        "voice_pending": None,
        "run_calculation": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def compute_sfft(ph, ktr1, ktr2, pi2, tvp_gt3):
    ktr_diff = ktr1 - ktr2
    f_score = 2.07 * ph + 0.08 * ktr_diff + 4.45 * pi2 + 2.12 * tvp_gt3 - 7.52
    probability = 1.0 / (1.0 + math.exp(-f_score))
    return probability


def apply_voice_pending():
    pending = st.session_state.voice_pending
    if not pending:
        return
    st.session_state[pending["field_key"]] = pending["value"]
    st.session_state.voice_pending = None
    st.session_state.run_calculation = True


def clear_voice_pending():
    st.session_state.voice_pending = None


def render_voice_ui():
    st.subheader("Голосовой ввод")
    st.caption(
        "Нажмите кнопку, произнесите параметр и значение. "
        "!!!Распознавание речи и валидация будут подключены позже."
    )

    if st.button("Голосовой ввод", type="primary", icon="🎤", use_container_width=True):
        # TODO: запись аудио → STT → parse_utterance() → заполнить voice_pending
        pass

    pending = st.session_state.voice_pending
    if pending:
        st.markdown("---")
        st.markdown("**Распознано**")
        st.text(f"Фраза: {pending.get('heard', '—')}")
        st.text(
            f"Поле: {pending.get('field_label', FIELD_LABELS.get(pending.get('field_key'), '—'))}"
        )
        st.text(
            f"Значение: {pending.get('display_value', pending.get('value', '—'))}")

        col_confirm, col_reject = st.columns(2)
        with col_confirm:
            if st.button("Подтвердить", type="primary", use_container_width=True):
                apply_voice_pending()
                st.rerun()
        with col_reject:
            if st.button("Отклонить", use_container_width=True):
                clear_voice_pending()
                st.info("Уточните значение вручную в форме ниже.")
                st.rerun()


init_state()
st.title("🧮 Прогноз СФФТ по УЗ-признакам")

render_voice_ui()

st.markdown("---")
st.subheader("Ввод признаков")

with st.form("inputs"):
    st.selectbox(
        "ПХ — предлежание хориона",
        options=[0, 1],
        format_func=lambda x: "Есть" if x == 1 else "Нет",
        key="ph",
    )

    st.number_input("КТР1 (мм)", min_value=0.0, step=0.1, key="ktr1")
    st.number_input("КТР2 (мм)", min_value=0.0, step=0.1, key="ktr2")
    st.caption(
        f"Разница КТР: {st.session_state.ktr1 - st.session_state.ktr2:.1f} мм")

    st.selectbox(
        "ПИ 2-го плода более 95%",
        options=[0, 1],
        format_func=lambda x: "Да" if x == 1 else "Нет",
        key="pi2",
    )

    st.selectbox(
        "ТВП 1 или 2 плода > 3 мм",
        options=[0, 1],
        format_func=lambda x: "Да" if x == 1 else "Нет",
        key="tvp_gt3",
    )

    submitted = st.form_submit_button("Рассчитать")

if submitted:
    st.session_state.run_calculation = True

if st.session_state.run_calculation:
    p = compute_sfft(
        st.session_state.ph,
        st.session_state.ktr1,
        st.session_state.ktr2,
        st.session_state.pi2,
        st.session_state.tvp_gt3,
    )

    st.markdown("---")
    st.subheader("Результат")

    if p < 0.25:
        st.success("Классификация: **не СФФТ** ")
    else:
        st.error("Классификация: **СФФТ** ")

    st.session_state.run_calculation = False
