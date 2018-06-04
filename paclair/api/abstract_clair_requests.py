# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

import requests

from paclair.exceptions import ResourceNotFoundException, ClairConnectionError
from paclair.logged_object import LoggedObject


class AbstractClairRequests(LoggedObject):
    """
    Base Api
    """
    __metaclass__ = ABCMeta

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

    @abstractmethod
    def get_ancestry(self, ancestry, statistics=False):
        """
        Analyse an ancestry

        :param ancestry: ancestry (name) to analyse
        :param statistics: only return statistics
        :return: json
        """
        raise NotImplementedError("Implement in sub classes")

    @abstractmethod
    def post_ancestry(self, ancestry):
        """
        Post ancestry to Clair

        :param ancestry: ancestry to push
        """
        raise NotImplementedError("Implement in sub classes")

    @abstractmethod
    def delete_ancestry(self, ancestry):
        """
        Delete ancestry from Clair

        :param ancestry: ancestry to delete
        """
        raise NotImplementedError("Implement in sub classes")