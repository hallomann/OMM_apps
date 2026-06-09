# app.py
import streamlit as st
import numpy as np

st.set_page_config(page_title="Прогноз & Шунтирование", page_icon="🍼")
st.header("СПОСОБ ОПРЕДЕЛЕНИЯ ПРОГНОЗА И НЕОБХОДИМОСТИ ВНУТРИУТРОБНОГО НЕФРОАМНИАЛЬНОГО ШУНТИРОВАНИЯ У ПЛОДОВ С ВРОЖДЕННЫМИ ОБСТРУКТИВНЫМИ УРОПАТИЯМИ")

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

c1, c2 = st.columns(2)
with c1:
    x1 = st.checkbox("Двустороннее поражение почек (X1)")
    x2 = st.checkbox("Мужской пол (X2)")
with c2:
    x3 = st.text_input("Продольный размер почки, мм (X3)")
    x4 = st.text_input("Толщина паренхимы, мм (X4)")
    x5 = st.text_input("Индекс васкуляризации VI (X5)")
    x6 = st.text_input("Индекс потока FI (X6)")

def calc_wi():
    vals = [
        int(x1),
        int(x2),
        num_or_none(x3),
        num_or_none(x4),
        num_or_none(x5),
        num_or_none(x6),
    ]
    if None in vals[2:]:
        st.session_state.wi_error = "Заполните все числовые поля (X3-X6)."
        return
    b = np.array([-0.292, -1.551, -0.054, 0.221, 0.065, 0.416])
    wi = float(np.dot(b, vals) - 4.673)
    st.session_state.wi = wi          # сохраняем
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
        y1 = st.text_input("Продольный размер почки, мм (Y1)")
        y2 = st.text_input("Толщина паренхимы, мм (Y2)")
        y3 = st.text_input("Индекс васкуляризации VI (Y3)")
        y4 = st.text_input("Индекс потока FI (Y4)")
    with d2:
        y5 = st.checkbox("Почка-киста (Y5)")
        y6 = st.checkbox("Кистозная дисплазия (Y6)")

    def calc_di():
        vals = [
            num_or_none(y1),
            num_or_none(y2),
            num_or_none(y3),
            num_or_none(y4),
            int(y5),
            int(y6),
        ]
        if None in vals[:4]:
            st.session_state.di_error = "Заполните все числовые поля (Y1-Y4)."
            return
        a = np.array([0.017, 0.222, 0.565, -0.388, 5.589, 7.005])
        di = float(np.dot(a, vals) - 0.463)
        st.session_state.di = di
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
