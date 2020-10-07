import sys
import os

from functools import partial

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from gui.dummy_widget import ImageWidget
from gui.camera_widget import CameraWidget
from gui.zoom_widget import ZoomWidget

pli_logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                             "data", "pli-logo.png")


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
        self.setWindowIcon(QtGui.QIcon(pli_logo_path))
        self.createMenu()
        self.createCentralWidget()
        self.connect_widgets()
        self.setBackground()

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)

    def createCentralWidget(self):
        '''Creates Widgets and adds them to layout of centralWidget of MainWindow'''
        self.layout = QtWidgets.QGridLayout()

        self.setCentralWidget(QtWidgets.QWidget(self))

        self.camwidget = CameraWidget(self)
        self.camwidget.setMinimumSize(QtCore.QSize(600, 600))

        self.plotwidget = ImageWidget(self)
        self.plotwidget.setMinimumSize(QtCore.QSize(300, 300))
        self.plotwidget.setMaximumSize(QtCore.QSize(600, 600))

        self.zoomwidget = ZoomWidget(self)
        self.zoomwidget.setMinimumSize(QtCore.QSize(300, 300))
        self.zoomwidget.setMaximumSize(QtCore.QSize(600, 600))

        self.tiltwidget = ImageWidget(self)
        self.tiltwidget.setMinimumSize(QtCore.QSize(300, 300))
        self.tiltwidget.setMaximumSize(QtCore.QSize(600, 600))

        self.logolabel = QtWidgets.QLabel()
        self.logolabel.setMaximumSize(QtCore.QSize(100, 100))
        self.logolabel.setMinimumSize(QtCore.QSize(100, 100))
        self.logolabel.setPixmap(
            QtGui.QPixmap.fromImage(QtGui.QImage(pli_logo_path)).scaled(
                self.logolabel.size().width(),
                self.logolabel.size().height(), QtCore.Qt.KeepAspectRatio))

        self.layout.addWidget(self.camwidget, 0, 0, 3, 1)
        self.layout.addWidget(self.zoomwidget, 0, 1, 1, 1)
        self.layout.addWidget(self.plotwidget, 1, 1, 1, 1)
        self.layout.addWidget(self.tiltwidget, 2, 1, 1, 1)
        self.layout.addWidget(self.logolabel, 3, 2)
        self.centralWidget().setLayout(self.layout)

    def createMenu(self):

        self.statusBar()
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
        self.action_fom = QtWidgets.QAction("&fom", self)
        self.pliMenu.addAction(self.action_fom)

        # CAMERA
        self.cameraMenu = self.mainMenu.addMenu('&camera')
        self.cameraPortMenu = self.cameraMenu.addMenu('port')
        self.cameraResolutionMenu = self.cameraMenu.addMenu('resolution')

        # HELP
        self.helpMenu = self.mainMenu.addMenu('&help')

        self.action_tracker = QtWidgets.QAction("&tracker", self)
        self.helpMenu.addAction(self.action_tracker)

    def connect_widgets(self):
        '''Connect Signal and Slots of the Widgets for inter Widget communication'''
        self.action_live.triggered.connect(
            partial(self.camwidget.set_mode, "live"))
        self.action_transmittance.triggered.connect(
            partial(self.camwidget.set_mode, "transmittance"))
        self.action_direction.triggered.connect(
            partial(self.camwidget.set_mode, "direction"))
        self.action_retardation.triggered.connect(
            partial(self.camwidget.set_mode, "retardation"))
        self.action_fom.triggered.connect(
            partial(self.camwidget.set_mode, "fom"))
        self.action_tracker.triggered.connect(self.camwidget.toogle_draw_helper)

        self.camwidget.zoom_update.connect(self.zoomwidget.update_image)

    def setBackground(self):
        '''
        Sets the Background Color
        '''
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(38, 65, 100))
        self.setPalette(p)

    def closeWidgets(self):
        self.camwidget.close()

    def closeEvent(self, event):
        '''
        Show a user dialog when window is closed
        '''

        self.closeWidgets()
        event.accept()
