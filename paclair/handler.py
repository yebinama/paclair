# -*- coding: utf-8 -*-
import json

from paclair.exceptions import PluginNotFoundException
from paclair.logged_object import LoggedObject
from paclair.config_reader import ConfigReader
from paclair.exceptions import ConfigurationError
from yaml import YAMLError


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
        self._config_reader = ConfigReader(config_file)
        try:
            self._plugins = self._config_reader.read_plugins('Plugins')
        except YAMLError:
            raise ConfigurationError("Incorrect configuration file")

    def _check_plugin(self, plugin):
        """
        Check if plugin is available

        :param plugin: plugin to check
        :raises PluginNotFoundException: if not found
        """
        if plugin not in self._plugins:
            raise PluginNotFoundException("Plugin {} is unknown".format(plugin))

    def analyse(self, plugin, name, delete=False, output=None):
        """
        Analyse a layer

        :param plugin: plugin's name
        :param name: resource to analyse
        :param delete: delete after analyse
        :param output: change default output
        :return: string
        :raises ResourceNotFoundException: if layer not found
        :raise ClairConnectionError: if an error occurs requesting Clair
        """
        self._check_plugin(plugin)

        self.logger.debug("Analysing {}".format(name))
        result = self._plugins[plugin].analyse(name, output)

        if output == "stats":
            result = '\n'.join(("{}: {}".format(k, v) for k, v in result.items()))
        elif output != "html":
            result = json.dumps(result)

        if delete:
            self.logger.debug("Deleting  {}".format(name))
            self._plugins[plugin].delete(name)
        return result

    def push(self, plugin, name):
        """
        Push layer to Clair

        :param plugin: plugin's name
        :param name: resource to push
        :return:
        """
        self._check_plugin(plugin)

        self.logger.debug("Push {} with plugin {}".format(name, plugin))
        self._plugins[plugin].push(name)

    def delete(self, plugin, name):
        """
        Delete image from Clair

        :param plugin: plugin's name
        :param name: resource to delete
        :raises ResourceNotFoundException: if layer not found
        :raise ClairConnectionError: if an error occurs requesting Clair
        """
        self._check_plugin(plugin)

        self.logger.debug("Delete {} with plugin {}".format(name, plugin))
        self._plugins[plugin].delete(name)
