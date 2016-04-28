# coding=utf-8
""" Module Docstring.

Author: Ian Davis
"""

from shared.widgets import ContextAction
from shared.widgets import ContextMenu

from hte.api import logger


class ClearFilters(ContextAction):
    """ Represent an action that clears out the filters from the current table view.

    :param view: The shared.views.TableView to clear from.
    :param parent: The parent object of the ContextAction.
    """

    def __init__(self, view, parent=None):
        ContextAction.__init__(self, 'clear_filters', 'Clear Filters', parent)
        self.view = view

    def run(self):
        """ Clear all active filter patterns from the attached table view.
        """
        self.view.clear_filters()


def context_menu(parent, view):
    """ Create a new image manager context menu, with all actions designed for the images table view included.

    :param parent: The parent object of the ContextMenu instance.
    :param view: The TableView instance that is displaying the products table.
    :return: New ContextMenu instance with all actions defined.
    """
    logger.debug('Initializing item view context menu.')

    menu = ContextMenu(parent)
    menu.add_action(ClearFilters(view, parent=menu))

    return menu
