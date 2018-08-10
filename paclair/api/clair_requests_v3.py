# -*- coding: utf-8 -*-

from paclair.api.abstract_clair_requests import AbstractClairRequests
from paclair.exceptions import PaclairException


class ClairRequestsV3(AbstractClairRequests):
    """
    Request Clair helper
    """

    _CLAIR_ANALYZE_URI = "/ancestry/{}?with_vulnerabilities=1&with_features=1"
    _CLAIR_POST_URI = "/ancestry"
    #_CLAIR_DELETE_URI = "/v1/ancestry/{}"

    def post_ancestry(self, ancestry):
        """
        Post ancestry to Clair

        :param ancestry: ancestry to push
        """
        json = ancestry.to_json()
        json['ancestry_name'] = ancestry.name.replace(':', '_')
        return self._request('POST', self._CLAIR_POST_URI, json=json)

    def get_ancestry_json(self, ancestry):
        """
        Analyse an ancestry

        :param ancestry: ancestry (name) to analyse
        :return: json
        """
        response = self._request('GET', self._CLAIR_ANALYZE_URI.format(ancestry.replace(':', '_')))
        return response.json()

    def get_ancestry_statistics(self, ancestry):
        """
        Get statistics for ancestry

        :param ancestry: ancestry (name) to analyse
        :return: statistics (dict)
        """
        clair_json = self.get_ancestry_json(ancestry)
        result = {}
        for feature in clair_json.get('ancestry', {}).get('features', []):
            for vuln in feature.get("vulnerabilities", []):
                if "fixedBy" in vuln:
                    result[vuln["severity"]] = result.setdefault(vuln["severity"], 0) + 1
        return result

    def delete_ancestry(self, ancestry):
        """
        Delete ancestry from Clair

        :param ancestry: ancestry to delete
        """
        raise PaclairException("Delete is not available for V3 api")

    def _clair_to_html_template(self, clair_json):
        """
        Convert clair_json into a list for the bottle template

        :param clair_json: json to convert
        :return: list
        """
        return []