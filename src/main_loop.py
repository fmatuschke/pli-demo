import enum
import functools

import numpy as np
from PyQt5 import QtCore, QtGui

from . import capture_device, pli, tracker


class MainThread():

    @enum.unique
    class State(enum.Enum):
        TRACKING = enum.auto()
        MEASUREMENT = enum.auto()
        LIVE = enum.auto()

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
        self._debug = True

        self.parent.main_menu['pli'].set_enabled(False)
        self.pli = pli.PLI(pli_threshold)

        self.tracker = tracker.Tracker(num_sticker=10, sticker_zero_id=10)

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
        self.show_image(frame)

    def next_live(self, frame: np.ndarray):
        pass

    def next_measurement(self, frame: np.ndarray):
        if self.pli.measurment_done():
            raise ValueError('measurment already done')

        angle = self.tracker.current_angle(frame)
        if angle is None:
            raise ValueError('angel is None')

        self.pli.insert(frame, angle)

        self.parent.statusBar().showMessage(f'{np.rad2deg(angle):.1f}')
        if self.pli.measurment_done():
            print("live view")
            self.state = self.State.LIVE
            self.parent.main_menu['pli'].set_enabled(True)
            self.parent.main_menu['pli'].add_action('process',
                                                    triggered=functools.partial(
                                                        self.pli.run_analysis))

    def next_tracking(self, frame: np.ndarray):
        self.show_image(frame)
        if self.tracker.calibrate(frame):
            self.state = self.State.MEASUREMENT

    def show_image(self, image):
        qimage = self.convertArray2QImage(image)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        self.display.setPixmap(pixmap)
