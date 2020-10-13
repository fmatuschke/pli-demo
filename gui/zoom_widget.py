import cv2
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from src import helper


class ZoomWidget(QtWidgets.QLabel):

    def __init__(self, parent=None, *args, **kwargs):
        super(ZoomWidget, self).__init__(parent, *args, **kwargs)

        self.image = helper.LOGO_IMG
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)

        # p = self.palette()
        # p.setColor(self.backgroundRole(), QtGui.QColor(255, 0, 0))
        # self.setAutoFillBackground(True)
        # self.setPalette(p)

    def resizeEvent(self, event):
        super(ZoomWidget, self).resizeEvent(event)
        self.update_image(self.image)

    def update_image(self, frame):
        self.image = frame.copy()

        if frame.ndim == 2:
            img_format = QtGui.QImage.Format_Grayscale8
        else:
            img_format = QtGui.QImage.Format_RGB888

        image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],
                             img_format)
        image = image.rgbSwapped()
        image = image.scaled(self.size().width(),
                             self.size().height(), QtCore.Qt.KeepAspectRatio)
        pixmap = QtGui.QPixmap.fromImage(image)

        # target indicator
        painter = QtGui.QPainter(pixmap)
        pen = QtGui.QPen()
        pen.setColor(QtCore.Qt.magenta)
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawEllipse(
            QtCore.QPointF(pixmap.width() / 2,
                           pixmap.height() / 2), 10, 10)

        del painter

        self.setPixmap(pixmap)
