# -*- coding: utf-8 -*-

import logging


class LoggedObject:
    """
    Classe permettant de simplifier l'accès au logging
    """

    def __init__(self, logger=None):
        """
        Constructeur
        :param logger: le logger
        """
        self.logger = logger or logging.getLogger(__name__)
