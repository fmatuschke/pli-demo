import cv2
import sys
import os

pli_logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                             "data", "pli-logo.png")


class Camera:

    def __init__(
        self,
        width=1280,
        height=960,
        fps=30,
        port_start=0,
        port_end=5,
        port_id=0,
    ):
        self.working_ports = []
        self.working_resolutions = []
        self.list_ports(port_start, port_end)
        self.set_port_id(port_id)
        self.list_resolutions()
        self.set_resolution(width, height)

        # TODO:
        # self.set_fps(fps)

    def reset(self):
        self.__init__()

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
            # Read the first three images to ensure the cam is ready
            [self.video_capture.read() for _ in range(3)]
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

            # Read the first three images to ensure the cam is ready
            [self.video_capture.read() for _ in range(3)]

    def set_fps(self, fps):
        if self.is_alive():
            self.video_capture.set(cv2.CAP_PROP_FPS, fps)
            # Read the first three images to ensure the cam is ready
            [self.video_capture.read() for _ in range(3)]

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

        print(self.working_resolutions)

        return self.working_resolutions

    def frame(self):
        if self.is_alive():
            ret, frame = self.video_capture.read()

            if not ret:
                print(f"camera disconnected: {ret}")
                self.video_capture = None
                return None

            return frame
        else:
            return cv2.imread(pli_logo_path, cv2.IMREAD_COLOR)
