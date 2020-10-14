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
        self.chart.setTheme(QtChart.QChart.ChartThemeDark)
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart.setBackgroundRoundness(0)
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

        if x_data.size == 0 or y_data.size == 0:
            return

        if x_data.ndim != 1 or y_data.ndim != 1:
            raise ValueError("x,y,data length")

        if x_data.size == 18:
            x_data = np.append(x_data, [np.pi])
            y_data = np.append(y_data, [y_data[0]])

        series = QtChart.QScatterSeries()
        for x, y in zip(x_data, y_data):
            series.append(np.rad2deg(x), y)
        self.chart.addSeries(series)

        # if x_data.size == 18:
        # self.chart.setTheme(QtChart.QChart.ChartThemeDark)
        # x_data = np.append(x_data, [np.pi])
        # y_data = np.append(y_data, [y_data[0]])
        # series = QtChart.QLineSeries()
        # for x, y in zip(x_data, y_data):
        #     series.append(np.rad2deg(x), y)
        # self.chart.addSeries(series)

        # colors for ChartThemeDark
        # print(self.chart.series()[-1].pen().color().getRgb())
        # (56, 173, 107, 255)
        # (60, 132, 167, 255)
        # (235, 136, 23, 255)
        # (123, 127, 140, 255)
        # (191, 89, 62, 255)

        self.chart.createDefaultAxes()
        self.chart.axes()[0].setMin(0)
        self.chart.axes()[0].setMax(180)
        self.chart.axes()[1].applyNiceNumbers()
