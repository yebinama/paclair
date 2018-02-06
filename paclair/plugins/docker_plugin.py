# -*- coding: utf-8 -*-

import re

from paclair import DOCKER_HUB_DOMAIN
from paclair import REGEX
from paclair.docker.docker_image import DockerImage
from paclair.docker.docker_registry import DockerRegistry
from paclair.exceptions import ResourceNotFoundException
from paclair.plugins.abstract_plugin import AbstractPlugin


class DockerPlugin(AbstractPlugin):
    """
    Docker plugin
    """

    def __init__(self, clair, registries=None):
        """
        Constructor

        :param clair: ClairRequests object
        :param registries: registries' configuration {'registry1_domain': {'conf': ...},
                                                      'registry2_domain': {'conf': ...}}
        """
        super().__init__(clair, "Docker")
        registries = registries or {}
        self.__registries = {domain: DockerRegistry(domain, **conf) for domain, conf in registries.items()}
        self.__docker_hub = DockerRegistry(DOCKER_HUB_DOMAIN)
        self._pattern = re.compile(REGEX['domain'] + REGEX['name'] + REGEX['tag'])
        self._domain_pattern = re.compile(r'(?P<repository>[a-zA-Z0-9-]*)\.(?P<domain>[a-zA-Z0-9-.]*)$')

    def create_docker_image(self, name):
        """
        Create docker image

        :param name: image's name
        :return: paclair.docker.DockerImage
        """
        matcher = self._pattern.match(name)
        if not matcher:
            raise ResourceNotFoundException("Incorrect image name: {}".format(name))

        # Base docker image
        if matcher.group("domain") is None:
            return DockerImage("library/" + matcher.group("name"), self.__docker_hub,
                               tag=matcher.group("tag") or 'latest')

        domain_regex_matcher = self._domain_pattern.search(matcher.group("domain") or "")
        # Repo docker
        if domain_regex_matcher is None:
            return DockerImage("{}/{}".format(matcher.group("domain"), matcher.group("name")), self.__docker_hub,
                               tag=matcher.group("tag") or 'latest')

        # Find the registry
        repo = ""
        if domain_regex_matcher.group("domain") in self.__registries:
            registry = self.__registries[domain_regex_matcher.group("domain")]
            repo = domain_regex_matcher.group("repository") or ""
        elif matcher.group("domain") in self.__registries:
            registry = self.__registries[matcher.group("domain")]
        else:
            registry = DockerRegistry(matcher.group("domain"))
        return DockerImage(matcher.group("name"), registry, repo, tag=matcher.group("tag") or 'latest')

    def push(self, name):
        docker_image = self.create_docker_image(name)

        # Additional data
        additional_data = {'Headers': {'Authorization': "Bearer {}".format(docker_image.token)},
                           'ParentName': ""}
        layers = docker_image.get_layers()
        partial_path = docker_image.registry.get_blobs_url(docker_image, '{digest}')

        # Push layers to Clair
        for layer in layers:
            data = self.clair.to_clair_post_data(layer, partial_path.format(digest=layer), self.clair_format,
                                                 **additional_data)
            self.clair.post_layer(data)
            additional_data['ParentName'] = layer

    def analyse(self, name):
        docker_image = self.create_docker_image(name)
        layer_name = docker_image.get_layers()[-1]
        return super().analyse(layer_name)

    def delete(self, name):
        docker_image = self.create_docker_image(name)
        for layer in docker_image.get_layers()[::-1]:
            super().delete(layer)
