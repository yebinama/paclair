import logging
import unittest
from unittest.mock import patch

import requests_mock
from elasticsearch import Elasticsearch

from paclair.api.clair_requests_v1 import ClairRequestsV1
from paclair.exceptions import ResourceNotFoundException, ClairConnectionError
from paclair.plugins.es_plugin import EsPlugin


class TestEsPlugin(unittest.TestCase):
    """
    Test de l'objet EsPlugin
    """
    
    def setUp(self):
        self.es = EsPlugin(ClairRequestsV1('http://localhost:6060'), [{'host': '172.18.8.10', 'port': 9200}],
                           'hbx-confo_factssysinfo', 'factssysinfo')
        self.layer_name = "toto"

    def test_push_not_found(self):
        """
        Test de la méthode push
        """
        with patch.object(Elasticsearch, "search", return_value={'hits': {'total': 0, 'hits': []}}),\
                self.assertRaises(ResourceNotFoundException):
            self.es.push(self.layer_name)

    @requests_mock.mock()
    def test_push_not_in_db(self, m):
        """
        Push avec layer non présent dans CLair
        """
        search = {'hits': {'total': 1, 'hits': [{'_id': "tutu"}]}}
        m.delete(self.es.clair.url + self.es.clair._CLAIR_DELETE_URI.format(self.layer_name),
                 status_code=404, reason="Not Found")
        m.post(self.es.clair.url + self.es.clair._CLAIR_POST_URI)
        with patch.object(Elasticsearch, "search", return_value=search):
            self.es.push(self.layer_name)

        path = 'http://172.18.8.10:9200/hbx-confo_factssysinfo/factssysinfo/tutu/_source?_source_include=sysinfo_clair'
        clair_data = {'Layer': {'Path': path, 'Format': 'Legacy', 'Name': 'toto'}}
        self.assertEqual(m.last_request.json(), clair_data)

    @requests_mock.mock()
    def test_push_already_in_db(self, m):
        """
        Push et layer présent dans Clair
        """
        search = {'hits': {'total': 1, 'hits': [{'_id': "tutu"}]}}
        m.delete(self.es.clair.url + self.es.clair._CLAIR_DELETE_URI.format(self.layer_name))
        m.post(self.es.clair.url + self.es.clair._CLAIR_POST_URI)
        with patch.object(Elasticsearch, "search", return_value=search):
            self.es.push(self.layer_name)

    @requests_mock.mock()
    def test_push_clair_error(self, m):
        """
        Push et erreur Clair
        """
        search = {'hits': {'total': 1, 'hits': [{'_id': "tutu"}]}}
        m.delete(self.es.clair.url + self.es.clair._CLAIR_DELETE_URI.format(self.layer_name))
        m.post(self.es.clair.url + self.es.clair._CLAIR_POST_URI, status_code=502)
        with patch.object(Elasticsearch, "search", return_value=search), self.assertRaises(ClairConnectionError):
            self.es.push(self.layer_name)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
