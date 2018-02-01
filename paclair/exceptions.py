# -*- coding: utf-8 -*-

"""
Paclair exceptions
"""


class PaclairException(Exception):
    """
    Error base class
    """
    pass


class ClairConnectionError(PaclairException):
    """
    Erreur liée à la connexion à l'api de Clair
    """
    def __init__(self, response):
        """
        Constructeur
        :param response: requests.response
        """
        super().__init__(response.reason)
        self.response = response


class ResourceNotFoundException(PaclairException):
    """
    Ressource non trouvée dans le dépôt
    """
    pass


class PluginNotFoundException(PaclairException):
    """
    Plugin inconnu
    """
    pass


class RegistryAccessError(PaclairException):
    """
    Erreur d'accès à la registry
    """
    pass
