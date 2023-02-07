import requests
from lxml import html
import logging
import re
import warnings
from model import EventModel
warnings.filterwarnings('ignore')


class BaseParser:
    model = EventModel

    def __init__(self):
        self._session = None
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def HOST(self):
        raise NotImplementedError

    @property
    def session(self):
        if self._session is None:
            self._session = requests.Session()
        return self._session

    @staticmethod
    def generate_html_tree(response):
        doc = html.fromstring(response.content.decode('utf-8'))
        return doc

    @staticmethod
    def clear_element_text(x):
        if x:
            x = x.replace('\xa0', ' ') \
                .replace('&thinsp;', ' ') \
                .replace('&nbsp;', ' ') \
                .replace('&mdash;', '-') \
                .replace('&#8470;', '№') \
                .replace('&lt;', '<') \
                .replace('&gt;', '> ') \
                .strip(' \r\n\t:,.')
            x = re.sub('<.+?>', '', x)
            x = re.sub(r'\s{2,}', ' ', x)
            x = x.strip()
            return x

    @classmethod
    def find_elements_text(cls, dom, xpath='.', text_content=False):
        elements = dom.xpath(xpath)
        if text_content:
            elements = [cls.clear_element_text(i.text_content()) for i in elements]
        else:
            elements = [cls.clear_element_text(i.text) for i in elements]
        elements = list(filter(bool, elements))
        return elements

    @classmethod
    def find_element_text(cls, dom, xpath='.', text_content=False):
        for i in dom.xpath(xpath):
            if text_content:
                return cls.clear_element_text(i.text_content())
            else:
                return cls.clear_element_text(i.text)

    def make_request(self, method, url, **kwargs):
        user_agent = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0'}
        if 'headers' not in kwargs:
            kwargs['headers'] = user_agent
        else:
            kwargs['headers'] = {**kwargs['headers'], **user_agent}
        r = self.session.request(method, url, verify=False, **kwargs)
        return r

    def parse(self):
        raise NotImplementedError

    @property
    def check_keys(self):
        raise NotImplementedError

    def main(self):
        for data in self.parse():
            data['site_link'] = self.HOST
            self.model.save_insert(data, self.check_keys)
