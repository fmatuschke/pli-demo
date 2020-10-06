import os

from functools import partial

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtMultimedia
from PyQt5 import QtMultimediaWidgets

from src.camera import Camera


class CameraWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super(CameraWidget, self).__init__(parent, *args, **kwargs)
        self.ui = parent
        self.init_camera()

    def init_camera(self):
        self.camera = Camera()
        self.camera.list_ports(0, 5)
        self.camera.list_resolutions()
        self.camera.set_resolution(1920, 1080)

    def resizeEvent(self, event):
        super(CameraWidget, self).resizeEvent(event)
