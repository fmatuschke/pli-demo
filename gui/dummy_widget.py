import os
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

pli_logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                             "data", "pli-logo.png")


class ImageWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super(ImageWidget, self).__init__(parent, *args, **kwargs)
        self.create_image()

    def create_image(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.qimage = QtGui.QImage(pli_logo_path)

        self.image_frame = QtWidgets.QLabel()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)
        self.update_qimage()

    def resizeEvent(self, event):
        super(ImageWidget, self).resizeEvent(event)
        self.update_qimage()

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        menu.addAction("action")
        menu.exec_(self.mapToGlobal(event.pos()))

    def update_qimage(self, qimage=None):
        if qimage is None:
            qimage = self.qimage

        pixmap = QtGui.QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(self.size().width(),
                               self.size().height(), QtCore.Qt.KeepAspectRatio)

        self.image_frame.setPixmap(pixmap)
