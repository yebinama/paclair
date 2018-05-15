# -*- coding: utf-8 -*-
from paclair.api.clair_requests_v1 import ClairRequestsV1
from paclair.api.clair_requests_v3 import ClairRequestsV3
from paclair.logged_object import LoggedObject
from paclair.exceptions import ConfigurationError
import importlib
import yaml


class ConfigReader(LoggedObject):
    """
    Read configuration file
    """

    def __init__(self, filename):
        """
        Constructor

        :param filename: configuration filename
        """
        super(ConfigReader, self).__init__()
        self.filename = filename

    def read_section(self, section):
        """
        Read section's configuration

        :param section: section's name
        """
        with open(self.filename, 'r') as f:
            # Load
            self.logger.debug("Reading section %s in file %s", section, self.filename)
            conf = yaml.safe_load(f)

            # Check structure
            if section not in conf:
                self.logger.error("No section %s in configuration file", section)
                return {}
            return conf[section]

    def read_plugins(self, plugin_section="Plugins"):
        """
        Read plugins

        :param plugin_section: plugins' section's name
        """
        plugins = self.read_section(plugin_section)
        clair_conf = self.read_section("General")
        if not clair_conf:
            raise ConfigurationError("Can't read Clair's configuration")

        # Read clair api class
        clair_api_version = clair_conf.pop("clair_api_version", 1)
        if clair_api_version == 3:
            clair = ClairRequestsV3(**clair_conf)
        else:
            clair = ClairRequestsV1(**clair_conf)

        result = {}
        for plugin, conf in plugins.items():
            try:
                self.logger.debug('Reading plugin %s', plugin)
                self.logger.debug('Configuration %s', conf)

                plugin_class = self._get_class(conf.pop('class'))
                result[plugin] = plugin_class(clair, **conf)
            except (ValueError, KeyError):
                self.logger.error("Can't read plugin %s", plugin)

        return result

    @staticmethod
    def _get_class(kls):
        """
        Instantiate a class from a String

        :param kls: class name
        """
        mod, _, cls = kls.rpartition('.')

        # Import module
        mod = importlib.import_module(mod)

        return getattr(mod, cls)
