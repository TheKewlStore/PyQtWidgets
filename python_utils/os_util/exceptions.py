# coding=utf-8
""" Module Docstring.

Author: Ian Davis
Last Updated: 9/17/2015
"""


class InvalidDirectoryError(Exception):
    """ Raised when a directory path given is invalid.

    :param path: The invalid path in question.
    """

    def __init__(self, path):
        self.message = '{path} is not a valid directory'.format(path=path)

    def __str__(self):
        return self.message


class NoDatabaseError(Exception):
    """ Raised by find_hobart_database when no database can be found at the specified path.

    :param path: The path that was searched.
    """

    def __init__(self, path):
        self.message = 'No proper Hobart database found under {path}'.format(path=path)

    def __str__(self):
        return self.message


class NoArgumentError(Exception):
    """ Raised when no argument is passed to a method that requires it.
    """
    pass


class UnknownModelError(Exception):
    """ Raised when the model name of the device cannot be determined.
    """
    def __str__(self):
        return 'The model name for this device is unknown.'
