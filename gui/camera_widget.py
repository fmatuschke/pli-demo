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


class CameraWidget(QtWidgets.QLabel):

    plot_update = QtCore.pyqtSignal(np.ndarray, np.ndarray, float, bool)
    # click_update = QtCore.pyqtSignal(int, int)
    zoom_update = QtCore.pyqtSignal(np.ndarray)

    def __init__(self, parent=None, *args, **kwargs):
        super(CameraWidget, self).__init__(parent, *args, **kwargs)
        self.ui = parent
        #
        self.rho = 0
        self.last_angle = 0
        self.show_angle = False
        self.show_tracker = False
        self.mode = "live"
        self.filter_image = True
        #
        self.plot_add = False
        self.plot_x = []
        self.plot_y = []
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_A),
                            self,
                            activated=partial(self.toogleAddPlot))
        #
        self.init_camera()
        self.tracker = Tracker()
        self.pli_stack = PliStack()

        # DEBUG
        # p = self.palette()
        # p.setColor(self.backgroundRole(), QtGui.QColor(255, 0, 0))
        # self.setAutoFillBackground(True)
        # self.setPalette(p)
        self.camera_and_tracker()  # for debug
        self.live.start(40)  # 1000/fps

    def toogleAddPlot(self):
        self.plot_add = not self.plot_add
        self.ui.textwidget.setText(f"plot_add: {self.plot_add}")

    def init_camera(self):
        self.camera = Camera(fps=25)

        for width, height in self.camera.working_resolutions:
            self.ui.cameraResolutionMenu.addAction(
                QtWidgets.QAction(f"{width}x{height}",
                                  self.ui.cameraResolutionMenu,
                                  triggered=partial(self.camera.set_resolution,
                                                    width, height)))

        # TODO: center, but value change with resize
        self.click_x = 0
        self.click_y = 0
        self.mask_offset = 0

        # setup image label
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # QTimer to access camera frames
        self.live = QtCore.QTimer(self)
        self.live.timeout.connect(self.camera_and_tracker)

    def resizeEvent(self, event):
        super(CameraWidget, self).resizeEvent(event)

    def toogle_draw_helper(self):
        self.show_tracker = not self.show_tracker
        self.show_angle = not self.show_angle

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

        # save parameter for coordinate transformation
        self.frame_height = frame.shape[0]
        self.frame_width = frame.shape[1]

        return image

    def widget2framecoordinates(self, click_x, click_y):
        '''
        Umrechnung der Click- Koordinaten im Widget in QtWidgets.QLabel Koordinaten und dann in Frame-Koordinaten
        '''
        pixmap_width = self.pixmap().size().width()
        pixmap_height = self.pixmap().size().height()

        widget_width = self.size().width()
        widget_height = self.size().height()

        # For centered alignment:
        offset_x = (widget_width - pixmap_width) / 2
        offset_y = (widget_height - pixmap_height) / 2

        frame_x = int((click_x - offset_x) / pixmap_width * self.frame_width +
                      0.5)
        frame_y = int((click_y - offset_y) / pixmap_height * self.frame_height +
                      0.5)

        # print("click", click_x, click_y)
        # print("pixmap.size", self.pixmap().size())
        # print("widget.size", self.size())
        # print("pixmap", int(click_x - offset_x), int(click_y - offset_y))
        # print("frame", frame_x, frame_y)

        return frame_x, frame_y

    def mousePressEvent(self, event):
        '''
        Sets Tracking coordinate to the clicked coordinate
        '''
        # if y coordinate is in QtWidgets.QLabel
        # if (event.y() > self.label_offset_y and
        #         event.y() < self.size().height() - self.label_offset_y):

        self.click_x, self.click_y = self.widget2framecoordinates(
            event.x(), event.y())
        # self.click_update.emit(self.click_x, self.click_y)
        self.set_mode(self.mode)

        x, y = self.pli_stack.get(self.click_x + self.mask_offset,
                                  self.click_y + self.mask_offset)

        if self.plot_add:
            self.plot_x.append(self.click_x + self.mask_offset)
            self.plot_y.append(self.click_y + self.mask_offset)
        else:
            self.plot_x = [self.click_x + self.mask_offset]
            self.plot_y = [self.click_y + self.mask_offset]

        self.plot_update.emit(x, y, self.rho, self.plot_add)

    def set_mode(self, mode):
        if mode != "live":
            if self.pli_stack.transmittance is None:
                self.ui.setText("pli not ready yet")
                return

        self.mode = mode
        if mode == "live":
            self.live.start()
        else:
            self.live.stop()

        if self.mode == "transmittance":
            frame = (self.pli_stack.transmittance /
                     np.amax(self.pli_stack.transmittance) * 255).astype(
                         np.uint8)
            self.update_image(frame)
        elif self.mode == "direction":
            frame = (self.pli_stack.direction / np.pi * 255).astype(np.uint8)
            self.update_image(frame)
        elif self.mode == "retardation":
            frame = (self.pli_stack.retardation * 255).astype(np.uint8)
            self.update_image(frame)
        elif self.mode == "fom":
            print("fom")

    def camera_and_tracker(self):
        # GET CAMERA FRAME
        if not self.camera.is_alive():
            return

        frame = self.camera.frame(crop=True)
        if frame is None:
            frame = helper.LOGO_IMG
            return

        # pre filter images
        if self.filter_image:
            if frame.ndim == 2:
                frame = cv2.medianBlur(frame, 5)
            else:
                for i in frame.shape[2]:
                    frame[:, :, i] = cv2.medianBlur(frame[:, :, i], 5)

        # RUN TRACKER
        # calibrate tracker
        if not self.tracker.is_calibrated:
            self.tracker.calibrate(frame)
            if self.tracker.is_calibrated:
                self.rho = 0
                self.last_angle = 0
                self.pli_stack.insert(0, frame)
                self.ui.textwidget.setText("Calibrated")

        # get pli stack
        elif not self.pli_stack.full():
            self.rho = self.tracker.track(frame)
            if self.rho is None:
                self.update_image(frame)
                return
            value = self.pli_stack.insert(self.rho, frame)

            if value:
                for i, (x, y) in enumerate(zip(self.plot_x, self.plot_y)):
                    x, y = self.pli_stack.get(x, y)

                    if i == 0:
                        self.plot_update.emit(x, y, self.rho, False)
                    else:
                        self.plot_update.emit(x, y, self.rho, True)

                p = self.palette()
                p.setColor(self.backgroundRole(), QtGui.QColor(0, 255, 0))
                self.ui.textwidget.setPalette(p)
                self.ui.textwidget.setText(
                    f"inserted: {np.rad2deg(self.rho):.0f}")
                p.setColor(self.backgroundRole(), QtGui.QColor(255, 0, 0))
                self.ui.textwidget.setPalette(p)

            # when done, calculate pli modalities
            if self.pli_stack.full():
                self.pli_stack.calc_coeffs()

        # get only angle
        else:
            self.rho = self.tracker.track(frame)
            if self.rho is None:
                self.update_image(frame)
                return

        # print current angle
        if np.rad2deg(np.abs(helper.diff_orientation(self.last_angle,
                                                     self.rho))) > 1:
            self.ui.textwidget.setText(f"{np.rad2deg(self.rho):.0f}")
            self.last_angle = self.rho

        if self.mode == "live":
            self.mask_offset = 0
            if self.show_tracker:
                frame = self.tracker.show()

            if self.show_angle:
                if self.tracker.is_calibrated:
                    d = np.array(
                        (np.cos(-self.rho) * min(frame.shape[:2]) * 0.42,
                         np.sin(-self.rho) * min(frame.shape[:2]) * 0.42))
                    p0 = (self.tracker.center - d // 2).astype(np.int)
                    p1 = (self.tracker.center + d // 2).astype(np.int)

                    frame = cv2.line(frame, tuple(p0), tuple(p1), (0, 255, 0),
                                     2)

            else:
                if self.tracker.is_calibrated:
                    if frame.ndim == 2:
                        frame = np.multiply(frame, self.tracker.img_mask)
                        d = int(min(frame.shape[:2]) * 0.28)
                        frame = np.array(frame[d // 2:-d // 2, d // 2:-d // 2])

                    else:
                        frame = np.multiply(frame, self.tracker.img_mask[:, :,
                                                                         None])
                        d = int(min(frame.shape[:2]) * 0.28)
                        frame = np.array(frame[d // 2:-d // 2,
                                               d // 2:-d // 2, :])
                    self.mask_offset = d

            self.update_image(frame)

    def update_image(self, image):
        # camera widget
        self.setPixmap(QtGui.QPixmap.fromImage(self.convertFrame2Image(image)))

        # zoom widget
        d = 42
        x = max(d, min(image.shape[1] - d - 1, self.click_x))
        y = max(d, min(image.shape[0] - d - 1, self.click_y))
        image = np.array(image[y - d:y + d, x - d:x + d])
        self.zoom_update.emit(image)
