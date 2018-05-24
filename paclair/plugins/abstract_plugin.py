# -*- coding: utf-8 -*-

"""
Plugin de base
"""

from abc import ABCMeta, abstractmethod
from paclair.logged_object import LoggedObject


class AbstractPlugin(LoggedObject):
    """
    Base Plugin
    """
    __metaclass__ = ABCMeta


    def __init__(self, clair, clair_format):
        """
        Constructor

        :param clair_format: Clair format
        :param clair: ClairRequests object
        """
        super().__init__()
        self.clair_format = clair_format
        self.clair = clair

    def analyse(self, name, statistics=False):
        """
        Analyse a resource

        :param name: resource to analyse
        :param statistics: only return statistics
        :return: json from clair
        """
        return self.clair.get_ancestry(name, statistics)

    def delete(self, name):
        """
        Delete a resource

        :param name: resource's name
        """
        return self.clair.delete_ancestry(self.create_ancestry(name))

    def push(self, name):
        """
        Push to Clair

        :param name: resource's name
        """
        return self.clair.post_ancestry(self.create_ancestry(name))

    @abstractmethod
    def create_ancestry(self, name):
        """
        Create ancestry associated with this plugin

        :param name: name
        :return: Ancestry object
        """
        raise NotImplementedError("Implement in sub classes")
