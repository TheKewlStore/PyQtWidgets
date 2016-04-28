# coding=utf-8
""" Define a QT Dialog that has two list views on either side, supporting pushing items from one list to the other.

Author: Ian Davis
"""

import sys

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QApplication
from PyQt4.QtGui import QDialog

from pyqt_widgets.models import TableModel

from message_boxes import warning_message
from ui.Ui_pushable_lists import Ui_pushable_list_dialog as PushableListsInterface


class PushableListsWidget(QDialog):
    """

    :param left_column:
    :param right_column:
    :param left_items:
    :param right_items:
    :param parent:
    """
    submitted = pyqtSignal(list, list)

    def __init__(self, left_column='Left', right_column='Right', left_items=None, right_items=None, parent=None):
        QDialog.__init__(self, parent)

        self.ui = PushableListsInterface()
        self.ui.setupUi(self)

        self.left_column = left_column
        self.right_column = right_column

        self.left_model = TableModel((left_column, ))
        self.right_model = TableModel((right_column, ))

        self._add_table_items(left_items, right_items)
        self._connect_slots()
        self._link_model_views()

    # noinspection PyUnresolvedReferences
    def _connect_slots(self):
        self.ui.push_left.clicked.connect(self.push_left)
        self.ui.push_right.clicked.connect(self.push_right)
        self.ui.ok.clicked.connect(self.submit)

    def _link_model_views(self):
        self.ui.left_list.setModel(self.left_model)
        self.ui.right_list.setModel(self.right_model)

    def submit(self):
        """


        """
        left_values = self.left_model.table_data.keys()
        right_values = self.right_model.table_data.keys()
        self.submitted.emit(left_values, right_values)
        self.done(0)

    def push_left(self):
        """ Take the items from the right model, and push them to the left model.

        :return:
        """
        try:
            selected_items = self.ui.right_list.pop_selected()
        except ValueError:
            warning_message('Selection required', 'You must make a selection in order to push items!')
            return

        for item in selected_items:
            converted_item = {self.left_column: item[self.right_column]}
            self.left_model.add_row(converted_item)

    def push_right(self):
        """ Take the items from the left model, and push them to the right model.

        :return:
        """
        try:
            selected_items = self.ui.left_list.pop_selected()
        except ValueError:
            warning_message('Selection required', 'You must make a selection in order to push items!')
            return

        for item in selected_items:
            converted_item = {self.right_column: item[self.left_column]}
            self.right_model.add_row(converted_item)

    def _add_table_items(self, left_items, right_items):
        if not left_items:
            left_items = []

        if not right_items:
            right_items = []

        for item in left_items:
            self.left_model.add_row({self.left_column: item})

        for item in right_items:
            self.right_model.add_row({self.right_column: item})


def print_results(left_items, right_items):
    """

    :param left_items:
    :param right_items:
    """
    print 'Left: {0}, Right: {1}'.format(left_items, right_items)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = PushableListsWidget(left_items=['Test1', 'Test2', 'Test3', 'Test4', 'Test5'])
    dialog.show()
    dialog.submitted.connect(print_results)
    app.exec_()
