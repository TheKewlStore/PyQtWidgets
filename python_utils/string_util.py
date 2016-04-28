# coding=utf-8
""" Module Docstring.

Author: Ian Davis
"""

import string
import random


def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    """

    :param size:
    :param chars:
    :return:
    """
    random_characters = (random.choice(chars) for _ in xrange(size))
    return ''.join(random_characters)


def quoted(string_):
    """

    :param string_:
    :return:
    """
    return '"{0}"'.format(string_)
