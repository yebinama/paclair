# -*- coding: utf-8 -*-

from paclair.api.abstract_clair_requests import AbstractClairRequests


class ClairRequestsV3(AbstractClairRequests):
    """
    Request Clair helper
    """

    _CLAIR_ANALYZE_URI = "/ancestry/{}?with_vulnerabilities&with_features"
    _CLAIR_POST_URI = "/ancestry"
    #_CLAIR_DELETE_URI = "/v1/ancestry/{}"

    def post_ancestry(self, ancestry):
        """
        Post ancestry to Clair

        :param ancestry: ancestry to push
        """
        return self._request('POST', self._CLAIR_POST_URI, json=ancestry.to_json())

    def get_ancestry(self, ancestry):
        """
        Analyse an ancestry

        :param ancestry: ancestry (name) to analyse
        :return: json
        """
        response = self._request('GET', self._CLAIR_ANALYZE_URI.format(ancestry))
        return response.json()