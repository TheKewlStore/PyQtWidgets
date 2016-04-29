import pytest

from pyqt_widgets.models.item_model import ItemModel


DATA = {'Column1': 'Value1',
        'Column2': 'Value2',
        'Column3': 'Value3',
        'Column4': 'Value4',
        }
PARENT = ItemModel(DATA)


@pytest.fixture
def item_model():
    return ItemModel(DATA, parent=PARENT)


def test_item_get(item_model):
    assert item_model.get('Column1') == 'Value1'
    assert item_model.get('Column2') == 'Value2'
    assert item_model.get('Column3') == 'Value3'
    assert item_model.get('Column4') == 'Value4'
    assert item_model.get('Column5') == None
    assert item_model.get('Column5', 'test') == 'test'


def test_item_getter(item_model):
    assert item_model['Column1'] == 'Value1'
    assert item_model['Column2'] == 'Value2'
    assert item_model['Column3'] == 'Value3'
    assert item_model['Column4'] == 'Value4'

    with pytest.raises(KeyError):
        assert item_model['Column5'] == 'Value5'


def test_item_set(qtbot, item_model):
    with qtbot.waitSignal(item_model.changed, raising=True):
        item_model['Column1'] = 'NewValue1'

    with qtbot.waitSignal(item_model.changed, raising=True):
        item_model['Column5'] = 'NewValue5'

    assert item_model['Column1'] == 'NewValue1'
    assert item_model['Column5'] == 'NewValue5'


def test_item_parent(item_model):
    assert item_model.parent == PARENT


def test_dictionary_interface(item_model):
    assert sorted(item_model.iteritems()) == sorted(DATA.iteritems())
    assert sorted(item_model.iterkeys()) == sorted(DATA.iterkeys())
    assert sorted(item_model.itervalues()) == sorted(DATA.itervalues())
    assert str(item_model) == str(DATA)
    assert 'Column1' in item_model
