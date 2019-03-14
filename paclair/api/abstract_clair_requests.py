# -*- coding: utf-8 -*-
import json
from abc import ABCMeta, abstractmethod
from pkg_resources import resource_filename
from bottle import template

import requests

from paclair.exceptions import ResourceNotFoundException, ClairConnectionError
from paclair.logged_object import LoggedObject


class AbstractClairRequests(LoggedObject):
    """
    Base Api
    """
    __metaclass__ = ABCMeta

    def __init__(self, clair_url, cve_whitelist=None, verify=True, html_template=None):
        """
        Constructor

        :param clair_url: Clair api URL
        :param cve_whitelist: cvs to whitelist
        :param verify: request verify certificate
        :param html_template: html template
        """
        super().__init__()
        self.url = clair_url
        self.whitelist = cve_whitelist or []
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
        :return: choosed output
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
        result = {}
        for vuln, feature, _ in self._iter_vulnerabilities(self.get_ancestry_json(ancestry)):
            if ("fixedBy" in vuln) or ("fixed_by" in vuln):
                result[vuln["severity"]] = result.setdefault(vuln["severity"], 0) + 1
        return result

    def get_ancestry_html(self, ancestry):
        """
        Get html output for ancestry

        :param ancestry: ancestry (name) to analyse
        :return: html
        """
        clair_info = []
        for vuln, feature, added_by in self._iter_vulnerabilities(self.get_ancestry_json(ancestry)):
            # metadata is a string in v3 and dict in v1
            metadata = vuln.get("Metadata", {})
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except ValueError:
                    metadata = {}
            cvss = metadata.get('NVD', {}).get("CVSSv2", {})
            cvss_vector = self.split_vectors(cvss.get('Vectors', ""))
            clair_info.append({"ID": len(clair_info),
                               "CVE": vuln.get("Name"),
                               "SEVERITY": vuln.get("Severity"),
                               "PACKAGE": feature.get("Name"),
                               "CURRENT": feature.get("Version"),
                               "FIXED": vuln.get("fixed_by", None) or vuln.get("FixedBy", ""),
                               "INTRODUCED": added_by,
                               "DESCRIPTION": vuln.get("Description"),
                               "LINK": vuln.get("Link"),
                               "VECTORS": cvss_vector,
                               "SCORE": cvss.get("Score")})
        return template(self.html_template, info=clair_info)

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

    @abstractmethod
    def _iter_vulnerabilities(self, clair_json):
        """
        Iterate over (vulnerability, feature, introduced_by) from clair_json via CaseInsensitiveDict

        :param clair_json: json to iterate overs
        """
        raise NotImplementedError("Implement in sub classes")

    @staticmethod
    def split_vectors(vectors_str):
        """
        Convert nvd metadata ("AV:N/AC:L/Au:N/C:N/I:N") into a dict

        :param vectors_str: string like "AV:N/AC:L/Au:N/C:N/I:N"
        :return: dict
        """
        npc = {'N': 'None', 'P': 'Partial', 'C': 'Complete'}
        vectors = {'AV': ('Access Vector', {'L': 'Local', 'A': 'Adjacent Network', 'N': 'Network'}),
                   'AC': ('Access Complexity', {'H': 'High', 'M': 'Medium', 'L': 'Low'}),
                   'Au': ('Authentication', {'S': 'Single', 'M': 'Multiple', 'N': 'None'}),
                   'C': ('Confidentiality impact', npc),
                   'I': ('Integrity impact', npc),
                   'A': ('Availability impact', npc)}
        try:
            dict_vectors = dict((vector.split(':') for vector in vectors_str.split('/')))
        except ValueError:
            dict_vectors = {}

        return {v[0]: v[1].get(dict_vectors.get(metric), "") for metric, v in vectors.items()}
