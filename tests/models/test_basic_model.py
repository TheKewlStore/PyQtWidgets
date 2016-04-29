import pytest

from PyQt4.QtCore import QModelIndex
from PyQt4.QtCore import Qt

from pyqt_widgets.models.basic import BasicModel


MODEL_HEADER = ('Column1', 'Column2', 'Column3', 'Column4', 'Column5', )


@pytest.fixture()
def basic_model():
    return BasicModel(MODEL_HEADER)


def test_interface_methods(qtbot, basic_model):
    """ Verify functionality of the basic QAbstractTableModel interface methods for our table model override.
    """
    assert basic_model.columnCount() == 5
    assert basic_model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == 'Column1'
    assert basic_model.headerData(10, Qt.Horizontal, Qt.DisplayRole) == None

    with qtbot.waitSignal(basic_model.headerDataChanged, raising=True):
        basic_model.setHeaderData(0, Qt.Horizontal, 'NewColumn1', Qt.DisplayRole)
        assert basic_model.headerData(0, Qt.Horizontal, Qt.DisplayRole) == 'Column1'
