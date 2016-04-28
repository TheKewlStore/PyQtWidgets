# coding=utf-8
""" Module Docstring.

Author: Ian Davis
Last Updated: 9/17/2015
"""

import os
import tarfile

import path


class Archive(object):
    """ Class implementation that manages creating and editing a tarball archive.

    :param archive_path: The path to the archive.
    :type archive_file: TarFile
    :type archive_path: str
    """

    def __init__(self, archive_path):
        self.archive_path = archive_path
        self.archive_file = tarfile.open(self.archive_path, 'w:gz')

    def close(self):
        """ If opened, close our internal tarfile object.
        """
        if self.archive_file:
            self.archive_file.close()

    def add_directory(self, filepath):
        """ Add the given directory to the archive.

        :param filepath: The directory to add.
        """
        self.archive_file.add(filepath, arcname=os.path.basename(filepath))

    def add_file(self, filepath):
        """ Add the given file to the archive.

        :param filepath: The file to add.
        """
        archive_path = path.make_path(os.path.basename(os.path.dirname(filepath)), os.path.basename(filepath))
        self.archive_file.add(filepath, arcname=archive_path)

    def add(self, filepath):
        """ Add a file or directory to the archive.

        :param filepath: The file or directory path to add.
        """
        if path.is_directory(filepath):
            self.add_directory(filepath)
        else:
            self.add_file(filepath)

    def __enter__(self):
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, value, traceback):
        self.close()
