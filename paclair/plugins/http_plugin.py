# -*- coding: utf-8 -*-
import requests

from paclair.plugins.abstract_plugin import AbstractPlugin
from paclair.exceptions import ResourceNotFoundException


class HttpPlugin(AbstractPlugin):
    """
    Http plugin
    """

    def __init__(self, clair, clair_format, base_url, verify):
        """
        Constructor

        :param clair: ClairRequest object
        :param clair_format: Clair format
        :param base_url: base url
        :param verify: request verify certificate
        """
        super().__init__(clair, clair_format)
        self.base_url = base_url
        self.verify = verify

    @staticmethod
    def _clean_name(name):
        """
        Delete extension and path

        :param name: the name to clean
        :return:
        """
        # Delete ext
        if name.endswith('.tar.gz'):
            name = name[:-7]
        elif name.endswith('.tgz'):
            name = name[:-4]

        # Delete subpath
        _, _, name = name.rpartition('/')
        return name

    def push(self, name):
        path = "{}/{}".format(self.base_url, name)
        result = requests.head(path, verify=self.verify)
        if result.status_code != requests.codes.ok:
            raise ResourceNotFoundException("{} not found".format(name))

        data = self.clair.to_clair_post_data(self._clean_name(name), path, self.clair_format)
        self.clair.post_layer(data)

    def analyse(self, name):
        return super().analyse(self._clean_name(name))