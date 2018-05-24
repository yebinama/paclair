# -*- coding: utf-8 -*-

from paclair.api.abstract_clair_requests import AbstractClairRequests


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

    def get_ancestry(self, ancestry):
        """
        Analyse an ancestry

        :param ancestry: ancestry (name) to analyse
        :param statistics: only return statistics
        :return: json
        """
        response = self._request('GET', self._CLAIR_ANALYZE_URI.format(ancestry.replace(':', '_')))
        return response.json()

    @staticmethod
    def statistics(clair_json):
        """
        Statistics from a json delivered by Clair

        :param clair_json: json delivered by Clair
        """
        result = {}
        for feature in clair_json.get('ancestry', {}).get('features', []):
            for vuln in feature.get("vulnerabilities", []):
                if "fixed_by" in vuln:
                    result[vuln["severity"]] = result.setdefault(vuln["severity"], 0) + 1
        return result