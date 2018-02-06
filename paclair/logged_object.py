# -*- coding: utf-8 -*-

import logging


class LoggedObject:
    """
    Easy access to logging
    """

    def __init__(self, logger=None):
        """
        Constructor

        :param logger: logger
        """
        self.logger = logger or logging.getLogger(__name__)
