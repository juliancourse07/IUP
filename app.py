# =============================================================
# DASHBOARD UNIPUTUMAYO — VALOR AGREGADO SABER T&T
# =============================================================

import numpy as np
import pandas as pd
import streamlit as st

from modules.charts import (
    fig_comparacion_programas,
    fig_promedios,
    fig_radar_programa,
    fig_va_tendencia,
)
from modules.data_loader import COMPONENTES, cargar_datos, get_programas
from modules.va_calculator import calcular_resultados

# =============================================================
# PAGE CONFIG (must be first Streamlit call)
# =============================================================

st.set_page_config(
    page_title="Uniputumayo | Valor Agregado T&T",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================
# CUSTOM CSS — Uniputumayo green theme
# =============================================================

st.markdown(
    """
<style>
    /* ── Header ─────────────────────────────────────────── */
    .header-container {
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 25px;
    }
    .header-title {
        color: white;
        font-size: 26px;
        font-weight: 800;
        margin: 0;
    }
    .header-subtitle {
        color: #A5D6A7;
        font-size: 14px;
        margin: 4px 0 0 0;
    }

    /* ── KPI Cards ──────────────────────────────────────── */
    .kpi-card {
        background: white;
        border-left: 5px solid #2E7D32;
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 32px;
        font-weight: 800;
        color: #2E7D32;
    }
    .kpi-label {
        font-size: 13px;
        color: #666;
        margin-top: 4px;
    }
    .kpi-card.positivo { border-left-color: #2E7D32; }
    .kpi-card.negativo { border-left-color: #C62828; }
    .kpi-card.neutro   { border-left-color: #1565C0; }

    /* ── Tabs ───────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #F1F8E9;
        padding: 8px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background: #2E7D32 !important;
        color: white !important;
    }

    /* ── Sidebar ─────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B5E20 0%, #2E7D32 100%);
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* ── Footer ──────────────────────────────────────────── */
    .footer {
        text-align: center;
        color: #888;
        font-size: 12px;
        margin-top: 40px;
        padding: 20px;
        border-top: 1px solid #E0E0E0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =============================================================
# DATA LOADING
# =============================================================


@st.cache_data(ttl=3600, show_spinner=False)
def _get_all_data():
    dfs, df_total = cargar_datos()
    programas = get_programas(df_total)
    df_resultados = calcular_resultados(dfs, df_total, programas)
    return dfs, df_total, programas, df_resultados


with st.spinner("📡 Cargando datos desde Google Sheets…"):
    dfs, df_total, PROGRAMAS, df_resultados = _get_all_data()

if not PROGRAMAS:
    st.error(
        "No se encontraron programas con datos suficientes. "
        "Verifique la conexión con Google Sheets."
    )
    st.stop()

# =============================================================
# HEADER
# =============================================================

# Optional logo
import os

logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo_uniputumayo.png")
col_logo, col_title = st.columns([1, 8])
with col_logo:
    if os.path.isfile(logo_path) and os.path.getsize(logo_path) > 0:
        st.image(logo_path, width=90)
    else:
        st.markdown("🎓", unsafe_allow_html=False)

with col_title:
    st.markdown(
        """
        <div class="header-container">
            <p class="header-title">Uniputumayo — Dashboard de Valor Agregado</p>
            <p class="header-subtitle">
                Saber T&amp;T | Análisis 2023 – 2024 | Todos los Programas Tecnológicos
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =============================================================
# SIDEBAR
# =============================================================

with st.sidebar:
    st.markdown("## 🎛️ Filtros")
    st.markdown("---")

    programa_sel = st.selectbox("📚 Programa", PROGRAMAS, index=0)

    anios_disponibles = sorted(df_resultados["Año"].unique().tolist())
    anio_sel = st.selectbox("📅 Año", anios_disponibles, index=len(anios_disponibles) - 1)

    componente_sel = st.selectbox(
        "📊 Componente (comparación)", list(COMPONENTES.keys()), index=0
    )

    st.markdown("---")
    st.markdown("### ℹ️ Metodología")
    st.markdown(
        """
**Valor Agregado (VA)**
Residual del modelo de regresión global:

`VA = TyT_obs − TyT_esperado(SB11)`

- **VA > 0** ✅ El programa supera lo esperado
- **VA ≤ 0** ❌ Por debajo de lo esperado
"""
    )
    st.markdown("---")
    if st.button("🔄 Recargar datos"):
        st.cache_data.clear()
        st.rerun()

# =============================================================
# HELPER: colour VA cells
# =============================================================


def _color_va(val):
    try:
        v = float(val)
        if v > 0:
            return "background-color: #C8E6C9; color: #1B5E20; font-weight: bold"
        return "background-color: #FFCDD2; color: #B71C1C; font-weight: bold"
    except (TypeError, ValueError):
        return ""


# =============================================================
# TABS
# =============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Resumen General",
        "🏫 Análisis por Programa",
        "🔍 Comparación Programas",
        "📈 Histórico Puntajes",
        "📋 Datos Completos",
    ]
)

