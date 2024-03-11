import scrapy


class FoodspiderSpider(scrapy.Spider):
    name = "foodspider"
    allowed_domains = ["comidasperuanas.com.pe"]
    start_urls = ["https://comidasperuanas.com.pe"]

    def parse(self, response):
        food = response.css('div.elementor-widget-container')
        for food in foods:
            yield {
                'name': food.css('figure figcaption::text').get()
                'url': food.css('figure a').attrib['href']
            }
