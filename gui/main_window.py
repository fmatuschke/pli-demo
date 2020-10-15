import sys
import os

from functools import partial

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from gui.camera_widget import CameraWidget
from gui.plot_widget import PlotWidget
from gui.setup_widget import SetupWidget
from gui.zoom_widget import ZoomWidget

logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                         "data")


class Color(QtWidgets.QWidget):

    def __init__(self, qcolor, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, qcolor)
        self.setPalette(palette)


class MainWindow(QtWidgets.QMainWindow):
    '''
    MainWindow of the application, which contains all widgets and sort them in a layout
    '''

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.__initUI__()

    def __initUI__(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("3D-PLI Demo")
        self.setWindowIcon(QtGui.QIcon(os.path.join(logo_path, "pli-logo.png")))
        self.createMenu()
        self.createCentralWidget()
        self.connect_widgets()
        self.setBackground()

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)

        # w = self.camwidget.size().width() / 3
        # h = self.camwidget.size().height() / 3
        # w, h = min(w, h), min(w, h)

        # self.plotwidget.setMinimumSize(QtCore.QSize(w, h))
        # self.plotwidget.setMaximumSize(QtCore.QSize(w, h))

        # self.zoomwidget.setMinimumSize(QtCore.QSize(w, h))
        # self.zoomwidget.setMaximumSize(QtCore.QSize(w, h))

        # self.setupwidget.setMinimumSize(QtCore.QSize(w, h))
        # self.setupwidget.setMaximumSize(QtCore.QSize(w, h))

    def createCentralWidget(self):

        self.setCentralWidget(QtWidgets.QWidget(self))

        self.camwidget = CameraWidget(self)
        self.camwidget.setMinimumSize(QtCore.QSize(600, 600))
        self.camwidget.setAlignment(QtCore.Qt.AlignCenter)
        self.camwidget.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                     QtWidgets.QSizePolicy.Preferred)

        self.plotwidget = PlotWidget(self)
        self.plotwidget.setMinimumSize(QtCore.QSize(200, 200))
        # self.plotwidget.setMaximumSize(QtCore.QSize(500, 500))
        self.plotwidget.setAlignment(QtCore.Qt.AlignCenter)
        self.plotwidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)

        # self.zoomwidget = ZoomWidget(self)
        # self.zoomwidget.setMinimumSize(QtCore.QSize(200, 200))
        # # self.zoomwidget.setMaximumSize(QtCore.QSize(500, 500))
        # self.zoomwidget.setAlignment(QtCore.Qt.AlignTop)

        self.setupwidget = SetupWidget(self)
        self.setupwidget.setMinimumSize(QtCore.QSize(100, 300))
        # self.setupwidget.setMaximumSize(QtCore.QSize(300, 500))

        self.logolabelpli = QtWidgets.QLabel()
        self.logolabelpli.setMinimumWidth(200)
        self.logolabelpli.setMaximumWidth(200)
        self.logolabelpli.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(os.path.join(logo_path, "pli-logo.png"))).scaled(
                    self.logolabelpli.size().width(),
                    self.logolabelpli.size().height(),
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.logolabelpli.setAlignment(QtCore.Qt.AlignTop)
        # p = self.logolabelpli.palette()
        # p.setColor(self.logolabelpli.backgroundRole(),
        #            QtGui.QColor(255, 0, 0, 0))
        # self.logolabelpli.setAutoFillBackground(True)
        # self.logolabelpli.setPalette(p)

        self.logolabelfzj = QtWidgets.QLabel()
        self.logolabelfzj.setMinimumWidth(200)
        self.logolabelfzj.setMaximumWidth(200)
        self.logolabelfzj.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(os.path.join(logo_path, "fzj-gray.png"))).scaled(
                    self.logolabelfzj.size().width(),
                    self.logolabelfzj.size().height(),
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.logolabelfzj.setAlignment(QtCore.Qt.AlignBottom)
        # p = self.logolabelfzj.palette()
        # p.setColor(self.logolabelfzj.backgroundRole(), QtGui.QColor(255, 0, 0))
        # self.logolabelfzj.setAutoFillBackground(True)
        # self.logolabelfzj.setPalette(p)

        #
        ''' LAYOUT
        '''
        self.layout = QtWidgets.QGridLayout()

        self.layout.addWidget(self.camwidget, 0, 0, 2, 1)
        self.layout.addWidget(self.setupwidget, 0, 1, 1, 1)
        self.layout.addWidget(self.logolabelpli, 0, 2, 1, 1)
        self.layout.addWidget(self.plotwidget, 1, 1, 1, 2)
        self.layout.addWidget(self.logolabelfzj, 2, 2, 1, 1)

        self.layout.setColumnStretch(0, 3)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)

        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

        self.layout.setSpacing(50)
        self.layout.setContentsMargins(50, 50, 50, 50)

        self.centralWidget().setLayout(self.layout)

    def createMenu(self):

        self.mainMenu = self.menuBar()

        # PLI
        self.pliMenu = self.mainMenu.addMenu('&PLI')
        #
        self.action_live = QtWidgets.QAction("&live", self)
        self.pliMenu.addAction(self.action_live)
        #
        self.action_transmittance = QtWidgets.QAction("&transmittance", self)
        self.pliMenu.addAction(self.action_transmittance)
        #
        self.action_direction = QtWidgets.QAction("&direction", self)
        self.pliMenu.addAction(self.action_direction)
        #
        self.action_retardation = QtWidgets.QAction("&retardation", self)
        self.pliMenu.addAction(self.action_retardation)
        #
        self.action_inclination = QtWidgets.QAction("&inclination", self)
        self.pliMenu.addAction(self.action_inclination)
        #
        self.action_fom = QtWidgets.QAction("&fom", self)
        self.pliMenu.addAction(self.action_fom)

        # CAMERA
        self.cameraMenu = self.mainMenu.addMenu('&camera')
        self.cameraPortMenu = self.cameraMenu.addMenu('&port')
        self.cameraResolutionMenu = self.cameraMenu.addMenu('&resolution')
        self.cameraFilterMenu = self.cameraMenu.addMenu('&filter')
        self.cameraDemoMenu = self.cameraMenu.addMenu('&demo')
        #
        self.action_filter_nlmd = QtWidgets.QAction("&nlmd")
        self.cameraFilterMenu.addAction(self.action_filter_nlmd)
        self.action_filter_none = QtWidgets.QAction("&none", self)
        self.cameraFilterMenu.addAction(self.action_filter_none)
        self.action_filter_gaus = QtWidgets.QAction("&gaus")
        self.cameraFilterMenu.addAction(self.action_filter_gaus)

        # HELP
        self.helpMenu = self.mainMenu.addMenu('&help')

        self.action_tracker = QtWidgets.QAction("&tracker", self)
        self.helpMenu.addAction(self.action_tracker)
        self.action_reset = QtWidgets.QAction("&reset", self)
        self.helpMenu.addAction(self.action_reset)

    def connect_widgets(self):
        self.action_live.triggered.connect(
            partial(self.camwidget.set_mode, "live"))
        self.action_transmittance.triggered.connect(
            partial(self.camwidget.set_mode, "transmittance"))
        self.action_direction.triggered.connect(
            partial(self.camwidget.set_mode, "direction"))
        self.action_retardation.triggered.connect(
            partial(self.camwidget.set_mode, "retardation"))
        self.action_inclination.triggered.connect(
            partial(self.camwidget.set_mode, "inclination"))
        self.action_fom.triggered.connect(
            partial(self.camwidget.set_mode, "fom"))
        self.action_tracker.triggered.connect(self.camwidget.toogle_draw_helper)
        self.action_reset.triggered.connect(lambda: self.reset())

        self.camwidget.plot_update.connect(self.plotwidget.update_plot)
        # self.camwidget.zoom_update.connect(self.zoomwidget.update_image)

        self.action_filter_none.triggered.connect(
            partial(self.camwidget.set_filter, "none"))
        self.action_filter_gaus.triggered.connect(
            partial(self.camwidget.set_filter, "gaus"))
        self.action_filter_nlmd.triggered.connect(
            partial(self.camwidget.set_filter, "nlmd"))

    def reset(self):
        self.camwidget.setVisible(False)
        # self.zoomwidget.setVisible(False)

        self.camwidget.live.stop()
        self.camwidget.camera._video_capture.release()
        del self.camwidget
        self.mainMenu.clear()

        self.createMenu()
        self.createCentralWidget()
        self.connect_widgets()
        self.setBackground()

    def setBackground(self):
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(38, 65, 100))
        self.setPalette(p)

    def closeWidgets(self):
        self.camwidget.close()

    def closeEvent(self, event):
        self.closeWidgets()
        event.accept()
