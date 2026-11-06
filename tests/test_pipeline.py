"""Pruebas de SpeedScrapyPipeline (limpieza de precios, stock y textos).

No se conectan a Speedlogic: usan items creados a mano.
"""
from speed_scrapy.items import Desktop_Items, Laptop_Items
from speed_scrapy.pipelines import SpeedScrapyPipeline


def procesar(item):
    return SpeedScrapyPipeline().process_item(item, spider=None)


def test_precios_se_convierten_a_entero():
    item = Laptop_Items(
        original_price="El precio original era: $7.919.000.",
        final_price="El precio actual es: $7.509.000.",
    )
    item = procesar(item)
    assert item.original_price == 7919000
    assert item.final_price == 7509000


def test_precio_sin_texto_de_accesibilidad():
    item = procesar(Laptop_Items(final_price="$3.119.000"))
    assert item.final_price == 3119000


def test_sin_precio_original_queda_none():
    """Producto sin descuento: no tiene precio tachado y no debe romperse."""
    item = procesar(Laptop_Items(final_price="$3.119.000"))
    assert item.original_price is None


def test_stock_none_se_asume_uno():
    item = procesar(Laptop_Items(stock=None))
    assert item.stock == 1


def test_stock_con_unidades():
    item = procesar(Laptop_Items(stock="10 disponibles"))
    assert item.stock == 10


def test_stock_agotado_es_cero():
    item = procesar(Laptop_Items(stock="Agotado"))
    assert item.stock == 0


def test_texto_con_dos_puntos_conserva_solo_el_valor():
    item = procesar(Laptop_Items(cpu="Procesador: Intel Core i7 13620H"))
    assert item.cpu == "Intel Core i7 13620H"


def test_texto_sin_dos_puntos_se_recorta():
    item = procesar(Desktop_Items(trademark="  POWER GROUP  "))
    assert item.trademark == "POWER GROUP"


def test_campos_none_no_rompen_el_pipeline():
    item = procesar(Desktop_Items())
    assert item.cpu is None
    assert item.final_price is None


def test_stock_con_texto_desconocido_es_cero():
    """Cualquier texto sin cantidad numerica se trata como sin existencias."""
    item = procesar(Laptop_Items(stock="Sin existencias"))
    assert item.stock == 0