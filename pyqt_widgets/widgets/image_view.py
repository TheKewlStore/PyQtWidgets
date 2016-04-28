# coding=utf-8
""" Module Docstring.

Author: Ian Davis
Last Updated: 10/13/2015
"""

from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QLabel


def image_view(image_path):
    """ Given the path to an image, return a QLabel displaying that image.

    :param image_path: The path of the image to display.
    """
    return ImageLabel(image_path)


class ImageLabel(QLabel):
    """ Custom QLabel implementation to make a label that manages displaying an image sized to fit the geometry given to the label.
    """

    def __init__(self, image_path):
        QLabel.__init__(self)

        self._image_path = image_path

        self.setMinimumWidth(1)
        self.setMinimumHeight(1)

        self.setFrameStyle(self.Box | self.Plain)

        self.pixmap = QPixmap(image_path)
        self.setScaledContents(True)
        self.setPixmap(self.pixmap)

    @property
    def image_path(self):
        """ Get the path to the current image being displayed.
        """
        return self._image_path

    @image_path.setter
    def image_path(self, new_image_path):
        """ Set the path to the current image being displayed.

        :param new_image_path: The path to the new image to be displayed.
        """
        self._image_path = new_image_path
        self.pixmap = QPixmap(new_image_path)
        self.setPixmap(self.pixmap)
