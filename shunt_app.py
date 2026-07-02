# shunt_app.py
import streamlit as st
import numpy as np

from clinical_ui import render_result
from configs.shunt_fields import WI_FIELDS, DI_FIELDS
from voice_helper.streamlit_bridge import (
    render_voice_session,
    consume_auto_calculate,
    is_voice_session_active,
)

st.set_page_config(page_title="Прогноз & Шунтирование", page_icon="🍼")
st.header(
    "СПОСОБ ОПРЕДЕЛЕНИЯ ПРОГНОЗА И НЕОБХОДИМОСТИ ВНУТРИУТРОБНОГО "
    "НЕФРОАМНИАЛЬНОГО ШУНТИРОВАНИЯ У ПЛОДОВ С ВРОЖДЕННЫМИ "
    "ОБСТРУКТИВНЫМИ УРОПАТИЯМИ"
)


def init_state() -> None:
    defaults = {
        "x1": False,
        "x2": False,
        "x3": 0.0,
        "x4": 0.0,
        "x5": 0.0,
        "x6": 0.0,
        "y1": 0.0,
        "y2": 0.0,
        "y3": 0.0,
        "y4": 0.0,
        "y5": False,
        "y6": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


init_state()


# ────────────────────────────────────────
# I. Прогностический индекс (WI)
# ────────────────────────────────────────
def compute_wi(values: dict) -> float:
    vals = [
        int(values["x1"]),
        int(values["x2"]),
        float(values["x3"]),
        float(values["x4"]),
        float(values["x5"]),
        float(values["x6"]),
    ]
    b = np.array([-0.292, -1.551, -0.054, 0.221, 0.065, 0.416])
    return float(np.dot(b, vals) - 4.673)


def calculate_wi_from_state() -> None:
    st.session_state.wi = compute_wi(st.session_state)
    st.session_state.wi_error = None


st.header("I этап. Определение прогноза врожденной обструктивной уропатии у плода")

st.subheader("Голосовой ввод I этапа")
render_voice_session(WI_FIELDS, state_prefix="wi_")

if is_voice_session_active(state_prefix="wi_"):
    st.info(
        "Форма I этапа временно скрыта: значения собираются в голосовом мастере "
        "и будут перенесены в поля после завершения всех шагов."
    )
    st.stop()

c1, c2 = st.columns(2)
with c1:
    st.checkbox("Двустороннее поражение почек (X1)", key="x1")
    st.checkbox("Мужской пол (X2)", key="x2")
with c2:
    st.number_input("Продольный размер почки, мм (X3)", min_value=0.0, key="x3")
    st.number_input("Толщина паренхимы, мм (X4)", min_value=0.0, key="x4")
    st.number_input("Индекс васкуляризации VI (X5)", key="x5")
    st.number_input("Индекс потока FI (X6)", key="x6")

if consume_auto_calculate(state_prefix="wi_"):
    calculate_wi_from_state()

if st.button("Рассчитать WI"):
    calculate_wi_from_state()

if "wi" in st.session_state:
    wi = st.session_state.wi
    st.subheader(f"WI = {wi:.3f}")
    render_result(
        is_positive=wi >= 0,
        title="Результат I этапа",
        positive_msg="Благоприятный прогноз – можно перейти ко 2-му этапу",
        negative_msg="Неблагоприятный прогноз",
    )


# ────────────────────────────────────────
# II. Диагностический индекс (DI)
# ────────────────────────────────────────
def compute_di(values: dict) -> float:
    vals = [
        float(values["y1"]),
        float(values["y2"]),
        float(values["y3"]),
        float(values["y4"]),
        int(values["y5"]),
        int(values["y6"]),
    ]
    a = np.array([0.017, 0.222, 0.565, -0.388, 5.589, 7.005])
    return float(np.dot(a, vals) - 0.463)


def calculate_di_from_state() -> None:
    st.session_state.di = compute_di(st.session_state)
    st.session_state.di_error = None


if st.session_state.get("wi", -1) >= 0:
    st.header(
        "II этап. Способ определения необходимости нефроамниального "
        "шунтирования у плодов с обструктивными уропатиями."
    )

    st.subheader("Голосовой ввод II этапа")
    render_voice_session(DI_FIELDS, state_prefix="di_")

    if is_voice_session_active(state_prefix="di_"):
        st.info(
            "Форма II этапа временно скрыта: значения собираются в голосовом мастере "
            "и будут перенесены в поля после завершения всех шагов."
        )
        st.stop()

    d1, d2 = st.columns(2)
    with d1:
        st.number_input("Продольный размер почки, мм (Y1)", min_value=0.0, key="y1")
        st.number_input("Толщина паренхимы, мм (Y2)", min_value=0.0, key="y2")
        st.number_input("Индекс васкуляризации VI (Y3)", key="y3")
        st.number_input("Индекс потока FI (Y4)", key="y4")
    with d2:
        st.checkbox("Почка-киста (Y5)", key="y5")
        st.checkbox("Кистозная дисплазия (Y6)", key="y6")

    if consume_auto_calculate(state_prefix="di_"):
        calculate_di_from_state()

    if st.button("Рассчитать DI"):
        calculate_di_from_state()

    if "di" in st.session_state:
        di = st.session_state.di
        st.subheader(f"DI = {di:.3f}")
        render_result(
            is_positive=di >= 0,
            title="Результат II этапа",
            positive_msg="Показаний для шунтирования нет",
            negative_msg="Необходимо провести нефроамниальное шунтирование",
        )
