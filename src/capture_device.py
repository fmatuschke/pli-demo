import enum
import os
import pathlib

import cv2
import numpy as np
import time

PATH = os.path.join(pathlib.Path().absolute(), 'data')

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


class CapDev:
    __is_frozen = False

    def __setattr__(self, key, value):
        if self.__is_frozen and not hasattr(self, key):
            raise TypeError('%r is a frozen class' % self)
        object.__setattr__(self, key, value)

    def __freeze(self):
        self.__is_frozen = True

    def __init__(
            self,
            port=0,
            port_list=range(5),
            file_name=None,  # 'data/half_720p.mp4'
            color_mode=Color.GREEN):

        self._device = None
        self._port = port
        self._ports = []
        self._videos = []
        self._resolutions = []
        self._color_mode = color_mode

        # freeze class
        self.__freeze()

        # run init member functions
        self._ports = self._check_ports(port_list, n_times=5)
        self._search_videos()

        if file_name is not None:
            self.activate_video(file_name)
        elif self._port in self._ports:
            self.activate_camera(self._port)
        else:
            self._device = None
            self._port = None
            self.release_device()

    def ports(self):
        return self._ports

    def videos(self):
        return self._videos

    def _search_videos(self):
        print("searching for videos")
        for file in os.listdir(PATH):
            if not os.path.isfile(os.path.join(PATH, file)):
                continue
            if not file.endswith('.mp4'):
                continue
            self._videos.append(os.path.join(PATH, file))

    def release_device(self):
        if self._device is not None:
            if self._device.isOpened():
                self._device.release()

    def activate_camera(self, port):
        self.release_device()
        if self._check_port(port):
            self._device = cv2.VideoCapture(port)
            # self._check_resolutions() # takes time
        else:
            print("Error: port is not working")

    def activate_video(self, file_name):
        self.release_device()
        self._device = cv2.VideoCapture(file_name)
        # TODO: catch input error

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

        self.release_device()
        return port_works

    def _check_ports(self, port_list, n_times=1):
        ports = [port for port in port_list if self._check_port(port, n_times)]
        print(f"INFO: working ports: {ports}")
        return ports

    def set_port(self, port):
        self.release_device()
        self._device = cv2.VideoCapture(port)
        if not self._device.isOpened():
            print(f'camera port "{port}" not opening')
        else:
            self._port = port

    def _check_resolutions(self):
        # TODO this should be available from the OS

        org_width = int(self._device.get(cv2.CAP_PROP_FRAME_WIDTH))
        org_height = int(self._device.get(cv2.CAP_PROP_FRAME_HEIGHT))
        org_fps = int(self._device.get(cv2.CAP_PROP_FPS))
        self._resolutions = [(org_width, org_height, org_fps)]

        # test_resolution = [(320, 480), (640, 480), (800, 600), (1024, 786),
        #                    (1280, 720), (1280, 800), (1280, 960),
        #                    (1280, 1024), (1440, 720), (1440, 900),
        #                    (1600, 1200), (1920, 1080), (1920, 1200),
        #                    (2560, 1440), (2560, 1600), (3840, 2160)]

        # EXIO cam USB2
        test_resolution = [(640, 480), (1024, 768), (1280, 720), (1280, 960),
                           (1920, 1080), (2048, 1536), (2560, 1440),
                           (2560, 1600), (3840, 2160)]

        # reset
        # self.set_port(self._port)

        print(f'INFO: start testing vor properties')
        for width, height in test_resolution:
            self.set_prop(width, height, 60)
            width = int(self._device.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self._device.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self._device.get(cv2.CAP_PROP_FPS))
            self._resolutions.append((width, height, fps))

        self._resolutions = list(set(self._resolutions))
        self._resolutions.sort(key=lambda x: x[1])
        self._resolutions.sort(key=lambda x: x[0])
        print(f'INFO: found {self._resolutions}')

        # reset to original
        self.set_prop(org_width, org_height, org_fps)

        return self._resolutions

    def set_prop(self, width, height, fps=25):
        # reset camera to set setting before image capture
        # self.set_port(self._port)

        self._device.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._device.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._device.set(cv2.CAP_PROP_FPS, fps)

        # Read some images to ensure the cam is ready
        for _ in range(42):
            if self._device.read()[0]:
                break
            print('INFO: trying to get image after setting options')
            time.sleep(0.42)

    def empty_frame(self):
        frame = np.zeros((128, 128), dtype=np.uint8)
        np.fill_diagonal(frame, 255)
        frame = np.flip(frame, 0)
        np.fill_diagonal(frame, 255)
        return frame

    def get_frame(self, quadratic=False):

        if self._device is None:
            return self.empty_frame()

        # if video frame count > 0
        video_frame_count = self._device.get(cv2.CAP_PROP_FRAME_COUNT)
        if video_frame_count:
            if video_frame_count == self._device.get(cv2.CAP_PROP_POS_FRAMES):
                self._device.set(cv2.CAP_PROP_POS_FRAMES, 0)

        success, frame = self._device.read()

        if not success:
            print('Error: camera disconnected')
            # TODO: Sometimes, cap may not have initialized the capture.
            # In that case, this code shows error. You can check whether
            # it is initialized or not by the method cap.isOpened(). If
            # it is True, OK. Otherwise open it using cap.open().
            return self.empty_frame()

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
