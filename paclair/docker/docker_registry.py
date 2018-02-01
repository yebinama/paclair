"""
Module docker_registry
"""

import requests
import re
from paclair.logged_object import LoggedObject
from paclair.exceptions import RegistryAccessError


class DockerRegistry(LoggedObject):
    """
    Classe représentant une registry Docker
    """
    BASE_API_URL = '{registry.protocol}://{registry.domain}{registry.api_prefix}'
    MANIFEST_URI = '/v2/{image.name}/manifests/{image.tag}'
    BLOBS_URI = '/v2/{image.name}/blobs/{digest}'
    TOKEN_REGEX = "Bearer realm=\"(?P<realm>.*)\",service=\"(?P<service>.*)\""

    def __init__(self, domain, token_url=None, api_prefix="", protocol="https", auth=None, verify=True):
        """
        Initialisation

        :param api_prefix: préfixe de l'api
        :param domain: le domaine de la registry (ex : registry.hub.docker.com)
        :param token_url: url qui permet d'avoir le token de connexion (ex : https://auth.docker.io)
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
        self.logger.debug("INITCLASS:API_AUTH:{}".format(self.auth))
        self.verify = verify
        self.logger.debug("INITCLASS:API_VERIFY:{}".format(self.verify))
        self.__token_url = token_url
        self.logger.debug("INITCLASS:TOKEN_URL:{}".format(self.__token_url))

    @property
    def token_url(self):
        """
        Construction de la token url si non présente, renvoi sinon
        """
        if self.__token_url is None:
            url = self.BASE_API_URL.format(registry=self) + "/v2/"
            self.logger.debug("REQUEST_BASE_API_URL_FOR_TOKEN_ENDPOINT:URL:{}".format(url))

            response = requests.get(url, verify=self.verify, auth=self.auth)
            if not "www-authenticate" in response.headers:
                self.logger.error("REQUEST_TOKEN:HTTPCODEERROR:{}".format(response.status_code))
                raise RegistryAccessError("Error access to : {} \nCode Error : {}".format(url, response.status_code))

            # Définition du realm et du service
            matcher = re.match(self.TOKEN_REGEX, response.headers["www-authenticate"])
            if matcher is None:
                raise RegistryAccessError("Can't find token url")
            self.__token_url = "{}?client_id=paclair&service={}&scope=repository:{}:pull".format(
                matcher.group("realm"), matcher.group("service"), "{image.name}")
            self.logger.debug("TOKEN_URL:{}".format(self.__token_url))

        return self.__token_url

    def get_base_api_url(self, docker_image):
        """
        Retourne l'url de base de l'api pour l'image associée

        :param docker_image: paclair.docker.DockerImage
        :return:
        """
        # Format pour les attributs de la registry
        url = self.BASE_API_URL.format(registry=self)
        # Format si des paramètres de l'image sont nécessaire ex: prefix_api=/api/{image.repo}
        return url.format(image=docker_image)

    def get_manifest_url(self, docker_image):
        """
        Renvoie l'url du manifest

        :param docker_image: paclair.docker.DockerImage
        :return: l'url du manifest pour l'image
        """
        url = self.get_base_api_url(docker_image) + self.MANIFEST_URI.format(image=docker_image)
        return url

    def get_blobs_url(self, docker_image, digest):
        """
        Renvoie l'url du blob digest de l'image docker_image

        :param docker_image: paclair.docker.DockerImage
        :param digest: digest à récupérer
        :return: l'url du blob digest de l'image docker_image
        """
        url = self.get_base_api_url(docker_image) + self.BLOBS_URI.format(image=docker_image, digest=digest)
        return url

    def get_token(self, docker_image):
        """
        Methode qui génère le token

        :param docker_image: paclair.docker.DockerImage
        :returns str:
        """
        # Création de l'url
        url = self.token_url.format(registry=self, image=docker_image)
        self.logger.debug("REQUEST_TOKEN:URL:{url}".format(url=url))

        # Interrogation de l'url et récupération du token
        resp = requests.get(url, verify=self.verify, auth=self.auth)
        if not resp.ok:
            self.logger.error("REQUEST_TOKEN:HTTPCODEERROR:{}".format(resp.status_code))
            raise RegistryAccessError("Error access to : {url} \nCode Error : {status_code}".format(
                url=url, status_code=resp.status_code))

        token = resp.json()['token']
        self.logger.debug("TOKEN:{token}".format(token=token))
        return token

    def get_manifest(self, docker_image):
        """
        Renvoie le manifest associé à docker_image

        :param docker_image: paclair.docker.DockerImage
        :return: manifest associé à l'image
        """
        # Création de l'url
        url = self.get_manifest_url(docker_image)
        self.logger.debug("REQUESTMANIFESTS:{url}".format(url=url))

        # Récupération du Token
        token = self.get_token(docker_image)
        resp = requests.get(url, verify=self.verify, headers={"Authorization": "Bearer {}".format(token)})

        if not resp.ok:
            self.logger.error("MANIFESTS:HTTPCODEERROR:{}".format(resp.status_code))
            raise RegistryAccessError("Error access to : {url} \nCode Error : {status_code}".format(
                url=url, status_code=resp.status_code))
        else:
            return resp.json()
