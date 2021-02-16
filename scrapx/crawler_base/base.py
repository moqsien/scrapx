import re
import os
import time
import pymongo
from os.path import join, exists
from scrapy.spiders import Spider
from scrapy.exceptions import UsageError
from scrapx.utils.extra import parse_js_object


class BaseSpider(Spider):

    def __init__(self, name=None, **kwargs):
        super(BaseSpider, self).__init__(name=name, **kwargs)
        self._mongodb = None
        self._crawlers_info_collection = None
        self._crawlers_statistic_collection = None
        self._first_re = re.compile(r'(.)([A-Z][a-z]+)')
        self._all_re = re.compile(r'([a-z0-9])([A-Z])')
        self._file_dir = None
        self.parse_js_object = parse_js_object

    def _get_file_dir(self, crawler, spider):
        # where to save attach files
        _path = crawler.settings.get('ATTACH_FILE_PATH', '/data/crawlers/')
        project_name = crawler.settings.get('BOT_NAME')
        spider_name = getattr(spider, 'name')
        spider_id = getattr(spider, 'id')
        _dir_name = f'{project_name}_{spider_name}_{spider_id}'
        _dir = join(_path, _dir_name)
        self._file_dir = _dir
        if not exists(_dir):
            try:
                os.makedirs(self._file_dir)
            except PermissionError:
                raise UsageError('Permission denied When creating "/data/crawlers/", Please create the dir first')

    def _set_mongo_connection(self, mongo_params):
        self._mongodb = pymongo.MongoClient(**mongo_params)

    @staticmethod
    def _format_url(_url):
        if _url.startswith('www'):
            _url = 'http://{}'.format(_url)
        return _url

    def _save_crawler_info(self, crawler=None):
        # get mongo collection
        if crawler:
            mongo_params = crawler.settings.getdict('MONGO_PARAMS')
            mongo_db = crawler.settings.get('MONGO_CRAWLER_DB', 'crawler')
            if mongo_params and not self._crawlers_info_collection:
                self._set_mongo_connection(mongo_params)
                self._crawlers_info_collection = self._mongodb[mongo_db]['crawlers_info']
        project_name = crawler.settings.get('BOT_NAME')
        spider_name = self.name
        spider_path = f'{project_name}.{spider_name}'
        # upsert crawler info
        if crawler and self._crawlers_info_collection:
            crawler_info = crawler.settings.getdict('CRAWLER_INFO')
            _uid = crawler_info.get('uid')
            is_existed = self._crawlers_info_collection.find_one({'uid': _uid})
            _info_item = dict()
            _info_item['url'] = self._format_url(getattr(self, 'site_url', None) or self.start_urls[0])
            _time = int(time.time())
            _info_item['update_time'] = _time
            _info_item['desc'] = crawler_info.get('desc', '')
            _info_item['spider_path'] = spider_path
            _info_item['workspace'] = crawler.settings.get('WORKSPACE_NAME', '')
            if not _info_item['desc']:
                raise UsageError('Please check your run file, "desc" can not be None')
            _info_item['data_type'] = crawler_info.get('data_type', 0)
            if not _info_item['data_type']:
                raise UsageError('Please check your run file, "data_type" can not be None or zero')
            if not is_existed:
                _info_item['uid'] = _uid
                _info_item['create_time'] = _time
                _res = self._crawlers_info_collection.find()
                _spider_id = 10000 if not _res.count() else _res.sort('spider_id', -1)[0]['spider_id'] + 1
                _info_item['spider_id'] = _spider_id
                self._crawlers_info_collection.insert(_info_item)
            else:
                _spider_id = is_existed['spider_id']
                _info_item['spider_id'] = _spider_id
                self._crawlers_info_collection.update(
                    {'uid': _uid},
                    {'$set': _info_item}
                )
            return _spider_id

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        is_debug = crawler.settings.getbool('DEBUG', False)
        spider.is_debug = is_debug
        spider.id = spider._save_crawler_info(crawler)
        spider._get_file_dir(crawler, spider)
        return spider

    def _camel_to_snake(self, _str):
        s1 = self._first_re.sub(r'\1_\2', _str)
        return self._all_re.sub(r'\1_\2', s1).lower()

    def _save_statistics_info(self, spider):
        mongo_db = spider.settings.get('MONGO_STATISTIC_DB', 'crawler_statistic')
        if not self._mongodb:
            mongo_params = spider.settings.getdict('MONGO_PARAMS')
            self._set_mongo_connection(mongo_params)
        collection_name = f'{self.bot_name}_{self.name}_{spider.id}'
        self._crawlers_statistic_collection = self._mongodb[mongo_db][collection_name]

        is_debug = spider.is_debug
        statistic_data = spider.crawler.stats._stats
        if not is_debug:
            _fields = spider.settings.get('MONGO_STATISTIC_FIELDS') or [i for i in statistic_data]
            _data = {
                'spider_id': spider.id
            }
            for _d in _fields:
                key = _d.replace('.', '-')
                _data[key] = statistic_data[_d]
            self._crawlers_statistic_collection.insert(_data)
        if self._mongodb:
            self._mongodb.close()

    @staticmethod
    def close(spider, reason):
        spider._save_statistics_info(spider)
        closed = getattr(spider, 'closed', None)
        if callable(closed):
            return closed(reason)
