# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


@dataclass
class Laptop_Items:
    # define the fields for your item here like:
    # name: str | None = None
    cpu: str | None = None
    memory: str | None = None
    storage: str | None = None
    gpu: str | None = None
    display: str | None = None
    color: str | None = None
    original_price: str | None = None
    final_price: str | None = None
    trademark: str | None = None
    stock: str | None = None

@dataclass
class Desktop_Items:
    cpu: str | None = None
    memory: str | None = None
    storage: str | None = None
    psu: str | None = None
    board: str | None = None
    display: str | None = None
    original_price: str | None = None
    final_price: str | None = None
    trademark: str | None = None
    stock: str | None = None
