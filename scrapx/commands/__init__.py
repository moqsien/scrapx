"""
Base class for Srapx Commands
"""
import os
from twisted.python import failure

from scrapy.utils.conf import arglist_to_dict, feed_process_params_from_cli
from scrapy.exceptions import UsageError


class ScrapxCommand(object):
    requires_project = False
    crawler_process = None
    default_settings = {}
    exitcode = 0

    def __init__(self):
        self.settings = None

    def set_crawler(self, crawler):
        if hasattr(self, '_crawler'):
            raise RuntimeError("crawler already set")
        self._crawler = crawler

    def short_desc(self):
        """
        A short description of the command
        """
        return ""

    def long_desc(self):
        """A long description of the command. Return short description when not
        available. It cannot contain newlines, since contents will be formatted
        by optparser which removes newlines and wraps text.
        """
        return self.short_desc()

    def help(self):
        """An extensive help for the command. It will be shown when using the
        "help" command. It can contain newlines, since no post-formatting will
        be applied to its contents.
        """
        return self.long_desc()

    def add_options(self, parser):
        """args
        Populate option parse with options available for this command
        """
        group = parser.add_argument_group('Global Options')
        group.add_argument("--logfile", metavar="FILE",
                           help="log file. if omitted stderr will be used")
        group.add_argument("-L", "--loglevel", metavar="LEVEL", default=None,
                           help=f"log level (default: {self.settings['LOG_LEVEL']})")
        group.add_argument("--nolog", action="store_true",
                           help="disable logging completely")
        group.add_argument("--profile", metavar="FILE", default=None,
                           help="write python cProfile stats to FILE")
        group.add_argument("--pidfile", metavar="FILE",
                           help="write process ID to FILE")
        group.add_argument("-s", "--set", action="append", default=[], metavar="NAME=VALUE",
                           help="set/override setting (may be repeated)")
        group.add_argument("--pdb", action="store_true", help="enable pdb on failure")

    def process_options(self, parser):
        args = parser.parse_args()
        try:
            self.settings.setdict(arglist_to_dict(args.set),
                                  priority='cmdline')
        except ValueError:
            raise UsageError("Invalid -s value, use -s NAME=VALUE", print_help=False)

        if args.logfile:
            self.settings.set('LOG_ENABLED', True, priority='cmdline')
            self.settings.set('LOG_FILE', args.logfile, priority='cmdline')

        if args.loglevel:
            self.settings.set('LOG_ENABLED', True, priority='cmdline')
            self.settings.set('LOG_LEVEL', args.loglevel, priority='cmdline')

        if args.nolog:
            self.settings.set('LOG_ENABLED', False, priority='cmdline')

        if args.pidfile:
            with open(args.pidfile, "w") as f:
                f.write(str(os.getpid()) + os.linesep)

        if args.pdb:
            failure.startDebugMode()

    def run(self, parser):
        """
        Entry point for running commands
        """
        raise NotImplementedError


class BaseRunSpiderCommand(ScrapxCommand):
    """
    Common class used to share functionality between the crawl, parse and runspider commands
    """

    def add_options(self, parser):
        ScrapxCommand.add_options(self, parser)
        parser.add_argument("-a", dest="spargs", action="append", default=[], metavar="NAME=VALUE",
                            help="set spider argument (may be repeated)")
        parser.add_argument("-o", "--output", metavar="FILE", action="append",
                            help="append scraped items to the end of FILE (use - for stdout)")
        parser.add_argument("-O", "--overwrite-output", metavar="FILE", action="append",
                            help="dump scraped items into FILE, overwriting any existing file")
        parser.add_argument("-t", "--output-format", metavar="FORMAT",
                            help="format to use for dumping items")

    def process_options(self, parser):
        ScrapxCommand.process_options(self, parser)
        args = parser.parse_args()
        try:
            args.spargs = arglist_to_dict(args.spargs)
        except ValueError:
            raise UsageError("Invalid -a value, use -a NAME=VALUE", print_help=False)
        if args.output or args.overwrite_output:
            feeds = feed_process_params_from_cli(
                self.settings,
                args.output,
                args.output_format,
                args.overwrite_output,
            )
            self.settings.set('FEEDS', feeds, priority='cmdline')
