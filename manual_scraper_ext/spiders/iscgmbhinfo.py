import scrapy
import re
from manual_scraper_ext.items import Manual


class IscGmbhInfoSpider(scrapy.Spider):
    name = "iscgmbhinfo"
    allowed_domains = ["www.isc-gmbh.info"]
    start_urls = ["https://www.isc-gmbh.info/isc_de_en/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.3,
        "CONCURRENT_REQUESTS": 5,
    }

    def parse(self, response):
        for link in response.css('div.form-group'):
            src = link.css("a::attr(href)").get()
            parent_product = link.css("span::text").get()
            if len(src.split("/")) == 8:
                yield response.follow(src, callback=self.parse_parent, meta={"product_parent": parent_product})

    def parse_parent(self, response):
        parent_product = response.meta["product_parent"]
        for link in response.css("div.item-span a::attr(href)").getall():
            yield response.follow(link, callback=self.parse_product, meta={"product_parent": parent_product})

        next_page = response.css("li.next a::attr(href)").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse_parent)

    def parse_product(self, response):
        brand = response.css(
            'table.product-numbers tr:last-child td:last-child::text').get()
        if "Coming soon" not in brand:
            manual = Manual()
            product = response.css('div.product-category div::text').get()
            manual["product"] = self.clean_product(product)
            product_parent = response.meta["product_parent"]
            manual["product_parent"] = self.clean_product(
                product_parent) if product_parent != None else ""
            manual["url"] = response.url
            manual["type"] = "Instructions"
            manual["model"] = self.clean_model(response.css(
                'div.product-name h1::text').get().replace("\n", " ").strip(), product)
            manual["source"] = "ics-gmbh.com"
            manual["brand"] = brand
            manual["product_lang"] = "en"
            manual["thumb"] = response.css(
                'div.product-image-wrap a::attr(href)').get()
            for div in response.xpath('//div[contains(@class, "result-name")]'):
                if div:
                    a_text = div.xpath('a/text()').get()
                    if a_text and 'Instructions' in a_text:
                        download_link = div.xpath('a/@href').get()
                        manual["file_urls"] = [download_link]

                        yield manual
                else:
                    self.logger.error("No Manuals in Product")
                    return

    def clean_model(self, model, product):
        pattern = r'^[\w\s-]+[^-_\s;]+'
        match = re.search(pattern, model)
        if match:
            output = match.group(0).replace(",", "").replace(
                ";", "").replace(".", " ").replace('"', "").replace("'", "").replace(product.lower(), "")
            return re.sub(r'"[\w\s]*"', '', output).strip()
        else:
            return model.replace(",", "").replace(";", "").replace("-", " ").strip()

    def clean_product(self, product):
        pattern = r"\s*\([^)]*\)"
        output_str = re.sub(pattern, "", product)
        output_str.replace(",", "").replace(";", "").strip()
        return output_str
