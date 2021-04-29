from PyQt5 import QtGui, QtWidgets


class Label(QtWidgets.QLabel):

    def __init__(self, parent=None, *args, **kwargs):
        super(Label, self).__init__(parent, *args, **kwargs)

        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(255, 0, 0))
        self.setAutoFillBackground(True)
        self.setPalette(p)
