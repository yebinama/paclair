# -*- coding: utf-8 -*-
from .clair_requests import ClairRequests
from .logged_object import LoggedObject
import importlib
import yaml


class ConfigReader(LoggedObject):
    """
    Classe permettant de lire le fichier de conf
    """

    def __init__(self, filename):
        """
        Initialisation

        :param filename: nom du fichier de conf
        """
        super(ConfigReader, self).__init__()
        self.filename = filename

    def read_section(self, section):
        """
        Renvoie la configuration associée à la section

        :param section: nom de la section
        :returns dict:
        """
        with open(self.filename, 'r') as f:
            # Chargement
            self.logger.debug("Lecture de la section %s du fichier %s" % (section, self.filename))
            conf = yaml.safe_load(f)

            # Vérification de la structure
            if section not in conf:
                self.logger.error("Pas de section %s dans le fichier de conf" % section)
                return {}
            return conf[section]

    def read_plugins(self, plugin_section="Plugins"):
        """
        Renvoie les plugins associés à la conf

        :param plugin_section: nom de la section plugins
        """
        plugins = self.read_section(plugin_section)
        clair_conf = self.read_section("General")
        clair = ClairRequests(**clair_conf)
        result = {}

        for plugin, conf in plugins.items():
            try:
                self.logger.debug('Lecture du plugin %s' % plugin)
                self.logger.debug('Configuration %s' % conf)

                plugin_class = self._get_class(conf.pop('class'))
                result[plugin] = plugin_class(clair, **conf)
            except (ValueError, KeyError):
                self.logger.error("Impossible de lire le plugin %s" % plugin)

        return result

    @staticmethod
    def _get_class(kls):
        """
        Fonction permettant d'instancier une classe à partir d'une String

        :param kls: nom de la classe à importer
        :return: la classe désirée
        """
        mod, _, cls = kls.rpartition('.')

        # Import du module
        mod = importlib.import_module(mod)

        return getattr(mod, cls)
