import os
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class SetupWidget(QtWidgets.QLabel):

    def __init__(self, parent=None, *args, **kwargs):
        super(SetupWidget, self).__init__(parent, *args, **kwargs)
        self.create_image()

        # p = self.palette()
        # p.setColor(self.backgroundRole(), QtGui.QColor(255, 0, 0))
        # self.setAutoFillBackground(True)
        # self.setPalette(p)

    def create_image(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.qimage = QtGui.QImage(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                         "data", "aufbau.png"))
        self.setLayout(self.layout)
        self.update_qimage()

    def resizeEvent(self, event):
        super(SetupWidget, self).resizeEvent(event)
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

        self.setPixmap(pixmap)
