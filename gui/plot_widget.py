import cv2
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
import pyqtgraph as pg
import numpy as np
from src import helper


class PlotWidget(QtWidgets.QLabel):

    def __init__(self, parent=None, *args, **kwargs):
        super(PlotWidget, self).__init__(parent, *args, **kwargs)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.graphWidget = pg.PlotWidget()
        self.layout.addWidget(self.graphWidget)
        self.setLayout(self.layout)
        # self.setCentralWidget(self.graphWidget)

    def resizeEvent(self, event):
        super(PlotWidget, self).resizeEvent(event)
        self.graphWidget.scaleToImage

    def update_plot(self, x, y, rho):
        self.graphWidget.clear()
        self.graphWidget.setAspectLocked(False)

        self.graphWidget.setXRange(0, 160)
        self.graphWidget.scale(self.size().width(), self.size().height())
        self.graphWidget.plot(np.rad2deg(x), y, symbol='+')

        pen = pg.mkPen(color="y")
        _, [y_min, y_max] = self.graphWidget.viewRange()
        self.graphWidget.plot(
            [np.rad2deg(rho), np.rad2deg(rho)], [y_min, y_max], pen=pen)
