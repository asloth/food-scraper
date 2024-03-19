import scrapy
from scrapy.selector import Selector


class YanuqspiderSpider(scrapy.Spider):
    name = "yanuqspider"
    allowed_domains = ["yanuq.com"]
    start_urls = ["https://yanuq.com"]

    def parse(self, response):
        cat = response.xpath('//ul[@id="sample-menu-3"]/li/a')
        listsubmenus = response.xpath('//ul[@id="sample-menu-3"]/li/ul/li/a')
        cat =  cat[:9]
        loncheras = ["https://www.yanuq.com"+item.attrib['href'] for item in listsubmenus if "lon" in item.attrib['href'].strip()]
        loncheras = [i for i in loncheras if "pre" not in i] #de momento sacaremos a loncheras pre escolar
        # Filter items with "#"
        filtered_array = [item.attrib['href'] for item in cat if "#" not in item.attrib['href'].strip()]
        modified_array = ["https://www.yanuq.com" + item for item in filtered_array]
        modified_array.extend(loncheras)
        for i in modified_array:
            yield scrapy.Request(i, callback=self.parse_category)

    def parse_category(self, response):
        obj = response.css('td table.divmarcocont td a.TextoArial')
        unique_array = list(set(obj))
        url_string = unique_array[0]
        parts = url_string.attrib['href'].split('#')
        modified_url = f"{parts[0]}?fragment={parts[1]}#{parts[1]}"
        complete_url = "https://www.yanuq.com/"+modified_url
        yield scrapy.Request(complete_url, callback=self.parse_recep)

    def parse_recep(self, response):
        obj = response.css('table.divmarcocont tr td a.TextoArial')
        filtered_array = [item.attrib['href'] for item in obj if item.attrib['href'].startswith("buscador")]
        modified_array = ["https://www.yanuq.com/" + item for item in filtered_array]
        for i in modified_array:
            yield scrapy.Request(i, callback=self.parse_food)

    def parse_food(self,response):
        food = response.css('table.divmarcobuscador')
        ingre = food.xpath('//table[@class="TextoArial"]/tr')
        preps = food.css('table table tr td.TextoArial')
        ingredients = []
        selected_selectors = []
        
        for p in preps:
            width_attribute = p.xpath('@width').get()
            if width_attribute == "95%":
                selected_selectors.append(p)

        text_inside_td = Selector(text=selected_selectors[1].get()).xpath('//text()').getall()
        text = ''.join(text_inside_td)

        for tr in ingre:
            # Select the second td element inside the tr
            td_elements = tr.xpath('.//td[2]')
            # Extract text from the second td element
            td_text = td_elements.xpath('.//text()').get()
            if td_text:
                ingredients.append(td_text.strip())
        
        for f in food:
            yield {
                'nombre': food.css('span.TextoArialG::text').get(),
                'url':'https://www.yanuq.com/',
                'ingredientes': ingredients,
                'pasos': text,
                'pais': 'Peru',
                'duracion': '',
                'porciones': '',
                'calorias': '',
                'categoria':'',
                'metodo':''
            }
