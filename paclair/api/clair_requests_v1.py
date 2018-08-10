# -*- coding: utf-8 -*-

from paclair.api.abstract_clair_requests import AbstractClairRequests


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

    def get_ancestry_statistics(self, ancestry):
        """
        Get statistics for ancestry

        :param ancestry: ancestry (name) to analyse
        :return: statistics (dict)
        """
        clair_json = self.get_layer(ancestry)
        result = {}
        for feature in clair_json.get('Layer', {}).get('Features', []):
            for vuln in feature.get("Vulnerabilities", []):
                if "FixedBy" in vuln:
                    result[vuln["Severity"]] = result.setdefault(vuln["Severity"], 0) + 1
        return result

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

    def _clair_to_html_template(self, clair_json):
        """
        Convert clair_json into a list for the bottle template

        :param clair_json: json to convert
        :return: list
        """
        return []

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
