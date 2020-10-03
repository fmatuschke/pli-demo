import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class ImageWidget(QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super(ImageWidget, self).__init__(parent, *args, **kwargs)
        self.create_image()

    def create_image(self):
        self.layout = QVBoxLayout(self)
        self.qimage = QImage(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "pli-logo.png"))

        self.image_frame = QLabel()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)
        self.update_qimage()

    def resizeEvent(self, event):
        super(ImageWidget, self).resizeEvent(event)
        self.update_qimage()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        templateAction = menu.addAction("action")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        print("action")

    def update_qimage(self, qimage=None):
        if qimage is None:
            qimage = self.qimage

        pixmap = QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(self.size().width(),
                               self.size().height(), Qt.KeepAspectRatio)

        self.image_frame.setPixmap(pixmap)
