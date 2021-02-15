import importlib
from configparser import ConfigParser
from scrapy.crawler import CrawlerProcess
from scrapx.commands import BaseRunSpiderCommand
from scrapx.utils.conf import closest_scrapy_cfg
from scrapx.utils.project import get_project_settings
from scrapy.exceptions import UsageError


class Command(BaseRunSpiderCommand):

    # requires_project = True

    def syntax(self):
        return "[options] <spider>"

    def short_desc(self):
        return "Run a spider"

    @staticmethod
    def _get_crawler_settings(spname):
        _settings = dict(get_project_settings())
        project_cfg_source = closest_scrapy_cfg(name='scrapx.cfg')
        if not project_cfg_source:
            raise UsageError('You are not in a project')
        project_cfg = ConfigParser()
        project_cfg.read(project_cfg_source)
        run_file_name = project_cfg.get('spiders', spname)
        project_name = project_cfg.get('deploy', 'botname')
        if not run_file_name:
            raise UsageError('cannot find spider in scrapx.cfg, please check for it')
        run_file_module = importlib.import_module(f'{project_name}.{run_file_name}')
        _attr_list = [i for i in dir(run_file_module) if i.isupper()]
        for _attr in _attr_list:
            _settings[_attr] = getattr(run_file_module, _attr)
        is_debug = _settings.get('DEBUG')
        if not is_debug:
            _settings['LOG_LEVEL'] = 'INFO'
        return _settings

    def add_options(self, parser):
        BaseRunSpiderCommand.add_options(self, parser)
        parser.add_argument('spidername', action='store', help='spider_name string')

    def run(self, parser):
        args = parser.parse_args()
        spname = args.spidername
        settings = self._get_crawler_settings(spname)
        crawler_process = CrawlerProcess(settings=settings)
        crawl_defer = crawler_process.crawl(spname)

        if getattr(crawl_defer, 'result', None) is not None and issubclass(crawl_defer.result.type, Exception):
            self.exitcode = 1
        else:
            crawler_process.start()

            if (
                crawler_process.bootstrap_failed
                or hasattr(crawler_process, 'has_exception') and crawler_process.has_exception
            ):
                self.exitcode = 1
