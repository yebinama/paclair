# -*- coding: utf-8 -*-

"""
Docker_image module
"""

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
        self.logger.debug("INITCLASS:REPOSITORY:{repository}".format(repository=self.repository))

    @property
    def token(self):
        """
        Token for this image

        :return:
        """
        return self.registry.get_token(self)

    @property
    def manifest(self):
        """
        Get manifest

        :returns dict:
        """
        return self.registry.get_manifest(self)

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
