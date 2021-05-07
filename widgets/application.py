import functools
import os
import pathlib

import numpy as np
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
from src import worker

from . import display, microscope, plot

PATH = os.path.join(pathlib.Path().absolute(), 'data')
COLORSPHERE = Image.open(os.path.join(PATH, 'color_sphere.png'))


class Application(QtWidgets.QMainWindow):
    """ 
    MainWindow of the application, which contains all widgets and
    sort them in a layout
    """

    def __init__(self, args, *qt_args, **qt_kwargs):

        super(Application, self).__init__(*qt_args, **qt_kwargs)
        self.__initUI__()

        self.args = args
        self.app = worker.MainThread(self)
        self.connectSignals()

        # run application loop
        for _ in range(10):
            self.app.next()  # first execution to look for python errors

        if self.args.first_n:
            exit(0)

        self.worker = QtCore.QTimer(self)
        # TODO: 1000//min(camera.fps, 25)
        self._mspf = 1000 // 60  # miliseconds per frame
        self.worker.timeout.connect(self.app.next)
        self.worker.start(self._mspf)

    def __initUI__(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("3D-PLI Demo")
        self.setWindowIcon(QtGui.QIcon(os.path.join(PATH, 'pli-logo.png')))
        self.setBackground()
        self.createMenu()
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

        self.main_display = display.Display(self)
        self.main_display.setMinimumSize(QtCore.QSize(545, 545))
        self.main_display.setAlignment(QtCore.Qt.AlignCenter)
        self.main_display.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                        QtWidgets.QSizePolicy.Minimum)

        self.plotwidget = plot.Plot()
        self.plotwidget.setMinimumSize(QtCore.QSize(200, 200))
        self.plotwidget.setAlignment(QtCore.Qt.AlignCenter)
        self.plotwidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)

        self.setupwidget = microscope.SetupWidget()
        self.setupwidget.setMinimumSize(QtCore.QSize(100, 200))

        self.logo_pli = QtWidgets.QLabel()
        self.logo_pli.setMinimumHeight(50)
        self.logo_pli.setMaximumHeight(50)
        self.logo_pli.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(os.path.join(PATH, "pli-logo.png"))).scaled(
                    self.logo_pli.size().width(),
                    self.logo_pli.size().height(), QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation))
        self.logo_pli.setAlignment(QtCore.Qt.AlignRight)
        self.logo_pli.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                    QtWidgets.QSizePolicy.Minimum)

        self.logo_fzj = QtWidgets.QLabel()
        self.logo_fzj.setMinimumHeight(50)
        self.logo_fzj.setMaximumHeight(50)
        self.logo_fzj.setPixmap(
            QtGui.QPixmap.fromImage(
                QtGui.QImage(os.path.join(PATH, "fzj-gray.png"))).scaled(
                    self.logo_fzj.size().width(),
                    self.logo_fzj.size().height(), QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation))
        self.logo_fzj.setAlignment(QtCore.Qt.AlignRight)
        self.logo_fzj.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                    QtWidgets.QSizePolicy.Maximum)

        # adding label to status bar
        # self.statusBar().showMessage('')
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Init", 3000)

        # Add angleLabel
        self.status_angle = QtWidgets.QLabel('')
        self.statusbar.addPermanentWidget(self.status_angle)

    def connectSignals(self):
        pass

    def createLayout(self):
        self.layout = QtWidgets.QGridLayout()
        self.layout_logos = QtWidgets.QGridLayout()

        self.layout.addWidget(self.main_display, 0, 0, 2, 1)
        self.layout.addWidget(self.setupwidget, 0, 1, 1, 1)
        self.layout.addWidget(self.plotwidget, 1, 1, 1, 1)
        self.layout.addLayout(self.layout_logos, 2, 1, 1, 1)
        self.layout_logos.addWidget(self.logo_pli, 0, 0, 1, 1)
        self.layout_logos.addWidget(self.logo_fzj, 0, 1, 1, 1)

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 1)

        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)

        self.layout.setSpacing(50)
        self.layout_logos.setSpacing(50)

        status_bar_height = self.statusBar().frameGeometry().height()
        self.layout.setContentsMargins(50, 50, 50, 50 - status_bar_height)

        self.centralWidget().setLayout(self.layout)

    def createMenu(self):
        """ create buttons, connection is seperated """

        class ActionWrapper(QtWidgets.QAction):

            def isAction(self):
                return True

            def isMenu(self):
                return False

            def set_enabled(self, value):
                self.setEnabled(value)

        class MenuWrapper:

            def __init__(self, qt_menu):
                self._qt_obj = qt_menu
                self._menu_dict = {}

            def isAction(self):
                return False

            def isMenu(self):
                return True

            def add_menu(self, name, active=True):
                if name in self._menu_dict:
                    raise ValueError(
                        f'entry "{name}" already exists in "{self._qt_obj}"')
                self._menu_dict[name] = MenuWrapper(
                    self._qt_obj.addMenu(f'&{name}'))
                self._menu_dict[name].set_enabled(active)

            def add_action(self, name, triggered, active=True):
                if name in self._menu_dict:
                    raise ValueError(
                        f'entry "{name}" already exists in "{self._qt_obj}"')
                self._menu_dict[name] = ActionWrapper(f'{name}',
                                                      triggered=triggered)
                self._qt_obj.addAction(self._menu_dict[name])
                self._menu_dict[name].set_enabled(active)

            def __getitem__(self, key):
                return self._menu_dict[key]

            def entries(self):
                return [elm for elm in self._menu_dict.values()]

            def set_enabled(self, value):
                self._qt_obj.setEnabled(value)

            def clear(self):
                self._qt_obj.clear()
                self._menu_dict = {}

            def clear_actions(self):
                to_pop = []
                for key, elm in self._menu_dict.items():
                    if elm.isAction():
                        self._qt_obj.removeAction(elm)
                        to_pop.append(key)
                for elm in to_pop:
                    self._menu_dict.pop(elm, None)

            def clear_menus(self):
                for elm in self.entries():
                    if elm.isMenu():
                        elm.clear()

            def clear_elements(self):
                self.clear_actions()
                self.clear_menus()

        self.main_menu = MenuWrapper(self.menuBar())

        # INFO:
        """
        actions will be mostly specified at the functions scr code
        containeing the methods

        examples:
        self.main_menu['camera'].add_menu('resolution')
        self.main_menu['camera']['resolution'].add_action('640x480')
        self.main_menu['help'].add_action('reset')
        self.main_menu['camera'].clear()
        self.main_menu['camera'].set_enabled(False)
        """

        # main structure
        """ the sub structure will be handled by the tools """
        self.main_menu.add_menu('pli')
        self.main_menu.add_menu('camera')
        self.main_menu.add_menu('tools')
        self.main_menu.add_menu('help')

        self.main_menu['camera'].add_menu('port')
        self.main_menu['camera'].add_menu('resolution')
        self.main_menu['camera'].add_menu('demo')

        self.main_menu['camera']['resolution'].add_action(
            'check resolution', lambda: self.app.check_device_properties())

        # secondary, never changing structure
        self.main_menu['tools'].add_action('save_plot',
                                           lambda: self.app.save_plot())
        self.main_menu['tools'].add_action('save_images',
                                           lambda: self.app.save_images())
        self.main_menu['tools'].add_action('apply offset',
                                           lambda: self.app.apply_offset())

        self.main_menu['help'].add_action('debug',
                                          lambda: self.app.switch_debug())
        self.main_menu['help'].add_action('reset', lambda: self.app.reset())

        def show_live():
            self.app.to_live_mode()
            self.app._last_img_name = 'live'

        def show_img_and_stop(image, cval, name):
            image = image / cval * 255
            image = image.astype(np.uint8)

            if name == 'fom':
                shape = np.array(image.shape[:-1]) // 6
                cs = COLORSPHERE.resize(shape, Image.NEAREST)
                cs = np.asarray(cs)[:, :, :-1]  # PIL returns RGBA
                image[0:shape[0], image.shape[1] - shape[1]:, :] = cs

            self.app.show_image(image)
            self.app._last_img_name = name  # TODO: enum with str as value
            self.worker.stop()

        self.main_menu['pli'].add_action('live', lambda: show_live())
        self.main_menu['pli'].add_action(
            'transmittance', lambda: show_img_and_stop(
                self.app.pli.transmittance(self.app._tilt.value), 255,
                'transmittance'))
        self.main_menu['pli'].add_action(
            'direction', lambda: show_img_and_stop(
                self.app.pli.direction(self.app._tilt.value), np.pi, 'direction'
            ))
        self.main_menu['pli'].add_action(
            'retardation', lambda: show_img_and_stop(
                self.app.pli.retardation(self.app._tilt.value), 1, 'retardation'
            ))
        self.main_menu['pli'].add_action(
            'inclination', lambda: show_img_and_stop(
                self.app.pli.inclination(self.app._tilt.value), 1, 'inclination'
            ))
        self.main_menu['pli'].add_action(
            'fom', lambda: show_img_and_stop(self.app.pli.fom, 1, 'fom'))

        self.main_menu['pli'].add_menu('tilts')

        def set_and_show_tilt(abc):
            self.app.set_tilt(abc)
            self.main_menu['pli'][self.app._last_img_name].trigger()
            self.app.update_plot()

        # TODO: why here partial and above lambda?
        for tilt_name in worker.MainThread.Tilt:
            self.main_menu['pli']['tilts'].add_action(
                tilt_name.value,
                functools.partial(set_and_show_tilt, tilt_name.value))
