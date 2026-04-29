import unicodedata
import pandas as pd
import streamlit as st

SHEET_ID = "18SHpWulw1uLPc6mZx3daDyT_WQuzHrF-Nz1py_YWfog"
HOJAS = {"2023": "2023", "2024": "2024"}
MUESTRA_MINIMA = 10
COL_PROGRAMA = "estu_prgm_academico"

COMPONENTES = {
    "Lectura Crítica": ("mod_lectura_critica_punt", "sb11_punt_lectura_critica"),
    "Razonamiento Cuantitativo": ("mod_razona_cuantitat_punt", "sb11_punt_matematicas"),
    "Inglés": ("mod_ingles_punt", "sb11_punt_ingles"),
    "Competencias Ciudadanas": ("mod_competen_ciudada_punt", "sb11_punt_sociales_ciudadanas"),
    "Comunicación Escrita": ("mod_comuni_escrita_punt", None),
}


def _strip_accents(text: str) -> str:
    """Remove accent marks from a string."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase, replace spaces with underscores, strip accents from column names."""
    df.columns = [
        _strip_accents(col.strip().lower().replace(" ", "_"))
        for col in df.columns
    ]
    return df


def _leer_sheet(sheet_id: str, hoja: str) -> pd.DataFrame:
    url = (
        f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        f"/gviz/tq?tqx=out:csv&sheet={hoja}"
    )
    df = pd.read_csv(url, low_memory=False)
    df = _normalize_columns(df)
    return df


def _limpiar(df: pd.DataFrame, anio: str) -> pd.DataFrame:
    """Coerce numeric columns and add year column."""
    cols_num = (
        [v[0] for v in COMPONENTES.values() if v[0]]
        + [v[1] for v in COMPONENTES.values() if v[1]]
        + ["sb11_punt_global", "percentil_global"]
    )
    for col in cols_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["año"] = int(anio)
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_datos():
    """Load data from all configured sheets and return (dfs dict, combined df)."""
    dfs = {}
    for anio, hoja in HOJAS.items():
        df = _leer_sheet(SHEET_ID, hoja)
        dfs[anio] = _limpiar(df, anio)
    df_total = pd.concat(list(dfs.values()), ignore_index=True)
    return dfs, df_total


def get_programas(df_total: pd.DataFrame, muestra_minima: int = MUESTRA_MINIMA):
    """Return list of programs with at least muestra_minima students across all years."""
    if COL_PROGRAMA not in df_total.columns:
        return []
    conteo = (
        df_total.groupby(COL_PROGRAMA)
        .agg(n=(COL_PROGRAMA, "count"))
        .reset_index()
        .query(f"n >= {muestra_minima}")
        .sort_values("n", ascending=False)
    )
    return conteo[COL_PROGRAMA].tolist()
