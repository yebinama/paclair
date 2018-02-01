# -*- coding: utf-8 -*-

from .logged_object import LoggedObject
from .exceptions import ClairConnectionError, ResourceNotFoundException
import requests


class ClairRequests(LoggedObject):
    """
    Objet de connexion à Clair
    """

    _CLAIR_ANALYZE_URI = "/v1/layers/{}?features&vulnerabilities"
    _CLAIR_POST_URI = "/v1/layers"
    _CLAIR_DELETE_URI = "/v1/layers/{}"

    def __init__(self, clair_url, verify=True):
        """
        Constructeur

        :param clair_url: URL de l'api de Clair
        :param verify: request verify certificate
        """
        super().__init__()
        self.url = clair_url
        self.verify = verify

    def _request(self, method, uri, **kwargs):
        """
        Exécution du verbe http method sur l'uri uri de Clair

        :param method: verbe http
        :param uri: uri à appeler
        :param kwargs: paramètres supplémentaires
        :return : la réponse du serveur
        """
        url = self.url + uri
        self.logger.debug("Requesting {} on {}".format(method, url))
        response = requests.request(method, url, verify=self.verify, **kwargs)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            self.logger.error("Bad http code {} requesting Clair".format(response.status_code))
            if response.reason == "Not Found":
                raise ResourceNotFoundException("Resource not found")
            raise ClairConnectionError(response)
        return response

    def get_layer(self, name):
        """
        Retourne l'analyse du layer name

        :param name: nom du layer
        :return: json
        """
        response = self._request('GET', self._CLAIR_ANALYZE_URI.format(name))
        return response.json()

    def post_layer(self, data):
        """
        POST sur l'api layer de Clair

        :param data: dictionnaire à envoyer à Clair en post sur la collection Layer
        """
        self.logger.debug("Sending to Clair: {}".format(data))
        return self._request('POST', self._CLAIR_POST_URI, json=data)

    def delete_layer(self, name):
        """
        Delete le layer name

        :param name: nom du layer
        """
        return self._request('DELETE', self._CLAIR_DELETE_URI.format(name))

    @staticmethod
    def to_clair_post_data(name, path, clair_format, **kwargs):
        """
        Helper

        :param name: nom de la ressource
        :param path: path de la ressource
        :param format: format Clair
        :params kwargs: arguments supplémentaires
        :return: json à envoyer à clair pour post
        """
        data = {"Layer": {"Name": name, "Path": path, "Format": clair_format}}
        data["Layer"].update(kwargs)
        return data
