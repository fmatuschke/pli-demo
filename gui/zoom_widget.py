import cv2
import numpy as np

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from src import helper


class ZoomWidget(QtWidgets.QLabel):

    def __init__(self, parent=None, *args, **kwargs):
        super(ZoomWidget, self).__init__(parent, *args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)

    def resizeEvent(self, event):
        super(ZoomWidget, self).resizeEvent(event)
        self.update_image(helper.LOGO_IMG, (56, 173, 107, 255))

    def update_image(self, frame, color):
        if not isinstance(frame, np.ndarray):
            return

        if frame.ndim == 2:
            img_format = QtGui.QImage.Format_Grayscale8
        else:
            img_format = QtGui.QImage.Format_RGB888

        totalBytes = frame.nbytes
        bytesPerLine = int(totalBytes / frame.shape[0])
        image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],
                             bytesPerLine, img_format)
        image = image.rgbSwapped()
        image = image.scaled(self.size().width(),
                             self.size().height(), QtCore.Qt.KeepAspectRatio,
                             QtCore.Qt.SmoothTransformation)
        pixmap = QtGui.QPixmap.fromImage(image)

        # target indicator
        painter = QtGui.QPainter(pixmap)
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor(color[0], color[1], color[2], color[3]))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawEllipse(
            QtCore.QPointF(pixmap.width() / 2,
                           pixmap.height() / 2), 10, 10)

        del painter

        self.setPixmap(pixmap)
