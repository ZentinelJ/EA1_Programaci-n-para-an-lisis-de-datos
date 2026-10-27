# Speedlogic Scraper · EA1 Programación para Análisis de Datos

Extracción con **Scrapy** de las fichas técnicas y los precios de los **portátiles** y los **computadores de escritorio** de la tienda colombiana [speedlogic.com.co](https://speedlogic.com.co), con limpieza y análisis descriptivo en **pandas**.

> Proyecto académico de la *Evidencia de aprendizaje 1: Análisis y herramientas de extracción de datos* del curso Programación para Análisis de Datos (IU Digital, 2026-2).

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
- **Datos personales (Ley 1581 de 2012).** Solo se extraen datos de **productos**: no se recogen comentarios, nombres de usuarios ni ningún dato que identifique a personas, así que no hay tratamiento de datos personales.
- **Uso.** Los datos se usan solo con fines académicos y no se redistribuyen con fines comerciales.

## ¿Por qué Scrapy?

El docente aclaró en el encuentro del 21 de octubre de 2026 que basta con una de las tres herramientas vistas (BeautifulSoup, Selenium o Scrapy), siempre que se justifique la elección. Escogimos Scrapy por lo que encontramos al inspeccionar el sitio:

1. **Los productos vienen en el HTML, sin JavaScript.** Una petición simple (`curl`) a la categoría ya trae los enlaces a los productos, y cada ficha trae precio, marca, existencias y descripción técnica en el HTML inicial. No hace falta un navegador real, así que **Selenium sobra**: sería más lento y pesado sin aportar nada.
2. **Hay paginación y dos niveles de navegación.** Portátiles tiene 3 páginas de listado (`/page/2/`, `/page/3/`), y los datos útiles no están en el listado sino en la página de cada producto. Scrapy resuelve las dos cosas con `response.follow`: sigue el `<link rel="next">` de la paginación y entra a cada ficha con un *callback* aparte (`parse_detail`). También descarta solo las URL repetidas (en el listado cada producto aparece enlazado dos veces, en la imagen y en el título).
3. **Ética configurable en un solo lugar.** `ROBOTSTXT_OBEY`, `DOWNLOAD_DELAY` y la concurrencia se definen en `settings.py`. Con BeautifulSoup + `requests` habría que programar a mano la lectura del robots.txt, las pausas y la cola de URL.
4. **Limpieza separada de la extracción.** El *pipeline* (`pipelines.py`) convierte los precios de texto (`"El precio actual es: $7.509.000"`) a enteros y normaliza las existencias, sin mezclar esa lógica con los selectores.
5. **Exportar es un parámetro.** `-O archivo.csv` (o `.json`) genera el archivo directamente con los campos del *item*, en UTF-8 (`FEED_EXPORT_ENCODING`). No hubo que escribir código de exportación.

## Estructura del proyecto

```text
scrappingv1-app/
├── README.md
├── requirements.txt
├── pyproject.toml / uv.lock             # alternativa con uv
├── VillaAlvarez_JuanPablo_Analizando_EA1.ipynb   # limpieza, análisis y métricas con pandas
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

Para el análisis, abre `VillaAlvarez_JuanPablo_Analizando_EA1.ipynb` en VS Code o Jupyter con el kernel del `.venv` y ejecuta todas las celdas desde la raíz del repositorio. El notebook genera `speedlogic_productos_limpio.csv`.

## Campos extraídos

| Campo | Portátiles | Escritorio | Descripción | Origen en la ficha |
|---|:-:|:-:|---|---|
| `cpu` | ✔ | ✔ | Procesador | Línea "Procesador" de la descripción |
| `memory` | ✔ | ✔ | Memoria RAM | Línea "Memoria RAM" |
| `storage` | ✔ | ✔ | Almacenamiento | Línea "Unidad de estado sólido" |
| `gpu` | ✔ | | Tarjeta gráfica | Línea "Gráfica" |
| `display` | ✔ | ✔ | Pantalla (portátil) o monitor incluido (escritorio) | Línea "Pantalla" o "Monitor" |
| `color` | ✔ | | Color | Línea "Color" |
| `psu` | | ✔ | Fuente de poder | Línea "Fuente" |
| `board` | | ✔ | Tarjeta madre | Línea "Board" |
| `original_price` | ✔ | ✔ | Precio antes del descuento (COP, entero) | Precio tachado (`p.price del`) |
| `final_price` | ✔ | ✔ | Precio de venta (COP, entero) | Precio vigente (`p.price ins` o `bdi`) |
| `trademark` | ✔ | ✔ | Marca | Pestaña de marca (`#tab-pwb_tab-content h3`) |
| `stock` | ✔ | ✔ | Unidades disponibles (entero) | `p.stock.in-stock` |

Las especificaciones se buscan primero como `<strong>Etiqueta:</strong> valor` y, si no existe, como un `<li>` de la descripción que contenga la etiqueta (XPath con `normalize-space`).

## Resultados y métricas

Métricas calculadas sobre los CSV del repositorio (`laptop_summary.csv` y `desktop_summary.csv`):

| Métrica | Portátiles | Escritorio | Total |
|---|--:|--:|--:|
| Productos extraídos | 25 | 9 | **34** |
| Completitud de celdas | 96,4 % | 100 % | 97,4 % |
| Filas 100 % completas | 17 de 25 | 9 de 9 | 26 de 34 |
| Registros con precio final | 100 % | 100 % | 100 % |
| Duplicados exactos | 0 | 0 | 0 |
| Precio final mínimo (COP) | 1.909.000 | 2.435.000 | |
| Precio final mediano (COP) | 6.229.000 | 3.345.000 | |
| Precio final máximo (COP) | 27.985.000 | 4.065.000 | |
| Descuento promedio | 7,72 % | 6,76 % | |
| Descuento máximo | 16,15 % | 11,98 % | |
| Marcas | Asus (12), MSI (7), Lenovo (6) | Power Group (8), Cougar (1) | |

Valores faltantes en portátiles: `gpu` (3, equipos con gráficos integrados cuya ficha no tiene esa línea), `color` (5) y `original_price` (1, producto sin precio tachado).

<!-- EJECUCION -->

## Relación con CRISP-DM

| Fase | En este proyecto |
|---|---|
| 1. Comprensión del negocio | ¿Cómo se posiciona Speedlogic en precio y descuentos en portátiles frente a escritorios? Se definieron métricas de éxito para la extracción. |
| 2. Comprensión de los datos | Inspección del HTML con DevTools: dónde están el precio tachado, el precio vigente, la marca y la ficha técnica. Perfilado de nulos y duplicados en el notebook. |
| 3. Preparación de los datos | Pipeline de Scrapy (precios a entero, existencias a número, textos sin prefijos) y limpieza en pandas (puntos sobrantes, marcas en mayúscula, `descuento_pct`, `ahorro`, `ram_gb`). |
| 4. Modelado | Análisis descriptivo: estadísticas de precio y descuento por categoría y marca, y relación RAM-precio. |
| 5. Evaluación | Verificación de las métricas de éxito en el notebook. |
| 6. Despliegue | CSV limpio y repositorio en GitHub, base para automatizar la extracción con GitHub Actions en la EA2 y la EA3. |

## Limitaciones

- **No se guarda nombre, SKU ni URL del producto.** No hay un identificador único: los duplicados solo se detectan sobre la fila completa y no se puede volver a la ficha de origen desde el CSV.
- **Existencias aproximadas.** Cuando la ficha no muestra un número de unidades, el pipeline asigna `stock = 1`; 18 de los 25 portátiles tienen ese valor, así que no siempre significa "una unidad".
- **Selectores atados al texto de la ficha.** Si la tienda cambia "Procesador" o "Memoria RAM" por otra redacción, o rediseña la plantilla, el campo queda vacío. Los textos no tienen un formato uniforme ("16GB DDR5", "DDR5 16GB.", "16G Ddr4").
- **Instantánea en el tiempo.** Los precios y descuentos cambian a diario; los resultados describen solo el momento de la extracción.
- **Muestra pequeña** (34 productos). Sirve para un análisis descriptivo, no para conclusiones estadísticas fuertes.
- **`Crawl-delay`.** El valor por defecto del proyecto (15 s) es menor que los 30 s del robots.txt; hay que pasar `-s DOWNLOAD_DELAY=30` para cumplirlo.

## Autores

- Juan Pablo Villa Álvarez
- Juan Manuel Arenas Rodríguez

**Curso:** Programación para Análisis de Datos (IDSD_PRO_ANA_DATOS_540) · Ingeniería de Software y Datos
**Institución:** Institución Universitaria Digital de Antioquia (IU Digital) · 2026-2, Bloque 2
**Docente:** Andrés Felipe Palacio Ángel
