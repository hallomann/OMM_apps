# app.py
import math

import streamlit as st

from clinical_ui import render_result
from configs.sfft_fields import SFFT_FIELDS
from voice_helper.streamlit_bridge import (
    consume_auto_calculate,
    is_voice_session_active,
    render_voice_session,
)

st.set_page_config(
    page_title="СФФТ: калькулятор риска", page_icon="🧮", layout="centered"
)


def init_state() -> None:
    defaults = {
        "ph": 0,
        "ktr1": 50.0,
        "ktr2": 50.0,
        "pi2": 0,
        "tvp_gt3": 0,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def compute_sfft(ph, ktr1, ktr2, pi2, tvp_gt3) -> float:
    ktr_diff = ktr1 - ktr2
    f_score = 2.07 * ph + 0.08 * ktr_diff + 4.45 * pi2 + 2.12 * tvp_gt3 - 7.52
    return 1.0 / (1.0 + math.exp(-f_score))


def render_sfft_result(probability: float) -> None:
    render_result(
        is_positive=probability < 0.25,
        title="Результат",
        positive_msg="Классификация: **не СФФТ**",
        negative_msg="Классификация: **СФФТ**",
    )


init_state()
st.title("🧮 Прогноз СФФТ по УЗ-признакам")

st.subheader("Голосовой ввод")
st.caption(
    "Один клик — пошаговый ввод всех признаков голосом."
)
render_voice_session(SFFT_FIELDS)

if is_voice_session_active():
    st.info(
        "Калькулятор временно скрыт: значения собираются в голосовом мастере "
        "и будут перенесены в поля после завершения всех шагов."
    )
    st.stop()

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
        f"Разница КТР: {st.session_state.ktr1 - st.session_state.ktr2:.1f} мм"
    )

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

if submitted or consume_auto_calculate():
    st.session_state.sfft_probability = compute_sfft(
        st.session_state.ph,
        st.session_state.ktr1,
        st.session_state.ktr2,
        st.session_state.pi2,
        st.session_state.tvp_gt3,
    )

if "sfft_probability" in st.session_state:
    st.markdown("---")
    render_sfft_result(st.session_state.sfft_probability)
