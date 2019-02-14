# -*- coding: utf-8 -*-

import re

from paclair import DOCKER_HUB_DOMAIN
from paclair import REGEX
from paclair.ancestries.docker import DockerAncestry
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
        self._domain_pattern = re.compile(r'(?P<repository>[a-zA-Z0-9-]*)\.(?P<domain>[a-zA-Z0-9-.]*)[:0-9]*$')

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

    def create_ancestry(self, name):
        return DockerAncestry(self.create_docker_image(name))

    def analyse(self, name, output=None):
        ancestry = self.create_ancestry(name)
        return super().analyse(ancestry.name, output)
