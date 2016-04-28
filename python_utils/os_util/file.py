# coding=utf-8
""" Module Docstring.

Author: Ian Davis
Last Updated: 9/17/2015
"""

import glob
import hashlib
import os
import shutil

import exceptions
import path

from contextlib import contextmanager

from path import make_path
from system import windows_platform


def clear_file(file_name):
    """ Clear all data from the specified file path.

    :param file_name: The path to the file to clear.
    """
    with open(file_name, 'w') as text_file:
        text_file.truncate()


def copy_file(original_path, destination_path):
    """ Copy file at original_path to file at destination_path

    :param original_path: The source file path.
    :param destination_path: The destination file path.
    """
    shutil.copyfile(original_path, destination_path)


def make_directory(filepath):
    """ Make the directory pointed too by path.

    :param filepath: The path to the directory to create.
    """
    if not filepath:
        return

    if not os.path.exists(filepath):
        os.mkdir(filepath)


def copy_directory_tree(directory_path, destination_directory_path, ignore_function=None):
    shutil.copytree(directory_path, destination_directory_path, ignore=ignore_function)


def remove_directory_tree(directory_path):
    shutil.rmtree(directory_path)


def move(old_location, new_location):
    return os.rename(old_location, new_location)


def rename(filepath, new_file_name=None, prefix=None, suffix=None, new_extension=None):
    """ Rename the file at path to new_file_name, optionally appending a prefix, suffix, and changing the extension.

    :param filepath: The path of the original file.
    :param new_file_name: The file name to rename too.
    :param prefix: An optional prefix to add too the name.
    :param suffix: An optional suffix to add too the name.
    :param new_extension: An optional extension to change too.
    :return: The new file path after rename.
    """
    old_file_path, old_extension = os.path.splitext(filepath)
    old_file_name = os.path.basename(old_file_path)
    file_dir = os.path.dirname(old_file_path)

    if not new_file_name:
        new_file_name = old_file_name

    if not new_extension:
        new_extension = old_extension

    if prefix:
        new_file_name = prefix + new_file_name

    if suffix:
        new_file_name += suffix

    new_file_path = os.path.join(file_dir, new_file_name + new_extension)
    os.rename(filepath, new_file_path)
    return new_file_path


def hobart_directory():
    if windows_platform():
        return make_path('C:', 'Program Files', 'Hobart')
    else:
        return make_path('usr', 'local', 'hobart')


def find_hobart_database(directory):
    """ Find a hobart compatible database in the given directory, if one exists.

    :param directory: The directory to search for a database in.
    :raise NoDatabaseError: If no hobart compatible database is found.
    :raise InvalidDirectoryError: If the directory specified does not exist.
    :return: The path to the database found.
    """
    if not path.is_directory(directory):
        raise exceptions.InvalidDirectoryError(directory)

    hobart_database_name = 'dbft?.db'
    hobart_glob = path.make_path(directory, hobart_database_name)
    results = glob.glob(hobart_glob)

    if not results or not len(results):
        raise exceptions.NoDatabaseError(directory)

    return results[-1]


def list_directory(filepath):
    """ List the contents of the directory at path.

    :param filepath: The path to list.
    :raise InvalidDirectoryError: If the path given is not a directory.
    """
    if not path.is_directory(filepath):
        raise exceptions.InvalidDirectoryError(filepath)

    return os.listdir(filepath)


def list_subdirectories(filepath):
    """ List only subdirectories of the given directory (Generator expression).

    :param filepath: The path to list.
    :raise InvalidDirectoryError: If the path given is not a directory.
    """
    filenames = list_directory(filepath)

    for file_name in filenames:
        full_path = path.make_path(filepath, file_name)
        if path.is_directory(full_path):
            yield full_path


def list_files(filepath):
    """ List only files under the given directory (Generator expression).

    :param filepath: The path to list.
    :raise InvalidDirectoryError: IF the path given is not a directory.
    """
    filenames = list_directory(filepath)

    for file_name in filenames:
        full_path = path.make_path(filepath, file_name)
        if path.is_file(full_path):
            yield full_path


@contextmanager
def change_working_directory(filepath):
    """ Context manager to temporarily change the script's working directory.

    :param filepath: The path to change the working directory too.
    """
    current_directory = os.getcwd()
    os.chdir(filepath)
    yield
    os.chdir(current_directory)


def md5(filename, block_size=256 * 128):
    """ Return the MD5 checksum value for the given file.

    :param filename: The file to calculate checksum for.
    :param block_size: The size of blocks to read for the md5 hash.
    :return: The MD5 checksum, as a string.
    """
    hash_ = hashlib.md5()

    with open(filename, 'rb') as file_:
        for chunk in iter(lambda: file_.read(block_size), b''):
            hash_.update(chunk)

    return hash_.hexdigest()


def remove_file(filepath):
    os.remove(filepath)
