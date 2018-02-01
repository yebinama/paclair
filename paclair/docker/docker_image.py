# -*- coding: utf-8 -*-

"""
Module docker_image
"""

from paclair.logged_object import LoggedObject


class DockerImage(LoggedObject):
    """
    Classe permettant d'exader aux donnees d'une image docker
    """

    def __init__(self, name, registry, repository="", tag='latest'):
        """
        Initialisation

        :param name: nom de l'imade docker (ex: ubuntu, centos, ...)
        :param repository: nom du dépôt
        :param tag: tag de l'image
        :param registry: registry Docker associée
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
        Token pour cette image

        :return:
        """
        return self.registry.get_token(self)

    @property
    def manifest(self):
        """
        Renvoie le manifest de l'image docker en format json

        :returns dict:
        """
        return self.registry.get_manifest(self)

    def get_layers(self):
        """
        Renvoie la liste des layers d'un docker dans l'ordre

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
