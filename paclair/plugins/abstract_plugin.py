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

    def analyse(self, name):
        """
        Analyse a resource

        :param name: resource to analyse
        :return: json from clair
        """
        return self.clair.get_layer(name)

    def delete(self, name):
        """
        Delete a resource

        :param name: resource's name
        """
        self.clair.delete_layer(name)

    @abstractmethod
    def push(self, name):
        """
        Push to Clair

        :param name: resource's name
        """
        raise NotImplementedError("Implement in sub classes")
