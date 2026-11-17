"""Prueba de humo de la interfaz: la aplicacion Streamlit se ejecuta sin errores.

Usa los CSV reales del repositorio (speed_scrapy/*.csv).
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent.parent / "streamlit_app.py"


def test_la_app_arranca_sin_excepciones():
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not at.exception
    assert at.title[0].value == "Precios y descuentos de Speedlogic"


def test_muestra_las_cuatro_metricas():
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    assert len(at.metric) == 4