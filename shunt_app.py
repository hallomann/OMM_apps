# app.py
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
st.header("СПОСОБ ОПРЕДЕЛЕНИЯ ПРОГНОЗА И НЕОБХОДИМОСТИ ВНУТРИУТРОБНОГО НЕФРОАМНИАЛЬНОГО ШУНТИРОВАНИЯ У ПЛОДОВ С ВРОЖДЕННЫМИ ОБСТРУКТИВНЫМИ УРОПАТИЯМИ")

def init_state():
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
# helpers
# ────────────────────────────────────────
def num_or_none(v):
    v = v.replace(",", ".").strip()
    return float(v) if v else None

# ────────────────────────────────────────
# I. Прогностический индекс (WI)
# ────────────────────────────────────────
st.header("I этап. Определение прогноза врожденной обструктивной уропатии у плода")

render_voice_session(
    WI_FIELDS,
    state_prefix="wi_",
)

if is_voice_session_active("wi_"):
    st.info(
        "Идет голосовой ввод. После завершения опроса значения автоматически "
        "появятся в форме."
    )
    st.stop()

c1, c2 = st.columns(2)
with c1:
    x1 = st.checkbox("Двустороннее поражение почек (X1)", key="x1")
    x2 = st.checkbox("Мужской пол (X2)", key="x2")
with c2:
    x3 = st.text_input("Продольный размер почки, мм (X3)", key="x3")
    x4 = st.text_input("Толщина паренхимы, мм (X4)", key="x4")
    x5 = st.text_input("Индекс васкуляризации VI (X5)", key="x5")
    x6 = st.text_input("Индекс потока FI (X6)", key="x6")

def calc_wi():
    vals = [
        int(st.session_state["x1"]),
        int(st.session_state["x2"]),
        num_or_none(st.session_state["x3"]),
        num_or_none(st.session_state["x4"]),
        num_or_none(st.session_state["x5"]),
        num_or_none(st.session_state["x6"]),
    ]

    if None in vals[2:]:
        st.session_state.wi_error = "Заполните все числовые поля (X3-X6)."
        return

    b = np.array([-0.292, -1.551, -0.054, 0.221, 0.065, 0.416])

    st.session_state.wi = float(np.dot(b, vals) - 4.673)
    st.session_state.wi_error = None

st.button("Рассчитать WI", on_click=calc_wi)

# вывод WI
if "wi_error" in st.session_state and st.session_state.wi_error:
    st.warning(st.session_state.wi_error)
elif "wi" in st.session_state:
    wi = st.session_state.wi
    st.subheader(f"WI = {wi:.3f}")
    if wi < 0:
        st.error("Неблагоприятный прогноз")
    else:
        st.success("Благоприятный прогноз – можно перейти ко 2-му этапу")

# ────────────────────────────────────────
# II. Диагностический индекс (DI)
# ────────────────────────────────────────
if st.session_state.get("wi", -1) >= 0:
    st.header("II этап. Способ определения необходимости нефроамниального шунтирования у плодов с обструктивными уропатиями.")

    d1, d2 = st.columns(2)
    with d1:
        y1 = st.text_input("Продольный размер почки, мм (Y1)", key="y1")
        y2 = st.text_input("Толщина паренхимы, мм (Y2)", key="y2")
        y3 = st.text_input("Индекс васкуляризации VI (Y3)", key="y3")
        y4 = st.text_input("Индекс потока FI (Y4)", key="y4")
    with d2:
        y5 = st.checkbox("Почка-киста (Y5)", key="y5")
        y6 = st.checkbox("Кистозная дисплазия (Y6)", key="y6")

    def calc_di():
        vals = [
            num_or_none(st.session_state["y1"]),
            num_or_none(st.session_state["y2"]),
            num_or_none(st.session_state["y3"]),
            num_or_none(st.session_state["y4"]),
            int(st.session_state["y5"]),
            int(st.session_state["y6"]),
        ]

    if None in vals[:4]:
        st.session_state.di_error = "Заполните все числовые поля (Y1-Y4)."
        return

    a = np.array([0.017, 0.222, 0.565, -0.388, 5.589, 7.005])

    st.session_state.di = float(np.dot(a, vals) - 0.463)
    st.session_state.di_error = None

    st.button("Рассчитать DI", on_click=calc_di)

    if "di_error" in st.session_state and st.session_state.di_error:
        st.warning(st.session_state.di_error)
    elif "di" in st.session_state:
        di = st.session_state.di
        st.subheader(f"DI = {di:.3f}")
        if di < 0:
            st.error("Необходимо провести нефроамниальное шунтирование")
        else:
            st.success("Показаний для шунтирования нет")
