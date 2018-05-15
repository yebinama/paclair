# -*- coding: utf-8 -*-
from paclair.logged_object import LoggedObject


class GenericAncestry(LoggedObject):
    """
    Ancestry object
    """

    def __init__(self, name, clair_format, layers=None):
        """
        Constructor

        :param name: ancestry's name
        :param clair_format: clair format
        :param layers: [{"name": str, "hash": str, "path": str, "headers":{}}]
        """
        super().__init__()
        self.logger.debug("Creating {} ancestry".format(name))
        self.name = name
        self.clair_format = clair_format
        self.layers = layers or []

    def to_json(self):
        """

        :return: dict
        """
        return {"ancestry_name": self.name, "format": self.clair_format,
                "layers": [{'hash': l.lhash, 'path': l.path, 'headers': l.headers}for l in self.layers]}


class Layer(LoggedObject):
    """
    Layer object
    """

    def __init__(self, name, lhash, path, headers=None, parent=""):
        """
        Constructor

        :param name: layer name
        :param lhash: hash
        :param path: path
        :param headers: headers
        :param parent: parent name
        """
        super().__init__()
        self.name = name
        self.lhash = lhash
        self.path = path
        self.headers = headers
        self.parent = parent
