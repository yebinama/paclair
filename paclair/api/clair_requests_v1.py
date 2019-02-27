# -*- coding: utf-8 -*-

from paclair.api.abstract_clair_requests import AbstractClairRequests
from paclair.struct import InsensitiveCaseDict
from bottle import template


class ClairRequestsV1(AbstractClairRequests):
    """
    Request Clair helper
    """

    _CLAIR_ANALYZE_URI = "/v1/layers/{}?features&vulnerabilities"
    _CLAIR_POST_URI = "/v1/layers"
    _CLAIR_DELETE_URI = "/v1/layers/{}"

    def get_ancestry_json(self, ancestry):
        """
        Analyse an ancestry

        :param ancestry: ancestry (name) to analyse
        :return: json
        """
        return self.get_layer(ancestry)

    def post_ancestry(self, ancestry):
        """
        Post ancestry to Clair

        :param ancestry: ancestry to push
        """
        additional_data = {}
        for layer in ancestry.layers:
            if layer.headers is not None:
                additional_data['Headers'] = layer.headers
            data = self.to_clair_post_data(layer.name, layer.path, ancestry.clair_format, **additional_data)
            self.post_layer(data)
            additional_data = {'ParentName': layer.name}

    def delete_ancestry(self, ancestry):
        """
        Delete ancestry from Clair

        :param ancestry: ancestry to delete
        """
        for layer in ancestry.layers[::-1]:
            self.delete_layer(layer.name)

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
        :param clair_format: Clair format
        :params kwargs: additional params
        :return: json to post to Clair
        """
        data = {"Layer": {"Name": name, "Path": path, "Format": clair_format}}
        data["Layer"].update(kwargs)
        return data

    def _iter_features(self, clair_json):
        for feature in clair_json.get("Layer", {}).get("Features", {}):
            yield InsensitiveCaseDict(feature)

    def get_ancestry_html(self, ancestry):
        clair_info = []
        for feature in self._iter_features(self.get_ancestry_json(ancestry)):
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
                if vuln.get("Name") not in self.whitelist:
                    clair_info.append({"ID": len(clair_info),
                                       "CVE": vuln.get("Name"),
                                       "SEVERITY": vuln.get("Severity"),
                                       "PACKAGE": feature.get("Name"),
                                       "CURRENT": feature.get("Version"),
                                       "FIXED": vuln.get("FixedBy", ""),
                                       "INTRODUCED": feature.get("AddedBy"),
                                       "DESCRIPTION": vuln.get("Description"),
                                       "LINK": vuln.get("Link"),
                                       "VECTORS": cvss_vector,
                                       "SCORE": cvss.get("Score")})
        return template(self.html_template, info=clair_info)
