import os
import pathlib

from PyQt5 import QtCore, QtGui, QtWidgets
from src import main_loop

from . import display, dummy, plot, animation

PATH = os.path.join(pathlib.Path().absolute(), 'data')


class Application(QtWidgets.QMainWindow):
    """ 
    MainWindow of the application, which contains all widgets and sort them in a layout
    """

    def __init__(self, args, *qt_args, **qt_kwargs):

        super(Application, self).__init__(*qt_args, **qt_kwargs)
        self.__initUI__()

        self.args = args
        self.app = main_loop.MainThread(self)
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

        self.main_display = display.Display()
        self.main_display.setMinimumSize(QtCore.QSize(545, 545))
        self.main_display.setAlignment(QtCore.Qt.AlignCenter)
        self.main_display.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                        QtWidgets.QSizePolicy.Minimum)

        self.plotwidget = plot.Plot()
        self.plotwidget.setMinimumSize(QtCore.QSize(200, 200))
        self.plotwidget.setAlignment(QtCore.Qt.AlignCenter)
        self.plotwidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)

        self.setupwidget = animation.SetupWidget()
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
        self.statusBar().showMessage('')

    def connectSignals(self):
        self.main_display.xy_signal.connect(self.app.update_plot)
        # self.main_display.rho_signal.connect(self.app.update_plot_rho)
        # self.app.rho_signal.connect(self.setupwidget.set_rotation)

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

        class Wrapper:

            def __init__(self, qt_menu):
                self._qt_obj = qt_menu
                self._menu_dict = {}

            def isAction(self):
                return False

            def isMenu(self):
                return True

            def add_menu(self, name):
                if name in self._menu_dict:
                    raise ValueError(
                        f'entry "{name}" already exists in "{qt_menu}"')
                self._menu_dict[name] = Wrapper(
                    self._qt_obj.addMenu(f'&{name}'))

            def add_action(self, name, triggered):
                if name in self._menu_dict:
                    raise ValueError(
                        f'entry "{name}" already exists in "{qt_menu}"')
                self._menu_dict[name] = ActionWrapper(f'{name}',
                                                      triggered=triggered)
                self._qt_obj.addAction(self._menu_dict[name])

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

        self.main_menu = Wrapper(self.menuBar())

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
        self.main_menu.add_menu('pli')
        self.main_menu.add_menu('camera')
        self.main_menu.add_menu('help')

        # self.main_menu['pli'].add_action('live', to_live_mode)

        # CAMERA
        # self.main_menu['camera'].add_menu('port')
        # self.main_menu['camera'].add_menu('demo')
        # self.main_menu['camera'].add_menu('resolution')
        # self.main_menu['camera'].add_menu('filter')
        # self.main_menu['camera'].add_menu('color')

        # HELP
        # def switch_debug():
        #     self.app._debug = not self.app._debug

        # def reset():
        #     self.app.reset()

        # self.main_menu['help'].add_action('debug', switch_debug)
        # self.main_menu['help'].add_action('reset', reset)
