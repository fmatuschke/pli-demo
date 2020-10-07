import os

import numpy as np
from functools import partial

import cv2
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from src.camera import Camera
from src.tracker import Tracker
from src.pli import Stack as PliStack
from src import helper


class CameraWidget(QtWidgets.QWidget):

    click_update = QtCore.pyqtSignal(int, int)
    zoom_update = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, parent=None, *args, **kwargs):
        super(CameraWidget, self).__init__(parent, *args, **kwargs)
        self.ui = parent
        self.init_camera()
        self.show_tracker = False
        self.show_angle = False
        self.tracker = Tracker()
        self.pli_stack = PliStack()
        self.mode = "live"

    def init_camera(self):
        self.camera = Camera(fps=25)

        for width, height in self.camera.working_resolutions:
            self.ui.cameraResolutionMenu.addAction(
                QtWidgets.QAction(f"{width}x{height}",
                                  self.ui.cameraResolutionMenu,
                                  triggered=partial(self.camera.set_resolution,
                                                    width, height)))
        self.click_x = int(self.camera.width() / 2 + 0.5)
        self.click_y = int(self.camera.height() / 2 + 0.5)

        # setup image label
        self.image_label = QtWidgets.QLabel()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.image_label)
        self.setLayout(self.layout)

        # QTimer to access camera frames
        self.live = QtCore.QTimer(self)
        self.live.timeout.connect(self.update_camera_frame)
        # self.timer.timeout.connect(self.update_zoomImage)
        self.live.start(40)  # 1000/fps

    def resizeEvent(self, event):
        super(CameraWidget, self).resizeEvent(event)

    def convertFrame2Image(self, frame):
        '''
        convert camera frame to qimage with size of qlabel
        '''
        if frame.ndim == 2:
            img_format = QtGui.QImage.Format_Grayscale8
        else:
            img_format = QtGui.QImage.Format_RGB888

        image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],
                             img_format)
        image = image.rgbSwapped()
        image = image.scaled(self.size().width(),
                             self.size().height(), QtCore.Qt.KeepAspectRatio)
        self.label_offset_y = (self.size().height() -
                               image.size().height()) * 0.5
        self.label_height = image.size().height()
        self.label_width = image.size().width()
        return image

    def toogle_draw_helper(self):
        self.show_tracker = not self.show_tracker
        self.show_angle = not self.show_angle

    def widget2framecoordinates(self, click_x, click_y):
        '''
        Umrechnung der Click- Koordinaten im Widget in QtWidgets.QLabel Koordinaten und dann in Frame-Koordinaten
        '''
        label_x = click_x
        label_y = click_y - self.label_offset_y

        frame_x = int(label_x * self.label_height / self.size().width() + 0.5)
        frame_y = int(label_y * self.label_height / self.size().width() + 0.5)

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
            self.update_zoomImage()

    def update_zoomImage(self):
        d = 42
        x = max(d, min(self.frame.shape[1] - d - 1, self.click_x))
        y = max(d, min(self.frame.shape[0] - d - 1, self.click_y))
        image = np.array(self.frame[y - d:y + d, x - d:x + d])
        self.zoom_update.emit(image)

    def set_mode(self, mode):
        if mode == "live":
            self.live.start()
        else:
            if self.pli_stack.transmittance is None:
                print("pli not ready yet")
                return
            self.live.stop()

        self.mode = mode
        if self.mode == "transmittance":
            self.frame = (self.pli_stack.transmittance /
                          np.amax(self.pli_stack.transmittance) * 255).astype(
                              np.uint8)
        elif self.mode == "direction":
            self.frame = (self.pli_stack.direction / np.pi * 255).astype(
                np.uint8)
        elif self.mode == "retardation":
            self.frame = (self.pli_stack.retardation * 255).astype(np.uint8)
        self.image_label.setPixmap(
            QtGui.QPixmap.fromImage(self.convertFrame2Image(self.frame)))
        self.update_zoomImage()

    def update_camera_frame(self):
        if self.camera.is_alive():
            self.frame = self.camera.frame(crop=True)
            if self.frame is None:
                self.image_label.setPixmap(
                    QtGui.QPixmap.fromImage(
                        self.convertFrame2Image(helper.LOGO_IMG)))
                return

            if not self.tracker.is_calibrated:
                self.tracker.calibrate(self.frame)
                if self.tracker.is_calibrated:
                    rho = 0
                    self.last_angle = 0
                    self.pli_stack.insert(0, self.frame)

                # gen mask
                Y, X = np.ogrid[:self.frame.shape[0], :self.frame.shape[1]]
                dist2_from_center = (X - self.tracker.center[0])**2 + (
                    Y - self.tracker.center[1])**2

                self.mask = dist2_from_center <= (min(self.frame.shape[:2]) *
                                                  0.28)**2

            elif not self.pli_stack.full():
                rho = self.tracker.track(self.frame)
                self.pli_stack.insert(rho, self.frame)

                # print current angle
                if np.rad2deg(
                        np.abs(helper.diff_orientation(self.last_angle,
                                                       rho))) > 1:
                    print(f"{np.rad2deg(rho):.0f}")
                    self.last_angle = rho

                if self.pli_stack.full():
                    self.pli_stack.calc_coeffs()
            else:
                rho = self.tracker.track(self.frame)

            if self.show_tracker:
                self.frame = self.tracker.show()

            if self.show_angle:
                if self.tracker.is_calibrated:
                    d = np.array(
                        (np.cos(-rho) * min(self.frame.shape[:2]) * 0.42,
                         np.sin(-rho) * min(self.frame.shape[:2]) * 0.42))
                    p0 = (self.tracker.center - d // 2).astype(np.int)
                    p1 = (self.tracker.center + d // 2).astype(np.int)
                    self.frame = cv2.line(self.frame, tuple(p0), tuple(p1),
                                          (0, 255, 0), 2)

            if not self.show_tracker:
                self.frame = np.multiply(self.frame, self.mask[:, :, None])
                d = int(min(self.frame.shape[:2]) * 0.28)
                self.frame = np.array(self.frame[d // 2:-d // 2,
                                                 d // 2:-d // 2, :])

            if self.mode == "live":
                self.image_label.setPixmap(
                    QtGui.QPixmap.fromImage(self.convertFrame2Image(
                        self.frame)))
                self.update_zoomImage()
