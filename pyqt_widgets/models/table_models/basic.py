# coding=utf-8
""" Define a QTableModel subclass that uses dictionaries instead of column indexes and maps them to an internal header list to manage data.

Author: Ian Davis
"""

import re
import sre_constants

from collections import OrderedDict as OrderedDictionary

from PyQt4.QtCore import QModelIndex
from PyQt4.QtCore import Qt

from pyqt_widgets import widgets

from pyqt_widgets.models.basic import BasicModel
from pyqt_widgets.models.item_model import ItemModel


class TableRow(ItemModel):
    def __init__(self, data, row=0, parent=None):
        ItemModel.__init__(self, data, parent)

        self.row = row


class TableModel(BasicModel):
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
        BasicModel.__init__(self, header, header_types, key_column, parent)

        self.table_data = OrderedDictionary()

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

    def rowCount(self, parent=QModelIndex()):
        """ Model-method, called by the view to determine how many rows are to be displayed at a given time.
        :param parent:
        """
        return len(self.table_data)

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

    def flags(self, index):
        """ QAbstractTableModel override method that is used to set the flags for the item at the given QModelIndex.
            Here, we just set all indexes to enabled, and selectable.
        :param index:
        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

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

