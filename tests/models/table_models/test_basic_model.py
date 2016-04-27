import pytest

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


def test_model_methods(qtbot, table_model):
    assert table_model.rowCount() == 0
    assert table_model.columnCount() == 5
    assert table_model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == 'Column1'

    with qtbot.waitSignal(table_model.headerDataChanged, raising=True):
        table_model.setHeaderData(0, Qt.Horizontal, Qt.DisplayRole)


def test_add_row(qtbot, table_model):
    for table_row, data in enumerate(TABLE_DATA):
        with qtbot.waitSignal(table_model.rowsInserted, raising=True):
            with qtbot.waitSignal(table_model.rowsAboutToBeInserted, raising=True):
                table_model.add_row(data)

        actual_row = table_model.table_data['Row{0}_Column1'.format(table_row + 1)]
        expected_row = TABLE_DATA[table_row]

        assert actual_row['Column1'] == expected_row['Column1']
        assert actual_row['Column2'] == expected_row['Column2']
        assert actual_row['Column3'] == expected_row['Column3']
        assert actual_row['Column4'] == expected_row['Column4']
        assert actual_row['Column5'] == expected_row['Column5']

    assert table_model.rowCount() == 4
    assert table_model.columnCount() == 5
