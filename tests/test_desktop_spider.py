"""Pruebas del spider de computadores de escritorio sobre HTML de ejemplo (sin red).

El HTML imita la estructura de una ficha de Speedlogic (WooCommerce).
"""
from scrapy.http import HtmlResponse, Request

from speed_scrapy.pipelines import SpeedScrapyPipeline
from speed_scrapy.spiders.desktop_spider import Desktop_Spider

URL = "https://speedlogic.com.co/tienda/computadores-de-escritorio/ejemplo/"

FICHA_CON_DESCUENTO = """
<html><body>
<p class="price">
  <del><span class="screen-reader-text">El precio original era: $3.499.000.</span></del>
  <ins><span class="screen-reader-text">El precio actual es: $3.299.000.</span></ins>
</p>
<p class="stock in-stock">5 disponibles</p>
<div id="tab-description"><ul>
  <li><strong>Procesador:</strong> Intel Core i5 12400</li>
  <li><strong>Memoria RAM:</strong> 16GB DDR4</li>
  <li><strong>Unidad de estado sólido:</strong> 512GB NVMe</li>
  <li><strong>Fuente:</strong> 500W 80 Plus</li>
  <li><strong>Board:</strong> H610M</li>
  <li><strong>Monitor:</strong> 24 pulgadas FHD</li>
</ul></div>
<div id="tab-pwb_tab-content"><h3>POWER GROUP</h3></div>
</body></html>
"""

FICHA_SIN_DESCUENTO = """
<html><body>
<p class="price"><span><bdi><span>$</span>2.450.000</bdi></span></p>
<div id="tab-description"><ul>
  <li><strong>Procesador:</strong> Intel Core i3</li>
</ul></div>
<div id="tab-pwb_tab-content"><h3>POWER GROUP</h3></div>
</body></html>
"""

FICHA_CAMPOS_EN_LISTA = """
<html><body>
<p class="price"><span><bdi><span>$</span>2.450.000</bdi></span></p>
<div id="tab-description"><ul>
  <li>Procesador: Intel Core i3 10100</li>
  <li>Fuente: 450W</li>
  <li>Board: A520M</li>
</ul></div>
</body></html>
"""


def respuesta(html):
    return HtmlResponse(url=URL, body=html, encoding="utf-8", request=Request(URL))


def extraer(html):
    spider = Desktop_Spider()
    item = next(iter(spider.parse_detail(respuesta(html))))
    return SpeedScrapyPipeline().process_item(item, spider)


def test_ficha_con_descuento():
    item = extraer(FICHA_CON_DESCUENTO)
    assert item.original_price == 3499000
    assert item.final_price == 3299000
    assert item.final_price < item.original_price
    assert item.cpu == "Intel Core i5 12400"
    assert item.memory == "16GB DDR4"
    assert item.trademark == "POWER GROUP"
    assert item.stock == 5


def test_campos_propios_de_escritorio():
    """Fuente, board y monitor solo existen en la ficha de escritorio."""
    item = extraer(FICHA_CON_DESCUENTO)
    assert item.psu == "500W 80 Plus"
    assert item.board == "H610M"
    assert item.display == "24 pulgadas FHD"


def test_ficha_sin_descuento_no_se_rompe():
    item = extraer(FICHA_SIN_DESCUENTO)
    assert item.original_price is None
    assert item.final_price == 2450000
    assert item.stock == 1  # sin unidades en la ficha -> se asume 1
    assert item.psu is None
    assert item.board is None


def test_campos_en_lista_sin_etiqueta_strong():
    """Respaldo: si no hay <strong>, el dato se toma del <li> completo."""
    item = extraer(FICHA_CAMPOS_EN_LISTA)
    assert item.cpu == "Intel Core i3 10100"
    assert item.psu == "450W"
    assert item.board == "A520M"


def test_parse_sigue_enlaces_de_producto_y_siguiente_pagina():
    html = """
    <html><head><link rel="next" href="https://speedlogic.com.co/categoria/computadores-de-escritorio/page/2/"></head>
    <body>
      <a href="https://speedlogic.com.co/tienda/computadores-de-escritorio/pc-a/">A</a>
      <a href="https://speedlogic.com.co/tienda/computadores-de-escritorio/pc-b/">B</a>
      <a href="https://speedlogic.com.co/carrito/">Carrito</a>
    </body></html>
    """
    resp = HtmlResponse(
        url="https://speedlogic.com.co/categoria/computadores-de-escritorio/",
        body=html, encoding="utf-8",
    )
    urls = [r.url for r in Desktop_Spider().parse(resp)]
    assert "https://speedlogic.com.co/tienda/computadores-de-escritorio/pc-a/" in urls
    assert "https://speedlogic.com.co/tienda/computadores-de-escritorio/pc-b/" in urls
    assert "https://speedlogic.com.co/categoria/computadores-de-escritorio/page/2/" in urls
    assert not any("carrito" in u for u in urls)