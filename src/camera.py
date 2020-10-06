import cv2


class Camera:

    def __init__(self):
        self.working_ports = []
        self.working_resolutions = []
        pass

    def check_port(self, port):
        camera = cv2.VideoCapture(port)
        port_works = False
        if camera.isOpened():
            is_reading, _ = camera.read()
            if is_reading:
                port_works = True
            camera.release()
        return port_works

    def list_ports(self, start=0, end=5):
        self.working_ports = [
            port for port in range(start, end + 1) if self.check_port(port)
        ]
        return self.working_ports

    def set_resolution(self, width, height):
        pass

    def list_resolutions(self):
        pass
