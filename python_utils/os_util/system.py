# coding=utf-8
""" Module Docstring.

Author: Ian Davis
Last Updated: 9/17/2015
"""

import ctypes
import numbers
import os
import re
import platform
import sys

import path

try:
    import wmi
except ImportError:
    wmi = None

from collections import namedtuple

from command import shell_command
from exceptions import UnknownModelError


def windows_platform():
    """ Return whether or not we are running an nt system.
    """
    return os.name == 'nt'


def sys_exit(exit_code):
    """

    :param exit_code:
    """
    sys.exit(exit_code)


def check_java_process(process_id, jars):
    """ Check to see if a specific jar is running, given the name of jars to check and the java PID.

    :param process_id: The process id of the java executable.
    :param jars: A list of the jars to check for.
    :return: True or False whether or not any of the jars in the list matched a running jar.
    """
    cmd = ('tasklist',
           '/fi',
           'pid eq {process_id}'.format(process_id=process_id),
           '/v',
           'fo',
           'csv')

    exit_code, stdout, stderr = shell_command(cmd)
    tasks = stdout.split('\r\n')

    for task in tasks:
        tokens = task.split(',')

        if not tokens:
            return False

        if not tokens[0]:
            return False

        if tokens[0] == '"Image Name"':
            return False

        jar_name = tokens[-1][1:-1]

        if jar_name in jars:
            return True

    return False


def process_running(process_name):
    """ Use psutil to determine if a given process is currently running.

    :param process_name: The name of the process to look for.
    :return: True or False depending on whether the process is running.
    """
    import psutil

    for process in psutil.process_iter():
        try:
            process_info = process.as_dict(attrs=['pid', 'name', 'exe', 'cmdline', 'cwd'])

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        if not process_info['name']:
            continue

        if process_info['name'] == process_name:
            return True

        elif check_java_process(process_id=process_info['pid'], jars=[process_name]):
            return True

    return False


def frozen_executable():
    """ Helper method to determine whether or not we are running as a frozen executable.
    """
    return getattr(sys, 'frozen', False)


def disk_usage():
    """Return drive free space (in bytes)."""
    DiskInformation = namedtuple('disk_information', ('free', 'used'))

    if platform.system() == 'Windows':
        total_bytes, free_bytes = ctypes.c_ulonglong(), ctypes.c_ulonglong()
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p('C:/'), None, ctypes.byref(total_bytes), ctypes.byref(free_bytes))
        used_bytes = total_bytes.value - free_bytes.value
    else:
        stat = os.statvfs('/')
        free_bytes = stat.f_bavail * stat.f_frsize
        used_bytes = (stat.f_blocks - stat.f_bfree) * stat.f_frsize

    return DiskInformation(free_bytes, used_bytes)


def flash_statistics():
    """ Calculate and return the flash used and flash free, in megabytes.

    :return: flash used and flash free, as a tuple.
    """
    # TODO: flash_statistics: test for posix and windows machines.
    disk_information = disk_usage()

    flash_used = disk_information.used
    flash_free = disk_information.free

    if not isinstance(flash_used, numbers.Number):
        flash_used = flash_used.value

    if not isinstance(flash_free, numbers.Number):
        flash_free = flash_free.value

    flash_used = flash_used / 1024 / 1024
    flash_free = flash_free / 1024 / 1024

    return flash_used, flash_free


def memory_statistics():
    """ Calculate and return the memory used and memory free, in megabytes.

    :return: memory used and memory free, as a tuple.
    """
    # TODO: memory_statistics: Test function for all system types.
    if windows_platform():
        return _windows_memory()
    else:
        return _linux_memory()


def _windows_memory():
    if not wmi:
        raise OSError('Python module wmi is not available on this system!')

    component = wmi.WMI()

    # total memory in bytes
    interface = component.Win32_ComputerSystem()[-1]
    memory_total = (int(interface.TotalPhysicalMemory) / 1024) / 1024

    # free memory in kilobytes
    operating_system = component.Win32_OperatingSystem()[-1]
    memory_free = (int(operating_system.FreePhysicalMemory) / 1024)

    memory_used = memory_total - memory_free

    return memory_used, memory_free


def _linux_memory():
    memory_free_pattern = re.compile(r"^MemFree:\s+[0-9]+\s+kB$")
    memory_total_pattern = re.compile(r"^MemTotal:\s+[0-9]+\s+kB$")
    memory_free = None
    memory_total = None

    with open('/proc/meminfo', 'r') as memory_file:
        for line in memory_file:
            if memory_free_pattern.match(line):
                tokens = line.split()
                memory_free = int(tokens[-2])
            elif memory_total_pattern.match(line):
                tokens = line.split()
                memory_total = int(tokens[-2])

    if not memory_free or not memory_total:
        raise ValueError('Could not retrieve necessary memory data from /proc/meminfo!')

    memory_used = memory_total - memory_free
    return memory_used, memory_free


def version_data():
    """ Retrieve the software version number and backend version number for the device.

    :return: software version number, backend version number, as a tuple.
    """
    # TODO: version_data: Implement function.
    software_version = ''
    backend_version = ''
    return software_version, backend_version


def model_name():
    """ Return the fully qualified model name for the given device.

    :return: Model name as a string.
    :raises: UnknownModelError
    """
    # TODO: model_name: Test function on htseries devices.
    try:
        with SerialFlashInformation() as serial_flash_info:
            return serial_flash_info.scale_style
    except (RuntimeError, OSError, IOError):
        raise UnknownModelError()


BLANK_SECTION = '\xff'
STYLE_START = '<SStyle>'
STYLE_END = '</SStyle>'


class SerialFlashInformation(object):
    """ Represent the information stored in serial flash on this device.
    """

    def __init__(self):
        self._scale_style = None
        self.board_assembly = None
        self.board_revision = None
        self.manufacture_date = None
        self.serial_number = None

    @property
    def scale_style(self):
        """ Convert first two letters of scale_style to uppercase, and the third letter to lowercase.
        """
        return self._scale_style[:2].upper() + self._scale_style[2] + self._scale_style[3:]

    def _read(self):
        if windows_platform():
            dump_filepath = self._dump_windows()
        else:
            dump_filepath = self._dump_linux()

        with open(dump_filepath, 'rb') as flash_dump:
            flash_data = flash_dump.read()

        section_marker = flash_data[0]

        if section_marker == BLANK_SECTION:
            raise OSError('Serial flash corrupt or missing and cannot be read!')

        self._read_scale_style(flash_data)

    def _read_scale_style(self, flash_data):
        start_index = flash_data.index(STYLE_START) + len(STYLE_START)
        end_index = flash_data.index(STYLE_END)
        self._scale_style = flash_data[start_index:end_index].strip(' "\'')

    @staticmethod
    def _dump_windows():
        if not path.is_directory(path.make_path('C:/', 'Program Files', 'Hobart', 'Bin')):
            raise OSError('Serial flash not found and cannot be read!')

        dump_filepath = 'C:/Program Files/Hobart/Bin/manufacturing_dump.bin'

        # arguments = ('C:/Program Files/Hobart/Bin/SPIFlashTest.exe', 'd', '100000', dump_filepath)
        # shell_command(arguments)

        return dump_filepath

    @staticmethod
    def _dump_linux():
        if not path.is_directory(path.make_path('/', 'dev', 'mtd3block3')):
            raise OSError('Serial flash not found and cannot be read!')

        return path.make_path('/', 'dev', 'mtd3')

    def __enter__(self):
        self._read()
        return self

    def __exit__(self, exc_type, traceback, value):
        return
