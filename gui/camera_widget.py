import os

from functools import partial

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from src.camera import Camera


class CameraWidget(QtWidgets.QWidget):

    click_update = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None, *args, **kwargs):
        super(CameraWidget, self).__init__(parent, *args, **kwargs)
        self.ui = parent
        self.init_camera()
        self.click_x = int(self.camera.width() / 2 + 0.5)
        self.click_y = int(self.camera.height() / 2 + 0.5)

    def init_camera(self):
        self.camera = Camera(fps=25, port_id=1)
        self.is_live = self.camera.live()

        for width, height in self.camera.working_resolutions:
            self.ui.cameraResolutionMenu.addAction(
                QtWidgets.QAction(f"{width}x{height}",
                                  self.ui.cameraResolutionMenu,
                                  triggered=partial(self.camera.set_resolution,
                                                    width, height)))

        # setup image label
        self.image_label = QtWidgets.QLabel()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout)

        # QTimer to access camera frames
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_camera_frame)
        # self.timer.timeout.connect(self.update_zoomImage)
        self.timer.start(40)  # 1000/fps

    def resizeEvent(self, event):
        super(CameraWidget, self).resizeEvent(event)

    def convertFrame2Image(self, frame):
        '''
        convert camera frame to qimage with size of qlabel
        '''
        image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],
                             QtGui.QImage.Format_RGB888)
        image = image.rgbSwapped()
        image = image.scaledToWidth(self.size().width())
        self.label_offset_y = (self.size().height() -
                               image.size().height()) * 0.5
        return image

    def widget2framecoordinates(self, click_x, click_y):
        '''
        Umrechnung der Click- Koordinaten im Widget in QtWidgets.QLabel Koordinaten und dann in Frame-Koordinaten
        '''
        label_x = click_x
        label_y = click_y - self.label_offset_y

        frame_x = int(label_x * self.camera.height() / self.size().width() +
                      0.5)
        frame_y = int(label_y * self.camera.height() / self.size().width() +
                      0.5)

        #print("widget ", click_x, click_y)
        #print("label  ", label_x, label_y)
        print("frame  ", frame_x, frame_y)

        return frame_x, frame_y

    def mousePressEvent(self, event):
        '''
        Sets Tracking coordinate to the clicked coordinate
        '''
        # if y coordinate is in QtWidgets.QLabel
        if (event.y() > self.label_offset_y and
                event.y() < self.size().height() - self.label_offset_y):
            self.click_x, self.click_y = self.widget2framecoordinates(
                event.x(), event.y())
            self.click_update.emit(self.click_x, self.click_y)
            # self.update_zoomImage()

    def update_camera_frame(self):
        if self.is_live:
            self.image_label.setPixmap(
                QtGui.QPixmap.fromImage(
                    self.convertFrame2Image(self.camera.frame())))
