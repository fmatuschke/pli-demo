import os
import glob

import numpy as np
import itertools
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

    def __init__(self, parent=None, *args, **kwargs):
        super(CameraWidget, self).__init__(parent, *args, **kwargs)
        self.ui = parent
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.setFrameStyle(QtWidgets.QFrame.Plain)

        # black background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.setPalette(palette)

        # variables
        self.rho = 0
        self.last_angle = 0
        self.show_angle = False
        self.show_tracker = False
        self.mode = "live"
        self.filter_image = "nlmd"
        self._string = ""

        # plot variables
        self.plot_add = False
        self.plot_x = []
        self.plot_y = []
        QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_A),
                            self,
                            activated=partial(self.toogleAddPlot))

        #
        self.init_camera()
        self.tracker = Tracker()
        self.pli_stack = PliStack(ui=parent)

        # DEBUG
        self.next_frame()  # first run for debug
        if self.camera.live:
            self.live.start(1000 // self.camera.fps)

    def toogleAddPlot(self):
        self.plot_add = not self.plot_add

    def init_camera(self):
        self.camera = Camera(fps=30)
        self.set_ports_to_menu()
        self.set_resolutions_to_menu()

        def video(self, file):
            self.live.stop()
            self.camera.set_video(file)
            self.tracker = Tracker()
            self.pli_stack = PliStack()
            self.ui.set_pli(False)
            self.live.start(30)

        for i, file in enumerate(sorted(glob.glob(os.path.join("data",
                                                               "*mp4")))):
            self.ui.cameraDemoMenu.addAction(
                QtWidgets.QAction(f"&{i} - {file}",
                                  self.ui.cameraPortMenu,
                                  triggered=partial(video, self, file)))

        # TODO: center, but value change with resize
        self.click_x = 0
        self.click_y = 0
        self.mask_origin = np.zeros(2, np.int)

        # setup image label
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # QTimer to access camera frames
        self.live = QtCore.QTimer(self)
        self.live.timeout.connect(self.next_frame)

    def set_ports_to_menu(self):

        def set_port(self, port):
            self.live.stop()
            self.camera.set_port(port)
            self.set_resolutions_to_menu()
            self.tracker = Tracker()
            self.pli_stack = PliStack()
            self.ui.set_pli(False)
            if self.camera.live:
                self.live.start(1000 // self.camera.fps)

        self.ui.cameraPortMenu.clear()
        for port in self.camera.available_ports:
            self.ui.cameraPortMenu.addAction(
                QtWidgets.QAction(f"{port}",
                                  self.ui.cameraPortMenu,
                                  triggered=partial(set_port, self, port)))

    def set_resolutions_to_menu(self):

        def set_res(self, width, height, fps):
            self.live.stop()
            self.camera.set_prop(width, height, fps)
            self.tracker = Tracker()
            self.pli_stack = PliStack()
            self.ui.set_pli(False)
            if self.camera.live:
                self.live.start(1000 // self.camera.fps)

        self.ui.cameraResolutionMenu.clear()
        for width, height in self.camera.available_resolutions:
            self.ui.cameraResolutionMenu.addAction(
                QtWidgets.QAction(f"{width}x{height}",
                                  self.ui.cameraResolutionMenu,
                                  triggered=partial(set_res, self, width,
                                                    height, 30)))

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

        totalBytes = frame.nbytes
        bytesPerLine = int(totalBytes / frame.shape[0])
        image = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],
                             bytesPerLine, img_format)
        image = image.rgbSwapped()
        image = image.scaled(self.size().width(),
                             self.size().height(), QtCore.Qt.KeepAspectRatio,
                             QtCore.Qt.SmoothTransformation)

        # save parameter for coordinate transformation
        self.frame_height = frame.shape[0]
        self.frame_width = frame.shape[1]

        return image

    def widget2framecoordinates(self, click_x, click_y):
        '''
        return pixmap coordinate. if data is cropped after masked, add mask offset if you want pli_stack.get()!
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

        return frame_x, frame_y

    def mousePressEvent(self, event):
        '''
        Sets Tracking coordinate to the clicked coordinate
        '''
        if self.pixmap() is None:
            return

        self.click_x, self.click_y = self.widget2framecoordinates(
            event.x(), event.y())
        # self.set_mode(self.mode)

        # save click coordinates
        if self.plot_add:
            self.plot_x.append(self.click_x)
            self.plot_y.append(self.click_y)
        else:
            self.plot_x = [self.click_x]
            self.plot_y = [self.click_y]

        # emit last clicked data
        x, y = self.pli_stack.get(self.click_x + self.mask_origin[1],
                                  self.click_y + self.mask_origin[0])
        self.plot_update.emit(x, y, self.rho, self.plot_add)

    def set_mode(self, mode):
        if mode != "live":
            if self.pli_stack.transmittance is None:
                self.ui.setText("pli not ready yet")
                return

        self.mode = mode
        if mode == "live":
            if self.camera.live:
                self.live.start(1000 // self.camera.fps)
            return
        else:
            self.live.stop()

        if self.pli_stack.is_analysed():
            self.ui.set_pli(True)
            self.mode = "live"
            if self.camera.live:
                self.live.start(1000 // self.camera.fps)
            return

        if self.mode == "transmittance":
            frame = (self.pli_stack.transmittance /
                     np.amax(self.pli_stack.transmittance) * 255).astype(
                         np.uint8)
        elif self.mode == "direction":
            frame = (self.pli_stack.direction / np.pi * 255).astype(np.uint8)
        elif self.mode == "retardation":
            frame = (self.pli_stack.retardation * 255).astype(np.uint8)
        elif self.mode == "inclination":
            frame = (self.pli_stack.inclination * 2 / np.pi * 255).astype(
                np.uint8)
        elif self.mode == "fom":
            frame = self.pli_stack.fom
            frame = np.multiply(frame, self.pli_stack.mask[:, :, None])

        frame = self.tracker.mask(frame)
        frame = self.tracker.crop(frame)
        self.mask_origin = self.tracker.mask_origin
        self.update_image(frame)

    def set_filter(self, filter):
        if filter == "nlmd":
            self.filter_image = filter
        elif filter == "none":
            self.filter_image = filter
        elif filter == "gaus":
            self.filter_image = filter
        else:
            raise ValueError("wrong input")

    def next_frame(self):
        # GET CAMERA FRAME
        # get frame, quadratic -> less data to analyse
        frame = self.camera.frame(quadratic=True)
        if frame is None:
            frame = helper.LOGO_IMG
            return

        # pre filter images
        if self.filter_image == "nlmd":
            denoise = lambda x: cv2.fastNlMeansDenoising(frame, x, 5, 5, 9)
        elif self.filter_image == "none":
            denoise = lambda x: x
        elif self.filter_image == "gaus":
            denoise = lambda x: cv2.GaussianBlur(x, (5, 5), 1)
        else:
            raise ValueError("wrong input")

        if frame.ndim == 2:
            frame = denoise(frame)
        else:
            for i in range(frame.shape[2]):
                frame[:, :, i] = denoise(frame[:, :, i])

        # RUN TRACKER
        # calibrate tracker
        if not self.tracker.is_calibrated:
            self.tracker.calibrate(frame)
            if self.tracker.is_calibrated:
                self.rho = 0
                self.last_angle = 0
                self.ui.statusBar().showMessage("Calibrated")

        # get pli stack
        elif not self.pli_stack.full:
            self.rho = self.tracker.track(frame)
            if self.rho is None:
                self.update_image(frame)
                return
            value = self.pli_stack.insert(self.rho, frame)

            if value:
                for i, (x, y) in enumerate(zip(self.plot_x, self.plot_y)):
                    x, y = self.pli_stack.get(x + self.mask_origin[0],
                                              y + self.mask_origin[1])

                    if i == 0:
                        self.plot_update.emit(x, y, self.rho, False)
                    else:
                        self.plot_update.emit(x, y, self.rho, True)

                self.ui.statusBar().showMessage(
                    f"inserted: {np.rad2deg(self.rho):.0f}", 2000)

        # get only angle
        else:
            self.rho = self.tracker.track(frame)
            if self.rho is None:
                self.update_image(frame)
                return

        # print current angle
        if np.rad2deg(np.abs(helper.diff_orientation(self.last_angle,
                                                     self.rho))) > 1:
            self.ui.statusBar().showMessage(f"{np.rad2deg(self.rho):.0f}")
            self.last_angle = self.rho

        if self.mode == "live":
            self.mask_origin = np.zeros(2, np.int)
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
                    frame = self.tracker.mask(frame)
                    frame = self.tracker.crop(frame)
                    self.mask_origin = self.tracker.mask_origin

            self.update_image(frame)

    def update_image(self, image):
        # camera widget
        pixmap = QtGui.QPixmap.fromImage(self.convertFrame2Image(image))

        colors = np.array([(56, 173, 107, 255), (60, 132, 167, 255),
                           (235, 136, 23, 255), (123, 127, 140, 255),
                           (191, 89, 62, 255)], np.uint8)  # ChartThemeDark
        last_color = colors[0]

        if self.tracker.is_calibrated:
            painter = QtGui.QPainter(pixmap)
            pen = QtGui.QPen()
            scale = pixmap.width() / image.shape[1]

            radius = self.tracker.radius * 0.99
            pen.setColor(QtCore.Qt.red)
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawEllipse(
                QtCore.QPointF(
                    (self.tracker.center[0] - self.mask_origin[0]) * scale,
                    (self.tracker.center[1] - self.mask_origin[1]) * scale),
                radius * scale, radius * scale)

            pen.setColor(QtCore.Qt.green)
            pen.setWidth(4)
            painter.setPen(pen)

            point_0 = QtCore.QPointF(
                (self.tracker.center[0] - self.mask_origin[0] +
                 np.cos(-self.rho) * radius * 0.98) * scale,
                (self.tracker.center[1] - self.mask_origin[1] +
                 np.sin(-self.rho) * radius * 0.98) * scale)
            point_1 = QtCore.QPointF(
                (self.tracker.center[0] - self.mask_origin[0] +
                 np.cos(-self.rho) * radius * 1.02) * scale,
                (self.tracker.center[1] - self.mask_origin[1] +
                 np.sin(-self.rho) * radius * 1.02) * scale)
            painter.drawLine(point_0, point_1)

            point_0 = QtCore.QPointF(
                (self.tracker.center[0] - self.mask_origin[0] +
                 np.cos(-self.rho + np.pi) * radius * 0.98) * scale,
                (self.tracker.center[1] - self.mask_origin[1] +
                 np.sin(-self.rho + np.pi) * radius * 0.98) * scale)
            point_1 = QtCore.QPointF(
                (self.tracker.center[0] - self.mask_origin[0] +
                 np.cos(-self.rho + np.pi) * radius * 1.02) * scale,
                (self.tracker.center[1] - self.mask_origin[1] +
                 np.sin(-self.rho + np.pi) * radius * 1.02) * scale)
            painter.drawLine(point_0, point_1)

            for rho in self.pli_stack.angles:
                for a, b in zip(
                        np.linspace(-1, 1, 10)[:-1],
                        np.linspace(-1, 1, 10)[1:]):
                    point_0 = QtCore.QPointF(
                        (self.tracker.center[0] - self.mask_origin[0] +
                         np.cos(-rho + np.deg2rad(a * 5)) * radius) * scale,
                        (self.tracker.center[1] - self.mask_origin[1] +
                         np.sin(-rho + np.deg2rad(a * 5)) * radius) * scale)
                    point_1 = QtCore.QPointF(
                        (self.tracker.center[0] - self.mask_origin[0] +
                         np.cos(-rho + np.deg2rad(b * 5)) * radius) * scale,
                        (self.tracker.center[1] - self.mask_origin[1] +
                         np.sin(-rho + np.deg2rad(b * 5)) * radius) * scale)
                    painter.drawLine(point_0, point_1)

                    rho = rho + np.pi
                    point_0 = QtCore.QPointF(
                        (self.tracker.center[0] - self.mask_origin[0] +
                         np.cos(-rho + np.deg2rad(a * 5)) * radius) * scale,
                        (self.tracker.center[1] - self.mask_origin[1] +
                         np.sin(-rho + np.deg2rad(a * 5)) * radius) * scale)
                    point_1 = QtCore.QPointF(
                        (self.tracker.center[0] - self.mask_origin[0] +
                         np.cos(-rho + np.deg2rad(b * 5)) * radius) * scale,
                        (self.tracker.center[1] - self.mask_origin[1] +
                         np.sin(-rho + np.deg2rad(b * 5)) * radius) * scale)
                    painter.drawLine(point_0, point_1)

                # Qt says full circle equals 5760 (16 * 360), but here *8
                # Qt says Positive values for the angles mean counter-clockwise
                #         while negative values mean the clockwise direction
                #         Zero degrees is at the 3 o'clock position.
                # buggy first drawArc, not dependend on value of rho
                # rho = int(np.rad2deg(rho))
                # painter.drawArc((self.tracker.center[0] - self.mask_origin[0] -
                #                  radius) * scale,
                #                 (self.tracker.center[1] - self.mask_origin[1] -
                #                  radius) * scale,
                #                 (self.tracker.center[0] - self.mask_origin[0] +
                #                  radius) * scale,
                #                 (self.tracker.center[1] - self.mask_origin[1] +
                #                  radius) * scale, (rho - 5) * 8,
                #                 (rho + 5) * 8)
                # painter.drawArc((self.tracker.center[0] - self.mask_origin[0] -
                #                  radius) * scale,
                #                 (self.tracker.center[1] - self.mask_origin[1] -
                #                  radius) * scale,
                #                 (self.tracker.center[0] - self.mask_origin[0] +
                #                  radius) * scale,
                #                 (self.tracker.center[1] - self.mask_origin[1] +
                #                  radius) * scale,
                #                 (rho - 5 + 180) * 8, (rho + 5 + 180) * 8)

            for x, y, c in zip(self.plot_x, self.plot_y,
                               itertools.cycle(colors)):
                pen.setColor(QtGui.QColor(c[0], c[1], c[2], c[3]))
                painter.setPen(pen)
                painter.drawEllipse(QtCore.QPointF(x * scale, y * scale), 5, 5)
                last_color = c

            del painter
        self.setPixmap(pixmap)

        # # zoom widget
        # d = 42
        # x = max(d, min(image.shape[1] - d - 1, self.click_x))
        # y = max(d, min(image.shape[0] - d - 1, self.click_y))
        # image = np.array(image[y - d:y + d, x - d:x + d])
        # self.zoom_update.emit(image, last_color)
