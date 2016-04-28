# coding=utf-8
""" Module Docstring.

Author: Ian Davis
"""

from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QInputDialog, QLineEdit

from PyQt4.QtCore import QDir
from PyQt4.QtGui import QFileDialog

from ui.Ui_multiple_choice import Ui_MultipleChoiceDialog as MultipleChoiceInterface


class UserCancelledPromptException(Exception):
    pass


class MultipleChoicePrompt(QDialog):
    """

    :param title:
    :param message:
    :param options:
    :param parent:
    """

    def __init__(self, title, message, options, parent=None):
        QDialog.__init__(self, parent)

        self._title = title
        self._message = message
        self._options = options

        self.ui = MultipleChoiceInterface()
        self.ui.setupUi(self)

        self.title = title
        self.message = message
        self.options = options

        self._connect_slots()

    # noinspection PyUnresolvedReferences
    def _connect_slots(self):
        self.ui.ok_button.clicked.connect(lambda: self.done(QDialog.Accepted))
        self.ui.cancel_button.clicked.connect(lambda: self.done(QDialog.Rejected))

    @property
    def title(self):
        """


        :return:
        """
        return self._title

    @title.setter
    def title(self, new_title):
        """

        :param new_title:
        """
        self.setWindowTitle(new_title)
        self._title = new_title

    @property
    def message(self):
        """


        :return:
        """
        return self._message

    @message.setter
    def message(self, new_message):
        """

        :param new_message:
        """
        self.ui.combo_label.setText(new_message)
        self._message = new_message

    @property
    def options(self):
        """
        :return:
        """
        return self._options

    @options.setter
    def options(self, new_options):
        """

        :param new_options:
        """
        self.ui.main_combo.clear()
        self.ui.main_combo.addItems(new_options)
        self._options = new_options

    def selected_option(self):
        """


        :return:
        """
        return str(self.ui.main_combo.currentText())


def text_prompt(title, message):
    # noinspection PyTypeChecker, PyArgumentList
    """

    :param title:
    :param message:
    :return: :raise UserCancelledPromptException:
    """
    text, accepted = QInputDialog.getText(None, title, message, QLineEdit.Normal)

    if not accepted:
        raise UserCancelledPromptException(title, message)

    return str(text), accepted


def multiple_choice_prompt(title, message, options):
    """ Display a prompt with multiple options for the user to choose from.

    :param title: The title to display on the prompt.
    :param message: A message to display in the prompts window.
    :param options: The options to display for the prompt.
    :raise UserCancelledPromptException: If no option was selected or the dialog was cancelled.
    :return: The option that was selected.
    """
    dialog = MultipleChoicePrompt(title, message, options)
    result = dialog.exec_()

    if not result == QDialog.Accepted:
        raise UserCancelledPromptException()

    return dialog.selected_option()


def save_file_prompt(title, home_path=None, file_extension_spec=None, parent=None):
    """
    :param title:
    :param home_path:
    :param parent:
    :return:
    """
    if not home_path:
        home_path = QDir.homePath()

    if not file_extension_spec:
        file_extension_spec = 'All Files (*.*)'

    file_name = str(QFileDialog.getSaveFileName(parent, title, home_path, file_extension_spec))

    if not file_name:
        raise UserCancelledPromptException('No Filename selected.')

    return file_name


def open_file_prompt(title, home_path=None, file_extension_spec=None, parent=None):
    """ Display a prompt to choose an existing file from the filesystem.

    :param title: The title to display for the prompt.
    :param home_path: The default filesystem path for the prompt.
    :param file_extension_spec: The specification of what file types will be shown by the prompt.
    :param parent: The parent widget of the prompt.
    :raise UserCancelledPromptException: If no files are selected or the user presses the cancel button.
    :return: The filename that was selected.
    """
    if not home_path:
        home_path = QDir.homePath()

    if not file_extension_spec:
        file_extension_spec = 'All Files (*.*)'

    file_name = str(QFileDialog.getOpenFileName(parent, title, home_path, file_extension_spec, None))

    if not file_name:
        raise UserCancelledPromptException('No Filename selected.')

    return file_name


def open_files_prompt(title, home_path=None, file_extension_spec=None, parent=None):
    """ Display a prompt to choose multiple existing files from the filesystem.

    :param title: The title to display for the prompt.
    :param home_path: The default filesystem path for the prompt.
    :param file_extension_spec: The specification of what file types will be shown by the prompt.
    :param parent: The parent widget of the prompt.
    :raise UserCancelledPromptException: If not files are selected or the user presses the cancel button.
    :return: A list of filepaths that were selected in the prompt.
    """
    if not home_path:
        home_path = QDir.homePath()

    if not file_extension_spec:
        file_extension_spec = 'All Files (*.*)'

    file_paths = QFileDialog.getOpenFileNames(parent, title, home_path, file_extension_spec, None)
    file_paths = [str(filepath) for filepath in file_paths]

    if not file_paths:
        raise UserCancelledPromptException('No filenames selected.')

    return file_paths
