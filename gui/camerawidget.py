import os

from PyQt5.QtCore import QByteArray, qFuzzyCompare, Qt, QTimer
from PyQt5.QtGui import QImage, QPalette, QPixmap
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
        self.init_camera()

    def init_camera(self):

        cameraDevice = QByteArray()
        videoDevicesGroup = QActionGroup(self)
        videoDevicesGroup.setExclusive(True)

        for deviceName in QCamera.availableDevices():
            description = QCamera.deviceDescription(deviceName)
            videoDeviceAction = QAction(description, videoDevicesGroup)
            videoDeviceAction.setCheckable(True)
            videoDeviceAction.setData(deviceName)

            if cameraDevice.isEmpty():
                cameraDevice = deviceName
                videoDeviceAction.setChecked(True)

        videoDevicesGroup.triggered.connect(self.updateCameraDevice)

        self.setCamera(cameraDevice)

    def setCamera(self, cameraDevice):
        if cameraDevice.isEmpty():
            self.camera = QCamera()
        else:
            self.camera = QCamera(cameraDevice)

    def updateCameraDevice(self, action):
        self.setCamera(action.data())

    def resizeEvent(self, event):
        super(CameraWidget, self).resizeEvent(event)
        pass
