import os

from functools import partial

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtMultimedia
from PyQt5 import QtMultimediaWidgets


class CameraWidget(QtWidgets.QWidget):

    def __init__(self, parent=None, *args, **kwargs):
        super(CameraWidget, self).__init__(parent, *args, **kwargs)
        self.ui = parent
        self.init_camera()

    def init_camera(self):
        self.checkCameraDevices()
        self.setCamera(self.cameraDevice)
        self.checkResolution()

    def checkCameraDevices(self):
        self.cameraDevice = QtCore.QByteArray()

        videoDevicesGroup = QtWidgets.QActionGroup(self)
        videoDevicesGroup.setExclusive(True)

        for deviceName in QtMultimedia.QCamera.availableDevices()[::-1]:
            description = QtMultimedia.QCamera.deviceDescription(deviceName)
            videoDeviceAction = QtWidgets.QAction(description,
                                                  videoDevicesGroup)
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
            self.camera = QtMultimedia.QCamera()
        else:
            self.camera = QtMultimedia.QCamera(cameraDevice)

        if self.camera.isCaptureModeSupported(
                QtMultimedia.QCamera.CaptureStillImage):
            self.camera.setCaptureMode(QtMultimedia.QCamera.CaptureStillImage)

        self.imageCapture = QtMultimedia.QCameraImageCapture(self.camera)
        self.viewfinder = QtMultimediaWidgets.QCameraViewfinder(self)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.addWidget(self.viewfinder, 0, 0, 1, 1)

        self.camera.setViewfinder(self.viewfinder)
        self.camera.start()

    def resizeEvent(self, event):
        super(CameraWidget, self).resizeEvent(event)
