# coding=utf-8
""" Module Docstring.

Author: Ian Davis
Last Updated: 12/7/2015
"""

from PyQt4 import QtGui

import message_boxes
import prompts

from pyqt_widgets import os_util
from pyqt_widgets.util import list_util
from pyqt_widgets.models import TableModel

from ui.Ui_media_manager import Ui_MediaManagerWindow as MediaManagerInterface
from ui.context_menus.clear_filters import context_menu as media_context_menu


def create_interface(media_root, supported_extensions=None, parent=None):
    return MediaManager(media_root, supported_extensions=supported_extensions, parent=parent)


class MediaManager(QtGui.QWidget):
    """ Create an interface to manage media files on the filesystem.

    :param media_root: The filesystem root for the media to manage.
    :param table_model: The table model to use to display our media files (blank for default table model)
    :param supported_extensions: If given, should be a dictionary mapping media type descriptions to it's extensions.
    :param parent: The qt widget parent of the interface.
    :param interface_class: The compiled ui class to use to display our manager (blank for the default manager ui).
    """
    def __init__(self, media_root, table_model=None, supported_extensions=None, parent=None, interface_class=MediaManagerInterface):
        QtGui.QWidget.__init__(self, parent)

        self._media_root = media_root
        self._supported_extensions = supported_extensions

        self.ui = interface_class()
        self.ui.setupUi(self)

        self.media_table_model = table_model
        self.context_menu = media_context_menu(self, self.ui.media_table_view)

        if not self.media_table_model:
            self.media_table_model = TableModel(header=('Name', ), parent=self)

        self.ui.media_table_view.setModel(self.media_table_model)
        self.ui.media_table_view.context_menu = self.context_menu

        self.delete_shortcut = QtGui.QShortcut(QtGui.QKeySequence('Del'), self.ui.media_table_view)

        self._connect_slots()

    @property
    def media_root(self):
        """ Get the media root.
        """
        return self._media_root

    @media_root.setter
    def media_root(self, new_root):
        """ Set the media root, and reload the list view from the new root.

        :param new_root: The filepath to use as the new media root.
        :return: None.
        """
        self._media_root = new_root
        self.load_media()

    def insert_into_view(self, filename):
        self.ui.media_table_view.add_new_row(filename)

    def add_media(self, files_to_add):
        for filepath in files_to_add:
            filename = os_util.filename(filepath)
            destination_path = os_util.make_path(self._media_root, filename)

            if os_util.exists(destination_path):
                message = 'The media file {0} is already in media root, and was ignored.'.format(filename)
                print(message)
                continue

            print('The media file {0} was copied to media root.'.format(filename))
            os_util.copy_file(filepath, destination_path)
            self.insert_into_view(filename)

    def add_selected_media(self):
        """ Prompt user to select media to add, copy it to the media root, and add it to our list view.

        :return: None.
        """
        if not self._supported_extensions:
            file_extension_spec = 'All Files (*.*)'
        else:
            file_extension_spec = self._create_file_extension_spec()

        try:
            files_to_add = prompts.open_files_prompt('Select media files to add',
                                                     file_extension_spec=file_extension_spec)
        except prompts.UserCancelledPromptException:
            return

        with message_boxes.background_message('Adding media files', 'Adding media files, please wait...'):
            self.add_media(files_to_add)

    def delete_media(self, filename_items):
        for filename_item in filename_items:
            filename = unicode(filename_item.text())
            media_filepath = os_util.make_path(self._media_root, filename)
            os_util.remove_file(media_filepath)
            self.ui.media_table_view.takeItem(self.ui.media_table_view.row(filename_item))
            print('Removed media file {0}'.format(filename))

    def delete_selected_media(self):
        """ Prompt user for confirmation to delete, and delete the media file that is selected in the list view.

        :return: None
        """
        selected_filename_items = self.ui.media_table_view.selectedItems()

        if not selected_filename_items:
            message_boxes.warning_message('No filenames selected.', 'You must select filenames to delete media.')
            return

        confirmation_message = 'Are you sure you want to remove selected media files?'

        if not message_boxes.confirmation_dialog('Confirm media removal', confirmation_message):
            return

        with message_boxes.background_message('Deleting media files', 'Delete selected media files, please wait...'):
            self.delete_media(selected_filename_items)

    def load_media(self):
        """ Load supported media files from the media root into our list view.

        :return: None
        """
        media_files = os_util.filenames(os_util.list_files(self._media_root))

        if self._supported_extensions:
            media_files = list_util.filter_by_value(media_files,
                                                    list_util.flatten(self._supported_extensions.itervalues()))

        for filename in media_files:
            data = {'Name': filename}
            self.media_table_model.add_row(data)

    def load_media_preview(self, table_row):
        file_path = os_util.make_path(self.media_root, table_row['Name'])
        self.ui.media_preview_label.image_path = file_path

    def _create_file_extension_spec(self):
        file_extension_template = '{description} ({extensions})'
        file_extension_strings = []

        for description, extensions in self._supported_extensions.iteritems():
            extensions_string = ' '.join('*{0}'.format(extension) for extension in extensions)
            file_extension_string = file_extension_template.format(description=description,
                                                                   extensions=extensions_string)
            file_extension_strings.append(file_extension_string)

        return ';;'.join(file_extension_strings)

    def _connect_slots(self):
        self.ui.add_media_button.clicked.connect(self.add_selected_media)
        self.ui.delete_media_button.clicked.connect(self.delete_selected_media)
        self.delete_shortcut.activated.connect(self.delete_selected_media)
        self.ui.media_table_view.row_selected.connect(self.load_media_preview)
