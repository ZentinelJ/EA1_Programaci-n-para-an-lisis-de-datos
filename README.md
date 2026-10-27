# Speedlogic Scraper · EA1 Programación para Análisis de Datos

Extracción con **Scrapy** de las fichas técnicas y los precios de los **portátiles** y los **computadores de escritorio** de la tienda colombiana [speedlogic.com.co](https://speedlogic.com.co), con limpieza y análisis descriptivo en **pandas**.



## Objetivo

Construir un proceso automatizado, repetible y respetuoso con el sitio que convierta las páginas de producto de Speedlogic (HTML semiestructurado) en un dataset tabular. Con ese dataset se compara la oferta de portátiles y de equipos de escritorio armados: rangos de precio, descuentos reales frente al precio tachado, marcas y configuraciones (procesador, RAM, almacenamiento, gráfica, pantalla y disponibilidad).

## Sitio analizado

| | |
|---|---|
| Tienda | Speedlogic (https://speedlogic.com.co), comercio electrónico colombiano de tecnología (WordPress + WooCommerce) |
| Categoría 1 | Portátiles: `https://speedlogic.com.co/categoria/portatiles/` (3 páginas de listado) |
| Categoría 2 | Computadores de escritorio: `https://speedlogic.com.co/categoria/computadores-de-escritorio/` (1 página) |
| Datos extraídos | Ficha técnica, precio original, precio final, marca y existencias de cada producto |

## Consideraciones éticas y legales

- **robots.txt.** Las rutas que recorremos (`/categoria/…` y `/tienda/…`) **no** están prohibidas. El archivo solo bloquea rutas administrativas (`/wp-admin/`, `/wp-login.php`, `/wp-content/`, entre otras) y a los bots Yandex y Baiduspider. El proyecto tiene `ROBOTSTXT_OBEY = True`, así que Scrapy descarga y respeta ese archivo antes de cada petición.
- **Pausas entre peticiones.** `CONCURRENT_REQUESTS_PER_DOMAIN = 1` (una petición a la vez) y `DOWNLOAD_DELAY = 15` segundos. El robots.txt declara además `Crawl-delay: 30`. Scrapy **no** aplica esa directiva por su cuenta, así que para cumplirla al pie de la letra se ejecuta con `-s DOWNLOAD_DELAY=30` (así se hizo la corrida de verificación de este README).
- **Volumen bajo.** Son unas 40 peticiones por ejecución completa, sin saltarse controles de acceso, sin iniciar sesión y sin formularios.
- **Datos personales.** Solo se extraen datos de **productos**: no se recogen comentarios, nombres de usuarios ni ningún dato que identifique a personas, así que no hay tratamiento de datos personales.
- **Uso.** Los datos se usan solo con fines académicos y no se redistribuyen con fines comerciales.

## ¿Por qué Scrapy?

1. **Los productos vienen en el HTML, sin JavaScript.** Una petición simple (`curl`) a la categoría ya trae los enlaces a los productos, y cada ficha trae precio, marca, existencias y descripción técnica en el HTML inicial. 
2. **Hay paginación y dos niveles de navegación.** Portátiles tiene 3 páginas de listado (`/page/2/`, `/page/3/`), y los datos útiles no están en el listado sino en la página de cada producto. Scrapy resuelve las dos cosas con `response.follow`: sigue el `<link rel="next">` de la paginación y entra a cada ficha con un *callback* aparte (`parse_detail`). También descarta solo las URL repetidas (en el listado cada producto aparece enlazado dos veces, en la imagen y en el título).
3. **Ética configurable en un solo lugar.** `ROBOTSTXT_OBEY`, `DOWNLOAD_DELAY` y la concurrencia se definen en `settings.py`. Con BeautifulSoup + `requests` habría que programar a mano la lectura del robots.txt, las pausas y la cola de URL.
4. **Limpieza separada de la extracción.** El *pipeline* (`pipelines.py`) convierte los precios de texto (`"El precio actual es: $7.509.000"`) a enteros y normaliza las existencias, sin mezclar esa lógica con los selectores.
5. **Exportar es un parámetro.** `-O archivo.csv` (o `.json`) genera el archivo directamente con los campos del *item*, en UTF-8 (`FEED_EXPORT_ENCODING`). 

## Estructura del proyecto

```text
scrappingv1-app/
├── README.md
├── requirements.txt
├── pyproject.toml / uv.lock             # alternativa con uv
├── Analizando_EA1.ipynb   # limpieza, análisis y métricas con pandas
└── speed_scrapy/                         # proyecto Scrapy
    ├── scrapy.cfg
    ├── laptop_summary.csv                # salida del spider "laptops"
    ├── desktop_summary.csv               # salida del spider "desktops"
    └── speed_scrapy/
        ├── items.py                      # Laptop_Items y Desktop_Items (dataclasses)
        ├── pipelines.py                  # limpieza de precios, existencias y textos
        ├── settings.py                   # robots.txt, pausas, concurrencia, exportación
        ├── middlewares.py                # plantilla por defecto de Scrapy (sin cambios)
        └── spiders/
            ├── laptop_spider.py          # spider "laptops"
            └── desktop_spider.py         # spider "desktops"
```

## Requisitos e instalación

- Python 3.12 o superior.

```bash
python3 -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Con [uv](https://docs.astral.sh/uv/) también sirve `uv sync` (solo instala Scrapy; para el notebook hay que añadir `pandas`, `matplotlib` e `ipykernel`).

## Cómo ejecutarlo

Los spiders se ejecutan desde la carpeta que contiene `scrapy.cfg`:

```bash
cd speed_scrapy
scrapy crawl laptops -O laptop_summary.csv -s DOWNLOAD_DELAY=30
scrapy crawl desktops -O desktop_summary.csv -s DOWNLOAD_DELAY=30
```

`-O` sobrescribe el archivo (con `-o` se añadirían filas al final). `-s DOWNLOAD_DELAY=30` aplica el `Crawl-delay` del robots.txt; sin ese parámetro se usan los 15 s de `settings.py`.

Para el análisis, abre `Analizando_EA1.ipynb` en VS Code o Jupyter con el kernel del `.venv` y ejecuta todas las celdas desde la raíz del repositorio. El notebook genera `speedlogic_productos_limpio.csv`.



## Autores

- Juan Pablo Villa Álvarez
- Juan Manuel Arenas Rodríguez

**Curso:** Programación para Análisis de Datos· Ingeniería de Software y Datos
**Institución:** Institución Universitaria Digital de Antioquia (IU Digital) 
**Docente:** Andrés Felipe Palacio Ángel
