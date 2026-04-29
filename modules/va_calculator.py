import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from modules.data_loader import COMPONENTES, COL_PROGRAMA, MUESTRA_MINIMA

MUESTRA_MINIMA_MODELO = 30  # minimum global observations to fit a regression model
MUESTRA_MINIMA_RESIDUALES = 3  # minimum paired (TyT, SB11) observations per program


def _entrenar_modelos_globales(dfs: dict) -> dict:
    """
    For each (year, component) pair, train a global OLS model:
        TyT_component ~ SB11_proxy
    Returns a dict keyed by (anio_str, component_name) -> fitted LinearRegression.
    """
    modelos = {}
    for anio, df_anio in dfs.items():
        for comp, (var_tyt, var_sb11) in COMPONENTES.items():
            if var_sb11 is None:
                continue
            if var_tyt not in df_anio.columns or var_sb11 not in df_anio.columns:
                continue
            mask = df_anio[var_tyt].notna() & df_anio[var_sb11].notna()
            df_c = df_anio[mask]
            if len(df_c) < MUESTRA_MINIMA_MODELO:
                continue
            modelo = LinearRegression()
            modelo.fit(df_c[[var_sb11]].values, df_c[var_tyt].values)
            modelos[(anio, comp)] = modelo
    return modelos


def _va_programa(
    df_prog: pd.DataFrame,
    anio: str,
    comp: str,
    var_tyt: str,
    var_sb11: str | None,
    df_anio: pd.DataFrame,
    modelos: dict,
) -> float | None:
    """Compute value-added for one program / year / component."""
    if var_tyt not in df_prog.columns:
        return None

    y_prog = pd.to_numeric(df_prog[var_tyt], errors="coerce")

    # Comunicación Escrita: no SB11 proxy → VA = program mean − global mean
    if var_sb11 is None:
        media_global = pd.to_numeric(df_anio[var_tyt], errors="coerce").mean()
        if pd.isna(media_global) or y_prog.isna().all():
            return None
        return round(float(y_prog.mean() - media_global), 3)

    modelo = modelos.get((anio, comp))
    if modelo is None or var_sb11 not in df_prog.columns:
        return None

    X = pd.to_numeric(df_prog[var_sb11], errors="coerce")
    mask = y_prog.notna() & X.notna()
    if mask.sum() < MUESTRA_MINIMA_RESIDUALES:
        return None

    residuales = y_prog[mask].values - modelo.predict(
        X[mask].values.reshape(-1, 1)
    )
    return round(float(residuales.mean()), 3)


def calcular_resultados(
    dfs: dict,
    df_total: pd.DataFrame,
    programas: list,
    muestra_minima: int = MUESTRA_MINIMA,
) -> pd.DataFrame:
    """
    Compute VA for every (program, year) combination.
    Returns a tidy DataFrame with columns:
        Programa, Año, N, <component names>, Valor Agregado Total
    """
    modelos = _entrenar_modelos_globales(dfs)
    resultados = []

    for programa in programas:
        for anio, df_anio in dfs.items():
            df_prog = df_anio[df_anio[COL_PROGRAMA] == programa].copy()
            if len(df_prog) < muestra_minima:
                continue

            fila: dict = {"Programa": programa, "Año": int(anio), "N": len(df_prog)}
            vas = []

            for comp, (var_tyt, var_sb11) in COMPONENTES.items():
                va = _va_programa(
                    df_prog, anio, comp, var_tyt, var_sb11, df_anio, modelos
                )
                fila[comp] = va
                if va is not None:
                    vas.append(va)

            fila["Valor Agregado Total"] = (
                round(float(np.mean(vas)), 3) if vas else np.nan
            )
            resultados.append(fila)

    return pd.DataFrame(resultados)
