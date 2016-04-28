from PyQt4.QtCore import QAbstractItemModel
from PyQt4.QtCore import QModelIndex
from PyQt4.QtCore import QObject
from PyQt4.QtCore import Qt


class BasicModel(QAbstractItemModel):
    def __init__(self, header, header_types=None, key_column=None, parent=None):
        QAbstractItemModel.__init__(self, parent)

        self.header = header
        self.header_types = header_types
        self.key_column = key_column

        if not self.key_column:
            self.key_column = self.header[0]

        if not self.header_types:
            self.header_types = {}
            for column in self.header:
                self.header_types[column] = 'string'

    def pack_dictionary(self, dictionary):
        """ Given a dictionary, create a new dictionary with columns missing from the original replaced with empty strings.

        :param dictionary: The dictionary to pack.
        :return: The packed dictionary.
        """
        packed_dictionary = {}

        for column in self.header:
            packed_dictionary[column] = dictionary.get(column, '')

        return packed_dictionary

    def columnCount(self, parent=QModelIndex()):
        """ Model-method, called by the view to determine how many columns are to be displayed at a given time.
        :param parent:
        """
        return len(self.header)

    def setData(self, index, data, role):
        """ Model-method, called by the view when a given index's data is changed to update the model with that change.

            In here, we lookup the pointer from the index (which will be an instance of our internal TableRow class),
            get the column name for the column edited, and set the table row's dictionary value for that column to the data entered.

        :param index:
        :param data:
        :param role:
        :return:
        """
        if not index.isValid():
            return False
        elif index.column() >= len(self.header):
            return False
        elif not role == Qt.EditRole:
            return False

        table_row = index.internalPointer()
        column_name = self.header[index.column()]

        if hasattr(data, 'toString'):
            table_row[column_name] = unicode(data.toString())
        else:
            table_row[column_name] = unicode(data)

        self.dataChanged.emit(index, index)

        return True

    def data(self, index, role):
        """ Model-method, called by the view to determine what to display for a given index and role.

        :param index: QModelIndex to display data for.
        :param role: The role to display (DisplayRole, TextAlignmentRole, etc).
        :return: The data to display.
        """
        if not index.isValid():
            return
        elif index.column() >= len(self.header):
            return
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif not role == Qt.DisplayRole:
            return

        table_row = index.internalPointer()
        column_name = self.header[index.column()]
        data = table_row[column_name]

        if not isinstance(data, QObject):
            if not data:
                data = ''

            data = unicode(data)

        return data

    def setHeaderData(self, section, orientation, value, role):
        """ Called to set the data for a given column in the header.

        :param section: The header section to change.
        :param orientation: The orientation of the section (Horizontal or Vertical).
        :param role: The role of the section (DisplayRole, etc).
        """
        self.headerDataChanged.emit(orientation, section, section)
        return True

    def headerData(self, section, orientation, role):
        """ Model-method, called by the view to determine what to display for a given section of the header.

        :param section: The section to display
        :param orientation: The orientation of the section (Horizontal or Vertical).
        :param role: The role of the section (DisplayRole, etc).
        :return:
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section >= len(self.header):
                return

            return self.header[section]