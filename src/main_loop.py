import enum

from PyQt5 import QtGui

from . import camera
from . import tracker
from . import pli


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

    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.display = self.parent.main_display

        self.camera = camera.Camera()
        self.tracker = tracker.Tracker()
        self.pli = pli.PLI()

        self.input_mode = None
        self.state = State.LIVE

        # freeze class
        self.__freeze()

    def reset(self):
        self.reset_measurements()
        self.reset_camera()
        self.reset_tracker()

    def reset_measurements(self):
        self.pli = pli.PLI()

    def reset_tracker(self):
        self.tracker = tracker.Tracker()

    def reset_camera(self):
        self.camera = camera.Camera()

    def switch_camera_port(self):
        pass

    def switch_input_mode(self):
        """ switch between camera and video """
        pass

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
        frame = self.camera.frame()
        pixmap = QtGui.QPixmap.fromImage(self.convertFrame2Image(frame))
        self.display.setPixmap(pixmap)
        pass

    def next_measurement(self):
        pass

    def next_tracking(self):
        pass
