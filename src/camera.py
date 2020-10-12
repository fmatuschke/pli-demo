import cv2
import sys
import os
import numpy as np


class Camera:

    def __init__(self,
                 width=1280,
                 height=960,
                 fps=30,
                 port_start=0,
                 port_end=5,
                 port_id=0,
                 gray_image=True):
        self.gray_image = gray_image
        self.working_ports = []
        self.working_resolutions = []
        self.list_ports(port_start, port_end)
        self.set_port_id(port_id)
        self.list_resolutions()
        self.set_resolution(width, height)

        # TODO:
        # self.set_fps(fps)

    def __del__(self):
        if self.video_capture:
            self.video_capture.release()

    def is_alive(self):
        return self.video_capture is not None

    def check_port(self, port):
        # TODO: ignore output
        camera = cv2.VideoCapture(port)
        port_works = False
        if camera.isOpened():
            is_reading, _ = camera.read()
            if is_reading:
                port_works = True
            camera.release()
        return port_works

    def list_ports(self, start, end):
        self.working_ports = [
            port for port in range(start, end + 1) if self.check_port(port)
        ]
        print(f"working ports: {self.working_ports}")
        return self.working_ports

    def set_port_id(self, i):
        if len(self.working_ports) > i:
            self.video_capture = cv2.VideoCapture(self.working_ports[i])
            # Read some images to ensure the cam is ready
            for _ in range(42):
                if self.video_capture.read()[0]:
                    break
        else:
            self.video_capture = None
            print("id extend port list")

    def set_resolution(self, width, height):
        if self.is_alive():
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            if self.width() != width or self.height() != height:
                print(
                    f"resolution {width}x{height} not available. Switch to {self.width()}x{self.height()}",
                )

            # Read some images to ensure the cam is ready
            for _ in range(42):
                if self.video_capture.read()[0]:
                    break

    def set_fps(self, fps):
        if self.is_alive():
            self.video_capture.set(cv2.CAP_PROP_FPS, fps)
            # Read some images to ensure the cam is ready
            for _ in range(42):
                if self.video_capture.read()[0]:
                    break

    def width(self):
        width = 0
        if self.is_alive():
            width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        return int(width)

    def height(self):
        height = 0
        if self.is_alive():
            height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return int(height)

    def list_resolutions(self):
        self.working_resolutions = []
        if self.is_alive():
            # test_resolution = [(320, 480), (640, 480), (800, 600), (1024, 786),
            #                    (1280, 720), (1280, 800), (1280, 960),
            #                    (1280, 1024), (1440, 720), (1440, 900),
            #                    (1600, 1200), (1920, 1080), (1920, 1200),
            #                    (2560, 1440), (2560, 1600), (3840, 2160)]

            # EXIO cam USB2
            test_resolution = [(640, 480), (1024, 768), (1280, 720),
                               (1280, 960), (1920, 1080), (2048, 1536)]

            org_width = self.width()
            org_height = self.height()

            for width, height in test_resolution:
                self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                width = self.width()
                height = self.height()
                self.working_resolutions.append((int(width), int(height)))

            self.working_resolutions = list(set(self.working_resolutions))
            self.working_resolutions.sort(key=lambda x: x[1])
            self.working_resolutions.sort(key=lambda x: x[0])

            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, org_width)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, org_height)

        return self.working_resolutions

    def frame(self, quadratic=False):
        if self.is_alive():
            ret, frame = self.video_capture.read()

            if not ret:
                print(f"camera disconnected: {ret}")
                self.video_capture = None
                return None

            if self.gray_image:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            if quadratic:
                height, width = frame.shape[0], frame.shape[1]
                l = min(height, width)
                delta = np.abs((width - height) // 2)

                frame = np.array(frame[:, delta:delta +
                                       l] if width > height else frame[
                                           delta:delta + l, :])

            return frame
        else:
            return None
