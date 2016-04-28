# coding=utf-8
""" Module Docstring.

Author: Ian Davis
"""
from PyQt4.QtCore import QObject
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import QThread
from PyQt4.QtCore import pyqtSignal


class ThreadPool(QObject):
    """ ThreadPool is a simple QObject subclass used to manage a "pool" of QThread or QThread subclasses.
    """
    finished = pyqtSignal()

    def __init__(self, max_threads=25, parent=None):
        """ ThreadPool constructor.

            :param max_threads: The maximum number of threads to allow to run concurrently.
            :param parent: The owner of this QObject, default: None
        """
        QObject.__init__(self, parent)
        self.max_threads = max_threads
        self.current_threads = []
        self.queued_threads = []
        self.terminating = False

    def start(self, thread):
        """ Most important interface method, pass it a QThread object, and it will determine
            whether or not it can start the thread now (depending on how many threads are currently running),
            or add it to a queued list of threads that it will start when another thread finishes.
        :param thread:
        """
        if len(self.current_threads) > self.max_threads:
            self.queued_threads.append(thread)
            return

        self.current_threads.append(thread)
        thread.start()

        thread.finished.connect(lambda: self.finish_thread(thread))

    def terminate(self):
        """ Another interface method that can be used to "attempt" to terminate all current threads.
            It does this by trying to join with the thread for 5 seconds, then calling QThread.terminate()
            to see if that can kill it.

            The behavior of terminate is not always dependable, especially when the thread is in a blocking
            call of execution.

            Other notable behaviors are to clear out the list of queued threads as well as current threads,
            and emit the ThreadPool.finished signal (bound).

            While it is "terminating", ThreadPool.terminating will be true. It will be false again once it is done.
        """
        self.terminating = True

        for thread in self.current_threads:
            # Attempt to force the thread to terminate by waiting until it's been killed.
            if not thread.wait(5000):
                thread.terminate()

        self.current_threads = []
        self.queued_threads = []
        self.finished.emit()

        self.terminating = False

    def finish_thread(self, thread):
        """ QT Slot method that gets connected to each thread's finish signal,
            and handles removing the thread from the current thread list, as well
            as popping a new thread from the queued list and starting it, if there
            are any. If there are no queued threads, it emits the finished signal,
            as all the threaded jobs are finished.
        :param thread:
        """
        if thread in self.current_threads:
            self.current_threads.remove(thread)

        if not self.terminating and len(self.queued_threads) >= 1:
            new_thread = self.queued_threads.pop(0)
            self.start(new_thread)

        if len(self.current_threads) < 1:
            # noinspection PyCallByClass,PyTypeChecker
            QTimer.singleShot(0, self.finished.emit)


class TargetThread(QObject):
    """ Simple QThread subclass made to support the ThreadPool interface,
        this thread uses the standard python approach to threading, of passing
        a callable to a Thread class.
    """
    finished = pyqtSignal()

    def __init__(self, target, *args, **kwargs):
        """ TargetThread constructor.

            :param target: callable that gets called in the new thread of execution.
            :param args: var-args to pass to the target callable.
            :param kwargs: keyword-args to pass to the target callable.
        """
        QObject.__init__(self)

        self.target = target
        self.args = args
        self.kwargs = kwargs

        self._thread = QThread()
        self.moveToThread(self._thread)
        self._connect_slots()

    def _connect_slots(self):
        self._thread.started.connect(self.run)

    def wait(self, timeout):
        """ Wait a given time, in seconds, for our thread to terminate.

        :param timeout: The time, in seconds, to wait.
        """
        self._thread.wait(timeout)

    def start(self):
        """ Start our QThread instance, beginning execution of our target thread.
        """
        self._thread.start()

    def run(self):
        """ Override of QThread run method that gets called from the new thread of execution,
            this is responsible for evoking the target callable with the args and kwargs given
            in the constructor. Lastly, it emits the finished signal to notify whom it may
            concern that our job is done.
        """
        self.target(*self.args, **self.kwargs)
        self.finished.emit()
        self._thread.finished.emit()

    def terminate(self):
        """ Terminate this thread of execution abruptly.
        """
        self._thread.terminate()
