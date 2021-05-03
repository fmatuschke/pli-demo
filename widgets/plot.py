from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtChart

import numpy as np


class Plot(QtChart.QChartView):

    def __init__(self, parent=None, *args, **kwargs):
        super(Plot, self).__init__(parent, *args, **kwargs)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)

        self.chart = QtChart.QChart()
        self.chart.setTheme(QtChart.QChart.ChartThemeDark)
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart.setBackgroundRoundness(0)
        self.setChart(self.chart)

        #variables for saving data
        self.x_save = []
        self.y_save = []

    def resizeEvent(self, event):
        super(Plot, self).resizeEvent(event)

    def update(self, x, y_data, rho):

        self.chart.removeAllSeries()

        if y_data is not None:
            for y in y_data:
                if 0.0 in x:
                    x = np.append(x, [np.pi])
                    y = np.append(y, [y[0]])
                    self.x_save = np.pi - x
                    self.y_save = y

                series = QtChart.QScatterSeries()
                for x_val, y_val in zip(x, y):
                    series.append(np.rad2deg(x_val), y_val)
                self.chart.addSeries(series)
                self.chart.createDefaultAxes()

        series = QtChart.QLineSeries()
        if rho is not None:
            if x is None:
                series.append(np.rad2deg(rho), 0)
                series.append(np.rad2deg(rho), 1)
            else:
                series.append(np.rad2deg(rho), self.chart.axes()[1].min())
                series.append(np.rad2deg(rho), self.chart.axes()[1].max())

        pen = QtGui.QPen()
        pen.setColor(QtCore.Qt.gray)
        pen.setWidth(3)
        series.setPen(pen)
        self.chart.addSeries(series)

        self.chart.createDefaultAxes()
        self.chart.axes()[0].setMin(0)
        self.chart.axes()[0].setMax(180)
        self.chart.axes()[1].applyNiceNumbers()
