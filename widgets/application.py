import os
import pathlib

from PyQt5 import QtCore, QtGui, QtWidgets

from . import dummy
from . import display

PATH = os.path.join(pathlib.Path().absolute(), 'data')


class Application(QtWidgets.QMainWindow):
    """ 
    MainWindow of the application, which contains all widgets and sort them in a layout
    """

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self.__initUI__()

    def __initUI__(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("3D-PLI Demo")
        self.setWindowIcon(QtGui.QIcon(os.path.join(PATH, 'pli-logo.png')))
        self.setBackground()
        self.createWidgets()
        self.createLayout()

    def resizeEvent(self, event):
        super(Application, self).resizeEvent(event)
        # add user specific resize functionality here

    def setBackground(self):
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(38, 65, 100))
        self.setPalette(p)

    def createWidgets(self):
        self.setCentralWidget(QtWidgets.QWidget(self))

        self.camwidget = display.Display()
        self.camwidget.setMinimumSize(QtCore.QSize(545, 545))
        self.camwidget.setAlignment(QtCore.Qt.AlignCenter)
        self.camwidget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                     QtWidgets.QSizePolicy.Minimum)

        self.plotwidget = dummy.Label()
        self.plotwidget.setMinimumSize(QtCore.QSize(200, 200))
        self.plotwidget.setAlignment(QtCore.Qt.AlignCenter)
        self.plotwidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)

        self.setupwidget = dummy.Label()
        self.setupwidget.setMinimumSize(QtCore.QSize(100, 200))

        self.logolabelpli = QtWidgets.QLabel()
        self.logolabelpli.setMinimumHeight(50)
        self.logolabelpli.setMaximumHeight(50)
        self.logolabelpli.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(os.path.join(PATH, "pli-logo.png"))).scaled(
                    self.logolabelpli.size().width(),
                    self.logolabelpli.size().height(),
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.logolabelpli.setAlignment(QtCore.Qt.AlignRight)
        self.logolabelpli.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                        QtWidgets.QSizePolicy.Minimum)

        self.logolabelfzj = QtWidgets.QLabel()
        self.logolabelfzj.setMinimumHeight(50)
        self.logolabelfzj.setMaximumHeight(50)
        self.logolabelfzj.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(os.path.join(PATH, "fzj-gray.png"))).scaled(
                    self.logolabelfzj.size().width(),
                    self.logolabelfzj.size().height(),
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.logolabelfzj.setAlignment(QtCore.Qt.AlignRight)
        self.logolabelfzj.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                        QtWidgets.QSizePolicy.Maximum)

    def createLayout(self):
        self.layout = QtWidgets.QGridLayout()
        self.layout_logos = QtWidgets.QGridLayout()

        self.layout.addWidget(self.camwidget, 0, 0, 2, 1)
        self.layout.addWidget(self.setupwidget, 0, 1, 1, 1)
        self.layout.addWidget(self.plotwidget, 1, 1, 1, 1)
        self.layout.addLayout(self.layout_logos, 2, 1, 1, 1)
        self.layout_logos.addWidget(self.logolabelpli, 0, 0, 1, 1)
        self.layout_logos.addWidget(self.logolabelfzj, 0, 1, 1, 1)

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 1)

        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

        self.layout.setSpacing(50)
        self.layout_logos.setSpacing(50)
        self.layout.setContentsMargins(50, 50, 50, 50)

        self.centralWidget().setLayout(self.layout)
