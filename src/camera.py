import enum
import os

import cv2
import numpy as np

# cv2 workaround
# https://forum.qt.io/topic/119109/using-pyqt5-with-opencv-python-cv2-causes-error-could-not-load-qt-platform-plugin-xcb-even-though-it-was-found/23
for k, v in os.environ.items():
    if k.startswith("QT_") and "cv2" in v:
        del os.environ[k]


@enum.unique
class Color(enum.Enum):
    RGB = enum.auto()
    GRAY = enum.auto()
    RED = enum.auto()
    GREEN = enum.auto()
    BLUE = enum.auto()


class Camera:
    __is_frozen = False

    def __setattr__(self, key, value):
        if self.__is_frozen and not hasattr(self, key):
            raise TypeError('%r is a frozen class' % self)
        object.__setattr__(self, key, value)

    def __freeze(self):
        self.__is_frozen = True

    def __init__(self,
                 width=1280,
                 height=960,
                 fps=25,
                 port=0,
                 port_list=range(5),
                 color_mode=Color.GREEN):

        self._device = None
        self._port = port
        self._ports = []
        self._color_mode = color_mode

        # freeze class
        self.__freeze()

        # run init member functions
        self._ports = self._check_ports(port_list, n_times=5)
        if self._port not in self._ports:
            self._device = None
            self._port = None
        else:
            print("setting port")
            self._device = cv2.VideoCapture(self._port)

    def _check_port(self, port, n_times=1):
        camera = cv2.VideoCapture(port)
        port_works = False
        for n in range(n_times):
            if camera.isOpened():
                is_reading, _ = camera.read()
                if is_reading:
                    port_works = True
                name = camera.getBackendName()
                camera.release()
                break

        return port_works

    def _check_ports(self, port_list, n_times=1):
        ports = [port for port in port_list if self._check_port(port, n_times)]
        print(f"INFO: working ports: {ports}")
        return ports

    def set_port(self, port):
        self._device = cv2.VideoCapture(i)
        if not self._device.isOpened():
            print(f'camera port "{port}" not opening')
        else:
            self._port = port

    def get_frame(self, quadratic=False):

        if self._device is None:
            return None

        success, frame = self._device.read()

        if not success:
            print('Error: camera disconnected')
            # TODO: Sometimes, cap may not have initialized the capture.
            # In that case, this code shows error. You can check whether
            # it is initialized or not by the method cap.isOpened(). If
            # it is True, OK. Otherwise open it using cap.open().
            return None

        if self._color_mode in [Color.GRAY, Color.RGB]:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        elif self._color_mode is Color.RED:
            frame = frame[:, :, 2]
        elif self._color_mode is Color.GREEN:
            frame = frame[:, :, 1]
        elif self._color_mode is Color.BLUE:
            frame = frame[:, :, 0]

        if quadratic:
            height, width = frame.shape[0], frame.shape[1]
            l = min(height, width)
            delta = np.abs((width - height) // 2)

            if width > height:
                frame = np.array(frame[:, delta:delta + l])
            else:
                frame = np.array(frame[delta:delta + l, :])

        return frame
