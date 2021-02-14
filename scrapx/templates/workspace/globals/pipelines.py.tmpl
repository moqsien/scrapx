# ----------------------------------------
# insert item into mongodb
# ----------------------------------------
import time
import logging
import pymongo


class MongoPipeline(object):

    def __init__(self):
        self.key = 'item_id'
        self.conn = None
        self.col = None

    def open_spider(self, spider):
        logging.info('SpiderId: %s' % spider.id)
        if not spider.is_debug:
            mongo_params = spider.settings.getdict('MONGO_PARAMS')
        else:
            mongo_params = spider.settings.getdict('MONGO_PARAMS_DEBUG')
        self.conn = pymongo.MongoClient(**mongo_params)

        _collection_name = spider.settings.get('COLLECTION_NAME')
        if not _collection_name:
            project_name = spider.settings.get('BOT_NAME')
            spider_name = getattr(spider, 'name')
            spider_id = getattr(spider, 'id')
            _collection_name = f'{project_name}_{spider_name}_{spider_id}'
        _db = spider.settings.get('MONGO_CRAWLER_DB', 'crawler_test')
        assert _collection_name, 'COLLECTION_NAME cannot be none'

        self.col = self.conn[_db][_collection_name]
        self.create_index(self.col, self.key, True)
        self.create_index(self.col, 'update_time')
        self.create_index(self.col, 'create_time')

    def process_item(self, item, spider):
        item.update({'spider_id': spider.id})
        unique_key_value = item[self.key]
        existed = self.col.find_one({self.key: unique_key_value})
        if not existed:
            _time = int(time.time())
            item['create_time'] = _time
            item['update_time'] = _time
            self.col.insert_one(item)
        else:
            need_update_fields = {}
            for key in item.keys():
                if item[key] and (key not in existed or item[key] != existed[key]):
                    need_update_fields[key] = item[key]
            if need_update_fields:
                need_update_fields['update_time'] = int(time.time())
                self.col.update({self.key: unique_key_value}, {'$set': need_update_fields})
        return item

    def close_spider(self, spider):
        self.conn.close()
        logging.info('SpiderId: %s' % spider.id)

    def create_index(self, collection, index, unique=False):
        indexes = collection.index_information()
        index_key = index + '_1'
        if index_key not in indexes.keys():
            collection.ensure_index([(index, pymongo.ASCENDING)], unique=unique)
