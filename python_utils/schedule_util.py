# coding=utf-8
""" Module Docstring.

Author: Ian Davis
"""

from datetime import datetime

from Pyqt4.QtCore import QTimer

SECOND = 1000
MINUTE = 60 * SECOND


class ScheduledJob(object):
    """

    :param name:
    :param data:
    :param time:
    :param day:
    :param frequency:
    """
    DAILY = 1
    WEEKLY = 2

    def __init__(self, name, data, time, day=None, frequency=None):
        self.name = name
        self.data = data
        self.time = datetime.strptime(time, '%H:%M')
        self.day = day.lower()
        self.frequency = frequency

    def ready(self):
        """


        :return:
        """
        current_date = datetime.now()
        current_day = current_date.strftime('%A').lower()

        if self.day and not current_day == self.day:
            return False
        elif not current_date.hour == self.time.hour:
            return False
        elif not current_date.minute == self.time.minute:
            return False

        return True


class Scheduler(object):
    """

    """

    def __init__(self):
        self.jobs = {}
        self.schedule_checker = QTimer()
        self.schedule_checker.setInterval(MINUTE)

        self._connect_slots()

        self.schedule_checker.start()

    # noinspection PyUnresolvedReferences
    def _connect_slots(self):
        self.schedule_checker.timeout.connect(self.process_jobs)

    def add_job(self, name, data, time, day=None, frequency=None):
        """

        :param name:
        :param data:
        :param time:
        :param day:
        :param frequency:
        """
        self.jobs[name] = ScheduledJob(name, data, time, day=day, frequency=frequency)

    def start_job(self, name, job):
        """

        :param name:
        :param job:
        """
        pass

    def process_jobs(self):
        """


        """
        for name, job in self.jobs.iteritems():
            if job.ready():
                self.start_job(name, job)


class UpdateScheduler(Scheduler):
    """

    :param update_queue:
    """

    def __init__(self, update_queue):
        self.update_queue = update_queue
        super(UpdateScheduler, self).__init__()

    def start_job(self, ip_address, job):
        """

        :param ip_address:
        :param job:
        """
        self.update_queue.queue(ip_address, **job.data)
        self.update_queue.start_update(ip_address)
