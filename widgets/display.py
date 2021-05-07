from __future__ import annotations

from PyQt5 import QtCore, QtGui, QtWidgets


class Display(QtWidgets.QLabel):

    __is_frozen = False

    xy_signal = QtCore.pyqtSignal(float, float)

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

    def resizeEvent(self, event):
        super(Display, self).resizeEvent(event)
        self.parent.app.show_image(self.parent.app._last_image)

    def _widgetNormedCoordinates(self, click_x: int,
                                 click_y: int) -> tuple(float, float):
        """
        return pixmap coordinate. if data is cropped after masked,
        add mask offset if you want pli_stack.get()!
        """
        pixmap_width = self.pixmap().size().width()
        pixmap_height = self.pixmap().size().height()

        widget_width = self.size().width()
        widget_height = self.size().height()

        # For centered alignment:
        offset_x = (widget_width - pixmap_width) / 2
        offset_y = (widget_height - pixmap_height) / 2

        x = (click_x - offset_x) / pixmap_width
        y = (click_y - offset_y) / pixmap_height
        return x, y

    def mousePressEvent(self, event):
        """
        Sets Tracking coordinate to the clicked coordinate
        """
        if self.pixmap() is None:
            return

        x, y = self._widgetNormedCoordinates(event.x(), event.y())
        if x >= 0 and x < 1 and y >= 0 and y < 1:
            self.parent.app.update_plot_coordinates_buffer(x, y)
