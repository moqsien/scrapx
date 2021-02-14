import re
import os
import string
from importlib import import_module
from os.path import join, exists, abspath
from shutil import ignore_patterns, move, copy2, copystat
from stat import S_IWUSR as OWNER_WRITE_PERMISSION

import scrapx
from scrapx.commands import ScrapxCommand
from scrapy.utils.template import render_templatefile, string_camelcase
from scrapy.exceptions import UsageError


TEMPLATES_TO_RENDER = (
    ('workspace.cfg',),
    ('settings.py.tmpl', ),
    ('pipelines.py.tmpl', ),
    ('middlewares.py.tmpl', ),
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
        return "<project_name> [project_dir]"

    def short_desc(self):
        return "Create new workspace"

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

    def add_options(self, parser):
        ScrapxCommand.add_options(self, parser)
        parser.add_argument('workspace_name', action='store', help='workspace_name string')

    def run(self, parser):
        args = parser.parse_args()

        workspace_name = args.workspace_name
        workspace_dir = args.workspace_name

        if exists(join(workspace_dir, 'workspace.cfg')):
            self.exitcode = 1
            print(f'Error: workspace.cfg already exists in {abspath(workspace_dir)}')
            return

        if not self._is_valid_name(workspace_name):
            self.exitcode = 1
            return

        self._copytree(self.templates_dir, abspath(workspace_dir))
        move(join(workspace_dir, 'globals'), join(workspace_dir, 'scrapx_globals'))
        for paths in TEMPLATES_TO_RENDER:
            path = join(*paths)
            absolute_workspace_dir = abspath(workspace_dir)
            _path = absolute_workspace_dir if 'workspace.cfg' in path else join(
                absolute_workspace_dir, 'scrapx_globals')
            tplfile = join(
                _path,
                string.Template(path).substitute(workspace_name=workspace_name)
            )
            render_templatefile(
                tplfile,
                workspace=workspace_name,
                set='$set'
            )
        print(f"New Scrapx workspace '{workspace_name}', using template directory "
              f"'{self.templates_dir}', created in:")
        print(f"    {abspath(workspace_dir)}\n")
        print("You can start your first project with:")
        print(f"    cd {workspace_dir}")
        print("    scrapx startproject project_name")

    @property
    def templates_dir(self):
        return join(
            join(scrapx.__path__[0], 'templates'),
            'workspace'
        )
