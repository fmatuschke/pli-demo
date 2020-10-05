import os

from functools import partial

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

# TODO: change to
from PyQt5 import QtCore, QtGui, QtWidgets


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

            self.ui.cameraPortMenu.addAction(
                QtWidgets.QAction(f"{deviceName}",
                                  self.ui.cameraPortMenu,
                                  triggered=partial(self.setCamera,
                                                    deviceName)))

    def checkResolution(self):
        supportedResolutions, _ = self.imageCapture.supportedResolutions()
        self.ui.cameraResolutionMenu = self.ui.cameraMenu.addMenu('resolution')
        for resolution in supportedResolutions:
            self.ui.cameraResolutionMenu.addAction(
                QtWidgets.QAction(f"{resolution.width()}x{resolution.height()}",
                                  self.ui.cameraResolutionMenu,
                                  triggered=partial(self.setResolution,
                                                    resolution.width(),
                                                    resolution.height())))

    def setResolution(self, width=100, height=200):
        print(width, height)
        pass

    def setCamera(self, cameraDevice):
        # TODO: clean befor set

        if cameraDevice.isEmpty():
            self.camera = QCamera()
        else:
            self.camera = QCamera(cameraDevice)

        if self.camera.isCaptureModeSupported(QCamera.CaptureStillImage):
            self.camera.setCaptureMode(QCamera.CaptureStillImage)

        self.imageCapture = QCameraImageCapture(self.camera)
        self.viewfinder = QCameraViewfinder(self)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.addWidget(self.viewfinder, 0, 0, 1, 1)

        self.camera.setViewfinder(self.viewfinder)
        self.camera.start()

    def resizeEvent(self, event):
        super(CameraWidget, self).resizeEvent(event)
