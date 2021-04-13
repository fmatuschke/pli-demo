import sys
import os
import numpy as np

from functools import partial

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QSpinBox, QVBoxLayout, QPushButton

from gui.camera_widget import CameraWidget
from gui.plot_widget import PlotWidget
from gui.setup_widget import SetupWidget
from gui.zoom_widget import ZoomWidget
from src.camera import CamMode, CamColor
from src.tracker import Tracker


import cv2

logo_path = "data"


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

    switch_window = QtCore.pyqtSignal(str)

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

    #def switch(self):
    #    self.switch_window.emit(self.line_edit.text)

    def createCentralWidget(self):
        # get Pixel of Mouse
        x = 0
        y = 0

        self.pixtext = f'x: {x},  y: {y}'
        self.pix = QLabel(self.pixtext, self)
        self.setMouseTracking(False)

        self.setCentralWidget(QtWidgets.QWidget(self))

        self.camwidget = CameraWidget(self)
        self.camwidget.setMinimumSize(QtCore.QSize(545, 545)) #(600,600)
        self.camwidget.setAlignment(QtCore.Qt.AlignCenter)
        self.camwidget.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                     QtWidgets.QSizePolicy.Minimum)

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
        self.setupwidget.setMinimumSize(QtCore.QSize(100, 200)) #QSize(100,300)
        # self.setupwidget.setMaximumSize(QtCore.QSize(300, 500))

        self.logolabelpli = QtWidgets.QLabel()
        self.logolabelpli.setMinimumHeight(50)
        self.logolabelpli.setMaximumHeight(50)
        self.logolabelpli.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(os.path.join(logo_path, "pli-logo.png"))).scaled(
                    self.logolabelpli.size().width(),
                    self.logolabelpli.size().height(),
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.logolabelpli.setAlignment(QtCore.Qt.AlignRight)
        self.logolabelpli.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                        QtWidgets.QSizePolicy.Minimum)
        # p = self.logolabelpli.palette()
        # p.setColor(self.logolabelpli.backgroundRole(), QtGui.QColor(255, 0, 0))
        # self.logolabelpli.setAutoFillBackground(True)
        # self.logolabelpli.setPalette(p)

        self.logolabelfzj = QtWidgets.QLabel()
        self.logolabelfzj.setMinimumHeight(50)
        self.logolabelfzj.setMaximumHeight(50)
        self.logolabelfzj.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(os.path.join(logo_path, "fzj-gray.png"))).scaled(
                    self.logolabelfzj.size().width(),
                    self.logolabelfzj.size().height(),
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.logolabelfzj.setAlignment(QtCore.Qt.AlignRight)
        self.logolabelfzj.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                        QtWidgets.QSizePolicy.Maximum)

        self.color_sphere = QtWidgets.QLabel()
        self.color_sphere.setMinimumHeight(50)
        self.color_sphere.setMaximumHeight(50)
        self.color_sphere.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(os.path.join(logo_path, "color_sphere.png"))).scaled(
                    self.color_sphere.size().width(),
                    self.color_sphere.size().height(),
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.color_sphere.setAlignment(QtCore.Qt.AlignRight)
        #self.color_sphere.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
        #                               QtWidgets.QSizePolicy.Maximum)



        ''' LAYOUT
        '''
        self.layout = QtWidgets.QGridLayout()
        self.layout_logos = QtWidgets.QGridLayout()

        self.layout.addWidget(self.camwidget, 0, 0, 2, 1)
        self.layout.addWidget(self.color_sphere, 1, 0, 2, 1) #(0,0,2,1)
        self.layout.addWidget(self.setupwidget, 0, 1, 1, 1)
        self.layout.addWidget(self.plotwidget, 1, 1, 1, 1)
        self.layout.addLayout(self.layout_logos, 2, 1, 1, 1)
        self.layout_logos.addWidget(self.logolabelpli, 0, 0, 1, 1)
        self.layout_logos.addWidget(self.logolabelfzj, 0, 1, 1, 1)
        self.layout.addWidget(self.pix, 2, 0, 1, 1)

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 1)
        # self.layout.setColumnStretch(2, 1)

        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

        self.layout.setSpacing(50)
        self.layout_logos.setSpacing(50)
        self.layout.setContentsMargins(50, 50, 50, 50 - 30)

        self.centralWidget().setLayout(self.layout)

    # Mousemovement
    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()

        pixtext = f'x: {x},  y: {y}'
        self.pix.setText(pixtext)

    # Def for saving data
    def savedata(self):
        np.savetxt("saved_data.txt", np.column_stack([self.plotwidget.x_save, self.plotwidget.y_save]), fmt="%1.3f")
        np.savetxt('saved_values.txt', self.camwidget.plot_val, fmt="%1.3f", header='Values of Inclination, Retardation, Direction, Transmittance and relative Transmittance')




    #def colorsphereon(self):
    #    self.color_sphere.setEnabled(True)

    #def colorsphereoff(self):
    #    self.color_sphere.setEnabled(False)

    #def colorsphere(self):
    #    self.color_sphere = QtWidgets.QLabel()
    #    self.color_sphere.setMinimumHeight(50)
    #    self.color_sphere.setMaximumHeight(50)
    #    self.color_sphere.setPixmap(
    #        QtGui.QPixmap.fromImage(
    #            QtGui.QImage(os.path.join(logo_path,
    #                                      "color_sphere.png"))).scaled(
    #            self.color_sphere.size().width(),
    #            self.color_sphere.size().height(),
    #            QtCore.Qt.KeepAspectRatio,
    #            QtCore.Qt.SmoothTransformation))
    #    self.color_sphere.setAlignment(QtCore.Qt.AlignRight)

    #    self.layout.addWidget(self.color_sphere, 1, 0, 2, 1)

    #def nocolorsphere(self):
     #       self.color_sphere.hide()

    def createMenu(self):

        self.statusBar()
        # self.statusBar().setStyleSheet("border :1px solid black;")
        # print(self.statusBar().size()) # (100.30)
        self.mainMenu = self.menuBar()

        # PLI
        self.pliMenu = self.mainMenu.addMenu('&PLI')
        #
        self.action_live = QtWidgets.QAction("&live", self)
        self.pliMenu.addAction(self.action_live)
        #
        self.action_transmittance = QtWidgets.QAction("&transmittance", self)
        self.action_transmittance.setEnabled(False)
        self.pliMenu.addAction(self.action_transmittance)
        #
        self.action_direction = QtWidgets.QAction("&direction", self)
        self.action_direction.setEnabled(False)
        self.pliMenu.addAction(self.action_direction)
        #
        self.action_retardation = QtWidgets.QAction("&retardation", self)
        self.action_retardation.setEnabled(False)
        self.pliMenu.addAction(self.action_retardation)
        #
        self.action_inclination = QtWidgets.QAction("&inclination", self)
        self.action_inclination.setEnabled(False)
        self.pliMenu.addAction(self.action_inclination)
        #
        self.action_fom = QtWidgets.QAction("&fom", self)
        self.action_fom.setEnabled(False)
        self.pliMenu.addAction(self.action_fom)
        #
        # Tilting
        self.tiltingMenu = self.pliMenu.addMenu("&tilting")
        self.tiltingMenu.setEnabled(False)
        #
        self.action_tilt_zero = QtWidgets.QAction("&zero", self)
        self.action_tilt_zero.setEnabled(False)
        self.tiltingMenu.addAction(self.action_tilt_zero)
        #
        self.action_tilt_north = QtWidgets.QAction("&north", self)
        self.action_tilt_north.setEnabled(False)
        self.tiltingMenu.addAction(self.action_tilt_north)
        #
        self.action_tilt_west = QtWidgets.QAction("&west", self)
        self.action_tilt_west.setEnabled(False)
        self.tiltingMenu.addAction(self.action_tilt_west)
        #
        self.action_tilt_south = QtWidgets.QAction("&south", self)
        self.action_tilt_south.setEnabled(False)
        self.tiltingMenu.addAction(self.action_tilt_south)
        #
        self.action_tilt_east = QtWidgets.QAction("&east", self)
        self.action_tilt_east.setEnabled(False)
        self.tiltingMenu.addAction(self.action_tilt_east)

        # CAMERA
        self.cameraMenu = self.mainMenu.addMenu('&camera')
        self.cameraPortMenu = self.cameraMenu.addMenu('&port')
        self.cameraResolutionMenu = self.cameraMenu.addMenu('&resolution')
        self.cameraFilterMenu = self.cameraMenu.addMenu('&filter')
        self.cameraColorMenu = self.cameraMenu.addMenu('&color')
        self.cameraDemoMenu = self.cameraMenu.addMenu('&demo')
        #
        self.action_color_gray = QtWidgets.QAction("&gray", self)
        self.cameraColorMenu.addAction(self.action_color_gray)
        self.action_color_rgb = QtWidgets.QAction("&rgb", self)
        self.cameraColorMenu.addAction(self.action_color_rgb)
        self.action_color_r = QtWidgets.QAction("&r", self)
        self.cameraColorMenu.addAction(self.action_color_r)
        self.action_color_g = QtWidgets.QAction("&g", self)
        self.cameraColorMenu.addAction(self.action_color_g)
        self.action_color_b = QtWidgets.QAction("&b", self)
        self.cameraColorMenu.addAction(self.action_color_b)
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

        # SAVE DATA
        self.saveMenu = self.mainMenu.addMenu('&Save')

        self.save_data = QtWidgets.QAction("&Save data", self)
        self.saveMenu.addAction(self.save_data)


    def set_pli_menu(self, value):
        value = bool(value)
        self.action_transmittance.setEnabled(value)
        self.action_direction.setEnabled(value)
        self.action_retardation.setEnabled(value)
        self.action_inclination.setEnabled(value)
        self.action_fom.setEnabled(value)
        self.tiltingMenu.setEnabled(value)
        self.action_tilt_zero.setEnabled(value)
        self.action_tilt_north.setEnabled(value)
        self.action_tilt_west.setEnabled(value)
        self.action_tilt_south.setEnabled(value)
        self.action_tilt_east.setEnabled(value)



    def connect_widgets(self):
        self.action_live.triggered.connect(
            partial(self.camwidget.set_mode, "live"))
        self.action_live.triggered.connect(
            partial(self.color_sphere.hide))
        #self.action_live.triggered.connect(
        #    partial(self.colorsphereoff))

        self.action_transmittance.triggered.connect(
            partial(self.camwidget.set_mode, "transmittance"))
        self.action_transmittance.triggered.connect(
           partial(self.color_sphere.hide))
        #self.action_transmittance.triggered.connect(
         #   partial(self.colorsphereoff))

        self.action_direction.triggered.connect(
            partial(self.camwidget.set_mode, "direction"))
        self.action_direction.triggered.connect(
            partial(self.color_sphere.hide))
        #self.action_direction.triggered.connect(
        #    partial(self.colorsphereoff))

        self.action_retardation.triggered.connect(
            partial(self.camwidget.set_mode, "retardation"))
        self.action_retardation.triggered.connect(
           partial(self.color_sphere.hide))
        #self.action_retardation.triggered.connect(
         #   partial(self.colorsphereoff))

        self.action_inclination.triggered.connect(
            partial(self.camwidget.set_mode, "inclination"))
        self.action_inclination.triggered.connect(
           partial(self.color_sphere.hide))
        #self.action_inclination.triggered.connect(
         #   partial(self.colorsphereoff))

        self.action_fom.triggered.connect(
            partial(self.camwidget.set_mode, "fom"))
        self.action_fom.triggered.connect(
           partial(self.color_sphere.show))
        #self.action_fom.triggered.connect(
         #   partial(self.colorsphereon))


        #
        def update_tilt(theta, phi, mode):
            self.setupwidget.set_tilt(theta, phi)
            self.camwidget.pli_stack.set_tilt_mode(mode)
            self.camwidget.set_mode(self.camwidget.mode)  # update frame
            self.setupwidget.update()

        self.action_tilt_zero.triggered.connect(partial(update_tilt, 0, 0, 0))
        self.action_tilt_north.triggered.connect(
            partial(update_tilt, 10, 270, 1))
        self.action_tilt_west.triggered.connect(partial(update_tilt, 10, 0, 2))
        self.action_tilt_south.triggered.connect(partial(
            update_tilt, 10, 90, 3))
        self.action_tilt_east.triggered.connect(partial(update_tilt, 10, 180,
                                                        4))
        #
        self.action_tracker.triggered.connect(self.camwidget.toogle_draw_helper)
        self.action_reset.triggered.connect(lambda: self.reset())

        #
        self.save_data.triggered.connect(self.savedata)





        #
        self.camwidget.plot_update.connect(self.plotwidget.update_plot)
        # self.camwidget.zoom_update.connect(self.zoomwidget.update_image)

        self.action_color_gray.triggered.connect(
            partial(self.camwidget.set_color, CamColor.GRAY))
        self.action_color_rgb.triggered.connect(
            partial(self.camwidget.set_color, CamColor.RGB))
        self.action_color_r.triggered.connect(
            partial(self.camwidget.set_color, CamColor.RED))
        self.action_color_g.triggered.connect(
            partial(self.camwidget.set_color, CamColor.GREEN))
        self.action_color_b.triggered.connect(
            partial(self.camwidget.set_color, CamColor.BLUE))

        self.action_filter_none.triggered.connect(
            partial(self.camwidget.set_filter, "none"))
        self.action_filter_gaus.triggered.connect(
            partial(self.camwidget.set_filter, "gaus"))
        self.action_filter_nlmd.triggered.connect(
            partial(self.camwidget.set_filter, "nlmd"))

    def keyPressEvent(self, event):
        if self.camwidget.camera._mode == CamMode.VIDEO:
            if event.key() == QtCore.Qt.Key_Comma:
                if self.camwidget.live.isActive():
                    self.camwidget.live.stop()
                next_frame = self.camwidget.camera._video_capture.get(
                    cv2.CAP_PROP_POS_FRAMES) - 2
                if next_frame < 0:
                    next_frame = self.camwidget.camera._video_capture.get(
                        cv2.CAP_PROP_FRAME_COUNT) - 1
                self.camwidget.camera._video_capture.set(
                    cv2.CAP_PROP_POS_FRAMES, next_frame)
                self.camwidget.next_frame()
            if event.key() == QtCore.Qt.Key_Period:
                if self.camwidget.live.isActive():
                    self.camwidget.live.stop()
                self.camwidget.next_frame()
            if event.key() == QtCore.Qt.Key_Space:
                if self.camwidget.live.isActive():
                    self.camwidget.live.stop()
                else:
                    self.camwidget.live.start(30)

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

#window for offset

class Offset(QtWidgets.QWidget):

    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Set Offset')

        layout = QtWidgets.QGridLayout()


        self.offsetvalue = QSpinBox(self)
        self.offsetvalue.setRange(-180, 180)

        self.button = QtWidgets.QPushButton('Confirm')
        self.button.clicked.connect(self.offset)

        layout.addWidget(self.offsetvalue)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def offset(self):
        #print(self.offsetvalue.value())
        self.switch_window.emit()


#switch windows
class Controller:

    def __init__(self):
        self.window = MainWindow()
        self.offset = Offset()

    def show_offset(self):
        self.offset.switch_window.connect(self.show_main)
        self.offset.show()

    def show_main(self):
        self.window.camwidget.polfilter_offset = np.deg2rad(
            self.offset.offsetvalue.value())
        self.offset.close()
        self.window.show()




