import pytest

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
    assert tree_model.columnCount() == 5
    assert tree_model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == 'Column1'

    with qtbot.waitSignal(tree_model.headerDataChanged, raising=True):
        tree_model.setHeaderData(0, Qt.Horizontal, 'NewColumn1', Qt.DisplayRole)
        assert tree_model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == 'Column1'

    assert tree_model.flags(tree_model.index(0, 0)) == Qt.ItemIsEnabled | Qt.ItemIsSelectable


def test_add_node(qtbot, tree_model):
    """ Verify functionality of adding a row(s) to the model.
    """

    for table_row, data in enumerate(TREE_DATA):
        actual_node = tree_model.add_node(data)

        key_value = 'Row{0}_Column1'.format(table_row + 1)
        expected_node = TREE_DATA[table_row]

        assert actual_node['Column1'] == expected_node['Column1']
        assert actual_node['Column2'] == expected_node['Column2']
        assert actual_node['Column3'] == expected_node['Column3']
        assert actual_node['Column4'] == expected_node['Column4']
        assert actual_node['Column5'] == expected_node['Column5']
        assert tree_model.rowCount() == table_row + 1
        assert key_value in tree_model.root.children

    table_row = tree_model.add_node({'Column1': 'Row5_Column1', 'Column3': 'Row5_Column3'})
    assert table_row['Column1'] == 'Row5_Column1'
    assert table_row['Column2'] == ''
    assert table_row['Column3'] == 'Row5_Column3'
    assert table_row['Column4'] == ''
    assert table_row['Column5'] == ''


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


def test_data_functions(qtbot, tree_model):
    """ Verify that the interface methods data and setData follow all expected procedures and emit signals properly.
    """
    table_row = tree_model.add_node(TREE_DATA[0])
    index = tree_model.index(0, 0)
    assert tree_model.data(index, Qt.DisplayRole) == table_row['Column1']

    with qtbot.waitSignal(tree_model.dataChanged, raising=True):
        with qtbot.waitSignal(table_row.changed, raising=True):
            table_row['Column1'] = 'Row1_Column1_New'

    assert tree_model.data(index, Qt.DisplayRole) == 'Row1_Column1_New'

    invalid_index = tree_model.index(-1, -1)
    unbound_index = tree_model.index(0, 10)

    assert tree_model.setData(index, 'Row1_Column1_Old', Qt.DisplayRole) == False
    assert tree_model.setData(invalid_index, 'Row1_Column1_Old', Qt.EditRole) == False
    assert tree_model.setData(unbound_index, 'Row1_Column10_Old', Qt.EditRole) == False

    with qtbot.waitSignal(tree_model.dataChanged, raising=True):
        with qtbot.waitSignal(table_row.changed, raising=True):
            assert tree_model.setData(index, 'Row1_Column1_Old', Qt.EditRole) == True

    assert table_row['Column1'] == 'Row1_Column1_Old'


def test_pack_dictionary(tree_model):
    only_one = {'Column1': 'Value1'}
    packed = tree_model.pack_dictionary(only_one)

    for column in TREE_HEADER:
        assert column in packed

    multiple = {'Column1': 'Value1', 'Column3': 'Value3', 'Column5': 'Value5'}
    packed = tree_model.pack_dictionary(multiple)

    for column in TREE_HEADER:
        assert column in packed
