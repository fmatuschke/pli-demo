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
        self.resize(min(self.size().width(),
                        self.size().height()),
                    min(self.size().width(),
                        self.size().height()))

    def resizeEvent(self, event):
        super(PlotWidget, self).resizeEvent(event)
        self.resize(min(self.size().width(),
                        self.size().height()),
                    min(self.size().width(),
                        self.size().height()))

    def update_plot(self, x, y, rho):

        if np.any(x == np.deg2rad(160)):
            x = np.append(x, np.deg2rad(180))
            y = np.append(y, y[0])

        self.graphWidget.clear()
        self.graphWidget.setAspectLocked(False)

        self.graphWidget.setXRange(0, 180)
        self.graphWidget.plot(np.rad2deg(x), y, symbol='+')

        self.graphWidget.addItem(pg.InfiniteLine(pos=np.rad2deg(rho), angle=90))
