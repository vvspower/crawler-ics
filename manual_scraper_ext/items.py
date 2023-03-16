# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Identity
import scrapy


class Manual(scrapy.Item):
    model = scrapy.Field()  # product name without brand
    model_2 = scrapy.Field()  # alternative product name (optional)
    brand = scrapy.Field()  # brand name
    product = scrapy.Field()  # product (for example "washing machines")
    product_parent = scrapy.Field()  # "domestic appliances" for example (optional)
    # product field language, two digit language code (optional)
    product_lang = scrapy.Field()
    file_urls = scrapy.Field()  # url to PDF (as an array)
    alt_files = scrapy.Field()  # only used for files without url
    eans = scrapy.Field()  # optional product EANs
    files = scrapy.Field()  # internal
    # type, for example "quick start guide", "datasheet" or "manual" (optional if type = manual)
    type = scrapy.Field()
    url = scrapy.Field()  # url of the page containing link to pdf
    thumb = scrapy.Field()  # thumbnail (optional)
    video = scrapy.Field()  # video (optional)
    # hostname without http/www to identify the source, for example dyson.com or walmart.com
    source = scrapy.Field()
    scrapfly = scrapy.Field()  # enable Scrapfly for download


class ManualLoader(ItemLoader):
    default_output_processor = TakeFirst()
    identity_fields = {"files", "alt_files", "file_urls"}
    for _field in identity_fields:
        exec(f"{_field}_out = Identity()")
