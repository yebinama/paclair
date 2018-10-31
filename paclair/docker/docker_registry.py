# -*- coding: utf-8 -*-

"""
Docker_registry module
"""

import requests
import re
from paclair.logged_object import LoggedObject
from paclair.exceptions import RegistryAccessError


class DockerRegistry(LoggedObject):
    """
    A Docker Registry
    """
    BASE_API_URL = '{registry.protocol}://{registry.domain}{registry.api_prefix}'
    MANIFEST_URI = '/v2/{image.name}/manifests/{image.tag}'
    BLOBS_URI = '/v2/{image.name}/blobs/{digest}'
    TOKEN_REGEX = "Bearer realm=\"(?P<realm>.*)\",service=\"(?P<service>.*)\""

    def __init__(self, domain, token_url=None, api_prefix="", protocol="https", auth=None, verify=True, token=None, token_type='Bearer'):
        """
        Constructor

        :param api_prefix: api prefix
        :param domain: domain registry (ex : registry.hub.docker.com)
        :param token_url: token url (ex : https://auth.docker.io)
        :param auth: (user, password)
        :param verify: requests ssl verify
        """
        super().__init__()
        self.domain = domain
        self.logger.debug("INITCLASS:DOMAIN:{domain}".format(domain=self.domain))
        self.api_prefix = api_prefix
        self.logger.debug("INITCLASS:API_PREFIX:{}".format(self.api_prefix))
        self.protocol = protocol
        self.logger.debug("INITCLASS:API_PROTOCOL:{}".format(self.protocol))
        self.auth = tuple(auth or [])
        self.verify = verify
        self.logger.debug("INITCLASS:API_VERIFY:{}".format(self.verify))
        self.__token_url = token_url
        self.logger.debug("INITCLASS:TOKEN_URL:{}".format(self.__token_url))
        self.__token = token
        self.logger.debug("INITCLASS:TOKEN:{}".format(self.__token))
        self.__token_type = token_type
        self.logger.debug("INITCLASS:TOKEN_TYPE:{}".format(self.__token_type))

    @property
    def token_url(self):
        """
        Find token url if not defined
        """
        if self.__token_url is None:
            url = self.BASE_API_URL.format(registry=self) + "/v2/"
            self.logger.debug("REQUEST_BASE_API_URL_FOR_TOKEN_ENDPOINT:URL:{}".format(url))

            response = requests.get(url, verify=self.verify)
            if not "www-authenticate" in response.headers:
                self.logger.error("REQUEST_TOKEN:HTTPCODEERROR:{}".format(response.status_code))
                raise RegistryAccessError("Error access to : {} \nCode Error : {}".format(url, response.status_code))

            # Find realm and service
            matcher = re.match(self.TOKEN_REGEX, response.headers["www-authenticate"])
            if matcher is None:
                raise RegistryAccessError("Can't find token url")
            self.__token_url = "{}?client_id=paclair&service={}&scope=repository:{}:pull".format(
                matcher.group("realm"), matcher.group("service"), "{image.name}")
            self.logger.debug("TOKEN_URL:{}".format(self.__token_url))

        return self.__token_url

    def get_base_api_url(self, docker_image):
        """
        Get base api url

        :param docker_image: paclair.docker.DockerImage
        :return:
        """
        # Format for registry
        url = self.BASE_API_URL.format(registry=self)
        # Format if image's parameters are required ex: prefix_api=/api/{image.repo}
        return url.format(image=docker_image)

    def get_manifest_url(self, docker_image):
        """
        Manifest's url

        :param docker_image: paclair.docker.DockerImage
        :return: manifest's url
        """
        url = self.get_base_api_url(docker_image) + self.MANIFEST_URI.format(image=docker_image)
        return url

    def get_blobs_url(self, docker_image, digest):
        """
        Blobs's url

        :param docker_image: paclair.docker.DockerImage
        :param digest: digest
        :return: blobs's url
        """
        url = self.get_base_api_url(docker_image) + self.BLOBS_URI.format(image=docker_image, digest=digest)
        return url

    def get_authorization(self, docker_image):
        """
        Get token

        :param docker_image: paclair.docker.DockerImage
        :returns str:
        """
        if self.__token is None:
            # Define url
            url = self.token_url.format(registry=self, image=docker_image)
            self.logger.debug("REQUEST_TOKEN:URL:{url}".format(url=url))

            # Get token
            resp = requests.get(url, verify=self.verify, auth=self.auth)
            if not resp.ok:
                self.logger.error("REQUEST_TOKEN:HTTPCODEERROR:{}".format(resp.status_code))
                raise RegistryAccessError("Error access to : {url} \nCode Error : {status_code}".format(
                    url=url, status_code=resp.status_code))

            token = resp.json()['token']
            self.logger.debug("TOKEN:{token}".format(token=token))
        else:
            token = self.__token
        return "{token_type} {token}".format(token_type=self.__token_type, token=token)

    def get_manifest(self, docker_image):
        """
        Get manifest

        :param docker_image: paclair.docker.DockerImage
        :return: manifest
        """
        # Define url
        url = self.get_manifest_url(docker_image)
        self.logger.debug("REQUESTMANIFESTS:{url}".format(url=url))

        # Get token
        token = self.get_authorization(docker_image)
        resp = requests.get(
            url,
            verify=self.verify,
            headers={"Authorization": "{}".format(token)}
        )

        if not resp.ok:
            self.logger.error("MANIFESTS:HTTPCODEERROR:{}".format(resp.status_code))
            raise RegistryAccessError("Error access to : {url} \nCode Error : {status_code}".format(
                url=url, status_code=resp.status_code))
        else:
            return resp.json()
