from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtChart

import numpy as np
from src import helper


class PlotWidget(QtChart.QChartView):

    def __init__(self, parent=None, *args, **kwargs):
        super(PlotWidget, self).__init__(parent, *args, **kwargs)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)

        self.chart = QtChart.QChart()
        self.setChart(self.chart)

        # p = self.palette()
        # p.setColor(self.backgroundRole(), QtGui.QColor(255, 0, 0))
        # self.setAutoFillBackground(True)
        # self.setPalette(p)

    def resizeEvent(self, event):
        super(PlotWidget, self).resizeEvent(event)

    def update_plot(self, x_data, y_data, rho, flag_add):
        if not flag_add:
            self.chart.removeAllSeries()

        if x_data.ndim != 1:
            print("x FOOOOOO")
        if y_data.ndim != 1:
            print("y FOOOOOO")

        if x_data[0] == 0:
            x_data = np.append(x_data, [np.pi])
            y_data = np.append(y_data, [y_data[0]])
        series = QtChart.QLineSeries()
        for x, y in zip(x_data, y_data):
            series.append(np.rad2deg(x), y)
        self.chart.addSeries(series)

        if not flag_add:
            self.chart.createDefaultAxes()
            axes = self.chart.axes()
            for a in axes:
                a.applyNiceNumbers()
