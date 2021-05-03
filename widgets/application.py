import os
import pathlib

from PyQt5 import QtCore, QtGui, QtWidgets

from . import dummy
from . import display
from src import main_loop

PATH = os.path.join(pathlib.Path().absolute(), 'data')


class Application(QtWidgets.QMainWindow):
    """ 
    MainWindow of the application, which contains all widgets and sort them in a layout
    """

    def __init__(self, args, *qt_args, **qt_kwargs):

        super(Application, self).__init__(*qt_args, **qt_kwargs)
        self.__initUI__()

        # run application loop
        self.args = args
        self.app = main_loop.MainThread(self)
        for _ in range(10):
            self.app.next()  # first execution to look for python errors
        self.worker = QtCore.QTimer(self)
        self.worker.timeout.connect(self.app.next)
        self.worker.start(1000 // 25)  # TODO: min(camera.fps, 25)

    def __initUI__(self):
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("3D-PLI Demo")
        self.setWindowIcon(QtGui.QIcon(os.path.join(PATH, 'pli-logo.png')))
        self.setBackground()
        self.createWidgets()
        self.createLayout()
        self.createMenu()

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

        self.plotwidget = dummy.Label()
        self.plotwidget.setMinimumSize(QtCore.QSize(200, 200))
        self.plotwidget.setAlignment(QtCore.Qt.AlignCenter)
        self.plotwidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)

        self.setupwidget = dummy.Label()
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

        class Wrapper:

            def __init__(self, qt_menu):
                self._qt_menu = qt_menu
                self._qt_menu_dict = {}
                self._menu_dict = {}

            def add_menu(self, name):
                self._qt_menu_dict[name] = self._qt_menu.addMenu(f'&{name}')

                # dict behavior
                self._menu_dict[name] = Wrapper(self._qt_menu_dict[name])

                # member property like behavior
                # self.__setattr__(name, Wrapper(self._qt_menu_dict[name]))

            def add_action(self, action):
                self._qt_menu_dict[f'{action}'] = QtWidgets.QAction(
                    f'&{action}')
                self._qt_menu.addAction(self._qt_menu_dict[f'{action}'])

            def __getitem__(self, key):
                # needed for dict behavior
                return self._menu_dict[key]

        self.main_menu = Wrapper(self.menuBar())

        # main structure
        self.main_menu.add_menu('pli')
        self.main_menu.add_menu('camera')
        self.main_menu.add_menu('help')

        # examples
        # self.main_menu['camera'].add_menu('resolution')
        # self.main_menu['camera']['resolution'].add_action('640x480')
        # self.main_menu['help'].add_action('reset')
