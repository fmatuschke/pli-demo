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
        # w = event.size().width()
        # h = event.size().height()
        # if w > h:
        #     w = h
        # else:
        #     h = w
        # self.setMaximumSize(w, h)
        super(PlotWidget, self).resizeEvent(event)

    def update_plot(self, x_data, y_data, rho):

        self.chart.removeAllSeries()

        for x, y in zip(x_data, y_data):

            if x.size == 0 or y.size == 0:
                return

            if x.ndim != 1 or y.ndim != 1:
                raise ValueError("x,y,data length")

            if 0 in x:
                x = np.append(x, [np.pi])
                y = np.append(y, [y[0]])

            series = QtChart.QScatterSeries()
            for x_val, y_val in zip(x, y):
                series.append(np.rad2deg(x_val), y_val)
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
            # self.chart.axes()[0].setMin(0)
            # self.chart.axes()[0].setMax(180)
            # self.chart.axes()[1].applyNiceNumbers()

        if len(x_data) > 0:
            print(self.chart.axes()[1].min())
            print(self.chart.axes()[1].max())
            series = QtChart.QLineSeries()
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
