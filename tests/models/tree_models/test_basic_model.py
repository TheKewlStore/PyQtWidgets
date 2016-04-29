import pytest

from PyQt4.QtCore import QModelIndex
from PyQt4.QtCore import QVariant
from PyQt4.QtCore import Qt

from pyqt_widgets.models import TreeModel, TreeItem


TREE_HEADER = ('Column1', 'Column2', 'Column3', 'Column4', 'Column5', )
TREE_DATA = [{'Column1': 'Row1_Column1', 'Column2': 'Row1_Column2', 'Column3': 'Row1_Column3', 'Column4': 'Row1_Column4', 'Column5': 'Row1_Column5'},
             {'Column1': 'Row2_Column1', 'Column2': 'Row2_Column2', 'Column3': 'Row2_Column3', 'Column4': 'Row2_Column4', 'Column5': 'Row2_Column5'},
             {'Column1': 'Row3_Column1', 'Column2': 'Row3_Column2', 'Column3': 'Row3_Column3', 'Column4': 'Row3_Column4', 'Column5': 'Row3_Column5'},
             {'Column1': 'Row4_Column1', 'Column2': 'Row4_Column2', 'Column3': 'Row4_Column3', 'Column4': 'Row4_Column4', 'Column5': 'Row4_Column5'},
            ]


@pytest.fixture
def tree_model():
    return TreeModel(TREE_HEADER)


def test_interface_methods(qtbot, tree_model):
    """ Verify functionality of the basic QAbstractTableModel interface methods for our table model override.
    """
    assert tree_model.flags(tree_model.index(0, 0)) == Qt.ItemIsEnabled | Qt.ItemIsSelectable


def test_add_node(qtbot, tree_model):
    """ Verify functionality of adding a row(s) to the model.
    """

    for index, data in enumerate(TREE_DATA):
        actual_node = tree_model.add_node(data)

        key_value = 'Row{0}_Column1'.format(index + 1)
        expected_node = TREE_DATA[index]

        assert actual_node['Column1'] == expected_node['Column1']
        assert actual_node['Column2'] == expected_node['Column2']
        assert actual_node['Column3'] == expected_node['Column3']
        assert actual_node['Column4'] == expected_node['Column4']
        assert actual_node['Column5'] == expected_node['Column5']
        assert tree_model.rowCount() == index + 1
        assert key_value in tree_model.root.children

    tree_node = tree_model.add_node({'Column1': 'Row5_Column1', 'Column3': 'Row5_Column3'})
    assert tree_node['Column1'] == 'Row5_Column1'
    assert tree_node['Column2'] == ''
    assert tree_node['Column3'] == 'Row5_Column3'
    assert tree_node['Column4'] == ''
    assert tree_node['Column5'] == ''

    tree_node = tree_model.add_node(TREE_DATA[0], children=[TREE_DATA[1], TREE_DATA[2]])
    assert len(tree_node.children) == 2


def test_find_node(tree_model):
    tree_node = tree_model.add_node(TREE_DATA[0])
    found_node = tree_model.find_node(tree_node['Column1'])
    assert found_node == tree_node

    with pytest.raises(KeyError):
        found_node = tree_model.find_node('Row5_Column1')


def test_remove_node(qtbot, tree_model):
    """ Verify functionality of the various ways of removing rows from the model.
    """
    tree_node = tree_model.add_node(TREE_DATA[0])

    with qtbot.waitSignal(tree_model.layoutChanged, raising=True):
        with qtbot.waitSignal(tree_model.layoutAboutToBeChanged, raising=True):
            tree_model.remove_node(tree_node)

    assert tree_model.rowCount() == 0
    assert 'Row1Column1' not in tree_model.root.children

    tree_nodes = []

    for data in TREE_DATA:
        tree_nodes.append(tree_model.add_node(data))

    for node in tree_nodes:
        with qtbot.waitSignal(tree_model.layoutChanged, raising=True):
            with qtbot.waitSignal(tree_model.layoutAboutToBeChanged, raising=True):
                tree_model.remove_node(node)

    parent_node = tree_model.add_node(TREE_DATA[0])
    child_node = tree_model.add_node(TREE_DATA[1], parent=parent_node)

    del parent_node.children[child_node['Column1']]

    with pytest.raises(KeyError):
        tree_model.remove_node(child_node)


