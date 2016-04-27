# coding=utf-8
""" Define a QTableModel subclass that uses dictionaries instead of column indexes and maps them to an internal header list to manage data.

Author: Ian Davis
"""

import re
import sre_constants

from collections import OrderedDict as OrderedDictionary

from PyQt4.QtCore import QAbstractTableModel
from PyQt4.QtCore import QModelIndex
from PyQt4.QtCore import QObject
from PyQt4.QtCore import Qt

from pyqt_widgets.models.item_model import ItemModel


class TableRow(ItemModel):
    def __init__(self, data, row=0, parent=None):
        ItemModel.__init__(self, data, parent)

        self.row = row


class TableModel(QAbstractTableModel):
    """ TableModel is an implementation of PyQt's QAbstractTableModel that overrides default indexing to use dictionary key-based mapping,
        mapping a column in the table's header to a value for that column. The goal here is to simplify indexing by being able to manage
        the data in a table based on string keys instead of arbitrary indexes, eliminating the need to cross-reference a header to find where
        to put a value.
    """
    def __init__(self, header, header_types=None, key_column=None, parent=None):
        """ TableModel initializer

        :param header: A list containing the header values for the table.
        :param header_types: A dictionary mapping the header values to their types, default is string.
        :param key_column: The primary key column for the table (the column to reference rows by).z
        :param parent: The QT Parent widget.
        """
        QAbstractTableModel.__init__(self, parent)

        self.header = header
        self.header_types = header_types

        if not self.header_types:
            self.header_types = {}
            for column in self.header:
                self.header_types[column] = 'string'

        self.key_column = key_column

        if not self.key_column:
            self.key_column = self.header[0]

        self.table_data = OrderedDictionary()

    def rowCount(self, parent=QModelIndex()):
        """ Model-method, called by the view to determine how many rows are to be displayed at a given time.
        :param parent:
        """
        return len(self.table_data)

    def columnCount(self, parent=QModelIndex()):
        """ Model-method, called by the view to determine how many columns are to be displayed at a given time.
        :param parent:
        """
        return len(self.header)

    # noinspection PyUnresolvedReferences
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

    def index(self, row, col, parent=QModelIndex()):
        """ Model-method, Return a QModelIndex that points to a given row, column and parent (parent is for Tree-based models mainly).

            Uses internal method createIndex defined by Qt to create a QModelIndex instance.

        :param row: The row of this index.
        :param col: The column of this index.
        :param parent: The parent of this index.
        :return: QModelIndex pointing at the given row and column.
        """
        try:
            table_row = self.table_data.values()[row]
        except IndexError:
            return QModelIndex()

        return self.createIndex(row, col, table_row)

    # noinspection PyUnresolvedReferences
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

    def flags(self, index):
        """ QAbstractTableModel override method that is used to set the flags for the item at the given QModelIndex.
            Here, we just set all indexes to enabled, and selectable.
        :param index:
        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def add_row(self, data):
        """ Add a new row to the table, displaying the data mapped from a dictionary to our table header.

        :param data: A dictionary mapping to our table header and the values for each column.
        :return: TableRow instance that was added to the model.
        """
        row = self.rowCount()
        table_row = TableRow(self.pack_dictionary(data), row)
        key_value = data[self.key_column]

        self.beginInsertRows(QModelIndex(), row, row)
        self.table_data[key_value] = table_row
        self._connect_node(table_row)
        self.endInsertRows()

        return table_row

    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    def remove_table_rows(self, table_rows):
        """ Given a collection of TableRow instances, remove their pointers from our model and emit layoutChanged to update any views.

        :param table_rows: Iterable of TableRow objects.
        """
        self.layoutAboutToBeChanged.emit()

        for table_row in table_rows:
            key_value = table_row[self.key_column]
            del self.table_data[key_value]

        self.layoutChanged.emit()

    def removeRows(self, row, count, parent=QModelIndex()):
        """ Model-method to remove a number of rows, starting at row.

        NOTE: removeRows is mainly an internal method, reimplemented just to support the QT API,
            it's behavior with multiple non-adjacent selection segments at one time is almost
            never correct, and remove_table_rows should be used instead.

        :param row: The row to begin removing from.
        :param count: The number of rows to remove.
        :param parent: The parent index of the row to begin from.
        :return: True if the rows were successfully removed.
        """
        self.beginRemoveRows(parent, row, row + count)
        new_data = self.table_data.copy()

        for key in new_data.keys()[row:row + count]:
            del self.table_data[key]

        self.endRemoveRows()

        return True

    def _connect_node(self, node):
        """ Helper function used to connect the data changed signals of our TableRow to the notify_data_changed method.

        NOTE: This method is automatically called for all TableRow objects added to our model (properly), to support
            updating the model and any views automatically when the data of the TableRow is changed programatically.

        :param node: TableRow instance to connect.
        """
        node.changed.connect(lambda: self._notify_data_changed(node))

    # noinspection PyUnresolvedReferences
    def _notify_data_changed(self, node):
        """ The data for a given TableRow has been changed, so emit the dataChanged signal to update views.

        :param node: The TableRow that was changed.
        """
        row = node.row
        top_left = self.createIndex(row, 0, node)
        bottom_right = self.createIndex(row, len(self.header), node)
        self.dataChanged.emit(top_left, bottom_right)

    def match_pattern(self, section, pattern):
        """ Match a given regex pattern to the rows in our table, and create a list of rows that matched.

        :param section: The column in the table to match against.
        :param pattern: The regex pattern to match.
        :return: The list of rows that matched the pattern.
        """
        try:
            compiled_regex = re.compile(pattern)
        except sre_constants.error:
            # This is raised when the regex is invalid (an unclosed escape sequence, etc)
            return widgets.warning_message('Improper regular expression filter',
                                           'The filter you entered is not a valid regular expression, please see the manual for more information on filtering.')

        column_name = self.header[section]
        rows_to_hide = []

        for table_row in self.table_data.itervalues():
            data = table_row[column_name]
            if not compiled_regex.match(str(data)):
                rows_to_hide.append(table_row.row)

        return rows_to_hide

    def pack_dictionary(self, dictionary):
        """ Given a dictionary, create a new dictionary with columns missing from the original replaced with empty strings.

        :param dictionary: The dictionary to pack.
        :return: The packed dictionary.
        """
        packed_dictionary = {}

        for column in self.header:
            packed_dictionary[column] = dictionary.get(column, '')

        return packed_dictionary
