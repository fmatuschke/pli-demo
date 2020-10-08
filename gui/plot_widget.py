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

        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(255, 0, 0))
        self.setAutoFillBackground(True)
        self.setPalette(p)

    def resizeEvent(self, event):
        super(PlotWidget, self).resizeEvent(event)

    def update_plot(self, x_data, y_data, rho):

        series = QtChart.QLineSeries()

        for x, y in zip(x_data, y_data):
            series.append(x, y)

        chart = QtChart.QChart()
        chart.addSeries(series)
        chart.createDefaultAxes()
        self.setChart(chart)
