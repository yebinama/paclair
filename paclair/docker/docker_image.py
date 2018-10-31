# -*- coding: utf-8 -*-

"""
Docker_image module
"""

import hashlib
from paclair.logged_object import LoggedObject


class DockerImage(LoggedObject):
    """
    A Docker Image
    """

    def __init__(self, name, registry, repository="", tag='latest'):
        """
        Constructor

        :param name: docker image's name (ex: ubuntu, centos, ...)
        :param repository: repository's name
        :param tag: image's tag
        :param registry: Docker registry
        """
        super(DockerImage, self).__init__()
        self.name = name
        self.logger.debug("INITCLASS:NAMEIMAGE:{name}".format(name=self.name))
        self.tag = tag
        self.logger.debug("INITCLASS:TAG:{tag}".format(tag=self.tag))
        self.registry = registry
        self.repository = repository
        self._manifest = None
        self._sha = None
        self.logger.debug("INITCLASS:REPOSITORY:{repository}".format(repository=self.repository))

    @property
    def authorization(self):
        """
        Token for this image

        :return:
        """
        return self.registry.get_authorization(self)

    @property
    def sha(self):
        """
        Sha256 of the layers list (used for clair layer_name)

        :return: sha256
        """
        if self._sha is None:
            m = hashlib.sha256(''.join(self.get_layers()).encode('utf-8'))
            self._sha = m.hexdigest()
        return self._sha

    @property
    def short_sha(self):
        """
        Sha short version (12 characters)
        """
        return self.sha[:12]

    @property
    def manifest(self):
        """
        Get manifest

        :returns dict:
        """
        if self._manifest is None:
            self._manifest = self.registry.get_manifest(self)
        return self._manifest

    def get_layers(self):
        """
        Get ordered layers

        :returns list:
        """
        manifest = self.manifest
        layers = []
        # Check Version
        if manifest["schemaVersion"] == 2:
            fs_layers = manifest['layers']
            digest_field = 'digest'
        else:
            fs_layers = manifest.get('fsLayers', [])[::-1]
            digest_field = 'blobSum'

        # List layers
        for fs_layer in fs_layers:
            if fs_layer[digest_field] not in layers:
                layers.append(fs_layer[digest_field])
        return layers
