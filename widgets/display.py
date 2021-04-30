import typing
from typing import Optional

import numpy as np
from PyQt5 import QtGui, QtWidgets


class Display(QtWidgets.QLabel):

    __is_frozen = False

    def __setattr__(self, key, value):
        if self.__is_frozen and not hasattr(self, key):
            raise TypeError('%r is a frozen class' % self)
        object.__setattr__(self, key, value)

    def __freeze(self):
        self.__is_frozen = True

    def __init__(self, parent=None, *args, **kwargs):
        super(Display, self).__init__(parent, *args, **kwargs)
        self.parent = parent

        # freeze class
        self.__freeze()

        # init
        self.initStyle()

    def initStyle(self) -> None:
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.setFrameStyle(QtWidgets.QFrame.Plain)

        # black background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.setPalette(palette)
