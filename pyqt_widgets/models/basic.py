from PyQt4.QtCore import QModelIndex


class BasicModel(object):
    def __init__(self, header, header_types=None, key_column=None):
        self.header = header
        self.header_types = header_types
        self.key_column = key_column

        if not self.key_column:
            self.key_column = self.header[0]

        if not self.header_types:
            self.header_types = {}
            for column in self.header:
                self.header_types[column] = 'string'

    def columnCount(self, parent=QModelIndex()):
        """ Model-method, called by the view to determine how many columns are to be displayed at a given time.
        :param parent:
        """
        return len(self.header)

    def pack_dictionary(self, dictionary):
        """ Given a dictionary, create a new dictionary with columns missing from the original replaced with empty strings.

        :param dictionary: The dictionary to pack.
        :return: The packed dictionary.
        """
        packed_dictionary = {}

        for column in self.header:
            packed_dictionary[column] = dictionary.get(column, '')

        return packed_dictionary
