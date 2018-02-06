# -*- coding: utf-8 -*-

"""
Paclair exceptions
"""


class PaclairException(Exception):
    """
    Error base class
    """
    pass


class ConfigurationError(PaclairException):
    """
    Error reading configuration file
    """
    pass


class ClairConnectionError(PaclairException):
    """
    Error reaching Clair
    """
    def __init__(self, response):
        """
        Constructor

        :param response: requests.response
        """
        super().__init__(response.reason)
        self.response = response


class ResourceNotFoundException(PaclairException):
    """
    Resource not found
    """
    pass


class PluginNotFoundException(PaclairException):
    """
    Unknown plugin
    """
    pass


class RegistryAccessError(PaclairException):
    """
    Error reaching registry
    """
    pass
