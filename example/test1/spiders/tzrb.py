import time
import re
import os
from urllib.parse import urljoin
import scrapy
from scrapx.crawler_base.base import BaseSpider


class Test1Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    _id = scrapy.Field()
    spider_id = scrapy.Field()
    item_id = scrapy.Field()
    url = scrapy.Field()
    list_html = scrapy.Field()
    html_text = scrapy.Field()
    update_time = scrapy.Field()
    create_time = scrapy.Field()
    attach_file = scrapy.Field()


class TzrbSpider(BaseSpider):
    name = 'tzrb'
    allowed_domains = []

    site_url = 'paper.taizhou.com.cn/tzrb/html/2018-08/07/node_4.htm'
    start_urls = ['http://paper.taizhou.com.cn/tzrb/html/2018-08/07/node_4.htm']

    def __init__(self, name=None, **kwargs):
        super(TzrbSpider, self).__init__(name=name, **kwargs)
        self.page_url = 'http://paper.taizhou.com.cn/tzrb/html/2018-08/07/node_{}.htm'
        self._host_url = 'http://paper.taizhou.com.cn/tzrb/html/2018-08/07/'
        self.bot_name = None
        self.mongodb_attach_base_dir = None
        self.attach_path_dir = None

    def start_requests(self):
        for url in self.start_urls:
            request = scrapy.Request(url, callback=self.parse, dont_filter=True)
            yield request

    def parse(self, response):
        self.bot_name = self.crawler.settings.get('BOT_NAME')
        if self.settings.get('INCREMENT'):
            total_page = 1
        else:
            total_page = 8
        url_list = response.xpath('//table[@width="318"]//div//a[contains(@href, "node")]/@href').extract()
        if url_list and len(url_list) >= total_page:
            for _url in url_list[:total_page]:
                node_id = re.search(r'node_(\d+?).htm', _url).group(1)
                url = self.page_url.format(node_id)
                request = scrapy.Request(url, callback=self.parse_page, dont_filter=True)
                yield request

    def parse_page(self, response):
        label_list = response.xpath('//table[@height="25"]//li/a')
        for label in label_list:
            item = Test1Item()
            item['list_html'] = label.get()
            url = urljoin(self._host_url, label.xpath('./@href').get())
            request = scrapy.Request(url=url, callback=self.parse_detail, dont_filter=True)
            request.meta['data'] = item
            yield request

    def parse_detail(self, response):
        item = response.meta['data']
        item['url'] = response.url
        item['item_id'] = re.search(r'content_(\d+?).htm', response.url).group(1)
        item['html_text'] = response.xpath('//table[@class="detail_table"]').get()
        # print(item['item_id'])
        yield item
