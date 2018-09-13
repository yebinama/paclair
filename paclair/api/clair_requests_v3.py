# -*- coding: utf-8 -*-

from paclair.api.abstract_clair_requests import AbstractClairRequests
from paclair.exceptions import PaclairException
from paclair.struct import InsensitiveCaseDict


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

    def delete_ancestry(self, ancestry):
        """
        Delete ancestry from Clair

        :param ancestry: ancestry to delete
        """
        raise PaclairException("Delete is not available for V3 api")

    def _iter_features(self, clair_json):
        for feature in clair_json.get("ancestry", {}).get("features", {}):
            yield InsensitiveCaseDict(feature)
