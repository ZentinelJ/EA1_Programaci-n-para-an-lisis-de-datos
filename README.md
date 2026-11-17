# Speedlogic: scraping, análisis y aplicación web · Programación para Análisis de Datos

![CI](https://github.com/ZentinelJ/EA1_Programaci-n-para-an-lisis-de-datos/actions/workflows/ci.yml/badge.svg)

Proyecto académico que extrae con **Scrapy** los precios y las fichas técnicas de los portátiles y computadores de escritorio de la tienda colombiana [speedlogic.com.co](https://speedlogic.com.co), los analiza con **pandas**, los publica en una **aplicación web** (Streamlit) y automatiza las pruebas y el despliegue con **GitHub Actions**.

| Evidencia | Qué se hizo |
|---|---|
| EA1 | Scraping con Scrapy, limpieza y análisis descriptivo (notebook) |
| EA2 | Flujo DevOps: ramas, Pull Requests, pruebas con pytest, CI y despliegue del análisis en GitHub Pages |
| EA3 | Aplicación web, CI/CD con GitHub Actions y despliegue en la nube (Render) |

## Enlaces

| Recurso | URL |
|---|---|
| Aplicación web (Render) | https://ea3-progrmacion-analisis-de-datos.onrender.com/ |
| Análisis del notebook (GitHub Pages) | https://zentinelj.github.io/EA1_Programaci-n-para-an-lisis-de-datos/ |
| Repositorio | https://github.com/ZentinelJ/EA1_Programaci-n-para-an-lisis-de-datos |

> La aplicación corre en el plan gratuito de Render: si pasan 15 minutos sin visitas se apaga y la primera carga siguiente puede tardar cerca de un minuto.

## Estructura del proyecto

```text
.
├── README.md
├── streamlit_app.py            # interfaz de la aplicación web
├── app/
│   └── data.py                 # lógica de datos (cargar, filtrar, resumir), sin interfaz
├── speed_scrapy/               # proyecto Scrapy
│   ├── scrapy.cfg
│   ├── laptop_summary.csv      # salida del spider "laptops"
│   ├── desktop_summary.csv     # salida del spider "desktops"
│   └── speed_scrapy/
│       ├── items.py            # Laptop_Items y Desktop_Items
│       ├── pipelines.py        # limpieza de precios, existencias y textos
│       ├── settings.py         # robots.txt, pausas, concurrencia
│       └── spiders/
│           ├── laptop_spider.py
│           └── desktop_spider.py
├── tests/                      # 30 pruebas con pytest
├── Analizando_EA1.ipynb        # limpieza y análisis con pandas
├── requirements.txt            # dependencias del scraper y el notebook
├── requirements-app.txt        # dependencias mínimas de la aplicación web (Render)
├── pyproject.toml / uv.lock    # entorno gestionado con uv
└── .github/workflows/
    ├── ci.yml                  # integración continua (pruebas)
    ├── deploy.yml              # despliegue del notebook en GitHub Pages
    └── deploy-render.yml       # despliegue de la app web en Render
```

## Instalación

Requisitos: Python 3.12 o superior y [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/ZentinelJ/EA1_Programaci-n-para-an-lisis-de-datos.git
cd EA1_Programaci-n-para-an-lisis-de-datos
uv sync
```

`uv sync` crea el entorno virtual (`.venv`) e instala las dependencias fijadas en `uv.lock`.

## Uso

**Ejecutar las pruebas**

```bash
uv run pytest -v
```

**Abrir la aplicación web en local** (usa los CSV que ya están en `speed_scrapy/`)

```bash
uv run streamlit run streamlit_app.py
```

Se abre en `http://localhost:8501`. La barra lateral filtra por categoría, marca y rango de precio; la página muestra cuatro indicadores, dos gráficos por marca y la tabla de productos.

**Volver a extraer los datos** (desde la carpeta que contiene `scrapy.cfg`)

```bash
cd speed_scrapy
uv run scrapy crawl laptops -O laptop_summary.csv -s DOWNLOAD_DELAY=30
uv run scrapy crawl desktops -O desktop_summary.csv -s DOWNLOAD_DELAY=30
```

`-O` sobrescribe el archivo y `-s DOWNLOAD_DELAY=30` aplica el `Crawl-delay: 30` del `robots.txt` del sitio.

**Análisis:** abrir `Analizando_EA1.ipynb` con el kernel del `.venv` y ejecutar todas las celdas desde la raíz del repositorio.

## Pruebas automatizadas

Ninguna prueba se conecta a Speedlogic: usan HTML y CSV de ejemplo.

| Archivo | Pruebas | Qué verifica |
|---|---|---|
| `test_pipeline.py` | 10 | Conversión de precios, existencias y limpieza de textos |
| `test_spiders.py` | 3 | Spider de portátiles: fichas con y sin descuento, enlaces y paginación |
| `test_desktop_spider.py` | 5 | Spider de escritorio: campos propios, fichas, enlaces y paginación |
| `test_app_data.py` | 10 | Lógica de la app: unir categorías, descuento, filtros y resumen |
| `test_app_ui.py` | 2 | La aplicación Streamlit arranca sin errores y muestra sus indicadores |

`tests/conftest.py` agrega al path la raíz del repositorio y la carpeta `speed_scrapy/`, necesario porque el paquete del scraper está anidado dentro de una carpeta con el mismo nombre.

## Automatización con GitHub Actions

Los flujos están en `.github/workflows/`. Cada archivo tiene comentarios línea por línea.

| Flujo | Se activa con | Qué hace |
|---|---|---|
| `ci.yml` | Push a `main` y `develop`; cada Pull Request | Instala con `uv sync` y ejecuta `uv run pytest -v` |
| `deploy.yml` | Push a `main`; ejecución manual | Repite las pruebas, convierte el notebook a HTML con nbconvert y lo publica en GitHub Pages |
| `deploy-render.yml` | Push a `main`; ejecución manual | Ejecuta las pruebas y, si pasan, lanza el despliegue de la app en Render |

### Cómo funciona `deploy-render.yml`

1. **Job `test`:** descarga el código (`actions/checkout`), instala uv (`astral-sh/setup-uv`), sincroniza dependencias (`uv sync`) y ejecuta las pruebas (`uv run pytest -v`).
2. **Job `deploy`** (`needs: test`, así que solo corre si `test` terminó en verde):
   - **Disparar el despliegue:** una petición `curl` a la URL del *deploy hook* de Render. `--fail` hace que el paso falle si Render responde con error.
   - **Verificar la aplicación:** consulta cada 20 segundos (hasta 30 veces) la ruta `/_stcore/health` de la app y falla si no responde en 10 minutos.
3. **Concurrencia:** el bloque `concurrency` impide dos despliegues simultáneos.

### Secretos y variables del repositorio

Se configuran en *Settings, Secrets and variables, Actions*:

| Tipo | Nombre | Para qué sirve |
|---|---|---|
| Secreto | `RENDER_DEPLOY_HOOK_URL` | URL privada del *deploy hook* de Render. Quien la conozca puede lanzar despliegues, por eso nunca va en el código |
| Variable | `APP_URL` | Dirección pública de la app, usada en el paso de verificación |

Si el secreto no existe, el paso de despliegue se omite con una advertencia y el flujo no falla.

## Despliegue en la nube (Render)

La aplicación se publica como **Web Service** en [Render](https://render.com) con el plan gratuito.

### Configuración del servicio

| Campo | Valor |
|---|---|
| Repositorio / rama | Este repositorio, rama `main` |
| Runtime | Python |
| Build Command | `pip install -r requirements-app.txt` |
| Start Command | `python -m streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true` |
| Instancia | Free |
| Auto-Deploy | Desactivado (solo despliega GitHub Actions) |

**Variables de entorno en Render**

| Variable | Valor | Para qué sirve |
|---|---|---|
| `PYTHON_VERSION` | 3.12.3 | Fija la versión de Python para que coincida con la local |
| `PORT` | La asigna Render | Puerto en el que debe escuchar la app (`$PORT` en el Start Command) |

### Pasos del despliegue

1. Se hace merge a `main` mediante Pull Request.
2. GitHub Actions ejecuta `deploy-render.yml`: pruebas y llamada al *deploy hook*.
3. Render descarga el repositorio, instala `requirements-app.txt` y arranca Streamlit.
4. El paso de verificación confirma que la app responde.

### Problemas encontrados y cómo se resolvieron

| Problema | Causa | Solución |
|---|---|---|
| `streamlit: command not found` (estado 127) | El comando de construcción por defecto no instalaba Streamlit | Build Command con `requirements-app.txt` y Start Command con `python -m streamlit` |
| Primera carga lenta | El plan gratuito apaga la app tras 15 min sin visitas | Abrir la URL antes de usarla; el paso de verificación espera hasta 10 minutos |

## Flujo de trabajo DevOps

```text
feature/* ──PR──> develop ──PR──> main ──> CI + Deploy (GitHub Pages y Render)
              (CI)           (CI)
```

- `main` es la versión estable y publicada; `develop` integra el trabajo; cada tarea va en una rama `feature/*` o `docs/*` creada desde `develop`.
- Los cambios entran solo por Pull Request, con el CI en verde.
- Los commits usan prefijo ([Conventional Commits](https://www.conventionalcommits.org/)): `feat`, `fix`, `test`, `refactor`, `ci`, `docs`, `chore`.
- Versiones marcadas con etiquetas: `v1.0` (EA2) y `v2.0` (EA3).

## Consideraciones éticas y legales

- **robots.txt:** las rutas recorridas (`/categoria/` y `/tienda/`) no están prohibidas. El proyecto usa `ROBOTSTXT_OBEY = True`.
- **Pausas:** `CONCURRENT_REQUESTS_PER_DOMAIN = 1` y `DOWNLOAD_DELAY = 15` en `settings.py`; el `Crawl-delay: 30` del sitio se cumple ejecutando con `-s DOWNLOAD_DELAY=30`.
- **Volumen bajo:** unas 55 peticiones por ejecución completa, sin iniciar sesión ni usar formularios.
- **Datos personales:** solo se extraen datos de productos; no se recogen comentarios ni datos de usuarios.
- **Pruebas y CI:** ninguna prueba ni flujo consulta el sitio, así que no se generan peticiones adicionales.
- **Uso:** los datos se emplean solo con fines académicos.

## Autores

- Juan Pablo Villa Álvarez
- Juan Manuel Arenas Rodríguez

**Curso:** Programación para Análisis de Datos · Ingeniería de Software y Datos
**Institución:** Institución Universitaria Digital de Antioquia (IU Digital)
**Docente:** Andrés Felipe Palacio Ángel