import sys
import os

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from gui.dummy import ImageWidget
from gui.camerawidget import CameraWidget

pli_logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "pli-logo.png")


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
        self.createMenue()
        self.createCentralWidget()
        self.connect_widgets()
        self.setBackground()

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)

    def createCentralWidget(self):
        '''Creates Widgets and adds them to layout of centralWidget of MainWindow'''
        self.layout = QtWidgets.QGridLayout()

        self.setCentralWidget(QtWidgets.QWidget(self))

        self.cam_resolution_target = (1280, 1024)
        self.camwidget = CameraWidget(self)
        self.camwidget.setMinimumSize(QtCore.QSize(600, 600))

        self.plotwidget = ImageWidget(self)
        self.plotwidget.setMinimumSize(QtCore.QSize(300, 300))
        self.plotwidget.setMaximumSize(QtCore.QSize(600, 600))

        self.zoomwidget = ImageWidget(self)
        self.zoomwidget.setMinimumSize(QtCore.QSize(300, 300))
        self.zoomwidget.setMaximumSize(QtCore.QSize(600, 600))

        self.tiltwidget = ImageWidget(self)
        self.tiltwidget.setMinimumSize(QtCore.QSize(100, 300))
        self.tiltwidget.setMaximumSize(QtCore.QSize(300, 500))

        self.image = QtGui.QImage(pli_logo_path)
        self.logolabel = QtWidgets.QLabel()
        self.logolabel.setMaximumSize(QtCore.QSize(100, 100))
        self.logolabel.setMinimumSize(QtCore.QSize(100, 100))
        self.logolabel.setPixmap(
            QtGui.QPixmap.fromImage(self.image).scaled(
                self.logolabel.size().width(),
                self.logolabel.size().height(), QtCore.Qt.KeepAspectRatio))

        self.layout.addWidget(self.camwidget, 0, 0, 3, 1)
        self.layout.addWidget(self.zoomwidget, 0, 1, 1, 2)
        self.layout.addWidget(self.plotwidget, 1, 1, 1, 2)
        self.layout.addWidget(self.tiltwidget, 2, 1, 1, 2)
        self.layout.addWidget(self.logolabel, 3, 2)
        self.centralWidget().setLayout(self.layout)

    def createMenue(self):

        self.statusBar()
        mainMenu = self.menuBar()

        # PLI
        pliMenu = mainMenu.addMenu('&PLI')
        #
        extractAction = QtWidgets.QAction("&live", self)
        pliMenu.addAction(extractAction)
        #
        extractAction = QtWidgets.QAction("&transmittion", self)
        pliMenu.addAction(extractAction)
        #
        extractAction = QtWidgets.QAction("&direction", self)
        pliMenu.addAction(extractAction)
        #
        extractAction = QtWidgets.QAction("&retardation", self)
        pliMenu.addAction(extractAction)
        #
        extractAction = QtWidgets.QAction("&fom", self)
        pliMenu.addAction(extractAction)

        # CAMERA
        cameraMenu = mainMenu.addMenu('&Camera')
        #
        extractAction = QtWidgets.QAction("&port", self)
        # extractAction.setShortcut("Ctrl+C")
        # extractAction.setStatusTip('Change camera device')
        cameraMenu.addAction(extractAction)
        #
        extractAction = QtWidgets.QAction("&resolution", self)
        cameraMenu.addAction(extractAction)

    def connect_widgets(self):
        '''Connect Signal and Slots of the Widgets for inter Widget communication'''
        pass

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
        reply = QtWidgets.QMessageBox.question(
            self, 'Window Close', 'Are you sure you want to close the window?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.closeWidgets()
            event.accept()
            print('Window closed')
        else:
            event.ignore()
