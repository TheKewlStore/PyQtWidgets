# coding=utf-8
""" Module Docstring.

Author: Ian Davis
"""

from PyQt4.QtCore import QPropertyAnimation
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QApplication
from PyQt4.QtTest import QTest

from pyqt_widgets.util import os_util


def animated_resize(widget, width=0, height=0):
    """ Perform an animated resize on the given widget to the given width and height.

    :param widget: The widget to resize.
    :param width: The width to resize too.
    :param height: The height to resize too.
    :return: The QPropertyAnimation object that was created and started.
    """
    animation = QPropertyAnimation(widget, 'size')
    animation.setEndValue(QSize(width, height))
    animation.start()

    return animation


def left_click(widget):
    # noinspection PyArgumentList
    """

    :param widget:
    """
    # noinspection PyArgumentList
    QTest.mouseClick(widget, Qt.LeftButton)


def right_click(widget):
    # noinspection PyArgumentList
    """

    :param widget:
    """
    # noinspection PyArgumentList
    QTest.mouseClick(widget, Qt.RightButton)


def qt_application():
    """


    :return:
    """
    return QApplication(os_util.command_line_arguments())
