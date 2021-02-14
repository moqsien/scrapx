import os
import uuid
import shutil
import string

from configparser import ConfigParser
from importlib import import_module
from os.path import join, dirname, abspath, exists, splitext

import scrapx
from scrapx.commands import ScrapxCommand
from scrapy.utils.template import render_templatefile, string_camelcase
from scrapy.exceptions import UsageError


def sanitize_module_name(module_name):
    """Sanitize the given module name, by replacing dashes and points
    with underscores and prefixing it with a letter if it doesn't start
    with one
    """
    module_name = module_name.replace('-', '_').replace('.', '_')
    if module_name[0] not in string.ascii_letters:
        module_name = "a" + module_name
    return module_name


class Command(ScrapxCommand):

    requires_project = False
    default_settings = {'LOG_ENABLED': False}

    def syntax(self):
        return "[options] <name> <domain>"

    def short_desc(self):
        return "Generate new spider using pre-defined templates"

    def add_options(self, parser):
        ScrapxCommand.add_options(self, parser)
        parser.add_argument("-l", "--list", dest="list", action="store_true",
                            help="List available templates")
        parser.add_argument("-d", "--dump", dest="dump", metavar="TEMPLATE",
                            help="Dump template to standard output")
        parser.add_argument("-t", "--template", dest="template", default="basic",
                            help="Uses a custom template.")
        parser.add_argument("--force", dest="force", action="store_true",
                            help="If the spider already exists, overwrite it with the template")
        parser.add_argument('spider_name', action='store', help='project_name string')
        parser.add_argument('domain', action='store', help='project_name string')

    @staticmethod
    def _spider_exists(spider_dir_path, module):
        _path = os.path.join(spider_dir_path, f'{module}.py')
        return os.path.exists(_path)

    def _find_template(self, template):
        template_file = join(self.templates_dir, f'{template}.py.tmpl')
        if exists(template_file):
            return template_file
        print(f"Unable to find template: {template}\n")
        print('Use "scrapy genspider --list" to see all available templates.')

    def _list_templates(self):
        print("Available templates:")
        for filename in sorted(os.listdir(self.templates_dir)):
            if filename.endswith('.tmpl'):
                print(f"  {splitext(filename)[0]}")

    @property
    def templates_dir(self):
        return join(
            join(scrapx.__path__[0], 'templates'),
            'spiders'
        )

    def run(self, parser):
        args = parser.parse_args()
        if args.list:
            self._list_templates()
            return
        if args.dump:
            template_file = self._find_template(args.dump)
            if template_file:
                with open(template_file, "r") as f:
                    print(f.read())
            return

        module = sanitize_module_name(args.spider_name)

        _path_1 = os.path.join(os.path.abspath('.'), 'scrapx.cfg')
        _path_2 = os.path.join(os.path.dirname(os.path.abspath('.')), 'scrapx.cfg')
        if os.path.exists(_path_1):
            _project_config_source = _path_1
            runfile_dir_path = os.path.dirname(_path_1)
            spider_dir_path = os.path.join(runfile_dir_path, 'spiders')
        elif os.path.exists(_path_2):
            _project_config_source = _path_2
            runfile_dir_path = os.path.dirname(_path_2)
            spider_dir_path = os.path.join(runfile_dir_path, 'spiders')
        else:
            print("Cannot generate a spider outside of a project")
            return

        project_cfg = ConfigParser()
        project_cfg.read(_project_config_source)
        botname = project_cfg.get('deploy', 'botname')
        if botname == module:
            print("Cannot create a spider with the same name as your project")
            return

        name = args.spider_name
        if not args.force and self._spider_exists(spider_dir_path, module):
            print('Spider module is already existed')
            return
        template_name = args.template
        domain = args.domain
        template_file = self._find_template(template_name)
        data_type = project_cfg.get('datatype', 'default')
        if template_file:
            self._genspider(module, name, domain, template_name, template_file, spider_dir_path, botname)
            self._genrunfile(name, runfile_dir_path, botname, _project_config_source, data_type)

    @staticmethod
    def _genspider(module, name, domain, template_name, template_file, spider_dir_path, botname):
        """Generate the spider module, based on the given template"""
        capitalized_module = ''.join(s.capitalize() for s in module.split('_'))
        tvars = {
            # 'project_name': botname,
            'ProjectName': string_camelcase(botname),
            # 'module': module,
            'name': name,
            'domain': domain,
            'classname': f'{capitalized_module}Spider'
        }
        spider_file = f"{join(spider_dir_path, module)}.py"
        shutil.copyfile(template_file, spider_file)
        render_templatefile(spider_file, **tvars)
        print(f"Created spider {name!r} using template {template_name!r} ")

    @property
    def _uuid(self):
        return str(uuid.uuid4())

    def _genrunfile(self, name, runfile_dir_path, botname, project_config_path, data_type):
        """Generate the runfile for a spider"""
        template_file = self._find_template('run')
        run_file_name = 'run_{}'.format(name)
        run_file = f"{join(runfile_dir_path, run_file_name)}.py"
        collection_name = '_'.join([botname, name])
        tvars = {
            'ProjectName': string_camelcase(botname),
            'spider_name': name,
            'collection_name': collection_name,
            'project_name': botname,
            'uid': self._uuid,
            'data_type': data_type
        }
        shutil.copyfile(template_file, run_file)
        render_templatefile(run_file, **tvars)
        self._register_run_file(name, run_file_name, project_config_path)
        print(f"Created runfile {name!r} using template run.py.tmpl ")

    def _register_run_file(self, name, run_file_name, project_config_file_path):
        _spider_config_str = f'\n{name}={run_file_name}'
        with open(project_config_file_path, 'a') as f:
            f.write(_spider_config_str)
