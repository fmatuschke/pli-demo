import os

from PyQt5.QtCore import QByteArray, qFuzzyCompare, Qt, QTimer
from PyQt5.QtGui import QImage, QPalette, QPixmap
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtMultimedia import (QAudioEncoderSettings, QCamera,
                                QCameraImageCapture, QImageEncoderSettings,
                                QMediaMetaData, QMediaRecorder, QMultimedia,
                                QVideoEncoderSettings)
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QDialog,
                             QLabel, QMainWindow, QMessageBox, QVBoxLayout,
                             QWidget)


class CameraWidget(QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super(CameraWidget, self).__init__(parent, *args, **kwargs)
        self.ui = parent
        self.init_camera()

    def init_camera(self):
        self.checkCameraDevices()
        self.setCamera(self.cameraDevice)
        self.checkResolution()

    def checkCameraDevices(self):
        self.cameraDevice = QByteArray()

        videoDevicesGroup = QActionGroup(self)
        videoDevicesGroup.setExclusive(True)

        for deviceName in QCamera.availableDevices()[::-1]:
            description = QCamera.deviceDescription(deviceName)
            videoDeviceAction = QAction(description, videoDevicesGroup)
            videoDeviceAction.setCheckable(True)
            videoDeviceAction.setData(deviceName)

            if self.cameraDevice.isEmpty():
                self.cameraDevice = deviceName
                videoDeviceAction.setChecked(True)

    def checkResolution(self):
        supportedResolutions, _ = self.imageCapture.supportedResolutions()
        for resolution in supportedResolutions:
            self.ui.cameraMenu.addAction(
                f"{resolution.width()}x{resolution.height()}")

    def setCamera(self, cameraDevice):
        if cameraDevice.isEmpty():
            self.camera = QCamera()
        else:
            self.camera = QCamera(cameraDevice)

        self.imageCapture = QCameraImageCapture(self.camera)
        self.viewfinder = QCameraViewfinder(self)
        self.camera.setViewfinder(self.viewfinder)
        self.camera.start()

    def resizeEvent(self, event):
        super(CameraWidget, self).resizeEvent(event)
