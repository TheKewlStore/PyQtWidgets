# coding=utf-8
""" Module Docstring.

*Author: Ian Davis
Last Updated: 9/17/2015
"""

import os
import sys

from datetime import datetime

from system import frozen_executable
from system import windows_platform


def make_path(*parts):
    """ Helper abstraction over os.path.join that handles drive letters properly on windows.

    :param parts: List-arg parts of the path to create.
    :return: The properly formatted path.
    """
    if parts[0].endswith(':') and windows_platform():
        # On NT based systems a separator still needs to follow drive letters ex C:
        # os.path.join does not seem to understand this, so we have to force it to happen by adding os.sep
        # to the list of parts to pass to os.path.join
        list_parts = list(parts)
        list_parts[0] += os.sep
        parts = list_parts

    if not parts[0].startswith('/') and not windows_platform():
        list_parts = list(parts)
        list_parts[0] = '/' + list_parts[0]
        parts = list_parts

    return os.path.join(*parts)


def is_file(path):
    """ Return whether a path points to an existing file or not.

    :param path: The path to check.
    """
    return os.path.isfile(path)


def is_directory(path):
    """ Return whether a path points to an existing directory or not.

    :param path: The path to check.
    """
    return os.path.isdir(path)


def exists(path):
    """ Return whether a path exists or not.

    :param path: The path to check.
    """
    return os.path.exists(path)


def filename(path):
    """ Return the filename stripped off from the given path.

    :param path: The path to the file.
    :return: The filename stripped from the path.
    """
    return os.path.basename(path)


def filenames(filepaths):
    """ Given a collection of filepaths, return a list of the filenames.

    :param filepaths: A collection of filepaths.
    :return: A list of only the filenames.
    """
    file_names = []

    for filepath in filepaths:
        file_names.append(filename(filepath))

    return file_names


def application_path():
    """ Get the path of the current application (handles bundled applications that set the "frozen" attribute).

    :return: The path of the current application.
    """

    if frozen_executable():
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def timestamped_path(*parts):
    file_name, extension = os.path.splitext(parts[-1])
    timestamp = datetime.now().strftime('%m-%d-%Y')

    new_filename = '{0}-{1}{2}'.format(file_name, timestamp, extension)
    new_parts = list(parts[:-1])
    new_parts.append(new_filename)

    return make_path(*new_parts)


def resource_file(file_name):
    """ Short-hand for getting a path to a file under the "resources" directory of the current application.

    :param file_name: The file-name or relative path to the file under the resources directory.
    :return: The absolute path to the file.
    """
    return make_path(application_path(), 'resources', file_name)


def example_file(file_name):
    """ Short-hand for getting a path to a file under the "examples" directory of the current application.

    :param file_name: The file-name or relative path to the file under the examples directory.
    :return: The absolute path to the file.
    """
    return make_path(application_path(), 'examples', file_name)


def working_directory():
    """ Return the current working directory.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.getcwd()