# ──────────────────────────────────────────────────────────────
# TAB 1 — RESUMEN GENERAL
# ──────────────────────────────────────────────────────────────
with tab1:
    st.markdown(f"### 📊 Resumen General — Año {anio_sel}")

    df_anio = df_resultados[df_resultados["Año"] == anio_sel]

    total_estudiantes = (
        int(
            dfs[str(anio_sel)]["estu_prgm_academico"]
            .isin(PROGRAMAS)
            .sum()
        )
        if str(anio_sel) in dfs
        else 0
    )

    va_tot_mean = df_anio["Valor Agregado Total"].mean()
    prog_positivos = int((df_anio["Valor Agregado Total"] > 0).sum())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""<div class="kpi-card neutro">
                <div class="kpi-value">{len(PROGRAMAS)}</div>
                <div class="kpi-label">Programas analizados</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""<div class="kpi-card neutro">
                <div class="kpi-value">{total_estudiantes:,}</div>
                <div class="kpi-label">Estudiantes {anio_sel}</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col3:
        tipo = "positivo" if pd.notna(va_tot_mean) and va_tot_mean > 0 else "negativo"
        emoji = "✅" if pd.notna(va_tot_mean) and va_tot_mean > 0 else "❌"
        va_disp = f"{va_tot_mean:.3f}" if pd.notna(va_tot_mean) else "N/A"
        st.markdown(
            f"""<div class="kpi-card {tipo}">
                <div class="kpi-value">{va_disp} {emoji}</div>
                <div class="kpi-label">VA Total promedio institucional</div>
            </div>""",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""<div class="kpi-card positivo">
                <div class="kpi-value">{prog_positivos}/{len(df_anio)}</div>
                <div class="kpi-label">Programas con VA positivo</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown(f"#### Valor Agregado por Programa y Componente — {anio_sel}")

    cols_show = ["Programa", "N"] + list(COMPONENTES.keys()) + ["Valor Agregado Total"]
    df_show = df_anio[[c for c in cols_show if c in df_anio.columns]].copy()
    comp_cols = [
        c
        for c in list(COMPONENTES.keys()) + ["Valor Agregado Total"]
        if c in df_show.columns
    ]
    styled = df_show.style.map(_color_va, subset=comp_cols).format(
        {c: "{:.3f}" for c in comp_cols}, na_rep="-"
    )
    st.dataframe(styled, use_container_width=True, height=400)

    st.markdown("#### Comparación VA Total por Programa")
    st.plotly_chart(
        fig_comparacion_programas(df_resultados, anio_sel, "Valor Agregado Total"),
        use_container_width=True,
    )

# ──────────────────────────────────────────────────────────────
# TAB 2 — ANÁLISIS POR PROGRAMA
# ──────────────────────────────────────────────────────────────
with tab2:
    st.markdown(f"### 🏫 {programa_sel}")

    df_prog_res = df_resultados[
        df_resultados["Programa"] == programa_sel
    ].sort_values("Año")

    # KPI row
    kpi_cols = st.columns(max(1, len(df_prog_res)))
    for i, (_, row) in enumerate(df_prog_res.iterrows()):
        va_val = row.get("Valor Agregado Total", np.nan)
        tipo = "positivo" if pd.notna(va_val) and va_val > 0 else "negativo"
        emoji = "✅" if pd.notna(va_val) and va_val > 0 else "❌"
        va_disp = f"{va_val:.3f}" if pd.notna(va_val) else "N/A"
        with kpi_cols[i % len(kpi_cols)]:
            st.markdown(
                f"""<div class="kpi-card {tipo}">
                    <div class="kpi-value">{va_disp} {emoji}</div>
                    <div class="kpi-label">VA Total {int(row['Año'])} | N={int(row['N'])}</div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown("#### Tabla VA por Componente")
    cols_tabla = ["Año", "N"] + list(COMPONENTES.keys()) + ["Valor Agregado Total"]
    df_tabla = df_prog_res[
        [c for c in cols_tabla if c in df_prog_res.columns]
    ].copy()
    comp_cols2 = [
        c
        for c in list(COMPONENTES.keys()) + ["Valor Agregado Total"]
        if c in df_tabla.columns
    ]
    styled2 = df_tabla.style.map(_color_va, subset=comp_cols2).format(
        {c: "{:.3f}" for c in comp_cols2}, na_rep="-"
    )
    st.dataframe(styled2, use_container_width=True)

    st.markdown("---")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.plotly_chart(
            fig_va_tendencia(df_prog_res, programa_sel), use_container_width=True
        )
    with col_g2:
        st.plotly_chart(
            fig_radar_programa(df_resultados, programa_sel, anio_sel),
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("#### 💬 Interpretación Automática")
    for _, row in df_prog_res.iterrows():
        va_t = row.get("Valor Agregado Total", np.nan)
        anio_r = int(row["Año"])
        if pd.notna(va_t):
            if va_t > 0.1:
                msg = (
                    f"✅ **{anio_r}**: El programa muestra **valor agregado positivo "
                    f"significativo** (VA={va_t:.3f}). Los egresados superan lo esperado "
                    "según su entrada en Saber 11."
                )
            elif va_t > 0:
                msg = (
                    f"🟡 **{anio_r}**: El programa presenta **valor agregado positivo "
                    f"leve** (VA={va_t:.3f}). Hay mejora, pero marginal."
                )
            else:
                msg = (
                    f"❌ **{anio_r}**: El programa presenta **valor agregado negativo** "
                    f"(VA={va_t:.3f}). Los resultados están por debajo de lo esperado "
                    "dado el perfil de entrada."
                )
            st.info(msg)

# ──────────────────────────────────────────────────────────────
# TAB 3 — COMPARACIÓN ENTRE PROGRAMAS
# ──────────────────────────────────────────────────────────────
with tab3:
    st.markdown(f"### 🔍 Comparación por Componente — {anio_sel}")
    st.plotly_chart(
        fig_comparacion_programas(df_resultados, anio_sel, componente_sel),
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("#### Todos los componentes")
    comp_pairs = list(COMPONENTES.keys())
    left_comps = comp_pairs[::2]
    right_comps = comp_pairs[1::2]
    for lc, rc in zip(left_comps, right_comps):
        c_l, c_r = st.columns(2)
        with c_l:
            st.plotly_chart(
                fig_comparacion_programas(df_resultados, anio_sel, lc),
                use_container_width=True,
            )
        with c_r:
            st.plotly_chart(
                fig_comparacion_programas(df_resultados, anio_sel, rc),
                use_container_width=True,
            )
    # Handle odd component (Comunicación Escrita is the 5th)
    if len(comp_pairs) % 2 != 0:
        st.plotly_chart(
            fig_comparacion_programas(df_resultados, anio_sel, comp_pairs[-1]),
            use_container_width=True,
        )

# ──────────────────────────────────────────────────────────────
# TAB 4 — HISTÓRICO DE PUNTAJES
# ──────────────────────────────────────────────────────────────
with tab4:
    st.markdown(f"### 📈 Histórico de Puntajes — {programa_sel}")
    st.plotly_chart(fig_promedios(dfs, programa_sel), use_container_width=True)

    st.markdown("#### Tabla de promedios")
    datos_prom = []
    for anio_k, df_anio_k in dfs.items():
        df_p = df_anio_k[df_anio_k["estu_prgm_academico"] == programa_sel]
        if len(df_p) < 10:
            continue
        fila_p: dict = {"Año": int(anio_k), "N": len(df_p)}
        for comp, (var_tyt, _) in COMPONENTES.items():
            if var_tyt in df_p.columns:
                fila_p[comp] = round(
                    pd.to_numeric(df_p[var_tyt], errors="coerce").mean(), 1
                )
        if "percentil_global" in df_p.columns:
            fila_p["Percentil Global"] = round(
                pd.to_numeric(df_p["percentil_global"], errors="coerce").mean(), 1
            )
        datos_prom.append(fila_p)

    if datos_prom:
        st.dataframe(pd.DataFrame(datos_prom), use_container_width=True)
    else:
        st.info("No hay datos suficientes para el programa seleccionado.")

# ──────────────────────────────────────────────────────────────
# TAB 5 — DATOS COMPLETOS
# ──────────────────────────────────────────────────────────────
with tab5:
    st.markdown("### 📋 Datos Completos")

    anio_data = st.radio("Año", list(dfs.keys()), horizontal=True)
    prog_filtro = st.multiselect(
        "Filtrar programas", PROGRAMAS, default=PROGRAMAS[:3]
    )

    df_data = dfs[anio_data].copy()
    if prog_filtro:
        df_data = df_data[df_data["estu_prgm_academico"].isin(prog_filtro)]

    st.dataframe(df_data, use_container_width=True, height=500)
    st.download_button(
        "⬇️ Descargar CSV",
        df_data.to_csv(index=False).encode("utf-8"),
        f"datos_tyt_{anio_data}.csv",
        "text/csv",
    )

# =============================================================
# FOOTER
# =============================================================

st.markdown(
    """
<div class="footer">
    🎓 <b>Institución Universitaria del Putumayo — Uniputumayo</b><br>
    Dashboard de Valor Agregado Saber T&amp;T | 2023 – 2024<br>
    Desarrollado con Streamlit · Datos ICFES
</div>
""",
    unsafe_allow_html=True,
)
