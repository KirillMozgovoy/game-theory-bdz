import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.optimize as opt

# ==========================================
# 1. Конфигурация страницы
# ==========================================
st.set_page_config(page_title="БДЗ: Теория Игр", layout="wide", initial_sidebar_state="collapsed")

st.markdown(r"""
<style>
    @media print {
        @page { size: A4 portrait; margin: 15mm; }
        body { font-family: "Times New Roman", serif; background: white; }
        .stApp { background: white; color: black; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ШАПКА ПРОЕКТА
# ==========================================
st.title("Оптимизация распределения вычислительных ресурсов в облаке")
st.subheader("Вариант 7. Академическое исследование антагонистического конфликта")

st.info(
    "Анализ конфликта между Облачным провайдером (максимизация маржинальности) и Клиентской средой (генерация наихудшего сценария нагрузки).")

col1, col2, col3 = st.columns(3)
col1.metric("Цена игры (v)", "9.75 у.е.", "Гарантированная средняя маржинальность")
col2.metric("Стратегия Провайдера (x*)", "(3/8, 5/8)", "Оптимальное распределение пула")
col3.metric("Стратегия Среды (y*)", "(0, 3/8, 5/8)", "Вероятностный профиль нагрузки")

st.divider()

# ==========================================
# 3. ПОСТАНОВКА ЗАДАЧИ И ДОМИНИРОВАНИЕ
# ==========================================
st.header("1. Постановка задачи и редукция платежной матрицы")

col_a, col_b = st.columns([1, 1.2])

with col_a:
    st.success("**Игрок A (Провайдер):**\n* A1 — Пакетный режим (batch)\n* A2 — Потоковый режим (streaming)")
    st.warning("**Игрок B (Среда):**\n* B1 — Равномерная нагрузка\n* B2 — Пиковый спрос\n* B3 — Ночная нагрузка")

with col_b:
    st.write("**Исходная платежная матрица $A$ (маржинальность в у.е.):**")
    original_matrix = pd.DataFrame(
        [[8, 16, 6], [14, 6, 12]],
        columns=["B1 (Равномерная)", "B2 (Пиковая)", "B3 (Ночная)"], index=["A1", "A2"]
    )
    st.dataframe(original_matrix, use_container_width=True)
    st.info(
        r"**Теорема о доминировании:** Сравнивая столбцы B1 (8, 14) и B3 (6, 12), видим, что элементы B3 попарно меньше ($6 \le 8$, $12 \le 14$). Для минимизирующего игрока B стратегия B3 строго выгоднее. Стратегия B1 исключается.")

reduced_matrix = np.array([[16, 6], [6, 12]])

st.divider()

# ==========================================
# 4. СЕДЛОВАЯ ТОЧКА
# ==========================================
st.header("2. Проверка принципа минимакса")

row_mins = np.min(reduced_matrix, axis=1)
col_maxs = np.max(reduced_matrix, axis=0)
alpha = np.max(row_mins)
beta = np.min(col_maxs)

col_mm1, col_mm2 = st.columns(2)
with col_mm1:
    st.write(f"**Нижняя цена игры (Maximin, $\\alpha$):** $\\max({row_mins[0]}, {row_mins[1]}) = {alpha}$")
    st.write(f"**Верхняя цена игры (Minimax, $\\beta$):** $\\min({col_maxs[0]}, {col_maxs[1]}) = {beta}$")
with col_mm2:
    st.error(
        f"Так как **{alpha} ≠ {beta}**, седловой точки отсутствует. Решение экономического конфликта лежит исключительно в области смешанных стратегий.")

st.divider()

# ==========================================
# 5. ГРАФОАНАЛИТИЧЕСКИЙ МЕТОД (ИНТЕРАКТИВНЫЙ)
# ==========================================
st.header("3. Графоаналитический метод (Смешанные стратегии)")

col_g1, col_g2 = st.columns(2)

# График A (Plotly)
with col_g1:
    p = np.linspace(0, 1, 100)
    E2 = 16 * p + 6 * (1 - p)
    E3 = 6 * p + 12 * (1 - p)
    env_low = np.minimum(E2, E3)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=p, y=E2, mode='lines', name='E2(p) = 10p + 6', line=dict(color='#3b82f6', width=3)))
    fig1.add_trace(go.Scatter(x=p, y=E3, mode='lines', name='E3(p) = 12 - 6p', line=dict(color='#ef4444', width=3)))
    fig1.add_trace(go.Scatter(x=p, y=env_low, fill='tozeroy', mode='none', fillcolor='rgba(16, 185, 129, 0.2)',
                              name='Нижняя огибающая'))
    fig1.add_trace(go.Scatter(x=[3 / 8], y=[9.75], mode='markers+text', marker=dict(color='black', size=10),
                              text=['p* = 3/8, v = 9.75'], textposition="top right", name='Оптимум'))

    fig1.update_layout(
        title='Игрок А (Поиск максимума минимальных выигрышей)',
        xaxis_title='Вероятность p (выбор A1)',
        yaxis_title='Ожидаемый выигрыш',
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)

# График B (Plotly)
with col_g2:
    q = np.linspace(0, 1, 100)
    G1 = 16 * q + 6 * (1 - q)
    G2 = 6 * q + 12 * (1 - q)
    env_high = np.maximum(G1, G2)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=q, y=G1, mode='lines', name='G1(q) = 10q + 6', line=dict(color='#3b82f6', width=3)))
    fig2.add_trace(go.Scatter(x=q, y=G2, mode='lines', name='G2(q) = 12 - 6q', line=dict(color='#ef4444', width=3)))
    # Заливка верхней огибающей
    fig2.add_trace(
        go.Scatter(x=q, y=[20] * len(q), mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
    fig2.add_trace(go.Scatter(x=q, y=env_high, fill='tonexty', mode='none', fillcolor='rgba(245, 158, 11, 0.2)',
                              name='Верхняя огибающая'))
    fig2.add_trace(go.Scatter(x=[3 / 8], y=[9.75], mode='markers+text', marker=dict(color='black', size=10),
                              text=['q* = 3/8, v = 9.75'], textposition="bottom right", name='Оптимум'))

    fig2.update_layout(
        title='Игрок В (Поиск минимума максимальных потерь)',
        xaxis_title='Вероятность q (выбор B2)',
        yaxis_title='Ожидаемые потери',
        yaxis_range=[0, 18],
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ==========================================
# 6. ЛИНЕЙНОЕ ПРОГРАММИРОВАНИЕ (ИНТЕРАКТИВНОЕ)
# ==========================================
st.header("4. Линейное программирование (Симплекс-метод)")

col_lp1, col_lp2, col_lp3 = st.columns([1, 1.5, 1])

with col_lp1:
    st.info(r"""
    **Прямая задача (В):**  
    $W = y_1 + y_2 \rightarrow \max$  
    $16y_1 + 6y_2 \le 1$  
    $6y_1 + 12y_2 \le 1$  
    $y_1, y_2 \ge 0$
    """)
    st.success(r"""
    **Двойственная (А):**  
    $Z = x_1 + x_2 \rightarrow \min$  
    $16x_1 + 6x_2 \ge 1$  
    $6x_1 + 12x_2 \ge 1$  
    $x_1, x_2 \ge 0$
    """)

with col_lp2:
    x_val = np.linspace(0, 0.15, 200)
    y1_val = (1 - 16 * x_val) / 6
    y2_val = (1 - 6 * x_val) / 12
    y_env = np.maximum(y1_val, y2_val)

    fig_lp = go.Figure()
    fig_lp.add_trace(
        go.Scatter(x=x_val, y=y1_val, mode='lines', name='16x1 + 6x2 >= 1', line=dict(color='#3b82f6', width=2)))
    fig_lp.add_trace(
        go.Scatter(x=x_val, y=y2_val, mode='lines', name='6x1 + 12x2 >= 1', line=dict(color='#ef4444', width=2)))
    # Заливка допустимой области
    fig_lp.add_trace(go.Scatter(x=x_val, y=[0.25] * len(x_val), mode='lines', line=dict(width=0), showlegend=False,
                                hoverinfo='skip'))
    fig_lp.add_trace(go.Scatter(x=x_val, y=y_env, fill='tonexty', mode='none', fillcolor='rgba(16, 185, 129, 0.2)',
                                name='Допустимая область'))

    fig_lp.add_trace(go.Scatter(x=[1 / 26], y=[5 / 78], mode='markers+text', marker=dict(color='black', size=10),
                                text=['(3/46, 5/46)'], textposition="top right", name='Оптимум'))

    fig_lp.update_layout(
        title="Геометрия допустимой области ЗЛП",
        xaxis_title="x1",
        yaxis_title="x2",
        xaxis_range=[0, 0.1],
        yaxis_range=[0, 0.2],
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_lp, use_container_width=True)

with col_lp3:
    st.write("**Восстановление вероятностей:**")
    st.latex(r"Z^* = x_1 + x_2 = \frac{4}{39}")
    st.latex(r"v = \frac{1}{Z^*} = 9.75")
    st.latex(r"p_1 = x_1 \cdot v = \frac{3}{8}")
    st.latex(r"p_2 = x_2 \cdot v = \frac{5}{8}")

st.divider()

# ==========================================
# 7. МЕТОД БРАУНА-РОБИНСОНА С ВИЗУАЛИЗАЦИЕЙ
# ==========================================
st.header("5. Итерационный метод Брауна-Робинсона")


def brown_robinson_detailed(matrix, iterations=200):
    rows, cols = matrix.shape
    U, V = np.zeros(cols), np.zeros(rows)
    data = []
    a_choice = 0

    for k in range(1, iterations + 1):
        V += matrix[a_choice, :]
        b_choice = np.argmin(V)
        U += matrix[:, b_choice]
        next_a = np.argmax(U)

        # ИСПРАВЛЕННАЯ ЛОГИКА ОЦЕНОК
        v_lower = np.min(V) / k  # Нижняя оценка формируется из вектора потерь В
        v_upper = np.max(U) / k  # Верхняя оценка формируется из вектора выигрышей А

        data.append({
            "Итерация k": k,
            "Ход А": f"A{a_choice + 1}",
            "Ход В": f"B{b_choice + 2}",
            "Нижняя оценка (v_lower)": round(v_lower, 4),
            "Верхняя оценка (v_upper)": round(v_upper, 4)
        })
        a_choice = next_a
    return pd.DataFrame(data)


df_br = brown_robinson_detailed(reduced_matrix, 200)

col_br1, col_br2 = st.columns([1, 2])

with col_br1:
    st.write("**Первые 15 итераций алгоритма:**")
    st.dataframe(df_br.head(15), use_container_width=True)

with col_br2:
    fig_br = go.Figure()

    # ИСПРАВЛЕННЫЕ ЛЕЙБЛЫ ГРАФИКОВ
    fig_br.add_trace(go.Scatter(x=df_br['Итерация k'], y=df_br['Верхняя оценка (v_upper)'], mode='lines',
                                name='Верхняя оценка (v_upper)', line=dict(color='#ef4444', width=2)))
    fig_br.add_trace(go.Scatter(x=df_br['Итерация k'], y=df_br['Нижняя оценка (v_lower)'], mode='lines',
                                name='Нижняя оценка (v_lower)', line=dict(color='#3b82f6', width=2)))

    fig_br.add_trace(go.Scatter(x=[1, 200], y=[9.75, 9.75], mode='lines', name='Точная цена (9.75)',
                                line=dict(color='black', width=2, dash='dash')))

    fig_br.update_layout(
        title="Динамика сходимости оценок (N = 200 итераций)",
        xaxis_title="Номер итерации (k)",
        yaxis_title="Оценка цены игры",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_br, use_container_width=True)

st.success(
    "Все три примененных математических аппарата сошлись к единому оптимальному смешанному расширению: $P^* = (0.375, 0.625)$ и цене игры $v = 9.75$. Математическая модель полностью консистентна.")