# coding=utf-8
""" Module Docstring

Author: Ian Davis
"""

from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSignal


class ItemModel(QObject):
    """ Generic Model item data container, that stores data via an internal dictionary and emulates the interface of a dictionary.
    """

    changed = pyqtSignal()

    def __init__(self, data, parent=None):
        QObject.__init__(self, parent)

        self._data = data

    @property
    def parent(self):
        return QObject.parent(self)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def iteritems(self):
        return self._data.iteritems()

    def iterkeys(self):
        return self._data.iterkeys()

    def itervalues(self):
        return self._data.itervalues()

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        self.changed.emit()

    def __str__(self):
        return str(self._data)