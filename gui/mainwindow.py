import sys
import os
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor, QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox
from PyQt5.QtWidgets import QGridLayout, QLabel
from PyQt5.QtWidgets import QMenuBar, QAction, qApp

from gui.dummy import ImageWidget


class MainWindow(QMainWindow):
    '''
    MainWindow of the application, which contains all widgets and sort them in a layout
    '''

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.__initUI__()

    def __initUI__(self):
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("3D-PLI Demo")
        self.createCentralWidget()
        self.connect_widgets()
        self.setBackground()

    def resizeEvent(self, event):
        super(MainWindow, self).resizeEvent(event)

    def createCentralWidget(self):
        '''Creates Widgets and adds them to layout of centralWidget of MainWindow'''
        self.layout = QGridLayout()

        self.setCentralWidget(QWidget(self))

        self.cam_resolution_target = (1280, 1024)
        self.camwidget = ImageWidget(self)
        self.camwidget.setMinimumSize(QSize(600, 600))

        self.plotwidget = ImageWidget(self)
        self.plotwidget.setMinimumSize(QSize(300, 300))
        self.plotwidget.setMaximumSize(QSize(600, 600))

        self.zoomwidget = ImageWidget(self)
        self.zoomwidget.setMinimumSize(QSize(300, 300))
        self.zoomwidget.setMaximumSize(QSize(600, 600))

        self.tiltwidget = ImageWidget(self)
        self.tiltwidget.setMinimumSize(QSize(100, 300))
        self.tiltwidget.setMaximumSize(QSize(300, 500))

        self.image = QImage(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "pli-logo.png"))
        self.logolabel = QLabel()
        self.logolabel.setMaximumSize(QSize(100, 100))
        self.logolabel.setMinimumSize(QSize(100, 100))
        self.logolabel.setPixmap(
            QPixmap.fromImage(self.image).scaled(self.logolabel.size().width(),
                                                 self.logolabel.size().height(),
                                                 Qt.KeepAspectRatio))

        self.layout.addWidget(self.camwidget, 0, 0, 3, 1)
        self.layout.addWidget(self.zoomwidget, 0, 1, 1, 2)
        self.layout.addWidget(self.plotwidget, 1, 1, 1, 2)
        self.layout.addWidget(self.tiltwidget, 2, 1, 1, 2)
        self.layout.addWidget(self.logolabel, 3, 2)
        self.centralWidget().setLayout(self.layout)

    def connect_widgets(self):
        '''Connect Signal and Slots of the Widgets for inter Widget communication'''
        pass

    def setBackground(self):
        '''
        Sets the Background Color
        '''
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(38, 65, 100))
        self.setPalette(p)

    def closeWidgets(self):
        self.buttons.close()
        self.camwidget.close()

    def closeEvent(self, event):
        '''
        Show a user dialog when window is closed
        '''
        reply = QMessageBox.question(
            self, 'Window Close', 'Are you sure you want to close the window?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.closeWidgets()
            event.accept()
            print('Window closed')
        else:
            event.ignore()
