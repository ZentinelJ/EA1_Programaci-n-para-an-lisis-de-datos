"""Pruebas del spider de portátiles sobre HTML de ejemplo (sin red).

El HTML imita la estructura de una ficha de Speedlogic (WooCommerce).
"""
from scrapy.http import HtmlResponse, Request

from speed_scrapy.pipelines import SpeedScrapyPipeline
from speed_scrapy.spiders.laptop_spider import Laptops_Spider

URL = "https://speedlogic.com.co/tienda/portatiles/ejemplo/"

FICHA_CON_DESCUENTO = """
<html><body>
<p class="price">
  <del><span class="screen-reader-text">El precio original era: $7.919.000.</span></del>
  <ins><span class="screen-reader-text">El precio actual es: $7.509.000.</span></ins>
</p>
<p class="stock in-stock">10 disponibles</p>
<div id="tab-description"><ul>
  <li><strong>Procesador:</strong> Intel Core 7 240H</li>
  <li><strong>Memoria RAM:</strong> 32GB DDR5</li>
  <li><strong>Unidad de estado sólido:</strong> M.2 NVMe 1 TB</li>
  <li><strong>Gráfica:</strong> RTX 4060 8GB</li>
  <li><strong>Pantalla:</strong> 16 pulgadas WUXGA</li>
</ul></div>
<div id="tab-pwb_tab-content"><h3>ASUS</h3></div>
</body></html>
"""

FICHA_SIN_DESCUENTO = """
<html><body>
<p class="price"><span><bdi><span>$</span>3.119.000</bdi></span></p>
<div id="tab-description"><ul>
  <li><strong>Procesador:</strong> Intel Core i5</li>
</ul></div>
<div id="tab-pwb_tab-content"><h3>LENOVO</h3></div>
</body></html>
"""


def respuesta(html):
    return HtmlResponse(url=URL, body=html, encoding="utf-8", request=Request(URL))


def extraer(html):
    spider = Laptops_Spider()
    item = next(iter(spider.parse_detail(respuesta(html))))
    return SpeedScrapyPipeline().process_item(item, spider)


def test_ficha_con_descuento():
    item = extraer(FICHA_CON_DESCUENTO)
    assert item.original_price == 7919000
    assert item.final_price == 7509000
    assert item.final_price < item.original_price
    assert item.cpu == "Intel Core 7 240H"
    assert item.memory == "32GB DDR5"
    assert item.trademark == "ASUS"
    assert item.stock == 10


def test_ficha_sin_descuento_no_se_rompe():
    item = extraer(FICHA_SIN_DESCUENTO)
    assert item.original_price is None
    assert item.final_price == 3119000
    assert item.trademark == "LENOVO"
    assert item.stock == 1  # sin unidades en la ficha -> se asume 1
    assert item.gpu is None


def test_parse_sigue_enlaces_de_producto_y_siguiente_pagina():
    html = """
    <html><head><link rel="next" href="https://speedlogic.com.co/categoria/portatiles/page/2/"></head>
    <body>
      <a href="https://speedlogic.com.co/tienda/portatiles/producto-a/">A</a>
      <a href="https://speedlogic.com.co/tienda/portatiles/producto-b/">B</a>
      <a href="https://speedlogic.com.co/carrito/">Carrito</a>
    </body></html>
    """
    resp = HtmlResponse(
        url="https://speedlogic.com.co/categoria/portatiles/",
        body=html, encoding="utf-8",
    )
    urls = [r.url for r in Laptops_Spider().parse(resp)]
    assert "https://speedlogic.com.co/tienda/portatiles/producto-a/" in urls
    assert "https://speedlogic.com.co/tienda/portatiles/producto-b/" in urls
    assert "https://speedlogic.com.co/categoria/portatiles/page/2/" in urls
    assert not any("carrito" in u for u in urls)