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

        self._only_line = True

        # #variables for saving data
        # self.x_save = []
        # self.y_save = []

    def resizeEvent(self, event):
        super(Plot, self).resizeEvent(event)

    def clear(self):
        self.chart.removeAllSeries()

    def update_data(self, x, y_data):
        self.clear()
        if len(y_data) == 0:
            return

        for y in y_data:

            if 0.0 in x:
                idx = np.argwhere(x == 0.0)
                x = np.append(x, [np.pi])
                y = np.append(y, [y[idx]])

            series = QtChart.QScatterSeries()
            for x_val, y_val in zip(x, y):
                series.append(np.rad2deg(x_val), y_val)
            self.chart.addSeries(series)

        self._only_line = False
        self.chart.createDefaultAxes()

    def update_rho(self, rho):
        series = QtChart.QLineSeries()
        if rho is not None:
            if self._only_line:
                if len(self.chart.series()):
                    self.chart.removeSeries(self.chart.series()[-1])
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

        self._only_line = True  # reset if data changes
