# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class SpeedScrapyPipeline:
    def process_item(self, item, spider):

        temp_dict = {}

        if item.original_price:
            item.original_price = int(item.original_price.replace("$", "").replace(".", "").replace("El precio original era: ", "").strip())

        if item.final_price:
             item.final_price = int(item.final_price.replace("$", "").replace(".", "").replace("El precio actual es: ", "").strip())

        if item.stock is None:
                item.stock = 1
        else:
            try:
                item.stock = int(item.stock.replace("disponibles", "").strip())
            except ValueError:
                    stock_text = item.stock.lower()
                    if "agotado" in stock_text:
                        item.stock = 0
                    else:
                        item.stock = 0

        for key, value in vars(item).items():
            if isinstance(value, str):
                if ":" in value:
                    temp_dict[key] = value.partition(":")[2].strip()
                else:
                    temp_dict[key] = value.strip()
            else:
                temp_dict[key] = value

        for key, value in temp_dict.items():
            setattr(item, key, value)
        
        return item
