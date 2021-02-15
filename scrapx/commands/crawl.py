import os
import importlib
from configparser import ConfigParser, NoOptionError
from scrapy.crawler import CrawlerProcess
from scrapx.commands import BaseRunSpiderCommand
from scrapx.utils.conf import closest_scrapy_cfg
from scrapx.utils.project import get_project_settings
from scrapy.exceptions import UsageError


class Command(BaseRunSpiderCommand):

    # requires_project = True

    def syntax(self):
        return "<spider_name or project_name.spider_name>"

    def short_desc(self):
        return "Run a spider"

    @staticmethod
    def _get_project_cfg_source(spider_path):
        if spider_path.count('.') == 0:
            project_cfg_source = closest_scrapy_cfg(name='scrapx.cfg')
            if not project_cfg_source:
                print('You can use "scrapx crawl project_name.spider_name in a workspace"')
                print('or use "scrapx crawl spider_name" in a project')
                raise UsageError('cannot find spider in your given path')
            spider_name = spider_path
        elif spider_path.count('.') == 1:
            workspace_cfg_source = os.path.join(os.path.abspath('.'), 'workspace.cfg')
            if os.path.exists(workspace_cfg_source):
                project_name, spider_name = spider_path.split('.')
                project_cfg_source = os.path.join(
                    os.path.abspath('.'),
                    '{}/scrapx.cfg'.format(project_name)
                )
                if not os.path.exists(project_cfg_source):
                    raise UsageError(f'spider_path: {spider_path} does not exist')
            else:
                print('You can use "scrapx crawl project_name.spider_name in a workspace"')
                print('or use "scrapx crawl spider_name" in a project')
                raise UsageError('cannot find spider in your given path')
        else:
            raise UsageError('You must specify a correct spider_path like "spider_project.spider_name"')
        return spider_name, project_cfg_source

    def _get_crawler_settings(self, spname):
        spider_path = spname
        spider_name, project_cfg_source = self._get_project_cfg_source(spider_path)
        project_cfg = ConfigParser()
        project_cfg.read(project_cfg_source)
        try:
            run_file_name = project_cfg.get('spiders', spider_name)
        except NoOptionError:
            raise UsageError(f'Can not find spider: {spider_name}')
        project_name = project_cfg.get('deploy', 'botname')
        if not run_file_name:
            raise UsageError('cannot find spider in scrapx.cfg, please check for it')
        _settings = dict(get_project_settings())
        run_file_module = importlib.import_module(f'{project_name}.{run_file_name}')
        _attr_list = [i for i in dir(run_file_module) if i.isupper()]
        for _attr in _attr_list:
            _settings[_attr] = getattr(run_file_module, _attr)
        is_debug = _settings.get('DEBUG')
        if not is_debug:
            _settings['LOG_LEVEL'] = 'INFO'
        return spider_name, _settings

    def add_options(self, parser):
        BaseRunSpiderCommand.add_options(self, parser)
        parser.add_argument('spidername', action='store', help='spider_name string')

    def run(self, parser):
        args = parser.parse_args()
        spider_path = args.spidername
        spname, settings = self._get_crawler_settings(spider_path)
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
