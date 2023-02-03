import re

import pandas as pd
from dateutil.relativedelta import relativedelta
from _base_parser import BaseParser
from datetime import date, datetime

class OperaParser(BaseParser):
    HOST = 'https://www.opera.lv'
    LANGS = ['en', 'lv']
    SCHEDULE_NAME = {
        'en': 'schedule',
        'lv': 'kalendars',
    }
    MONTHS = {
        'en': [
            'jan',
            'feb',
            'mar',
            'apr',
            'may',
            'jun',
            'jul',
            'aug',
            'sep',
            'oct',
            'nov',
            'dec'
        ],
        'lv': [
            'janv',
            'febr',
            'marts',
            'apr',
            'maijs',
            'jūn',
            'jūl',
            'aug',
            'sept,'
            'okt',
            'nov',
            'dec',
        ],
    }

    def __init__(self):
        super().__init__()

    @property
    def check_keys(self):
        return ['inner_id']

    def parse_calendar_info(self, lang: str, idate: date):
        self.logger.info(f'Parse links: {idate} [{lang}]')

        url = self.HOST + f'/{lang}/{self.SCHEDULE_NAME.get(lang)}/{idate.year}/{idate.month}/0/list'
        r = self.make_request('get', url)
        doc = self.generate_html_tree(r)
        for row in doc.xpath('//article[@data-role="calendar-block-event"]'):
            info = {}
            event_date_item = row.xpath('./div/section[@class="calendar-list-entry__date"]')[0]
            info['month'] = self.MONTHS[lang].index(event_date_item[1].text.lower().strip('.')) + 1
            info['day'] = int(self.find_element_text(event_date_item[0], '.'))

            event_time_item = row.xpath('./div/section[@class="calendar-list-entry__day"]')[0][1]
            info['event_time'] = event_time_item.text

            author = self.find_element_text(row, './div/section/h3[@class="calendar-list-entry__author"]')
            title = self.find_element_text(row, './div/section/h2[@class="calendar-list-entry__title"]', text_content=True)
            info['title'] = ' - '.join(i for i in [author, title] if i)

            info['source_link'] = self.HOST + row.xpath('./div/section/h2[@class="calendar-list-entry__title"]/a/@href')[0]
            info['lang'] = lang
            info['location'] = 'Latvijas Nacionālā opera un balets'
            yield info

    def parse_buy_info(self, id_, event_date):
        self.logger.info(f'Parse buy {id_}')
        url = self.HOST + f'?rt=shows&ac=tickets&id={id_}'
        r = self.make_request('get', url)
        doc = self.generate_html_tree(r)
        for buy_link in doc.xpath('//li/a/@href'):
            if 'javascript' not in buy_link:
                self.logger.debug(f'Parse buy link {buy_link}')
                r = self.make_request('get', buy_link)
                doc = self.generate_html_tree(r)
                date_element = self.find_element_text(doc, '//span[contains(@class, "git-day-date")]')
                if date_element:
                    date_text = re.findall('\d{2}.\d{2}.\d{4}', date_element)[0]
                    day, month, year = map(int, date_text.split('.'))
                    if event_date == date(year, month, day):
                        data = {}
                        data['buy_link'] = buy_link
                        data['inner_id'] = id_ + '_' + buy_link.strip('/').split('/')[-1]
                        prices = [int(re.findall(r'\d+', i.text)[0]) for i in doc.xpath('//div[contains(text(), "€")]')]
                        prices.sort()
                        data['price'] = f'{prices[0]}€ - {prices[-1]}€'
                        return data


    def parse_detailed_info(self, url: str, event_date):
        self.logger.info(f'Parse link {url}')
        info = {'source_link': url}
        r = self.make_request('get', url)
        doc = self.generate_html_tree(r)
        info['description'] = self.find_element_text(doc, '//div[@class = "event-module"]/p')
        buy_id = doc.xpath('//div[@class = "slider__body"]//a[contains(@href, "javascript")]/@data-show')
        if buy_id:
            info['inner_id'] = buy_id[0]
            buy_info = self.parse_buy_info(buy_id[0], event_date)
            if buy_info:
                info = {**info, **buy_info}
        return info

    def parse(self):
        start_date = date(date.today().year, date.today().month, 1)
        for month_diff in range(13):
            idate = start_date + relativedelta(months=month_diff)
            for lang in self.LANGS:
                for cinfo in self.parse_calendar_info(lang, idate):
                    month = cinfo.pop('month')
                    day = cinfo.pop('day')
                    event_date = date(idate.year, month, day)
                    month = self.MONTHS['en'][month-1].capitalize()
                    cinfo['event_date'] = f'{month} {day}'
                    dinfo = self.parse_detailed_info(cinfo['source_link'], event_date)
                    result_info = {**cinfo, **dinfo}
                    yield result_info

if __name__ == '__main__':
    from GIS_Tools import FastLogging
    from pprint import pprint
    _ = FastLogging.getLogger('OperaParser')
    p = OperaParser()
    p.main()