from collections import OrderedDict as OrderedDictionary

from PyQt4.QtCore import QAbstractItemModel
from PyQt4.QtCore import QModelIndex
from PyQt4.QtCore import QObject
from PyQt4.QtCore import Qt

from pyqt_widgets.models.item_model import ItemModel


class TreeItem(ItemModel):
    def __init__(self, data, parent=None):
        ItemModel.__init__(data, parent)


class TreeModel(QAbstractItemModel):
    """ TreeModel is an implementation of PyQt's QAbstractItemModel that overrides default indexing support to use
        python dictionaries mapping a column in the table header supplied to a value for said column. The goal here
        is to simplify indexing by being able to manage the data in a table based on string keys instead of arbitrary
        indexes, eliminating the need to cross-reference a header to find where to put a value.
    """

    def __init__(self, header, header_types=None, key_column=None, parent=None):
        """ TreeModel constructor
        :param header: The header to use
        :type header: Iterable
        :param parent: A QWidget that QT will give ownership of this Widget too.
        """
        super(TreeModel, self).__init__(parent)

        self.header = header
        self.header_types = header_types

        if not self.header_types:
            for column in self.header:
                self.header_types[column] = 'string'

        self.key_column = key_column

        if not self.key_column:
            self.key_column = self.header[0]

        self.root = TreeItem(header)

    def find_index(self, pointer):
        """ Helper method to find a QModelIndex that points to a given pointer.

            NOTE: Intended as an internal helper method, as you should almost never need a QModelIndex
                with this implementation, but left public and available in case it should be needed.

        :param pointer: The TableRow to find a QModelIndex for.
        :return: QModelIndex, or None.
        """
        for index in self.persistentIndexList():
            if index.column() != 0:
                continue

            if index.internalPointer() == pointer:
                return index

    def _connect_node(self, node):
        """ Helper function used to connect the data changed signals of our TreeItem to the notify_data_changed method.

        NOTE: This method is automatically called for all TableRow objects added to our model (properly), to support
            updating the model and any views automatically when the data of the TableRow is changed programatically.

        :param node: TableRow instance to connect.
        """
        node.changed.connect(lambda: self._notify_data_changed(node))

    # noinspection PyUnresolvedReferences
    def _notify_data_changed(self, node):
        """ The data for a given TreeItem has been changed, so emit the dataChanged signal to update views.

        :param node: The TreeItem that was changed.
        """
        row = node.row()
        top_left = self.createIndex(row, 0, node)
        bottom_right = self.createIndex(row, len(self.header), node)
        self.dataChanged.emit(top_left, bottom_right)

    def add_node(self, values, children=None, parent=None):
        """ Add a new root TreeItem to our model, using the values passed as the data.
            Optional args: children, parent
        :param values: A dictionary mapping the model's header to the values to use for this TreeItem.
        :param children: A collection of dictionaries mapping the model's header to the values to use for each child
            TreeItem.
        :param parent: The parent to give ownership of this TreeItem too, if not given, defaults to the root TreeItem
        :return: The TreeItem instance that was added.
        """
        if not parent:
            parent = self.root

        key = values[self.key_column]
        node = TreeItem(values, parent)

        if children:
            for values_ in children:
                self.add_node(values_, parent=node)

        parent.children[key] = node

        self._connect_node(node)
        return node

    def remove_node(self, key_value, parent=None):
        """ Remove the node that matches the key value and parent given.
        :param key_value: str
        :param parent: TreeItem
        :return: bool
        """
        if not parent:
            parent = self.root

        parent_index = self.find_index(parent)
        if key_value not in parent.children:
            raise KeyError('{key} not found in {node}'.format(key=key_value, node=parent[self.key_column]))

        row = parent.children.keys().index(key_value)

        self.removeRow(row, parent_index)

        return True

    def flags(self, index):
        """ QAbstractItemModel override method that is used to set the flags for the item at the given QModelIndex.
            Here, we just set all indexes to enabled, and selectable.
        :param index:
        """
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index, role):
        """ Return the data to display for the given index and the given role.
            This method should not be called directly. This method is called implicitly by the QTreeView that is
            displaying us, as the way of finding out what to display where.
        :param index:
        :param role:
        """
        if not index.isValid():
            return

        elif not role == Qt.DisplayRole:
            return

        item = index.internalPointer()
        column = self.header[index.column()]

        if column not in item.data:
            return

        data = item.data[column]

        if not isinstance(data, QObject):
            data = str(data)

        return data

    def index(self, row, col, parent):
        """ Return a QModelIndex instance pointing the row and column underneath the parent given.
            This method should not be called directly. This method is called implicitly by the QTreeView that is
            displaying us, as the way of finding out what to display where.
        :param row:
        :param col:
        :param parent:
        """
        if not parent or not parent.isValid():
            parent = self.root

        else:
            parent = parent.internalPointer()

        if row < 0 or row >= len(parent.children.keys()):
            return QModelIndex()

        row_name = parent.children.keys()[row]

        child = parent.children[row_name]
        return self.createIndex(row, col, child)

    def parent(self, index=None):
        """ Return the index of the parent TreeItem of a given index. If index is not supplied, return an invalid
                QModelIndex.
            Optional args: index

        :param index: QModelIndex
        :return:
        """
        if not index:
            return QModelIndex()

        elif not index.isValid():
            return QModelIndex()

        child = index.internalPointer()
        parent = child.parent

        if parent == self.root:
            return QModelIndex()

        elif child == self.root:
            return QModelIndex()

        return self.createIndex(parent.row(), 0, parent)

    def rowCount(self, parent):
        """ Return the number of rows a given index has under it. If an invalid QModelIndex is supplied, return the
                number of children under the root.

        :param parent: QModelIndex
        """
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parent = self.root

        else:
            parent = parent.internalPointer()

        return len(parent.children)

    def headerData(self, section, orientation, role):
        """ Return the header data for the given section, orientation and role. This method should not be called
            directly. This method is called implicitly by the QTreeView that is displaying us, as the way of finding
            out what to display where.
        :param section:
        :param orientation:
        :param role:
        """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.root.data[section]

    def __iter__(self):
        for child in self.root.children.itervalues():
            yield child
