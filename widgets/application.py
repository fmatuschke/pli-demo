import os
import pathlib

from PyQt5 import QtCore, QtGui, QtWidgets

PATH = pathlib.Path().absolute()
print(PATH)


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
        self.setWindowIcon(QtGui.QIcon(os.path.join(PATH, "pli-logo.png")))
        self.setBackground()

    def resizeEvent(self, event):
        super(Application, self).resizeEvent(event)
        # add user specific resize functionality here

    def setBackground(self):
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(38, 65, 100))
        self.setPalette(p)
