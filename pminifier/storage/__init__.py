"""Base class for storage implementations."""

from abc import ABCMeta, abstractmethod, abstractproperty

class StorageBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def cache_get_id_multi(self, results):
        """Cache the results of ``get_id_multi`` (i.e. {string: id})"""
        pass

    @abstractmethod
    def cache_get_string_multi(self, results):
        """Cache the results of ``get_string_multi`` (i.e. {id: string})"""
        pass

    def get_id(self, string, create_missing=True):
        return self.get_id_multi(
            [string],
            create_missing=create_missing
        ).get(string)

    @abstractmethod
    def get_id_multi(self, strings, create_missing=True):
        pass

    def get_string(self, id):
        return self.get_string_multi([id]).get(id)

    @abstractmethod
    def get_string_multi(self, ids):
        pass
