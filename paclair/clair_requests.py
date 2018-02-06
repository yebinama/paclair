# -*- coding: utf-8 -*-

from paclair.logged_object import LoggedObject
from paclair.exceptions import ClairConnectionError, ResourceNotFoundException
import requests


class ClairRequests(LoggedObject):
    """
    Request Clair helper
    """

    _CLAIR_ANALYZE_URI = "/v1/layers/{}?features&vulnerabilities"
    _CLAIR_POST_URI = "/v1/layers"
    _CLAIR_DELETE_URI = "/v1/layers/{}"

    def __init__(self, clair_url, verify=True):
        """
        Constructor

        :param clair_url: Clair api URL
        :param verify: request verify certificate
        """
        super().__init__()
        self.url = clair_url
        self.verify = verify

    def _request(self, method, uri, **kwargs):
        """
        Execute http method on uri

        :param method: http verb
        :param uri: uri to request
        :param kwargs: other params
        :return : server's response
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
        Analyse a layer

        :param name: layer's name
        :return: json
        """
        response = self._request('GET', self._CLAIR_ANALYZE_URI.format(name))
        return response.json()

    def post_layer(self, data):
        """
        POST layer to Clair

        :param data: data to send to clair
        """
        self.logger.debug("Sending to Clair: {}".format(data))
        return self._request('POST', self._CLAIR_POST_URI, json=data)

    def delete_layer(self, name):
        """
        Delete layer

        :param name: layer's name
        """
        return self._request('DELETE', self._CLAIR_DELETE_URI.format(name))

    @staticmethod
    def to_clair_post_data(name, path, clair_format, **kwargs):
        """
        Helper

        :param name: resource's name
        :param path: resource path
        :param format: Clair format
        :params kwargs: additional params
        :return: json to post to Clair
        """
        data = {"Layer": {"Name": name, "Path": path, "Format": clair_format}}
        data["Layer"].update(kwargs)
        return data
