import scrapy
import re
from manual_scraper_ext.items import Manual


class IscGmbhInfoSpider(scrapy.Spider):
    name = "isc-gmbh.info"
    allowed_domains = ["www.isc-gmbh.info"]
    start_urls = ["https://www.isc-gmbh.info/isc_de_en/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response):
        for link in response.css('div.form-group a::attr(href)').getall():
            if len(link.split("/")) == 8:
                yield response.follow(link, callback=self.parse_parent)

    def parse_parent(self, response):
        for link in response.css("div.item-span a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_product)

        next_page = response.css("li.next a::attr(href)").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse_parent)

    def parse_product(self, response):
        brand = response.css(
            'table.product-numbers tr:last-child td:last-child::text').get()
        if "Coming soon" not in brand:
            file_urls = []
            manual = Manual()
            product = response.css('div.product-category div::text').get()
            manual["product"] = product
            # checking product
            product_parent = response.xpath(
                "//ul[contains(@class, 'clearfix')]/li[last()-1]//a/span/text()").get()
            manual["product_parent"] = product_parent if product_parent.lower(
            ) != product.lower() else ""
            manual["url"] = response.url
            manual["type"] = "Instructions"
            manual["model"] = response.css(
                'div.product-name h1::text').get().replace("\n", " ").strip()
            manual["source"] = "ics-gmbh.com"
            manual["brand"] = brand
            for div in response.xpath('//div[contains(@class, "result-name")]'):
                if div:
                    a_text = div.xpath('a/text()').get()
                    if a_text and 'Instructions' in a_text:
                        download_link = div.xpath('a/@href').get()
                        file_urls.append(download_link)
                else:
                    self.logger("No Manuals in Product")
                    return
            manual["thumb"] = response.css(
                'div.product-image-wrap a::attr(href)').get()
            manual["file_urls"] = file_urls
            manual["product_lang"] = "en"

            if len(file_urls) != 0:
                yield manual
