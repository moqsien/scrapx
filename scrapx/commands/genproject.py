import re
import os
from configparser import ConfigParser
from importlib import import_module
from os.path import join, exists, abspath
from shutil import ignore_patterns, move, copy2, copystat
from scrapy.utils.template import render_templatefile
from stat import S_IWUSR as OWNER_WRITE_PERMISSION

import scrapx
from scrapx.commands import ScrapxCommand
from scrapx.utils.conf import closest_scrapy_cfg
from scrapy.exceptions import UsageError


TEMPLATES_TO_RENDER = (
    ('scrapx.cfg',)
)

IGNORE = ignore_patterns('*.pyc', '__pycache__', '.svn')


def _make_writable(path):
    current_permissions = os.stat(path).st_mode
    os.chmod(path, current_permissions | OWNER_WRITE_PERMISSION)


class Command(ScrapxCommand):

    requires_project = False
    default_settings = {'LOG_ENABLED': False,
                        'SPIDER_LOADER_WARN_ONLY': True}

    def syntax(self):
        return "<project_name>"

    def short_desc(self):
        return "Create new project"

    def _is_valid_name(self, project_name):
        def _module_exists(module_name):
            try:
                import_module(module_name)
                return True
            except ImportError:
                return False

        if not re.search(r'^[_a-zA-Z]\w*$', project_name):
            print('Error: Project names must begin with a letter and contain'
                  ' only\nletters, numbers and underscores')
        elif _module_exists(project_name):
            print(f'Error: Module {project_name!r} already exists')
        else:
            return True
        return False

    def add_options(self, parser):
        ScrapxCommand.add_options(self, parser)
        parser.add_argument('project_name', action='store', help='project_name string')

    def _copytree(self, src, dst):
        """
        Since the original function always creates the directory, to resolve
        the issue a new function had to be created. It's a simple copy and
        was reduced for this case.

        More info at:
        https://github.com/scrapy/scrapy/pull/2005
        """
        ignore = IGNORE
        names = os.listdir(src)
        ignored_names = ignore(src, names)

        if not os.path.exists(dst):
            os.makedirs(dst)

        for name in names:
            if name in ignored_names:
                continue

            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            if os.path.isdir(srcname):
                self._copytree(srcname, dstname)
            else:
                copy2(srcname, dstname)
                _make_writable(dstname)

        copystat(src, dst)
        _make_writable(dst)

    def run(self, parser):
        args = parser.parse_args()

        project_name = args.project_name
        project_dir = args.project_name

        if not exists('workspace.cfg'):
            self.exitcode = 1
            print('Error: a project cannot be started outside of workspace')
            print('Hint: scrapx initiate <workspace name> ')
            return

        workspace_cfg_source = closest_scrapy_cfg(name='workspace.cfg')
        workspace_cfg = ConfigParser()
        workspace_cfg.read(workspace_cfg_source)
        if workspace_cfg.get('deploy', 'spacename') == project_name:
            self.exitcode = 1
            print('Error: project_name cannot be the same with workspace_name')
            return

        if exists(join(project_dir, 'scrapx.cfg')):
            self.exitcode = 1
            print(f'Error: scrapx.cfg already exists in {abspath(project_dir)}')
            return

        if not self._is_valid_name(project_name):
            self.exitcode = 1
            return

        self._copytree(self.templates_dir, abspath(project_dir))
        project_config_file_path = join(abspath(project_dir), 'scrapx.cfg')
        render_templatefile(project_config_file_path, project_name=project_name)
        # move(join(project_dir, 'module'), join(project_dir, project_name))
        print(f"New Scrapx project '{project_name}', using template directory "
              f"'{self.templates_dir}', created in:")
        print(f"    {abspath(project_dir)}\n")
        print("You can start your first spider with:")
        print(f"    cd {project_dir}")
        print("    scrapx genspider example example.com")

    @property
    def templates_dir(self):
        return join(
            join(scrapx.__path__[0], 'templates'),
            'project'
        )
