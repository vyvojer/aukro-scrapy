import json
import logging

from scrapy import Spider
from scrapy.http import Response, Request

logger = logging.getLogger(__name__)


class AukroSpider(Spider):
    name = 'aukro'
    site_url = 'https://aukro.cz'
    api_url = site_url + "/backend/api/offers"

    def __init__(self, category='hry', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category
        self.start_urls = [
            'https://aukro.cz/{}?size=180'.format(category),
        ]

    def parse(self, response: Response):
        yield self.get_page_request(0)

    def get_page_request(self, page):
        url = self.api_url + "/search?page={}&size=180&sort="
        my_data = {"categorySeoUrl": self.category}
        request = Request(url.format(page), method='POST',
                          body=json.dumps(my_data),
                          headers={'Content-Type': 'application/json'},
                          callback=self.parse_api)
        return request

    def parse_api(self, response: Response):
        rd = json.loads(response.text)
        content = rd['content']
        page = rd['page']['number']
        page_count = rd['page']['size']
        for item in content:
            id = item['itemId']
            seo_url = item['seoUrl']
            item_url = '{}/{}-{}'.format(self.site_url, seo_url, id)
            item_request = Request(item_url, callback=self.parse_item)
            item_request.meta['item_id'] = id
            yield item_request
        next_page = page + 1
        if next_page < page_count:
            logger.info("Page: %s", next_page)
            yield self.get_page_request(next_page)

    def parse_item(self, response: Response):
        url = "{}/{}/detail".format(self.api_url, response.meta['item_id'])
        data = {"pageType": "OUTER"}
        request = Request(url,
                          method='POST',
                          body=json.dumps(data),
                          headers={'Content-Type': 'application/json'},
                          callback=self.parse_item_api
                          )
        yield request

    def parse_item_api(self, response: Response):
        item = json.loads(response.text)
        price = item['price']
        name = item['itemName']
        offer_type = item['offerTypeCode']
        item = dict(name=name, price=price, offer_type=offer_type)
        yield item
