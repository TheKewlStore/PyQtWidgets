# coding=utf-8
""" Module Docstring.

Author: Ian Davis
"""
from PyQt4 import QtCore
from PyQt4 import QtGui

from python_utils import pyqt_util

from ui.Ui_collapsible_widget import Ui_CollapsibleWidget as CollapsibleWidgetInterface


class CollapsibleWidget(QtGui.QWidget):
    """ Represent a container widget that supports collapsing it's child to preserve space.
    :param widget: The widget to collapse.
    :type widget: QtGui.QWidget
    :param parent: The parent of the container widget.
    """

    widget_collapsed = QtCore.pyqtSignal()
    widget_expanded = QtCore.pyqtSignal()

    def __init__(self, widget, parent=None):
        """
        :param widget: The widget to make collapsible
        :type widget: QWidget
        :param parent: The collapsible widgets' parent
        :type parent: QWidget
        """
        QtGui.QWidget.__init__(self, parent)

        self.ui = CollapsibleWidgetInterface()
        self.ui.setupUi(self)

        self._collapsed = False
        self._store_resize = True
        self.animation = None

        self.default_height = None
        self.default_width = None

        self._setup_widget(widget)
        self._connect_slots()

    def _setup_widget(self, widget):
        self.main_layout = QtGui.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)
        self.main_layout.addWidget(widget)
        self.ui.containerWidget.setLayout(self.main_layout)

    # noinspection PyUnresolvedReferences
    def _connect_slots(self):
        self.ui.butToggle.clicked.connect(self.toggle_widget)

    def redraw_widget(self):
        """ Redraw the container widget's size.
        """
        width = self.ui.containerWidget.width()
        height = self.ui.containerWidget.height()

        if self._collapsed:
            self.ui.containerWidget.resize(width, 0)
        else:
            self.ui.containerWidget.resize(width, height)

    def collapse(self):
        """ Collapse the widget contained.
        """
        self.animation = pyqt_util.animated_resize(self.ui.containerWidget, width=self.default_width, height=0)

        self.ui.butToggle.setText('+')
        self._collapsed = True

        self.ui.containerWidget.setVisible(False)

        self.widget_collapsed.emit()

    def expand(self):
        """ Expand the widget contained.
        """
        self.ui.containerWidget.setVisible(True)
        self.ui.butToggle.setText('-')

        self.animation = pyqt_util.animated_resize(self.ui.containerWidget, width=self.default_width, height=self.default_height)
        self._collapsed = False
        self._store_resize = True

        self.widget_expanded.emit()

    def toggle_widget(self):
        """ Toggle the widget's collapsed status.
        """
        if self._store_resize:
            self._store_resize = not self._store_resize
            self.default_height = self.ui.containerWidget.height()
            self.default_width = self.ui.containerWidget.width()
            print self.default_height, self.default_width

        if not self._collapsed:
            self.collapse()
        else:
            self.expand()
