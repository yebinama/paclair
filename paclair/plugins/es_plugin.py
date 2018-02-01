# -*- coding: utf-8 -*-
import base64
import datetime

from elasticsearch import Elasticsearch, RequestsHttpConnection

from paclair.plugins.abstract_plugin import AbstractPlugin
from paclair.exceptions import ResourceNotFoundException


class EsPlugin(AbstractPlugin):
    """
    Plugin pour elasticsearch
    """

    __SOURCE_URL = "{}/{}/{}/{}/_source?_source_include=sysinfo_clair"

    def __init__(self, clair, hosts, index, doc_type, suffix=None, timedelta=None):
        """
        Constructeur

        :param clair: object ClairRequest
        :param hosts: hosts elasticsearch ex:[{'host': '172.18.8.10', 'port': 9200}]
        :param index: index elasticsearch
        :param doc_type: doc_type elasticsearch
        :param suffix: index suffix (ex: index différent par jour)
        :param timedelta: timedelta from today for suffix
        """
        super().__init__(clair, "Legacy")
        self._es = Elasticsearch(hosts, connection_class=RequestsHttpConnection)
        self.index = index
        self.doc_type = doc_type
        if suffix is not None:
            timedelta = timedelta or {}
            self.index += (datetime.datetime.today() + datetime.timedelta(**timedelta)).strftime(suffix)

    def push(self, name):
        # Récupération de l'ID
        search = {"size": 1, "sort": {'@timestamp': "desc"}, "_source": False,
                  "query": {'match_phrase': {'hostname': name}}}
        result = self._es.search(index=self.index, doc_type=self.doc_type, body=search)['hits']
        # Pas de résultat
        if result['total'] == 0:
            raise ResourceNotFoundException("{} not found".format(name))

        self.logger.debug("Remove layer {} from Clair's Database.".format(name))
        try:
            self.delete(name)
        except ResourceNotFoundException:
            self.logger.debug("Layer {} not yet in Clair's Database.".format(name))

        id_name = result['hits'][0]['_id']
        path = self.__SOURCE_URL.format(self._es.transport.get_connection().host, self.index, self.doc_type, id_name)

        # Authentification
        auth = self._es.transport.get_connection().session.auth
        if auth is not None:
            digest = "{}:{}".format(*auth)
            digest = base64.b64encode(digest.encode("utf-8"))
            headers = {'Headers': {'Authorization': 'Basic {}'.format(digest.decode('utf-8'))}}
            data = self.clair.to_clair_post_data(name, path, self.clair_format, **headers)
        else:
            data = self.clair.to_clair_post_data(name, path, self.clair_format)
        self.clair.post_layer(data)
