import re

from _base_parser import BaseParser

class LiveRigaParser(BaseParser):
    LANGS = [
        'en',
        'lv',
        'de',
    ]
    def __init__(self):
        super().__init__()

    @property
    def check_keys(self):
        return ['inner_id', 'lang', 'event_date']

    @property
    def HOST(self):
        return 'https://www.liveriga.com'

    def parse_lang_links(self, link):
        self.logger.info(f'Parse lang links')
        url = self.HOST + link
        r = self.make_request('get', url)
        doc = self.generate_html_tree(r)
        links = {i.text.lower(): i.get('href') for i in doc.xpath('//ul[@class="dropdown-menu"]/li/a')}
        links['en'] = link
        return links

    def parse_calendar_info(self):
        self.logger.info(f'Parse links')
        page = 1
        while True:
            self.logger.info(f'Page {page}')
            url = self.HOST + '/en/visit/events'
            r = self.make_request('get', url, params={'page': page})
            doc = self.generate_html_tree(r)
            links = doc.xpath('//a[contains(@class, "card-item")]/@href')
            if links:
                for link in links:
                    yield link
                page += 1
            else:
                return

    def parse_detailed_info(self, link):
        self.logger.debug(f'Parse link {link}')
        result = {}
        url = self.HOST + link
        r = self.make_request('get', url)
        doc = self.generate_html_tree(r)
        title = self.find_element_text(doc, '//h1[@class="head-title"]')
        if title == '404':
            return
        else:
            result['title'] = title
            result['location'] = self.find_element_text(doc, '//*[@class="location"]')
            result['source_link'] = url
            result['description'] = self.find_element_text(doc, '//div[@class="textual-content"]', text_content=True)
            price = self.find_element_text(doc, '//div[@class="info-price"]/p')
            if price:
                result['price'] = price.replace('EUR ', '€')
            result['event_date'] = self.find_element_text(doc, '//div[@class="startDateShort"]', text_content=True)
            result['event_time'] = self.find_element_text(doc, '//div[@class="startTime"]', text_content=True)
            buy_btn = doc.xpath('//a[contains(@class, "buy-btn")]')
            if buy_btn:
                result['buy_link'] = buy_btn[0].get('href')
            return result

    def parse(self):
        for link in self.parse_calendar_info():
            lang_links = self.parse_lang_links(link)
            inner_id = re.findall(r'/(\d+)-', lang_links['de'])[0]
            for lang in self.LANGS:
                lang_link = lang_links[lang]
                data = self.parse_detailed_info(lang_link)
                if data:
                    data['inner_id'] = inner_id
                    data['lang'] = lang
                    yield data


if __name__ == '__main__':
    from GIS_Tools import FastLogging
    from pprint import pprint
    _ = FastLogging.getLogger('LiveRigaParser')
    p = LiveRigaParser()
    p.main()