import sys

from scrapy.crawler import CrawlerProcess
from scrapx.utils.project import get_project_settings


# debug or not
DEBUG = False

# just crawl newly published data
INCREMENT = False

# project name
BOT_NAME = 'test1'

# crawler info
CRAWLER_INFO = {
    'uid': '1b1d7b26-b55f-4bfd-b855-badb8419d4fa',
    'desc': '台州日报',
    'data_type': 1
}

# where to save crawled items, if not given, it will be "{project_name}_{spider_name}_{spider_id}"
COLLECTION_NAME = ''

# spider modules
SPIDER_MODULES = ['test1.spiders']
NEWSPIDER_MODULE = 'test1.spiders'

ROBOTSTXT_OBEY = False

DOWNLOAD_WARNSIZE = 500 * 1024 * 1024
DOWNLOAD_TIMEOUT = 1800

# concurrency
# CONCURRENT_REQUESTS = 32
# DOWNLOAD_DELAY = 3
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# USER_AGENT = 'test1 (+http://www.yourdomain.com)'
# DEFAULT_REQUEST_HEADERS = {
#    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#    'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'test1.middlewares.Test1SpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'test1.middlewares.Test1DownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapx_globals.pipelines.MongoPipeline': 300,
}


def main():
    _global = globals()
    is_debug = _global.get('DEBUG')
    settings = dict(get_project_settings())
    if not is_debug:
        settings['LOG_LEVEL'] = 'INFO'
    for k, v in _global.items():
        if k.isupper():
            settings[k] = v
    args = sys.argv
    for arg in args[1:]:
        if arg.count('=') == 1:
            key, value = arg.split('=')
            key = key.upper()
            settings[key] = value

    process = CrawlerProcess(settings=settings)
    process.crawl('tzrb')
    process.start()


if __name__ == '__main__':
    main()
