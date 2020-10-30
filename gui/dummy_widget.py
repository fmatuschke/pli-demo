import os
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

LOGO_PATH = os.path.join("data", "pli-logo.png")
LOGO_IMG = cv2.imread(LOGO_PATH, cv2.IMREAD_COLOR)


class ImageWidget(QtWidgets.QLabel):

    def __init__(self, parent=None, *args, **kwargs):
        super(ImageWidget, self).__init__(parent, *args, **kwargs)
        self.create_image()

        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(255, 0, 0))
        self.setAutoFillBackground(True)
        self.setPalette(p)

    def create_image(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.qimage = QtGui.QImage(pli_logo_path)
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
                               self.size().height(),
                               QtCore.Qt.SmoothTransformation)

        self.setPixmap(pixmap)
