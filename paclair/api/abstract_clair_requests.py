# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from bottle import template
from pkg_resources import resource_filename

import requests

from paclair.exceptions import ResourceNotFoundException, ClairConnectionError
from paclair.logged_object import LoggedObject
from paclair.struct import InsensitiveCaseDict


class AbstractClairRequests(LoggedObject):
    """
    Base Api
    """
    __metaclass__ = ABCMeta

    def __init__(self, clair_url, verify=True, html_template=None):
        """
        Constructor

        :param clair_url: Clair api URL
        :param verify: request verify certificate
        :param html_template: html template
        """
        super().__init__()
        self.url = clair_url
        self.verify = verify
        self.html_template = html_template or resource_filename(__name__, 'template/report.tpl')

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

    def get_ancestry(self, ancestry, output=None):
        """
        Analyse an ancestry

        :param ancestry: ancestry (name) to analyse
        :param output: change default output (choose between stats and html)
        :return: choosed outpu
        """
        if output == "stats":
            return self.get_ancestry_statistics(ancestry)
        elif output == "html":
            return self.get_ancestry_html(ancestry)
        else:
            return self.get_ancestry_json(ancestry)

    @abstractmethod
    def get_ancestry_json(self, ancestry):
        """
        Get json output for ancestry

        :param ancestry: ancestry (name) to analyse
        :return: json
        """
        raise NotImplementedError("Implement in sub classes")

    def get_ancestry_statistics(self, ancestry):
        """
        Get statistics for ancestry

        :param ancestry: ancestry (name) to analyse
        :return: statistics (dict)
        """
        clair_json = self.get_ancestry_json(ancestry)
        result = {}
        for feature in self._iter_features(clair_json):
            for vuln in feature.get("vulnerabilities", []):
                vuln = InsensitiveCaseDict(vuln)
                if "fixedBy" in vuln:
                    result[vuln["severity"]] = result.setdefault(vuln["severity"], 0) + 1
        return result

    @abstractmethod
    def get_ancestry_html(self, ancestry):
        """
        Get html output for ancestry

        :param ancestry: ancestry (name) to analyse
        :return: html
        """
        clair_info = self._clair_to_html_template(self.get_ancestry_json(ancestry))
        return template(self.html_template, info=clair_info)

    @abstractmethod
    def _clair_to_html_template(self, clair_json):
        """
        Convert clair_json into a list for the bottle template

        :param clair_json: json to convert
        :return: list
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

    @staticmethod
    def split_vectors(vectors):
        """
        Convert nvd metadata ("AV:N/AC:L/Au:N/C:N/I:N") into a dict

        :param vectors: string like "AV:N/AC:L/Au:N/C:N/I:N"
        :return: dict
        """
        NPC = {'N': 'None', 'P': 'Partial', 'C': 'Complete'}
        VECTORS = {'AV': ('Access Vector', {'L': 'Local', 'A': 'Adjacent Network', 'N': 'Network'}),
                   'AC': ('Access Complexity', {'H': 'High', 'M': 'Medium', 'L': 'Low'}),
                   'Au': ('Authentication', {'S': 'Single', 'M': 'Multiple', 'N': 'None'}),
                   'C': ('Confidentiality impact', NPC),
                   'I': ('Integrity impact', NPC),
                   'A': ('Availability impact', NPC)}
        try:
            dict_vectors = dict((vector.split(':') for vector in vectors.split('/')))
        except ValueError:
            dict_vectors = {}

        return {v[0]: v[1].get(dict_vectors.get(metric), "") for metric, v in VECTORS.items()}

    @abstractmethod
    def _iter_features(self, clair_json):
        """
        Iterate over features from clair_json via CaseInsensitiveDict

        :param clair_json: json to iterate overs
        """
        raise NotImplementedError("Implement in sub classes")