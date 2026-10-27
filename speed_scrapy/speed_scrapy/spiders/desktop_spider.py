import scrapy
from speed_scrapy.items import Desktop_Items

class Desktop_Spider(scrapy.Spider):
    name = "desktops"
    start_urls = ["https://speedlogic.com.co/categoria/computadores-de-escritorio/"]

    def parse(self, response):

        urls = response.css("a[href*='/tienda/computadores-de-escritorio']::attr(href)").getall()

        for url in urls:
            yield response.follow(url, callback = self.parse_detail)

        next_page = response.css("link[rel = 'next']::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback = self.parse)

    def parse_detail(self, response):

        item = Desktop_Items()

        item.original_price = response.css("p.price del span.screen-reader-text::text").get()
        if item.original_price is None:
            item.original_price = response.css("p.price del + span.screen-reader-text::text").get()

        item.final_price = response.css("p.price ins span.screen-reader-text::text").get()
        if item.final_price is None:
            item.final_price = response.css("p.price ins + span.screen-reader-text::text").get()
        if item.final_price is None:
            item.final_price = response.css("p.price bdi::text").get()

        item.cpu = response.xpath("//strong[contains(text(), 'Procesador')]/following-sibling::text()").get()
        if item.cpu is None:
            item.cpu = response.xpath("normalize-space(//div[@id='tab-description']//li[contains(., 'Procesador')])").get() or None

        item.memory = response.xpath("//strong[contains(text(), 'Memoria RAM')]/following-sibling::text()").get()
        if item.memory is None:
            item.memory = response.xpath("normalize-space(//div[@id='tab-description']//li[contains(., 'Memoria RAM')])").get() or None

        item.storage = response.xpath("//strong[contains(text(), 'Unidad de estado sólido')]/following-sibling::text()").get()
        if item.storage is None:
            item.storage = response.xpath("normalize-space(//div[@id='tab-description']//li[contains(., 'Unidad de estado sólido')])").get() or None

        item.display = response.xpath("//strong[contains(text(), 'Monitor')]/following-sibling::text()").get()
        if item.display is None:
            item.display = response.xpath("normalize-space(//div[@id='tab-description']//li[contains(., 'Monitor')])").get() or None

        item.psu = response.xpath("//strong[contains(text(), 'Fuente')]/following-sibling::text()").get()
        if item.psu is None:
            item.psu = response.xpath("normalize-space(//div[@id='tab-description']//li[contains(., 'Fuente')])").get() or None

        item.board = response.xpath("//strong[contains(text(), 'Board')]/following-sibling::text()").get()
        if item.board is None:
            item.board = response.xpath("normalize-space(//div[@id='tab-description']//li[contains(., 'Board')])").get() or None

        item.trademark = response.css("#tab-pwb_tab-content h3::text").get()
        item.stock = response.css("p.stock.in-stock::text").get()

        yield item
