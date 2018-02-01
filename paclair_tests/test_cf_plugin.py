import logging
import unittest

import requests_mock

from paclair.clair_requests import ClairRequests
from paclair.exceptions import ResourceNotFoundException
from paclair.plugins.cf_plugin import CfPlugin


class TestCfPlugin(unittest.TestCase):
    """
    Test de l'objet CfPlugin
    """
    
    artifacURI = 'http://artifac'
    artifacVERIFY = 'verifymock'
    clairURI = 'http://clair'

    def setUp(self):
        self.cf = CfPlugin(ClairRequests(self.clairURI), self.artifacURI, self.artifacVERIFY)


    @requests_mock.mock()
    def test_push_not_found(self, m):
        """
        Test de la méthode push quand l'image n'existe pas
        """
        # mock artifactory reponse
        m.head(self.artifacURI + "/tutu", status_code = 404)
        with self.assertRaises(ResourceNotFoundException):
            self.cf.push("tutu")

    @requests_mock.mock()
    def test_push_found(self, m):
        """
        Test de la méthode push quand l'image existe
        """
        # mock artifactory reponse
        m.head(self.artifacURI + "/tutu", status_code = 200)
        # mock clair reponse
        m.post(self.clairURI + '/v1/layers')
        self.cf.push("tutu")
        clair_data = {'Layer': {'Path': self.artifacURI + "/tutu", 'Format': 'cflinuxfs', 'Name': 'tutu'}}
        self.assertEqual(m.last_request.json(), clair_data)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
