import pandas as pd
import plotly.graph_objects as go

from modules.data_loader import COMPONENTES, COL_PROGRAMA, MUESTRA_MINIMA

# Colour palette for each component / metric
COLORES: dict[str, str] = {
    "Competencias Ciudadanas": "#1565C0",
    "Comunicación Escrita": "#E65100",
    "Inglés": "#546E7A",
    "Lectura Crítica": "#F9A825",
    "Razonamiento Cuantitativo": "#0277BD",
    "Valor Agregado Total": "#2E7D32",
    "Percentil": "#6A1B9A",
}


def fig_va_tendencia(df_prog_res: pd.DataFrame, programa: str) -> go.Figure:
    """Line chart: VA by component over available years for one program."""
    componentes_plot = list(COMPONENTES.keys()) + ["Valor Agregado Total"]
    fig = go.Figure()

    for comp in componentes_plot:
        if comp not in df_prog_res.columns:
            continue
        vals = df_prog_res[comp]
        if vals.notna().sum() == 0:
            continue
        fig.add_trace(
            go.Scatter(
                x=df_prog_res["Año"],
                y=vals,
                mode="lines+markers+text",
                name=comp,
                line=dict(color=COLORES.get(comp), width=2),
                marker=dict(size=8),
                text=[f"{v:.3f}" if pd.notna(v) else "" for v in vals],
                textposition="top center",
            )
        )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="black",
        opacity=0.4,
        annotation_text="Sin VA",
        annotation_position="right",
    )
    fig.update_layout(
        title=f"Valor Agregado por Componente<br><b>{programa}</b>",
        xaxis_title="Año",
        yaxis_title="Valor Agregado (VA)",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.4),
        height=450,
    )
    return fig


def fig_promedios(dfs: dict, programa: str) -> go.Figure:
    """Line chart: average raw scores by component over years for one program."""
    datos = []
    for anio, df_anio in dfs.items():
        df_p = df_anio[df_anio[COL_PROGRAMA] == programa]
        if len(df_p) < MUESTRA_MINIMA:
            continue
        fila: dict = {"Año": int(anio)}
        for comp, (var_tyt, _) in COMPONENTES.items():
            if var_tyt in df_p.columns:
                fila[comp] = round(
                    pd.to_numeric(df_p[var_tyt], errors="coerce").mean(), 1
                )
        if "percentil_global" in df_p.columns:
            fila["Percentil"] = round(
                pd.to_numeric(df_p["percentil_global"], errors="coerce").mean(), 1
            )
        datos.append(fila)

    if not datos:
        return go.Figure()

    df_plot = pd.DataFrame(datos).sort_values("Año")
    fig = go.Figure()

    for comp in list(COMPONENTES.keys()) + ["Percentil"]:
        if comp not in df_plot.columns or df_plot[comp].notna().sum() == 0:
            continue
        fig.add_trace(
            go.Scatter(
                x=df_plot["Año"],
                y=df_plot[comp],
                mode="lines+markers+text",
                name=comp,
                line=dict(color=COLORES.get(comp), width=2),
                marker=dict(size=8),
                text=[f"{v:.0f}" if pd.notna(v) else "" for v in df_plot[comp]],
                textposition="top center",
            )
        )

    fig.update_layout(
        title=f"Resultados Promedio por Componente<br><b>{programa}</b>",
        xaxis_title="Año",
        yaxis_title="Puntaje Promedio",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.4),
        height=450,
    )
    return fig


def fig_radar_programa(
    df_resultados: pd.DataFrame, programa: str, anio: int
) -> go.Figure:
    """Radar chart: VA per component for one program in one year."""
    df_p = df_resultados[
        (df_resultados["Programa"] == programa) & (df_resultados["Año"] == anio)
    ]
    if df_p.empty:
        return go.Figure()

    cats = list(COMPONENTES.keys())
    vals = [
        df_p[c].values[0] if c in df_p.columns else 0 for c in cats
    ]
    vals_plot = [float(v) if pd.notna(v) else 0.0 for v in vals]

    fig = go.Figure(
        go.Scatterpolar(
            r=vals_plot + [vals_plot[0]],
            theta=cats + [cats[0]],
            fill="toself",
            fillcolor="rgba(46,125,50,0.2)",
            line=dict(color="#2E7D32", width=2),
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        title=f"Radar VA — {programa} ({anio})",
        template="plotly_white",
        height=400,
    )
    return fig


def fig_comparacion_programas(
    df_resultados: pd.DataFrame, anio: int, componente: str
) -> go.Figure:
    """Horizontal bar chart: VA for all programs for a given year and component."""
    if componente not in df_resultados.columns:
        return go.Figure()

    df_a = (
        df_resultados[df_resultados["Año"] == anio]
        .dropna(subset=[componente])
        .sort_values(componente, ascending=True)
    )

    if df_a.empty:
        return go.Figure()

    colores_bar = [
        "#C8E6C9" if v > 0 else "#FFCDD2" for v in df_a[componente]
    ]
    fig = go.Figure(
        go.Bar(
            x=df_a[componente],
            y=df_a["Programa"],
            orientation="h",
            marker_color=colores_bar,
            text=[f"{v:.3f}" for v in df_a[componente]],
            textposition="outside",
        )
    )
    fig.add_vline(x=0, line_color="black", line_dash="dash", opacity=0.5)
    fig.update_layout(
        title=f"Comparación VA — {componente} ({anio})",
        xaxis_title="Valor Agregado",
        template="plotly_white",
        height=max(300, len(df_a) * 50),
    )
    return fig
