import cv2


class Camera:

    def __init__(
        self,
        width=1600,
        height=1200,
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
        self.set_fps(fps)
        pass

    def reset(self):
        self.__init__()

    def live(self):
        return self.video_capture is not None

    def check_port(self, port):
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
            self.video_capture = cv2.VideoCapture(
                self.working_ports[self.working_ports[i]])
        else:
            self.video_capture = None
            print("id extend port list")

    def set_resolution(self, width, height):
        print(width, height)
        if self.live():
            self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def set_fps(self, fps):
        if self.live():
            self.video_capture.set(cv2.CAP_PROP_FPS, fps)

    def width(self):
        width = 0
        if self.live():
            width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        return width

    def height(self):
        height = 0
        if self.live():
            height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return height

    def list_resolutions(self):
        self.working_resolutions = []
        if self.live():
            test_resolution = [(320, 480), (640, 480), (800, 600), (1024, 786),
                               (1280, 720), (1280, 800), (1440, 720),
                               (1440, 900), (1600, 1200), (1920, 1080),
                               (1920, 1200), (2560, 1440), (2560, 1600),
                               (3840, 2160)]

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

    def frame(self):
        ret, frame = self.video_capture.read()

        if not ret:
            print("camera disconnected")
            self.video_capture = None
            return None

        return frame
