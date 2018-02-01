# -*- coding: utf-8 -*-

"""
Plugin de base
"""

from abc import ABCMeta, abstractmethod
from paclair.logged_object import LoggedObject


class AbstractPlugin(LoggedObject):
    """
    Plugin de base
    """
    __metaclass__ = ABCMeta


    def __init__(self, clair, clair_format):
        """
        Constructeur

        :param clair_format: format de la ressource à analyser
        :param clair: objet ClairRequests
        """
        super().__init__()
        self.clair_format = clair_format
        self.clair = clair

    def analyse(self, name):
        """
        Requête Clair pour analyser name

        :param name: nom de la ressource à analyser
        :return: json renvoyé par clair
        """
        return self.clair.get_layer(name)

    def delete(self, name):
        """
        Supprime l'entrée name de la base Clair

        :param name: nom de la ressource à supprimer
        """
        self.clair.delete_layer(name)

    @abstractmethod
    def push(self, name):
        """
        Pousse dans Clair la ressource name
        :param name: nom de la ressource
        """
        raise NotImplementedError("A implémenter dans les classes fille")
