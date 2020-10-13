import cv2
import sys
import os
import numpy as np
import enum


class CamMode(enum.Enum):
    NONE = 0
    CAMERA = 1
    VIDEO = 2


class Camera:

    def __init__(self,
                 width=1280,
                 height=960,
                 fps=30,
                 port=None,
                 port_start=0,
                 port_end=5,
                 gray_image=True):

        self._mode = CamMode.NONE
        self._port = port
        self._video_capture = cv2.VideoCapture()
        self._working_ports = []
        self._working_resolutions = []

        self._check_ports(port_start, port_end)
        self.set_port(
            self._port if self._port is not None else self._working_ports[0])
        self._check_resolutions()
        self.set_prop(width, height, fps)
        self._gray_image = gray_image
        self.check_readout()

    @property
    def available_ports(self):
        if len(self._working_ports) == 0:
            self._check_ports(0, 5)
        return self._working_ports

    @property
    def available_resolutions(self):
        if len(self._working_resolutions) == 0:
            self._check_resolutions()
        return self._working_resolutions

    def __del__(self):
        if self._video_capture:
            self._video_capture.release()

    def _reset(self):
        self._video_capture.release()
        self._mode = CamMode.NONE
        self._port = None
        self._video_capture = cv2.VideoCapture()
        self._working_ports = []
        self._working_resolutions = []

    def set_video(self, file_name="data/medium.webm"):
        self._video_capture = cv2.VideoCapture(file_name)
        self._mode = CamMode.VIDEO

    def _check_port(self, port):
        # TODO: ignore output
        camera = cv2.VideoCapture(port)
        port_works = False
        if camera.isOpened():
            is_reading, _ = camera.read()
            if is_reading:
                port_works = True
            name = camera.getBackendName()
            print("port:", port, name)
            camera.release()
        return port_works

    def _check_ports(self, start, end):
        self._working_ports = [
            port for port in range(start, end + 1) if self._check_port(port)
        ]
        print(f"working ports: {self._working_ports}")
        return self._working_ports

    def set_port(self, i):
        self._port = i
        self._mode = CamMode.CAMERA
        if self._video_capture.isOpened():
            self._video_capture.release()
        if i != self._port:
            self._working_resolutions = []

        self._video_capture = cv2.VideoCapture(i)

        if not self._video_capture.isOpened():
            print("camera unavailable")
            if i in self._working_ports:
                self._working_ports = list(
                    filter(lambda x: x != i, self._working_ports))

    def check_readout(self, i=42):
        # Read some images to ensure the cam is ready
        if self._video_capture.isOpened():
            for _ in range(i):
                if self._video_capture.read()[0]:
                    self._mode = CamMode.CAMERA
                    self._port = i
                    break

    def _check_resolutions(self):
        self._working_resolutions = []
        if self._mode == CamMode.CAMERA:
            # test_resolution = [(320, 480), (640, 480), (800, 600), (1024, 786),
            #                    (1280, 720), (1280, 800), (1280, 960),
            #                    (1280, 1024), (1440, 720), (1440, 900),
            #                    (1600, 1200), (1920, 1080), (1920, 1200),
            #                    (2560, 1440), (2560, 1600), (3840, 2160)]

            # EXIO cam USB2
            test_resolution = [(640, 480), (1024, 768), (1280, 720),
                               (1280, 960), (1920, 1080), (2048, 1536)]

            org_width = int(self._video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            org_height = int(self._video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # reset
            self.set_port(self._port)

            for width, height in test_resolution:
                self._video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self._video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                width = int(self._video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self._video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self._working_resolutions.append((width, height))

            self._working_resolutions = list(set(self._working_resolutions))
            self._working_resolutions.sort(key=lambda x: x[1])
            self._working_resolutions.sort(key=lambda x: x[0])

            self._video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, org_width)
            self._video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, org_height)

        return self._working_resolutions

    def set_prop(self, width, height, fps=25):
        if self._mode == CamMode.CAMERA:

            # reset camera to set setting befor image capture
            self.set_port(self._port)

            self._video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            # self._video_capture = cv2.
            if self._video_capture.get(cv2.CAP_PROP_FRAME_WIDTH
                                      ) != width or self._video_capture.get(
                                          cv2.CAP_PROP_FRAME_HEIGHT) != height:
                print(
                    f"resolution {width}x{height} not available. Switch to {int(self._video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self._video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))}"
                )

            self._video_capture.set(cv2.CAP_PROP_FPS, fps)
            if self._video_capture.get(cv2.CAP_PROP_FPS) != fps:
                print(
                    f"fps {fps} not available. Switch to {self._video_capture.get(cv2.CAP_PROP_FPS)}"
                )

            # Read some images to ensure the cam is ready
            for _ in range(42):
                if self._video_capture.read()[0]:
                    break

    def frame(self, quadratic=False):
        if self._mode == CamMode.CAMERA:
            ret, frame = self._video_capture.read()

            if not ret:
                print(f"camera disconnected: {ret}")
                self._mode == CamMode.NONE
                return None
        elif self._mode == CamMode.VIDEO:
            ret, frame = self._video_capture.read()
            if not ret:
                print(self._video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0))
                ret, frame = self._video_capture.read()
                if not ret:
                    print("video file corrupted")
                    self._mode == CamMode.NONE
                    return None
        else:
            return None

        if self._gray_image:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        if quadratic:
            height, width = frame.shape[0], frame.shape[1]
            l = min(height, width)
            delta = np.abs((width - height) // 2)

            frame = np.array(frame[:, delta:delta +
                                   l] if width > height else frame[delta:delta +
                                                                   l, :])
        return frame
