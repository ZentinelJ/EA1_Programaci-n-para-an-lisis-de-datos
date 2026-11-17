"""Logica de datos de la aplicacion web (sin interfaz).

Se separa de la interfaz (streamlit_app.py) para poder probarla con pytest
sin abrir la aplicacion.
"""
from pathlib import Path

import pandas as pd

# Los CSV los genera Scrapy con "-O" dentro de la carpeta speed_scrapy/
DATA_DIR = Path(__file__).resolve().parent.parent / "speed_scrapy"
LAPTOPS_CSV = DATA_DIR / "laptop_summary.csv"
DESKTOPS_CSV = DATA_DIR / "desktop_summary.csv"

RENOMBRAR = {
    "trademark": "marca",
    "original_price": "precio_original",
    "final_price": "precio_final",
}


def cargar_datos(laptops_csv=LAPTOPS_CSV, desktops_csv=DESKTOPS_CSV) -> pd.DataFrame:
    """Une los CSV de portatiles y escritorio en una sola tabla lista para analizar.

    - Agrega la columna 'categoria'.
    - Normaliza la marca (mayusculas, sin espacios).
    - Convierte los precios a numero y calcula 'descuento_pct'.
    """
    portatiles = pd.read_csv(laptops_csv)
    portatiles["categoria"] = "Portátil"
    escritorio = pd.read_csv(desktops_csv)
    escritorio["categoria"] = "Escritorio"

    df = pd.concat([portatiles, escritorio], ignore_index=True)
    df = df.rename(columns=RENOMBRAR)

    df["marca"] = df["marca"].astype("string").str.strip().str.upper()
    df["precio_original"] = pd.to_numeric(df["precio_original"], errors="coerce")
    df["precio_final"] = pd.to_numeric(df["precio_final"], errors="coerce")

    # Descuento = 1 - precio final / precio original. Sin precio tachado no hay descuento (NaN).
    original_valido = df["precio_original"].where(df["precio_original"] > 0)
    df["descuento_pct"] = (1 - df["precio_final"] / original_valido) * 100
    return df


def filtrar(df, categorias=None, marcas=None, precio_min=None, precio_max=None) -> pd.DataFrame:
    """Aplica los filtros de la barra lateral. Un filtro en None no se aplica."""
    resultado = df
    if categorias:
        resultado = resultado[resultado["categoria"].isin(categorias)]
    if marcas:
        resultado = resultado[resultado["marca"].isin(marcas)]
    if precio_min is not None:
        resultado = resultado[resultado["precio_final"] >= precio_min]
    if precio_max is not None:
        resultado = resultado[resultado["precio_final"] <= precio_max]
    return resultado


def resumen(df) -> dict:
    """Indicadores principales de la tabla (los que se muestran como metricas)."""
    descuentos = df["descuento_pct"].dropna()
    return {
        "productos": int(len(df)),
        "con_descuento": int(len(descuentos[descuentos > 0])),
        "precio_mediano": None if df["precio_final"].dropna().empty else float(df["precio_final"].median()),
        "descuento_promedio": None if descuentos.empty else float(descuentos.mean()),
    }


def por_marca(df, columna) -> pd.Series:
    """Promedio de una columna ('precio_final' o 'descuento_pct') por marca, de mayor a menor."""
    return df.groupby("marca")[columna].mean().dropna().sort_values(ascending=False)