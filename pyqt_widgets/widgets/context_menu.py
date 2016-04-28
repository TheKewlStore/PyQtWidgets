# coding=utf-8
""" Module Docstring.

Author: Ian Davis
"""

from PyQt4.QtGui import QAction
from PyQt4.QtGui import QMenu


class ContextAction(QAction):
    """ Represent a context menu action that can be displayed by a context menu, with customizable behavior to be executed when triggered.

    :param name: The name of the action (typically an internal name).
    :param text: The description of the action (typically what is displayed on the context menu).
    :param parent: The parent object of the QAction.
    """

    def __init__(self, name, text, parent=None):
        QAction.__init__(self, text, parent)

        self.name = name
        self._text = text

    @property
    def text(self):
        """ Get the description of this action (typically what is displayed on the context menu).
        """
        return self._text

    @text.setter
    def text(self, new_text):
        """ Set the description of this action (typically what is displayed on the context menu).

        :param new_text: The new description to use for this action.
        """
        self._text = new_text
        self.setText(new_text)

    def run(self, *args, **kwargs):
        """ Activate this action, performing any operations actually intended to complete the action's behavior.

        :param args: optional arguments needed for the action.
        :param kwargs: optional keyword arguments needed for the action/
        :raise NotImplementedError: Always, as this is an abstract method designed to be overridden by subclasses.
        """
        raise NotImplementedError('This method should be overridden by ContextAction implementers.')


class ContextMenu(QMenu):
    """ Represent a context menu that can be displayed, exposing any number of customized actions to perform in that context.

    :param parent: The parent object of the QMenu.
    :param actions: A list of ContextActions that this menu should expose.
    """

    def __init__(self, parent=None, **actions):
        QMenu.__init__(self, parent)
        self.actions = actions

        self.addActions(list(self.actions.itervalues()))

    def add_action(self, action):
        """

        :param action:
        """
        self.actions[action.name] = action
        self.addAction(action)


def show_menu(context_menu, origin, *args, **kwargs):
    """ Show an instance of ContextMenu at the given origin point.

    :param context_menu: The ContextMenu instance to show.
    :param origin: The origin (QPoint) to place the context menu at.
    :param args: optional arguments to pass to the action.process method.
    :param kwargs: optional keyword arguments to pass to the action.process method.
    :return:
    """
    if not context_menu:
        return

    if not origin:
        return

    action = context_menu.exec_(origin)
    """ :type: ContextAction"""

    if not action:
        return

    action.run(*args, **kwargs)
