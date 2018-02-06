# -*- coding: utf-8 -*-
import requests

from paclair.plugins.abstract_plugin import AbstractPlugin
from paclair.exceptions import ResourceNotFoundException


class CfPlugin(AbstractPlugin):
    """
    Cflinuxfs2 plugin
    """

    def __init__(self, clair, base_url, verify):
        """
        Constructor

        :param clair: ClairRequest object
        :param base_url: base url
        :param verify: request verify certificate
        """
        super().__init__(clair, "cflinuxfs")
        self.base_url = base_url
        self.verify = verify

    def push(self, name):
        rootfs_path = "{}/{}".format(self.base_url, name)
        result = requests.head(rootfs_path, verify=self.verify)
        if result.status_code != requests.codes.ok:
            raise ResourceNotFoundException("{} not found".format(name))

        data = self.clair.to_clair_post_data(name, rootfs_path, self.clair_format)
        self.clair.post_layer(data)
