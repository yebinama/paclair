#-*- coding: UTF-8 -*-
from collections import MutableMapping


class InsensitiveCaseDict(MutableMapping):
    """
    An insensitive case dict
    """

    def __init__(self, data=None, **kwargs):
        """
        Init the dictionnary

        :param data: an existing dictionnary
        :param kwargs: other arguments
        """
        self._storage = {}
        data = data or {}
        self.update(data, **kwargs)

    def __getitem__(self, item):
        return self._storage[self._lower(item)]

    def __setitem__(self, key, value):
        self._storage[self._lower(key)] = value

    def __delitem__(self, key):
        del self._storage[self._lower(key)]

    def __iter__(self):
        return iter(self._storage)

    def __len__(self):
        return len(self._storage)

    @staticmethod
    def _lower(item):
        """
        Lowercase item

        :param item: item to lowercase
        :return: Lowercased item
        """
        if isinstance(item, str):
            return item.lower()
        return item
