from __future__ import annotations

import enum
import functools

import numpy as np
from PyQt5 import QtCore, QtGui

from . import capture_device, pli, tracker

# from functools import wraps
# from time import time

# def timing(f):

#     @wraps(f)
#     def wrap(*args, **kw):
#         ts = time()
#         result = f(*args, **kw)
#         te = time()
#         print(f'func:{f.__name__} took: {te - ts:.2f}sec')
#         return result

#     return wrap


def diff_angles(a, b, U):
    d = b - a
    d = (d + U / 2) % U - U / 2
    return d


class MainThread():

    @enum.unique
    class State(enum.Enum):
        TRACKING = enum.auto()
        MEASUREMENT = enum.auto()
        LIVE = enum.auto()

    # rho_signal = QtCore.pyqtSignal(float)

    __is_frozen = False

    def __setattr__(self, key, value):
        if self.__is_frozen and not hasattr(self, key):
            raise TypeError('%r is a frozen class' % self)
        object.__setattr__(self, key, value)

    def __freeze(self):
        self.__is_frozen = True

    def __init__(self, parent):
        self.parent = parent
        self.display = self.parent.main_display
        self.reset()

        # freeze class
        self.__freeze()

    def reset(self, pli_threshold=np.deg2rad(4.2)):
        self.input_mode = None
        self.state = self.State.TRACKING
        self._debug = False
        self._plot = [None, None]
        self._image_height = None
        self._image_width = None
        self._angle = None
        self._last_angle = None
        self._update_angle = np.deg2rad(2.5)

        # pli
        self.parent.main_menu['pli'].set_enabled(False)
        self.pli = pli.PLI(pli_threshold)

        # tracker
        self.tracker = tracker.Tracker(num_sticker=10, sticker_zero_id=10)

        # camera
        self.parent.main_menu['camera']['port'].clear()
        self.device = capture_device.CapDev(port=self.parent.args.port,
                                            file_name=self.parent.args.video)

        def switch_port(port):
            # TODO: RFC reset
            self.parent.main_menu['pli'].set_enabled(False)
            self.state = self.State.TRACKING
            self.pli.reset()
            self.tracker.reset()
            self.device.activate_camera(port)

        # TODO: reset if triggered
        for port in self.device.ports():
            self.parent.main_menu['camera']['port'].add_action(
                f'{port}', triggered=functools.partial(switch_port, port))

        def switch_video(video):
            # TODO: RFC reset
            self.parent.main_menu['pli'].set_enabled(False)
            self.state = self.State.TRACKING
            self.pli.reset()
            self.tracker.reset()
            self.device.activate_video(video)

        for video in self.device.videos():
            print(video)
            self.parent.main_menu['camera']['demo'].add_action(
                f'{video}', triggered=functools.partial(switch_video, video))

    def switch_camera_port(self):
        pass

    def switch_input_mode(self):
        """ switch between device and video """
        pass

    def convertArray2QImage(self, frame):
        frame = np.ascontiguousarray(frame)
        bytesPerLine = int(frame.nbytes / frame.shape[0])
        if frame.ndim == 2:
            img_format = QtGui.QImage.Format_Grayscale8
        else:
            img_format = QtGui.QImage.Format_RGB888

        qimage = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],
                              bytesPerLine, img_format)
        qimage = qimage.scaled(self.display.size().width(),
                               self.display.size().height(),
                               QtCore.Qt.KeepAspectRatio,
                               QtCore.Qt.SmoothTransformation)

        #TODO: save parameter for coordinate transformation
        # self.frame_height = frame.shape[0]
        # self.frame_width = frame.shape[1]

        return qimage

    def next(self):
        """ process next iteration """

        frame = self.device.get_frame()

        if self.state == self.State.LIVE:
            self.next_live(frame)
        elif self.state == self.State.TRACKING:
            self.next_tracking(frame)
        elif self.state == self.State.MEASUREMENT:
            self.next_measurement(frame)
        elif self.state in self.State:
            raise ValueError('Not implemented yet')
        else:
            raise ValueError('Undefined State')

        if self._debug:
            frame = self.tracker.add_info_view(frame)

        if not self._debug:
            frame = self.tracker.crop(frame)
            frame = self.tracker.mask(frame)
        self.show_image(frame)

        if self._last_angle is None:
            self._last_angle = self._angle
        else:
            if abs(diff_angles(self._last_angle, self._angle,
                               np.pi)) > self._update_angle:
                self._last_angle = self._angle
                self.parent.plotwidget.update(self._plot[0], self._plot[1],
                                              self._angle)
                self.parent.setupwidget.set_rotation(self._angle)
                self.parent.setupwidget.update()

    def update_plot(self, x, y):

        # to frame coordinates
        x = int(x * self._image_width + 0.5)
        y = int(y * self._image_height + 0.5)

        self._plot[0] = self.pli.images.rotations
        self._plot[1] = [self.pli.images.images[y, x, :]]

    def next_live(self, frame: np.ndarray):
        self._angle = self.tracker.current_angle(frame)

    def enable_pli_results(self):

        def show_img_and_stop(image, cval):
            image = image / cval * 255
            image = image.astype(np.uint8)

            self.show_image(image)
            self.parent.worker.stop()

        self.parent.main_menu['pli'].add_action(
            'transmittance',
            lambda: show_img_and_stop(self.pli.modalities.transmittance, 255))
        self.parent.main_menu['pli'].add_action(
            'direction',
            lambda: show_img_and_stop(self.pli.modalities.direction, np.pi))
        self.parent.main_menu['pli'].add_action(
            'retardation',
            lambda: show_img_and_stop(self.pli.modalities.retardation, 1))

    def next_measurement(self, frame: np.ndarray):
        if self.pli.measurment_done():
            raise ValueError('measurment already done')

        self._angle = self.tracker.current_angle(frame)
        if self._angle is None:
            raise ValueError('angel is None')

        frame = self.tracker.crop(frame)
        self.pli.insert(frame, self._angle)

        self.parent.statusBar().showMessage(f'{np.rad2deg(self._angle):.1f}')
        if self.pli.measurment_done():
            print("live view")
            self.state = self.State.LIVE
            self.parent.main_menu['pli'].set_enabled(True)
            self.pli.run_analysis(self.enable_pli_results)
            # TODO: restliche ergebnisse

    def next_tracking(self, frame: np.ndarray):
        self.show_image(frame)
        if self.tracker.calibrate(frame):
            self.state = self.State.MEASUREMENT

    def show_image(self, image):
        qimage = self.convertArray2QImage(image)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        self._image_height = image.shape[0]
        self._image_width = image.shape[1]
        self.display.setPixmap(pixmap)
