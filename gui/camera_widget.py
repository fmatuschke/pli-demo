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

    def __init__(self, parent=None, *args, **kwargs):
        super(CameraWidget, self).__init__(parent, *args, **kwargs)
        self.ui = parent
        self.init_camera()
        self.show_tracker = True
        self.show_angle = True
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

    def convertFrame2Image(self, frame, img_format=QtGui.QImage.Format_RGB888):
        '''
        convert camera frame to qimage with size of qlabel
        '''
        image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],
                             img_format)
        image = image.rgbSwapped()
        image = image.scaled(self.size().width(),
                             self.size().height(), QtCore.Qt.KeepAspectRatio)
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

    def set_mode(self, mode):
        self.mode = mode

        if self.pli_stack.transmittance is None:
            print("pli not ready yet")
            return

        if self.mode == "live":
            self.live.start()
        else:
            self.live.stop()

        if self.mode == "transmittance":
            transmittance = (self.pli_stack.transmittance /
                             np.amax(self.pli_stack.transmittance) *
                             255).astype(np.uint8)
            self.image_label.setPixmap(
                QtGui.QPixmap.fromImage(
                    self.convertFrame2Image(transmittance,
                                            QtGui.QImage.Format_Grayscale8)))
        elif self.mode == "direction":
            direction = (self.pli_stack.direction / np.pi * 255).astype(
                np.uint8)
            self.image_label.setPixmap(
                QtGui.QPixmap.fromImage(
                    self.convertFrame2Image(direction,
                                            QtGui.QImage.Format_Grayscale8)))
        elif self.mode == "retardation":
            retardation = (self.pli_stack.retardation * 255).astype(np.uint8)
            self.image_label.setPixmap(
                QtGui.QPixmap.fromImage(
                    self.convertFrame2Image(retardation,
                                            QtGui.QImage.Format_Grayscale8)))

    def update_camera_frame(self):
        if self.camera.is_alive():
            frame = self.camera.frame(crop=True)
            if frame is None:
                self.image_label.setPixmap(
                    QtGui.QPixmap.fromImage(
                        self.convertFrame2Image(helper.LOGO_IMG)))
                return

            if not self.tracker.is_calibrated:
                self.tracker.calibrate(frame)
                if self.tracker.is_calibrated:
                    rho = 0
                    self.last_angle = 0
                    self.pli_stack.insert(0, frame.copy())
            elif not self.pli_stack.full():
                rho = self.tracker.track(frame)
                self.pli_stack.insert(rho, frame)

                # print current angle
                if np.rad2deg(
                        np.abs(helper.diff_orientation(self.last_angle,
                                                       rho))) > 1:
                    print(f"{np.rad2deg(rho):.0f}")
                    self.last_angle = rho

                if self.pli_stack.full():
                    self.pli_stack.calc_coeffs()
            else:
                rho = self.tracker.track(frame)

            if self.show_tracker:
                frame = self.tracker.show()

            if self.show_angle:
                if self.tracker.is_calibrated:
                    d = np.array((np.cos(-rho) * min(frame.shape[:2]) * 0.42,
                                  np.sin(-rho) * min(frame.shape[:2]) * 0.42))
                    p0 = (self.tracker.center - d // 2).astype(np.int)
                    p1 = (self.tracker.center + d // 2).astype(np.int)
                    frame = cv2.line(frame, tuple(p0), tuple(p1), (0, 255, 0),
                                     2)

            if self.mode == "live":
                self.image_label.setPixmap(
                    QtGui.QPixmap.fromImage(self.convertFrame2Image(frame)))
