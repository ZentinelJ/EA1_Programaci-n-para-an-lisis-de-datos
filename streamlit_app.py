"""Explorador de precios y descuentos de Speedlogic (aplicacion web con Streamlit).

Ejecutar en local:   uv run streamlit run streamlit_app.py
"""
import streamlit as st

from app.data import cargar_datos, filtrar, por_marca, resumen

st.set_page_config(page_title="Precios Speedlogic", layout="wide")


@st.cache_data
def datos():
    # Se guarda en cache para no releer los CSV en cada interaccion.
    return cargar_datos()


df = datos()

st.title("Precios y descuentos de Speedlogic")
st.caption(
    "Portátiles y computadores de escritorio extraídos con Scrapy "
    "(proyecto académico, IU Digital)."
)

# --- Filtros (barra lateral) ---
st.sidebar.header("Filtros")
categorias = st.sidebar.multiselect(
    "Categoría", sorted(df["categoria"].unique()), default=sorted(df["categoria"].unique())
)
marcas = st.sidebar.multiselect("Marca", sorted(df["marca"].dropna().unique()))
precio_max_total = int(df["precio_final"].max())
rango = st.sidebar.slider("Precio final (COP)", 0, precio_max_total, (0, precio_max_total), step=100000)

filtrado = filtrar(df, categorias, marcas, rango[0], rango[1])

# --- Indicadores ---
r = resumen(filtrado)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Productos", r["productos"])
c2.metric("Con descuento", r["con_descuento"])
c3.metric("Precio mediano", "-" if r["precio_mediano"] is None else f"${r['precio_mediano']:,.0f}")
c4.metric("Descuento promedio", "-" if r["descuento_promedio"] is None else f"{r['descuento_promedio']:.1f} %")

# --- Gráficos ---
if filtrado.empty:
    st.warning("Ningún producto cumple los filtros seleccionados.")
else:
    g1, g2 = st.columns(2)
    g1.subheader("Precio promedio por marca (COP)")
    g1.bar_chart(por_marca(filtrado, "precio_final"))
    g2.subheader("Descuento promedio por marca (%)")
    g2.bar_chart(por_marca(filtrado, "descuento_pct"))

    st.subheader("Productos")
    columnas = [c for c in ["categoria", "marca", "cpu", "memory", "storage", "precio_original", "precio_final", "descuento_pct", "stock"] if c in filtrado.columns]
    st.dataframe(filtrado[columnas], width="stretch", hide_index=True)