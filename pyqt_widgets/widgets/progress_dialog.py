# coding=utf-8
""" Module Docstring.

Author: Ian Davis
Last Updated: 11/13/2015
"""

from PyQt4 import QtGui
from PyQt4 import QtCore

from ui.Ui_progress_dialog import Ui_progress_dialog as ProgressDialogInterface


class QProgressNotifier(QtCore.QObject):
    show_ = QtCore.pyqtSignal()
    current_step_ = QtCore.pyqtSignal(int)
    total_steps_ = QtCore.pyqtSignal(int)
    notify_operation_ = QtCore.pyqtSignal(str)
    complete_step_ = QtCore.pyqtSignal(str)
    complete_step_blank = QtCore.pyqtSignal()
    reset_ = QtCore.pyqtSignal()

    def __init__(self, dialog, parent=None):
        QtCore.QObject.__init__(self, parent)
        self.dialog = dialog

        self.connect_signals()

    def connect_signals(self):
        def _set_total_steps(steps):
            self.dialog.total_steps = steps

        def _set_current_step(step):
            self.dialog.current_step = step

        self.show_.connect(self.dialog.show)
        self.current_step_.connect(_set_current_step)
        self.total_steps_.connect(_set_total_steps)
        self.complete_step_.connect(self.dialog.complete_step)
        self.complete_step_blank.connect(self.dialog.complete_step)
        self.notify_operation_.connect(self.dialog.notify_operation)
        self.reset_.connect(self.dialog.reset)

    @property
    def current_step(self):
        """ Get the current step number the dialog is on.
        """
        return self.dialog.current_step

    @current_step.setter
    def current_step(self, new_step):
        """ Set the current step number the dialog is on.

        :param new_step: The new step number to jump too.
        """
        self.current_step_.emit(new_step)

    @property
    def total_steps(self):
        return self.dialog.total_steps

    @total_steps.setter
    def total_steps(self, new_total):
        self.total_steps_.emit(new_total)

    def notify_operation(self, operation):
        self.notify_operation_.emit(operation)

    def complete_step(self, operation_description=None):
        if operation_description:
            self.complete_step_.emit(operation_description)
        else:
            self.complete_step_blank.emit()

    def show(self):
        self.show_.emit()

    def reset(self):
        self.reset_.emit()


class ProgressDialog(QtGui.QWidget):
    """ Manage a popup dialog with a progress bar and log window to display status of a long-running operation.

    :param total_steps: The number of steps that will be executed in the operation.
    :param parent: The parent object of the QWidget.
    """
    operation_cancelled = QtCore.pyqtSignal()

    def __init__(self, operation_description=None, total_steps=100, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.ui = ProgressDialogInterface()
        self.ui.setupUi(self)

        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)

        if operation_description:
            self.setWindowTitle(operation_description)

        self._current_step = 0
        self._total_steps = total_steps

        self.ui.progress_bar.setMaximum(self._total_steps)

        # self.close_timer = QtCore.QTimer()
        # self.auto_close_seconds = 5

        self._connect_slots()

    @property
    def current_step(self):
        """ Get the current step number the dialog is on.
        """
        return self._current_step

    @current_step.setter
    def current_step(self, new_step):
        """ Set the current step number the dialog is on.

        :param new_step: The new step number to jump too.
        """
        self._current_step = new_step
        self.ui.progress_bar.setValue(self._current_step)

    @property
    def total_steps(self):
        """ Get the total steps defined for the operation we are tracking.
        """
        return self._total_steps

    @total_steps.setter
    def total_steps(self, new_steps):
        """ Set the total steps defined for the operation we are tracking.

        :param new_steps: The total number of steps for the operation.
        """
        self._total_steps = new_steps
        self.ui.progress_bar.setMaximum(self._total_steps)

    def notify_operation(self, operation_description):
        """ Append a line of text to the log window

        :param operation_description:
        """
        if len(operation_description) > 75:
            shortened_message = operation_description[:72] + '...'
        else:
            shortened_message = operation_description

        self.ui.log_window.append(shortened_message)

    def complete_step(self, operation_description=None):
        """ Complete the next step in the operation, writing an optional step description to the log window.

        :param operation_description: An optional description of the step that was completed to be written to the log window.
        """
        if operation_description:
            self.notify_operation(operation_description)

        self.current_step += 1

        if self.current_step == self.total_steps:
            self.finish()

    def finish(self, finished_message=None):
        if finished_message:
            self.notify_operation(finished_message)

        self.current_step = self.total_steps

        # self.ui.background_button.setText("Finish (Auto-close in 5)")
        self.ui.background_button.setText("Finish")

        self.ui.cancel_button.setEnabled(False)
        # self.close_timer.start(1000)

    def reset(self):
        """ Set our current step back to 0 to reset the operation.
        """
        # self.close_timer.stop()
        # self.auto_close_seconds = 5
        self.current_step = 0
        self.ui.cancel_button.setEnabled(True)
        self.ui.background_button.setText("Background")

    def _update_button_timer(self):
        self.auto_close_seconds -= 1

        # self.ui.background_button.setText("Finish (Auto-close in {0})".format(str(self.auto_close_seconds)))
        self.ui.background_button.setText("Finish")

        if self.auto_close_seconds <= 0:
            self.auto_close_seconds = 5
            self.close_timer.stop()
            # self.close()

    def _connect_slots(self):
        self.ui.background_button.clicked.connect(self.close)
        self.ui.cancel_button.clicked.connect(self.operation_cancelled.emit)
        # self.close_timer.timeout.connect(self._update_button_timer)
