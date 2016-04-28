# coding=utf-8
""" Module Docstring.

Author: Ian Davis
"""

from contextlib import contextmanager

from PyQt4.QtGui import QMessageBox


def information_message(title, message):
    # noinspection PyTypeChecker, PyArgumentList
    """

    :param title:
    :param message:
    :return:
    """
    # noinspection PyArgumentList
    return QMessageBox.information(None, title, message)


def warning_message(title, message):
    # noinspection PyTypeChecker, PyArgumentList
    """

    :param title:
    :param message:
    :return:
    """
    # noinspection PyArgumentList
    return QMessageBox.warning(None, title, message)


def confirmation_dialog(title, message):
    # noinspection PyTypeChecker, PyArgumentList
    """

    :param title:
    :param message:
    :return:
    """
    result = QMessageBox.warning(None, title, message, QMessageBox.StandardButtons(QMessageBox.No | QMessageBox.Yes))

    return result == QMessageBox.Yes


@contextmanager
def background_message(title, message):
    message_box = QMessageBox()
    message_box.setWindowTitle(title)
    message_box.setText(message)
    message_box.show()
    yield
    message_box.close()
