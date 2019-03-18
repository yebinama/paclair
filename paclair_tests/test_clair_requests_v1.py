import json
import logging
import os
import unittest
from unittest.mock import Mock

import requests_mock

from paclair.ancestries.generic import GenericAncestry, Layer
from paclair.api.clair_requests_v1 import ClairRequestsV1
from paclair.exceptions import ResourceNotFoundException, ClairConnectionError, PaclairException


class TestClairRequestV1(unittest.TestCase):
    """
    Test ClairRequest
    """

    clairURI = 'http://clair'

    def setUp(self):
        self.clair = ClairRequestsV1(self.clairURI)
        self.fixtures_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/clair")

    @requests_mock.mock()
    def test_request(self, m):
        """
        Test _request method
        """
        # 404
        m.get(self.clairURI + "/tutu", status_code = 404, reason="Not Found")
        with self.assertRaises(ResourceNotFoundException):
            self.clair._request("GET", "/tutu")

        # Other error
        m.get(self.clairURI + "/tutu", status_code=502)
        with self.assertRaises(ClairConnectionError):
            self.clair._request("GET", "/tutu")

        # Ok
        m.get(self.clairURI + "/tutu", status_code=200)
        response = self.clair._request("GET", "/tutu")
        self.assertEqual(response.status_code, 200)

    @requests_mock.mock()
    def test_get_ancestry_json(self, m):
        """
        Test get_ancestry_json
        """
        # 404
        m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("ubuntu"), status_code=404, reason="Not Found")
        with self.assertRaises(ResourceNotFoundException):
            self.clair.get_ancestry_json("ubuntu")

        with open(os.path.join(self.fixtures_dir, "ubuntu_v1.json")) as f:
            m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("ubuntu"), status_code=200, json=json.load(f))
        ancestry_json = self.clair.get_ancestry_json("ubuntu")
        self.assertEqual(len(ancestry_json["Layer"]["Features"]), 148)

    @requests_mock.mock()
    def test_get_ancestry_statistics(self, m):
        """
        Test get_ancestry_statistics
        """
        # 404
        m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("ubuntu"), status_code=404, reason="Not Found")
        with self.assertRaises(ResourceNotFoundException):
            self.clair.get_ancestry_statistics("ubuntu")

        with open(os.path.join(self.fixtures_dir, "ubuntu_v1.json")) as f:
            m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("ubuntu"), status_code=200, json=json.load(f))
        ancestry_stats = self.clair.get_ancestry_statistics("ubuntu")
        self.assertDictEqual(ancestry_stats, {'Medium': 1, 'High': 1, 'Low': 1})

    @requests_mock.mock()
    def test_get_ancestry_statistics_with_whitelist(self, m):
        """
        Test get_ancestry_statistics
        """
        clair = ClairRequestsV1(self.clairURI, cve_whitelist=['CVE-2017-9445', 'CVE-2017-9217'])

        with open(os.path.join(self.fixtures_dir, "ubuntu_v1.json")) as f:
            m.get(self.clairURI + clair._CLAIR_ANALYZE_URI.format("ubuntu"), status_code=200, json=json.load(f))
        ancestry_stats = clair.get_ancestry_statistics("ubuntu")
        self.assertDictEqual(ancestry_stats, {'Medium': 1})

    @requests_mock.mock()
    def test_get_ancestry_html(self, m):
        """
        Test get_ancestry_html
        """
        # 404
        m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("ubuntu"), status_code=404, reason="Not Found")
        with self.assertRaises(ResourceNotFoundException):
            self.clair.get_ancestry_html("ubuntu")

        with open(os.path.join(self.fixtures_dir, "ubuntu_v1.json")) as f:
            m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("ubuntu"), status_code=200, json=json.load(f))
        ancestry_html = self.clair.get_ancestry_html("ubuntu")
        with open(os.path.join(self.fixtures_dir, "ubuntu_v1.html")) as f:
            expected = f.read()
            self.assertEqual(expected, ancestry_html)

    @requests_mock.mock()
    def test_post_ancestry(self, m):
        """
        Test post_ancestry
        """
        self.clair._request = Mock(autospec=True)
        ancestry = GenericAncestry("ubuntu", "Docker", [Layer("aaaaa", "hash_aaaaa", "path_aaaaa"),
                                                        Layer("bbbbb", "hash_bbbbb", "path_bbbbb")])
        self.clair.post_ancestry(ancestry)
        self.clair._request.assert_any_call('POST', self.clair._CLAIR_POST_URI,
                                               json={'Layer': {'Name': 'aaaaa', 'Path': 'path_aaaaa', 'Format': 'Docker'}})
        self.clair._request.assert_any_call('POST', self.clair._CLAIR_POST_URI,
                                            json={'Layer': {'Name': 'bbbbb', 'Path': 'path_bbbbb', 'Format': 'Docker',
                                                            'ParentName': 'aaaaa'}})

    def test_delete_ancestry(self):
        """
        Test delete_ancestry
        """
        self.clair._request = Mock(autospec=True)
        ancestry = GenericAncestry("ubuntu", "Docker", [Layer("aaaaa", "hash_aaaaa", "path_aaaaa"),
                                                        Layer("bbbbb", "hash_bbbbb", "path_bbbbb")])
        self.clair.delete_ancestry(ancestry)
        self.clair._request.assert_any_call("DELETE", self.clair._CLAIR_DELETE_URI.format("aaaaa"))
        self.clair._request.assert_any_call("DELETE", self.clair._CLAIR_DELETE_URI.format("bbbbb"))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
