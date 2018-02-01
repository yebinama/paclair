# -*- coding: utf-8 -*-
import json

from .exceptions import PluginNotFoundException
from .logged_object import LoggedObject
from .config_reader import ConfigReader
from .exceptions import PaclairException
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
        Constructeur

        :param config_file: fichier de configuration
        """
        super().__init__()
        self._config_reader = ConfigReader(config_file or DEFAULT_CONFIG_FILE)
        self._plugins = self._config_reader.read_plugins('Plugins')

    def analyse(self, plugin, name, delete=False):
        """
        Analyse du layer

        :param plugin: nom du plugin
        :param name: ressource à analyser
        :param delete: supprimer le layer après analyse
        :return: json clair
        :raises ResourceNotFoundException: si le layer n'est pas présent dans la base Clair
        :raise ClairConnectionError: en cas d'erreur de connexion à Clair
        """
        if plugin not in self._plugins:
            raise PluginNotFoundException("Plugin {} inconnu".format(plugin))

        # Exécution
        self.logger.debug("Analyse de  {}".format(name))
        result = self._plugins[plugin].analyse(name)
        if delete:
            self.logger.debug("Suppression de  {}".format(name))
            self._plugins[plugin].delete(name)
        return result

    def push(self, plugin, name):
        """
        Push de la ressource sur Clair

        :param plugin: nom du plugin
        :param name: ressource à pousser
        :return:
        """
        if plugin not in self._plugins:
            raise PluginNotFoundException("Plugin {} inconnu".format(plugin))

        # Exécution
        self.logger.debug("Push de {} avec le plugin {}".format(name, plugin))
        self._plugins[plugin].push(name)

    @staticmethod
    def statistics(clair_json):
        """
        Analyse un json clair pour en sortir des statistiques

        :param clair_json: json résultat de clair
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
    :return:
    """
    # Création du parser
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

    # Récupération des arguments
    args = parser.parse_args()

    # Initialisation du logger
    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(level=logging.DEBUG)
    else:
        logger.setLevel(level=logging.INFO)

    if args.syslog:
        # Formatter du logger
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
