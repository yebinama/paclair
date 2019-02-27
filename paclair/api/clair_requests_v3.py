# -*- coding: utf-8 -*-

from paclair.api.abstract_clair_requests import AbstractClairRequests
from paclair.exceptions import PaclairException
from paclair.struct import InsensitiveCaseDict
from bottle import template


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
        for feature in clair_json.get("ancestry", {}).get("layers", {}):
            yield InsensitiveCaseDict(feature)


    def get_ancestry_html(self, ancestry):
        clair_info = []
        for layer in self._iter_features(self.get_ancestry_json(ancestry)):
            for feature in layer.get("detected_features", {}):
                feature = InsensitiveCaseDict(feature)
                for vuln in feature.get("vulnerabilities", {}):
                    vuln = InsensitiveCaseDict(vuln)
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
                                       "FIXED": vuln.get("fixed_by", ""),
                                       "INTRODUCED": layer.get("layer").get("hash"),
                                       "DESCRIPTION": vuln.get("Description"),
                                       "LINK": vuln.get("Link"),
                                       "VECTORS": cvss_vector,
                                       "SCORE": cvss.get("Score")})
        return template(self.html_template, info=clair_info)
