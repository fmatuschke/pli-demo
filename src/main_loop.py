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

        self.device = capture_device.CapDev(port=self.parent.args.port,
                                            file_name=self.parent.args.video)
        self.tracker = tracker.Tracker()
        self.pli = pli.PLI()

        self.input_mode = None
        self.state = self.State.LIVE

        # freeze class
        self.__freeze()

    def reset(self):
        self.reset_measurements()
        self.reset_device()
        self.reset_tracker()

    def reset_measurements(self):
        self.pli = pli.PLI()

    def reset_tracker(self):
        self.tracker = tracker.Tracker()

    def reset_device(self):
        self.device = capture_device.CapDev()

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

        if frame is None:
            print("Error: device returns none")
            return

        qimage = self.convertArray2QImage(frame)
        pixmap = QtGui.QPixmap.fromImage(qimage)
        self.display.setPixmap(pixmap)

    def next_measurement(self):
        pass

    def next_tracking(self):
        pass