def test_parent_index(tree_model):
    parent_node = tree_model.add_node(TREE_DATA[0])
    child_node = tree_model.add_node(TREE_DATA[1], parent=parent_node)

    parent_index = tree_model.index(0, 0)
    child_index = tree_model.index(0, 0, parent=parent_index)

    assert tree_model.data(child_index, Qt.DisplayRole) == child_node['Column1']

    assert tree_model.parent() == QModelIndex()
    assert tree_model.parent(QModelIndex()) == QModelIndex()
    assert tree_model.parent(parent_index) == QModelIndex()
    assert tree_model.parent(child_index) == parent_index


def test_data_functions(qtbot, tree_model):
    """ Verify that the interface methods data and setData follow all expected procedures and emit signals properly.
    """
    tree_node = tree_model.add_node(TREE_DATA[0])
    index = tree_model.index(0, 0)

    assert tree_model.data(index, Qt.DisplayRole) == tree_node['Column1']

    with qtbot.waitSignal(tree_model.dataChanged, raising=True):
        with qtbot.waitSignal(tree_node.changed, raising=True):
            tree_node['Column1'] = 'Row1_Column1_New'

    assert tree_model.data(index, Qt.DisplayRole) == 'Row1_Column1_New'
    assert tree_model.data(index, Qt.TextAlignmentRole) == Qt.AlignCenter
    assert tree_model.data(index, Qt.EditRole) == None

    assert tree_model.setData(index, 'Row1_Column1_Old', Qt.DisplayRole) == False

    with qtbot.waitSignal(tree_model.dataChanged, raising=True):
        with qtbot.waitSignal(tree_node.changed, raising=True):
            assert tree_model.setData(index, 'Row1_Column1_Old', Qt.EditRole) == True

    assert tree_node['Column1'] == 'Row1_Column1_Old'

    invalid_index = QModelIndex()
    unbound_index = tree_model.index(0, 10)

    assert tree_model.data(invalid_index, Qt.DisplayRole) == None
    assert tree_model.data(unbound_index, Qt.DisplayRole) == None

    assert tree_model.setData(invalid_index, 'Row1_Column1_Old', Qt.EditRole) == False
    assert tree_model.setData(unbound_index, 'Row1_Column10_Old', Qt.EditRole) == False

    data = QVariant('Row1_Column1_New')

    with qtbot.waitSignal(tree_model.dataChanged, raising=True):
        with qtbot.waitSignal(tree_node.changed, raising=True):
            assert tree_model.setData(index, data, Qt.EditRole) == True

    assert tree_node['Column1'] == data
    assert tree_model.data(index, Qt.DisplayRole) == data

    tree_node['Column1'] = None
    assert tree_model.data(index, Qt.DisplayRole) == ''


def test_pack_dictionary(tree_model):
    only_one = {'Column1': 'Value1'}
    packed = tree_model.pack_dictionary(only_one)

    for column in TREE_HEADER:
        assert column in packed

    multiple = {'Column1': 'Value1', 'Column3': 'Value3', 'Column5': 'Value5'}
    packed = tree_model.pack_dictionary(multiple)

    for column in TREE_HEADER:
        assert column in packed


def test_row_count(tree_model):
    tree_node = tree_model.add_node(TREE_DATA[0])
    assert tree_model.rowCount() == 1
    assert tree_model.rowCount(QModelIndex()) == 1

    invalid_index = tree_model.index(0, 1)
    assert tree_model.rowCount(invalid_index) == 0

    child_node1 = tree_model.add_node(TREE_DATA[1], parent=tree_node)
    child_node2 = tree_model.add_node(TREE_DATA[2], parent=tree_node)

    parent_index = tree_model.index(0, 0)

    assert tree_model.rowCount(parent_index) == 2

    assert tree_model.root.row() == 0


def test_iterator(tree_model):
    tree_nodes = []

    for data in TREE_DATA:
        tree_nodes.append(tree_model.add_node(data))

    for actual_node, expected_node in zip(tree_model, tree_nodes):
        assert actual_node == expected_node
