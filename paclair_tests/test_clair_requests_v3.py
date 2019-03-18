import json
import logging
import os
import unittest
from unittest.mock import Mock

import requests_mock

from paclair.ancestries.generic import GenericAncestry, Layer
from paclair.api.clair_requests_v3 import ClairRequestsV3
from paclair.exceptions import ResourceNotFoundException, PaclairException


class TestClairRequestV3(unittest.TestCase):
    """
    Test ClairRequest
    """

    clairURI = 'http://clair'

    def setUp(self):
        self.clair = ClairRequestsV3(self.clairURI)
        self.fixtures_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fixtures/clair")

    @requests_mock.mock()
    def test_get_ancestry_json(self, m):
        """
        Test get_ancestry_json
        """
        # 404
        m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("debian"), status_code=404, reason="Not Found")
        with self.assertRaises(ResourceNotFoundException):
            self.clair.get_ancestry_json("debian")

        with open(os.path.join(self.fixtures_dir, "debian_v3.json")) as f:
            m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("debian"), status_code=200, json=json.load(f))
        ancestry_json = self.clair.get_ancestry_json("debian")
        self.assertEqual(len(ancestry_json["ancestry"]["layers"][0]["detected_features"]), 141)

    @requests_mock.mock()
    def test_get_ancestry_statistics(self, m):
        """
        Test get_ancestry_statistics
        """
        # 404
        m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("debian"), status_code=404, reason="Not Found")
        with self.assertRaises(ResourceNotFoundException):
            self.clair.get_ancestry_statistics("debian")

        with open(os.path.join(self.fixtures_dir, "debian_v3.json")) as f:
            m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("debian"), status_code=200, json=json.load(f))
        ancestry_stats = self.clair.get_ancestry_statistics("debian")
        self.assertDictEqual(ancestry_stats, {'High': 10, 'Low': 2, 'Medium': 7, 'Unknown': 1})

    @requests_mock.mock()
    def test_get_ancestry_statistics_with_whitelist(self, m):
        """
        Test get_ancestry_statistics
        """
        clair = ClairRequestsV3(self.clairURI, cve_whitelist=['CVE-2018-16864', 'CVE-2019-3815'])

        with open(os.path.join(self.fixtures_dir, "debian_v3.json")) as f:
            m.get(self.clairURI + clair._CLAIR_ANALYZE_URI.format("debian"), status_code=200, json=json.load(f))
        ancestry_stats = clair.get_ancestry_statistics("debian")
        self.assertDictEqual(ancestry_stats, {'High': 10, 'Low': 1, 'Medium': 6, 'Unknown': 1})

    @requests_mock.mock()
    def test_get_ancestry_html(self, m):
        """
        Test get_ancestry_html
        """
        # 404
        m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("debian"), status_code=404, reason="Not Found")
        with self.assertRaises(ResourceNotFoundException):
            self.clair.get_ancestry_html("debian")

        with open(os.path.join(self.fixtures_dir, "debian_v3.json")) as f:
            m.get(self.clairURI + self.clair._CLAIR_ANALYZE_URI.format("debian"), status_code=200, json=json.load(f))
        ancestry_html = self.clair.get_ancestry_html("debian")

        with open(os.path.join(self.fixtures_dir, "debian_v3.html")) as f:
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
        expected_json = {'ancestry_name': 'ubuntu', 'format': 'Docker', 'layers':
            [{'hash': 'hash_aaaaa', 'path': 'path_aaaaa', 'headers': None},
             {'hash': 'hash_bbbbb', 'path': 'path_bbbbb', 'headers': None}]}
        self.clair.post_ancestry(ancestry)
        self.clair._request.assert_called_with('POST', '/ancestry', json=expected_json)

    def test_delete_ancestry(self):
        """
        Test delete_ancestry
        """
        ancestry = GenericAncestry("ubuntu", "Docker", [Layer("aaaaa", "hash_aaaaa", "path_aaaaa"),
                                                        Layer("bbbbb", "hash_bbbbb", "path_bbbbb")])
        with self.assertRaises(PaclairException):
            self.clair.delete_ancestry(ancestry)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
