# -*- coding: utf-8 -*-
import json

from paclair.exceptions import PluginNotFoundException
from paclair.logged_object import LoggedObject
from paclair.config_reader import ConfigReader
from paclair.exceptions import PaclairException
import logging
import logging.handlers
import argparse
import os

DEFAULT_CONFIG_FILE = "/etc/paclair.conf"


class PaClair(LoggedObject):
    """
    Class Main
    """
    def __init__(self, config_file=None):
        """
        Constructor

        :param config_file: configuration file
        """
        super().__init__()
        self._config_reader = ConfigReader(config_file or DEFAULT_CONFIG_FILE)
        self._plugins = self._config_reader.read_plugins('Plugins')

    def analyse(self, plugin, name, delete=False):
        """
        Analyse a layer

        :param plugin: plugin's name
        :param name: resource to analyse
        :param delete: delete after analyse
        :return: json clair
        :raises ResourceNotFoundException: if layer not found
        :raise ClairConnectionError: if an error occurs requesting Clair
        """
        if plugin not in self._plugins:
            raise PluginNotFoundException("Plugin {} inconnu".format(plugin))

        self.logger.debug("Analyse de  {}".format(name))
        result = self._plugins[plugin].analyse(name)
        if delete:
            self.logger.debug("Suppression de  {}".format(name))
            self._plugins[plugin].delete(name)
        return result

    def push(self, plugin, name):
        """
        Push layer to Clair

        :param plugin: plugin's name
        :param name: resource to push
        :return:
        """
        if plugin not in self._plugins:
            raise PluginNotFoundException("Plugin {} inconnu".format(plugin))

        self.logger.debug("Push de {} avec le plugin {}".format(name, plugin))
        self._plugins[plugin].push(name)

    @staticmethod
    def statistics(clair_json):
        """
        Statistics from a json delivered by Clair

        :param clair_json: json delivered by Clair
        """
        result = {}
        for feature in clair_json.get('Layer', {}).get('Features', []):
            for vuln in feature.get("Vulnerabilities", []):
                if "FixedBy" in vuln:
                    result[vuln["Severity"]] = result.setdefault(vuln["Severity"], 0) + 1
        return result


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
    parser_analyse = subparsers.add_parser("analyse", help="Analyse images/hosts already pushed to Clair")
    parser_analyse.add_argument("--statistics", help="Only print statistics", action="store_true")

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
    paclair_object = PaClair(args.conf)
    for host in args.hosts:
        try:
            if args.subparser_name == "push":
                paclair_object.push(args.plugin, host)
                logger.info("Pushed {} to Clair.".format(host))
            else:
                result = paclair_object.analyse(args.plugin, host)
                if args.statistics:
                    result = paclair_object.statistics(result)
                    logger.info('\n'.join(("{}: {}".format(k, v) for k, v in result.items())))
                else:
                    logger.info(json.dumps(result))
        except PluginNotFoundException as error:
            logger.error("Can't find plugin {} in configuration file.".format(args.plugin))
            logger.error(error)
        except PaclairException as error:
            logger.error("Error treating {}".format(host))
            logger.error(error)


if __name__ == "__main__":
    main()
