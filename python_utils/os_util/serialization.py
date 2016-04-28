# coding=utf-8
""" Module Docstring.

Author: Ian Davis
Last Updated: 9/17/2015
"""

import cPickle


def dump_object(python_object, file_path):
    """ Dump an object to a pickle file using cPickle.

    :param python_object: The object to dump.
    :param file_path: The path to dump the object too.
    """
    with open(file_path, 'wb') as binary_file:
        cPickle.dump(python_object, binary_file)


def load_object(file_path):
    """ Load a pickled object from file path.

    :param file_path: The path to load from.
    :return: The object that was loaded from the path.
    """
    with open(file_path, 'rb') as binary_file:
        return cPickle.load(binary_file)
