import enum

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

    def reset(self, pli_threshold=np.deg2rad(2)):
        self.input_mode = None
        self.state = self.State.TRACKING

        self.pli = pli.PLI(pli_threshold)
        self.tracker = tracker.Tracker(10, 10)
        self.device = capture_device.CapDev(port=self.parent.args.port,
                                            file_name=self.parent.args.video)

    def switch_camera_port(self):
        pass

    def switch_input_mode(self):
        """ switch between device and video """
        pass

    def convertArray2QImage(self, frame):
        frame = np.ascontiguousarray(frame)
        bytesPerLine = int(frame.nbytes / frame.shape[0])
        qimage = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],
                              bytesPerLine, QtGui.QImage.Format_Grayscale8)
        # qimage = qimage.rgbSwapped()
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

        if self.state == self.State.LIVE:
            self.next_live()
        elif self.state == self.State.TRACKING:
            self.next_tracking()
        elif self.state == self.State.MEASUREMENT:
            self.next_measurement()
        elif self.state in self.State:
            raise ValueError('Not implemented yet')
        else:
            raise ValueError('Undefined State')

    def next_live(self):
        frame = self.device.get_frame()
        self.show_image(frame)

    def next_measurement(self):
        if self.pli.measument_done:
            raise ValueError('measurment already done')

        frame = self.device.get_frame()
        self.pli.insert(frame, self.tracker.get_rotation_angle())
        if self.pli.measurment_done:
            self.stat = self.State.LIVE

        self.show_image(frame)

    def next_tracking(self):
        frame = self.device.get_frame()
        self.tracker.calibrate(frame)
        self.show_image(frame)
        if self.tracker.calibrated():
            self.stat = self.State.LIVE

    def show_image(self, image):
        qimage = self.convertArray2QImage(image)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        self.display.setPixmap(pixmap)
