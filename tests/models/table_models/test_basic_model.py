import pytest

from PyQt4.QtCore import QModelIndex
from PyQt4.QtCore import QVariant
from PyQt4.QtCore import Qt

from pyqt_widgets.models import TableModel, TableRow


TABLE_HEADER = ('Column1', 'Column2', 'Column3', 'Column4', 'Column5', )
TABLE_DATA = [{'Column1': 'Row1_Column1', 'Column2': 'Row1_Column2', 'Column3': 'Row1_Column3', 'Column4': 'Row1_Column4', 'Column5': 'Row1_Column5'},
              {'Column1': 'Row2_Column1', 'Column2': 'Row2_Column2', 'Column3': 'Row2_Column3', 'Column4': 'Row2_Column4', 'Column5': 'Row2_Column5'},
              {'Column1': 'Row3_Column1', 'Column2': 'Row3_Column2', 'Column3': 'Row3_Column3', 'Column4': 'Row3_Column4', 'Column5': 'Row3_Column5'},
              {'Column1': 'Row4_Column1', 'Column2': 'Row4_Column2', 'Column3': 'Row4_Column3', 'Column4': 'Row4_Column4', 'Column5': 'Row4_Column5'},
             ]


@pytest.fixture
def table_model():
    return TableModel(TABLE_HEADER)


def test_interface_methods(qtbot, table_model):
    """ Verify functionality of the basic QAbstractTableModel interface methods for our table model override.
    """
    assert table_model.flags(table_model.index(0, 0)) == Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable


def test_add_row(qtbot, table_model):
    """ Verify functionality of adding a row(s) to the model.
    """

    for table_row, data in enumerate(TABLE_DATA):
        with qtbot.waitSignal(table_model.rowsInserted, raising=True):
            with qtbot.waitSignal(table_model.rowsAboutToBeInserted, raising=True):
                table_model.add_row(data)

        key_value = 'Row{0}_Column1'.format(table_row + 1)
        actual_row = table_model.table_data[key_value]
        expected_row = TABLE_DATA[table_row]

        assert actual_row['Column1'] == expected_row['Column1']
        assert actual_row['Column2'] == expected_row['Column2']
        assert actual_row['Column3'] == expected_row['Column3']
        assert actual_row['Column4'] == expected_row['Column4']
        assert actual_row['Column5'] == expected_row['Column5']
        assert table_model.rowCount() == table_row + 1
        assert key_value in table_model.table_data

    table_row = table_model.add_row({'Column1': 'Row5_Column1', 'Column3': 'Row5_Column3'})
    assert table_row['Column1'] == 'Row5_Column1'
    assert table_row['Column2'] == ''
    assert table_row['Column3'] == 'Row5_Column3'
    assert table_row['Column4'] == ''
    assert table_row['Column5'] == ''


def test_remove_rows(qtbot, table_model):
    """ Verify functionality of the various ways of removing rows from the model.
    """
    table_row = table_model.add_row(TABLE_DATA[0])

    with qtbot.waitSignal(table_model.layoutChanged, raising=True):
        with qtbot.waitSignal(table_model.layoutAboutToBeChanged, raising=True):
            table_model.remove_table_rows([table_row])

    assert table_model.rowCount() == 0
    assert 'Row1Column1' not in table_model.table_data

    table_rows = []

    for data in TABLE_DATA:
        table_rows.append(table_model.add_row(data))

    with qtbot.waitSignal(table_model.layoutChanged, raising=True):
        with qtbot.waitSignal(table_model.layoutAboutToBeChanged, raising=True):
            table_model.remove_table_rows(table_rows)

    for data in TABLE_DATA:
        table_model.add_row(data)

    with qtbot.waitSignal(table_model.rowsRemoved, raising=True):
        with qtbot.waitSignal(table_model.rowsAboutToBeRemoved, raising=True):
            table_model.removeRows(0, 4)


def test_data_functions(qtbot, table_model):
    """ Verify that the interface methods data and setData follow all expected procedures and emit signals properly.
    """
    table_row = table_model.add_row(TABLE_DATA[0])
    index = table_model.index(0, 0)

    assert table_model.data(index, Qt.DisplayRole) == table_row['Column1']

    with qtbot.waitSignal(table_model.dataChanged, raising=True):
        with qtbot.waitSignal(table_row.changed, raising=True):
            table_row['Column1'] = 'Row1_Column1_New'

    assert table_model.data(index, Qt.DisplayRole) == 'Row1_Column1_New'
    assert table_model.data(index, Qt.TextAlignmentRole) == Qt.AlignCenter
    assert table_model.data(index, Qt.EditRole) == None

    assert table_model.setData(index, 'Row1_Column1_Old', Qt.DisplayRole) == False

    with qtbot.waitSignal(table_model.dataChanged, raising=True):
        with qtbot.waitSignal(table_row.changed, raising=True):
            assert table_model.setData(index, 'Row1_Column1_Old', Qt.EditRole) == True

    assert table_row['Column1'] == 'Row1_Column1_Old'

    invalid_index = QModelIndex()
    unbound_index = table_model.index(0, 10)

    assert table_model.data(invalid_index, Qt.DisplayRole) == None
    assert table_model.data(unbound_index, Qt.DisplayRole) == None
    assert table_model.setData(invalid_index, 'Row1_Column1_Old', Qt.EditRole) == False
    assert table_model.setData(unbound_index, 'Row1_Column10_Old', Qt.EditRole) == False

    data = QVariant('Row1_Column1_New')

    with qtbot.waitSignal(table_model.dataChanged, raising=True):
        with qtbot.waitSignal(table_row.changed, raising=True):
            assert table_model.setData(index, data, Qt.EditRole) == True

    assert table_row['Column1'] == data
    assert table_model.data(index, Qt.DisplayRole) == data

    table_row['Column1'] = None
    assert table_model.data(index, Qt.DisplayRole) == ''


def test_match_pattern(table_model):
    for data in TABLE_DATA:
        table_model.add_row(data)

    table_rows = table_model.match_pattern(0, 'Row[0-9]_Column1')
    assert len(table_rows) == 0

    table_rows = table_model.match_pattern(1, 'Row[0-9]_Column2')
    assert len(table_rows) == 0

    table_rows = table_model.match_pattern(2, 'Row[0-9]_Column5')
    assert len(table_rows) == 4

    table_rows = table_model.match_pattern(0, 'Row1_Column1')
    assert len(table_rows) == 3

    table_rows = table_model.match_pattern(0, 'Row[1-3]_Column1')
    assert len(table_rows) == 1

    table_rows = table_model.match_pattern(0, '\Row(1-3_Column1')


def test_pack_dictionary(table_model):
    only_one = {'Column1': 'Value1'}
    packed = table_model.pack_dictionary(only_one)

    for column in TABLE_HEADER:
        assert column in packed

    multiple = {'Column1': 'Value1', 'Column3': 'Value3', 'Column5': 'Value5'}
    packed = table_model.pack_dictionary(multiple)

    for column in TABLE_HEADER:
        assert column in packed
