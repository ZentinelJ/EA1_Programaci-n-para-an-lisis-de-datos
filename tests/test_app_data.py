"""Pruebas de la logica de datos de la aplicacion web (app/data.py).

Usan CSV pequenos creados en una carpeta temporal: no dependen de Speedlogic
ni de los CSV reales del repositorio.
"""
import pandas as pd
import pytest

from app.data import cargar_datos, filtrar, por_marca, resumen

LAPTOPS = """cpu,memory,storage,gpu,display,color,original_price,final_price,trademark,stock
Intel Core i7,32GB,1TB,RTX 4060,16 pulgadas,Negro,7919000,7509000,ASUS,10
Intel Core i5,16GB,512GB,Integrada,15.6 pulgadas,Gris,,3119000,LENOVO,1
Intel Core i9,64GB,2TB,RTX 5090,18 pulgadas,Negro,28000000,27985000,MSI,1
"""

DESKTOPS = """cpu,memory,storage,psu,board,display,original_price,final_price,trademark,stock
Intel Core i5,16GB,512GB,500W,H610M,24 pulgadas,3499000,3299000, power group ,5
"""


@pytest.fixture
def df(tmp_path):
    (tmp_path / "laptops.csv").write_text(LAPTOPS, encoding="utf-8")
    (tmp_path / "desktops.csv").write_text(DESKTOPS, encoding="utf-8")
    return cargar_datos(tmp_path / "laptops.csv", tmp_path / "desktops.csv")


def test_une_ambas_categorias(df):
    assert len(df) == 4
    assert set(df["categoria"]) == {"Portátil", "Escritorio"}


def test_normaliza_la_marca(df):
    assert "POWER GROUP" in set(df["marca"])


def test_calcula_el_descuento(df):
    asus = df[df["marca"] == "ASUS"].iloc[0]
    # 1 - 7.509.000 / 7.919.000 = 5,18 %
    assert asus["descuento_pct"] == pytest.approx(5.177, abs=0.01)


def test_sin_precio_original_no_hay_descuento(df):
    lenovo = df[df["marca"] == "LENOVO"].iloc[0]
    assert pd.isna(lenovo["descuento_pct"])


def test_filtra_por_categoria_y_marca(df):
    assert len(filtrar(df, categorias=["Escritorio"])) == 1
    assert len(filtrar(df, marcas=["ASUS", "MSI"])) == 2


def test_filtra_por_rango_de_precio(df):
    r = filtrar(df, precio_min=3_000_000, precio_max=8_000_000)
    assert sorted(r["marca"]) == ["ASUS", "LENOVO", "POWER GROUP"]


def test_sin_filtros_devuelve_todo(df):
    assert len(filtrar(df)) == len(df)


def test_resumen(df):
    r = resumen(df)
    assert r["productos"] == 4
    assert r["con_descuento"] == 3  # Lenovo no tiene precio tachado
    assert r["precio_mediano"] == pytest.approx(5_404_000)


def test_resumen_de_tabla_vacia(df):
    r = resumen(filtrar(df, marcas=["NO EXISTE"]))
    assert r["productos"] == 0
    assert r["precio_mediano"] is None
    assert r["descuento_promedio"] is None


def test_precio_promedio_por_marca_ordenado(df):
    s = por_marca(df, "precio_final")
    assert s.index[0] == "MSI"
    assert list(s) == sorted(s, reverse=True)