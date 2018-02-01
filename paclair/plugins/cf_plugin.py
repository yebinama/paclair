# -*- coding: utf-8 -*-
import requests

from paclair.plugins.abstract_plugin import AbstractPlugin
from paclair.exceptions import ResourceNotFoundException


class CfPlugin(AbstractPlugin):
    """
    Plugin pour Cflinuxfs2
    """

    def __init__(self, clair, base_url, verify):
        """
        Constructeur

        :param clair: objet ClairRequest
        :param base_url: chemin pour construire l'url artifactory
        :param verify: certificats ssl pour artifactory
        """
        super().__init__(clair, "cflinuxfs")
        self.base_url = base_url
        self.verify = verify
        

    def push(self, name):
      rootfs_path = "{}/{}".format(self.base_url, name)
      result = requests.head(rootfs_path, verify = self.verify)
      if result.status_code != requests.codes.ok:
          raise ResourceNotFoundException("{} not found".format(name))

      data = self.clair.to_clair_post_data(name, rootfs_path, self.clair_format)
      self.clair.post_layer(data)
