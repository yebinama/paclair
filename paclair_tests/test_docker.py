import json
import os
import unittest

import requests_mock

from paclair import DOCKER_HUB_TOKEN_REQUEST, DOCKER_HUB_DOMAIN
from paclair.docker.docker_image import DockerImage
from paclair.docker.docker_registry import DockerRegistry
from paclair.exceptions import RegistryAccessError

###################################################
# Global Variables
###################################################

FIXTURES_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/")


class TestDockerImage(unittest.TestCase):
    """
    Test de l'objet DockerImage
    """
    EXPECTED_LAYERS = ['sha256:cf4e6d5921e259d673f63d820189f85cbfe8d0395f2c622a1a319fcfe33ed300',
                       'sha256:a3ed95caeb02ffe68cdd9fd84406680ae93d633cb16422d00e8a7c22955b46d4',
                       'sha256:08d02af113c958358618db8f237ce540588a62c590bfd1bbad7eba3eea97a02d',
                       'sha256:b36fdace5c59dfc1c02752efd7d6549b4dcb7ca5eb29e1c2b5f79a7a931aa248',
                       'sha256:64d3843af9ec26cad084b1e517243c3e2a4f309a8471d0e7a282b5c8b6ebbdce',
                       'sha256:ef25dcef04e03fa71fa4837dc77fe0d35f5dcc62a282b1852370848aeb140dce',
                       'sha256:1359e66c6258c932de98053676348b8923854079d85697b192684fd9d10a58be',
                       'sha256:cdd7b9a0b9a3da1d891f54aab8559a324a210495f2324abbb6ab78ae387ae9db',
                       'sha256:1819a55d3931f29312b52d14f1d4e8fb9be94a870f24261168464d0ff5159507',
                       'sha256:f01836d9fae29e08f1ec1377039152f46fef36627201e2828cb33a60fb33ebac',
                       'sha256:5e530ab118e05274008baf34b470a56a2273b0349653400410c6a66e98dc0061']

    EXPECTED_LAYERS_V2 = ['sha256:e692418e4cbaf90ca69d05a66403747baa33ee08806650b51fab815ad7fc331f',
                          'sha256:3c3a4604a545cdc127456d94e421cd355bca5b528f4a9c1905b15da2eb4a4c6b',
                          'sha256:ec4b8955958665577945c89419d1af06b5f7636b4ac3da7f12184802ad867736']

    def setUp(self):
        with open(FIXTURES_FOLDER + 'docker/manifest.json') as data_file:
            self.manifest_json = json.load(data_file)
        with open(FIXTURES_FOLDER + 'docker/manifestv2.json') as data_file:
            self.manifestv2_json = json.load(data_file)
        with open(FIXTURES_FOLDER + '/docker/token.json') as data_file:
            self.token_json = json.load(data_file)
        self.token = self.token_json['token']

    @requests_mock.mock()
    def test_get_layers_docker_hub(self, m):
        """
        Test de la méthode get_layer
        """
        registry = DockerRegistry(DOCKER_HUB_DOMAIN, token_url=DOCKER_HUB_TOKEN_REQUEST)
        image = DockerImage('library/monimage', registry, tag='tag')
        m.get(DOCKER_HUB_TOKEN_REQUEST.format(image=image), json=self.token_json)
        m.get(registry.get_manifest_url(image), json=self.manifest_json,
              headers={'Authorization': 'Bearer {token}'.format(token=self.token)})

        layers = image.get_layers()
        self.assertEqual(layers, self.EXPECTED_LAYERS)

    @requests_mock.mock()
    def test_sha(self, m):
        """
        Test sha method
        """
        registry = DockerRegistry(DOCKER_HUB_DOMAIN, token_url=DOCKER_HUB_TOKEN_REQUEST)
        image = DockerImage('library/monimage', registry, tag='tag')
        m.get(DOCKER_HUB_TOKEN_REQUEST.format(image=image), json=self.token_json)
        m.get(registry.get_manifest_url(image), json=self.manifest_json,
              headers={'Authorization': 'Bearer {token}'.format(token=self.token)})
        self.assertEqual("58c0a48e3b6a2c9f3b1d8166e096789f20b769f538f4aecaa73d5eae15672b2b", image.sha)
        self.assertEqual("58c0a48e3b6a", image.short_sha)

    @requests_mock.mock()
    def test_get_layers_docker_hub_v2(self, m):
        """
        Test de la méthode get_layer
        """
        registry = DockerRegistry(DOCKER_HUB_DOMAIN, token_url=DOCKER_HUB_TOKEN_REQUEST)
        image = DockerImage('library/monimage', registry, tag='tag')
        m.get(DOCKER_HUB_TOKEN_REQUEST.format(image=image), json=self.token_json)
        m.get(registry.get_manifest_url(image), json=self.manifestv2_json,
              headers={'Authorization': 'Bearer {token}'.format(token=self.token)})

        layers = image.get_layers()
        self.assertEqual(layers, self.EXPECTED_LAYERS_V2)

    @requests_mock.mock()
    def test_get_layers_artifactory(self, m):
        """
        Test de la méthode get_layer
        """
        artifactory_registry = 'registry.artifactory.net'
        token_url = "https://{registry.domain}/api/docker/{image.repository}/v2/token?service={registry.domain}"
        registry = DockerRegistry(artifactory_registry, token_url=token_url, protocol="http")
        image = DockerImage('monimage', registry)
        m.get(token_url.format(image=image, registry=registry), json=self.token_json)
        m.get(registry.get_manifest_url(image), json=self.manifest_json,
              headers={'Authorization': 'Bearer {token}'.format(token=self.token)})

        layers = image.get_layers()
        self.assertEqual(layers, self.EXPECTED_LAYERS)

    @requests_mock.mock()
    def test_get_layers_artifactory_v2(self, m):
        """
        Test de la méthode get_layer
        """
        artifactory_registry = 'registry.artifactory.net'
        token_url = "https://{registry.domain}/api/docker/{image.repository}/v2/token?service={registry.domain}"
        registry = DockerRegistry(artifactory_registry, token_url=token_url, protocol="http")
        image = DockerImage('monimage', registry)
        m.get(token_url.format(image=image, registry=registry), json=self.token_json)
        m.get(registry.get_manifest_url(image), json=self.manifestv2_json,
              headers={'Authorization': 'Bearer {token}'.format(token=self.token)})

        layers = image.get_layers()
        self.assertEqual(layers, self.EXPECTED_LAYERS_V2)

    @requests_mock.mock()
    def test_get_layers_other_registery(self, m):
        """
        Test de la méthode get_layer
        """
        domain_lambda = 'registery.host'
        registry = DockerRegistry(domain_lambda, token_url="https://token_url")
        image = DockerImage('monimage', registry)
        # Token
        m.get("https://token_url", json=self.token_json)
        # Manifest
        m.get(registry.get_manifest_url(image), json=self.manifest_json,
              headers={'Authorization': 'Bearer {token}'.format(token=self.token)})

        layers = image.get_layers()
        self.assertEqual(layers, self.EXPECTED_LAYERS)

    @requests_mock.mock()
    def test_get_layers_other_registery_v2(self, m):
        """
        Test de la méthode get_layer
        """
        domain_lambda = 'registery.host'
        registry = DockerRegistry(domain_lambda, token_url="https://token_url")
        image = DockerImage('monimage', registry)
        # Token
        m.get("https://token_url", json=self.token_json)
        # Manifest
        m.get(registry.get_manifest_url(image), json=self.manifestv2_json,
              headers={'Authorization': 'Bearer {token}'.format(token=self.token)})

        layers = image.get_layers()
        self.assertEqual(layers, self.EXPECTED_LAYERS_V2)

    @requests_mock.mock()
    def test_get_token(self, m):
        """
        Test de la méthode get_token
        """
        domain_lambda = 'registery.host'
        registry = DockerRegistry(domain_lambda, token=self.token, token_type='Basic')
        image = DockerImage('monimage', registry)
        # Manifest
        m.register_uri('GET', registry.get_manifest_url(image), json=self.manifestv2_json,
                       request_headers={'Authorization': 'Basic {token}'.format(token=self.token)})

        layers = image.get_layers()
        self.assertTrue(m.called)
        self.assertEqual(layers, self.EXPECTED_LAYERS_V2)

    @requests_mock.mock()
    def test_manifest_http_error(self, m):
        """
        Http Error en cas d'erreur d'accès à la registry

        """
        domain_lambda = 'registery.host'
        registry = DockerRegistry(domain_lambda, token_url="https://token_url")
        image = DockerImage('monimage', registry)
        # Token
        m.get("https://token_url", json=self.token_json)
        # Manifest
        m.register_uri('GET', registry.get_manifest_url(image), json=self.manifest_json,
                       headers={'Authorization': 'Beare {token}'.format(token=self.token)}, status_code=401)

        with self.assertRaises(RegistryAccessError):
            image.get_layers()

    @requests_mock.mock()
    def test_token_endpoint(self, m):
        """
        Test de la méthode token_endpoint
        """
        m.register_uri('GET', "https://{}/v2/".format(DOCKER_HUB_DOMAIN), status_code=401,
                       headers={'Www-Authenticate':
                                    'Bearer realm="https://auth.docker.io/token",service="registry.docker.io"'})
        registry = DockerRegistry(DOCKER_HUB_DOMAIN)
        self.assertEqual(registry.token_url, DOCKER_HUB_TOKEN_REQUEST)

        m.register_uri('GET', "https://{}/v2/".format(DOCKER_HUB_DOMAIN), headers={})
        with self.assertRaises(RegistryAccessError):
            registry = DockerRegistry(DOCKER_HUB_DOMAIN)
            print(registry.token_url)


if __name__ == '__main__':
    unittest.main()
