import unittest
from unittest.mock import patch

import requests_mock

from paclair.api.clair_requests_v1 import ClairRequestsV1
from paclair.docker.docker_image import DockerImage
from paclair.exceptions import ResourceNotFoundException
from paclair.plugins.docker_plugin import DockerPlugin


class TestDockerPlugin(unittest.TestCase):
    """docstring for TestDockerPlugin"""

    def setUp(self):
        self.docker = DockerPlugin(ClairRequestsV1('http://localhost:6060'))

    @requests_mock.mock()
    def test_push(self, m):
        get_layers = ['fffffffffffffffffffffffffffffffffffffffff']
        m.post(self.docker.clair.url + self.docker.clair._CLAIR_POST_URI,
               status_code=201, reason="OK")
        with patch.object(DockerImage, "get_layers", return_value=get_layers):
            with patch.object(DockerImage, "authorization", return_value="Basic MYTOKEN"):
                self.docker.push('monimage:tags')

    @requests_mock.mock()
    def test_push_404(self, m):
        get_layers = ['fffffffffffffffffffffffffffffffffffffffff']
        m.post(self.docker.clair.url + self.docker.clair._CLAIR_POST_URI,
               status_code=404, reason="Not Found")
        with patch.object(DockerImage, "get_layers", return_value=get_layers):
            with patch.object(DockerImage, "authorization", return_value="Basic MYTOKEN"), self.assertRaises(ResourceNotFoundException):
                self.docker.push('monimage:tags')