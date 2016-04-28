# coding=utf-8
""" Module Docstring.

Author: Ian Davis
"""

import itertools


def filter_by_type(list_, filter_type):
    """ Filter the given list down to a list of the given types.

    :param list_: The unfiltered list.
    :param filter_type: The type of element to filter down too.
    :return: The filtered list, with only elements of the given type.
    """
    filtered_list = []

    for item in list_:
        if type(item) is filter_type:
            filtered_list.append(item)

    return filtered_list


def filter_by_value(list_, filter_values):
    """ Filter the given list by value.

    :note: Objects in the list will be compared as strings, but they will be returned in their original form.

    :param list_: The list to filter.
    :param filter_values: A list of search expressions to filter by.
    :return: The filtered list.
    """
    filtered_list = []

    for value in list_:
        for filter_value in filter_values:
            if filter_value in str(value):
                filtered_list.append(value)

    return filtered_list


def pairwise(iterable):
    """ Iterate through the given iterable two elements at a time.

    :param iterable: The iterable to loop through.
    :return: Generator that iterates through the iterable two elements at a time.
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def flatten(iterable):
    new_list = []

    for row in iterable:
        new_list.extend(row)

    return new_list
