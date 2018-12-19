# -*- coding: utf-8 -*-
from paclair.exceptions import PluginNotFoundException
from paclair.exceptions import PaclairException, ConfigurationError
from paclair.handler import PaClair

import logging
import logging.handlers
import argparse
import os
import sys

DEFAULT_CONFIG_FILE = "/etc/paclair.conf"

def main():
    """
    Main

    """
    # Create parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="Debug mode", action="store_true")
    parser.add_argument("--syslog", help="Log to syslog", action="store_true")
    parser.add_argument("--conf", help="Conf file", action="store", default=DEFAULT_CONFIG_FILE)
    parser.add_argument("plugin", help="Plugin to launch", action="store")
    parser.add_argument("hosts", help="Image/hostname to analyse", nargs='+', action="store")

    # Subparsers
    subparsers = parser.add_subparsers(help="Command to launch", dest="subparser_name")
    subparsers.add_parser("push", help="Push images/hosts to Clair")
    subparsers.add_parser("delete", help="Delete images/hosts from Clair")
    parser_analyse = subparsers.add_parser("analyse", help="Analyse images/hosts already pushed to Clair")
    parser_analyse.add_argument("--output-format", help="Change default output format (default: json)",
                                choices=['stats', 'html'])
    parser_analyse.add_argument("--output-report", help="Change report location (default: logger)",
                                choices=['file', 'term'])
    parser_analyse.add_argument("--output-dir", help="Change output directory (default: current)", action="store",
                                default=".")
    parser_analyse.add_argument("--delete", help="Delete after analyse", action="store_true")

    # Parse args
    args = parser.parse_args()

    # Init logger
    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(level=logging.DEBUG)
    else:
        logger.setLevel(level=logging.INFO)

    if args.syslog:
        # Logger format
        formatter = logging.Formatter(
            'PACLAIR[{}]: ({}) %(levelname).1s %(message)s'.format(os.getpid(), os.getenv('USER')))
        # Syslog Handler
        syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
        syslog_handler.setFormatter(formatter)
        logger.addHandler(syslog_handler)
    else:
        logger.addHandler(logging.StreamHandler())

    # Run
    try:
        paclair_object = PaClair(args.conf)
    except (OSError, ConfigurationError) as error:
        logger.error(error)
        sys.exit(1)

    for host in args.hosts:
        try:
            if args.subparser_name == "push":
                paclair_object.push(args.plugin, host)
                logger.info("Pushed {} to Clair.".format(host))
            elif args.subparser_name == "delete":
                paclair_object.delete(args.plugin, host)
                logger.info("{} was deleted from Clair.".format(host))
            elif args.subparser_name == "analyse":
                result = paclair_object.analyse(args.plugin, host, args.delete, args.output_format)
                # Report
                if args.output_report == "term":
                    print(result)
                elif args.output_report == "file":
                    filename = os.path.join(args.output_dir, '{}.{}'.format(host.replace('/', '_'), args.output_format
                                                                            or 'json'))
                    try:
                        with open(filename, "w", encoding="utf-8") as report_file:
                            report_file.write(result)
                    except (OSError, IOError):
                        logger.error("Can't write in directory: {}".format(args.output_dir))
                        sys.exit(4)
                else:
                    logger.info(result)
            else:
                parser.print_help()
        except PluginNotFoundException as error:
            logger.error("Can't find plugin {} in configuration file.".format(args.plugin))
            logger.error(error)
            sys.exit(2)
        except PaclairException as error:
            logger.error("Error treating {}".format(host))
            logger.error(error)
            sys.exit(3)


if __name__ == "__main__":
    main()
