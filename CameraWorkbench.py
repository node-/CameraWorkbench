#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author: Jacob Kosberg
"""

from SaveState import guisave, guirestore
from PyQt4 import QtGui, QtCore, uic
from camera import AmscopeCamera, WebCamera

import cv2
import time
import os
import argparse
import sys

# This is the time it takes to switch Amscope cameras. Used for interval
# calculation. For webcams, we set equal to 0 since we don't deactivate
# cameras. (Less risk of hitting USB bandwidth.)
CAMERA_ACTIVATION_TIME_SECONDS = 5

class MainWindow(QtGui.QMainWindow):
    """MainWindow initializes UI objects like buttons, text/check/spin boxes, etc."""
    def __init__(self, worker):
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi('ui/main.ui', self)
        self.setWindowTitle("Camera Workbench")
        self.setFixedSize(self.size())
        self.settings = QtCore.QSettings('ui/main.ini', QtCore.QSettings.IniFormat)
        guirestore(self)
        self.worker = worker
        self.populateDeviceList()
        self.setInitValues()
        self.wireUiElements()

    def populateDeviceList(self):
        i = 0
        for camera in self.worker.cameras:
            item = QtGui.QListWidgetItem(str(camera.deviceNameStr))
            self.deviceList.addItem(item)

            # Select and activate the first camera
            if i == 0:
                self.deviceList.setCurrentItem(item)
                self.switchCamera(item)
            i += 1

    def setInitValues(self):
        self.worker.scale = self.previewScaleSpinBox.value()
        self.worker.interval = self.intervalSpinBox.value()
        self.worker.intervalEnabled = self.intervalEnabled.isChecked()
        self.worker.previewEnabled = self.previewEnabled.isChecked()
        self.worker.setImagesPath(str(self.capturePath.text()))

    def wireUiElements(self):
        # Change device to selected device
        self.deviceList.itemClicked.connect(self.switchCamera)

        # Camera Settings/Parameters Button
        self.settingsButton.clicked.connect(lambda: self.worker.camera.show())

        # Preview Window
        self.previewScaleSpinBox.valueChanged.connect(
            lambda: self.worker.setScale(self.previewScaleSpinBox.value()))
        self.previewEnabled.stateChanged.connect(
            lambda: self.worker.setPreviewEnabled(self.previewEnabled.isChecked()))

        # Capture path
        self.capturePath.textChanged.connect(
            lambda: self.worker.setImagesPath(str(self.capturePath.text())))

        # Capture Image, either ALL or Selected Device
        self.snapAllButton.clicked.connect(lambda: self.worker.captureAll())
        self.snapSelectedButton.clicked.connect(lambda: self.worker.captureImage())

        # Interval value and checkbox
        self.intervalSpinBox.valueChanged.connect(
            lambda: self.worker.setInterval(self.intervalSpinBox.value()))
        self.intervalEnabled.stateChanged.connect(
            lambda: self.worker.setIntervalEnabled(self.intervalEnabled.isChecked()))

    def switchCamera(self, item):
        i = int(self.deviceList.indexFromItem(item).row())
        self.worker.switchCamera(i)

    def closeEvent(self, event):
        self.worker.running = False
        for settings in self.worker.cameras:
            settings.closeEvent(event)
        self.intervalEnabled.setChecked(False)
        guisave(self)
        event.accept()


class CameraSettings(QtGui.QWidget):
    def __init__(self, camera, device):
        QtGui.QWidget.__init__(self)
        self.ui = uic.loadUi('ui/amscope_parameters.ui', self)
        self.setWindowTitle("Camera Settings")
        self.camera = camera
        self.deviceId = device
        self.deviceNameStr = self.deviceId
        self.setFixedSize(self.size())
        self.settings = QtCore.QSettings(
            'ui/amscope_parameters_'+str(self.deviceId)+'.ini',
            QtCore.QSettings.IniFormat)
        guirestore(self)
        self.deviceNameStr = str(self.deviceName.text())
        self.wireUiElements()

    def wireUiElements(self):
        self.connectObjs((self.brightnessSlider, self.brightnessSpinBox), self.setBrightness)
        self.connectObjs((self.contrastSlider, self.contrastSpinBox), self.setContrast)
        self.connectObjs((self.exposureSlider, self.exposureSpinBox), self.setExposure)
        self.connectObjs((self.tempSlider, self.tempSpinBox), self.setTempTint)
        self.connectObjs((self.tintSlider, self.tintSpinBox), self.setTempTint)
        self.connectObjs((self.hueSlider, self.hueSpinBox), self.setHue)
        self.connectObjs((self.rotationSlider, self.rotationSpinBox), self.setRotation)
        self.connectObjs((self.gammaSlider, self.gammaSpinBox), self.setGamma)
        self.connectObjs((self.saturationSlider, self.saturationSpinBox), self.setSaturation)
        self.deviceName.textChanged.connect(
            lambda: self.changeName(str(self.deviceName.text())))

    def connectObjs(self, objTuple, setFunction):
        """
        Mutually connect two objects in a tuple so their values stay equal.
        Used to wire up sliders to spin boxes for camera settings.
        """
        first, second = objTuple
        first.valueChanged.connect(
            lambda: self.changeValue(first, second, setFunction))
        second.valueChanged.connect(
            lambda: self.changeValue(second, first, setFunction))

    def changeValue(self, fromObj, toObj, setFunction):
        toObj.setValue(fromObj.value())
        setFunction()

    def changeName(self, deviceName):
        self.deviceNameStr = deviceName

    def setBrightness(self):
        self.camera.set_brightness(self.brightnessSpinBox.value())

    def setContrast(self):
        self.camera.set_contrast(self.contrastSpinBox.value())

    def setExposure(self):
        self.camera.set_exposure(self.exposureSpinBox.value())

    def setTempTint(self):
        self.camera.set_temp_tint(self.tempSpinBox.value(), self.tintSpinBox.value())

    def setHue(self):
        self.camera.set_hue(self.hueSpinBox.value())

    def setGamma(self):
        self.camera.set_gamma(self.gammaSpinBox.value())

    def setSaturation(self):
        self.camera.set_saturation(self.saturationSpinBox.value())

    def setRotation(self):
        self.camera.set_rotation(self.rotationSpinBox.value())

    def applySettings(self):
        settingsFuncs = [self.setBrightness, self.setContrast, self.setExposure,
                        self.setTempTint, self.setHue, self.setGamma, 
                        self.setSaturation, self.setRotation]

        for func in settingsFuncs:
            func()

    def reset(self):
        guirestore(self)
        self.applySettings()

    def closeEvent(self, event):
        guisave(self)
        event.accept()


class Worker(QtCore.QThread):
    """
    QT thread for activating cameras, capturing and scaling images.
    self.cameras is actually a list of CameraSettings, which act as
    camera managers 
    """
    def __init__(self, cameras):
        QtCore.QThread.__init__(self)
        self.cameras = cameras
        self.camera = None
        self.running = True
        self.intervalEnabled = False
        self.scale = 60
        self.previewEnabled = False

        # not implemented
        self.hdrEnabled = False

    def run(self):
        while self.running:
            if self.intervalEnabled:
                self.captureAll()
                # actual interval is different from the specified interval due to
                # the time it takes for cameras to activate
                interval = self.interval - len(self.cameras)*CAMERA_ACTIVATION_TIME_SECONDS
                start = time.time()
                while time.time() < start + interval:
                    self.show_frame()
            else:
                self.show_frame()

        self.kill()

    def createPathIfNotExists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def assertPathNotNull(self, path):
        if path in [None, ""]:
            raise ValueError("Path cannot be empty!")

    def show_frame(self):
        title = "Preview"
        if self.previewEnabled and self.camera.camera.capture:
            self.camera.camera.show_frame(title, scale=self.scale)
        else:
            cv2.destroyWindow(title)

    def captureAll(self):
        for i in range(len(self.cameras)):
            self.switchCamera(i)
            self.captureImage()

    def captureImage(self):
        cameraSettings = self.camera
        frame = cameraSettings.camera.get_frame()
        filename = self.getImageFilepath(self.imagesPath, cameraSettings.deviceNameStr)
        cv2.imwrite(filename, frame)

    def getImageFilepath(self, path, deviceName):
        """
        Creates file path under 'deviceName' folder in parent images path.
        Uses date and time as filename. Ex: '2017-08-08_10-29-57.png'
        """
        self.assertPathNotNull(path)
        newPath = os.path.join(path, str(deviceName))
        self.createPathIfNotExists(newPath)
        dateString = time.strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(newPath, dateString + ".png")

    def setIntervalEnabled(self, enabled):
        self.intervalEnabled = enabled

    def setPreviewEnabled(self, enabled):
        self.previewEnabled = enabled

    def setImagesPath(self, path):
        self.imagesPath = path

    def setScale(self, scale):
        self.scale = scale

    def setInterval(self, interval):
        self.interval = interval

    def switchCamera(self, index):
        if self.camera:
            self.camera.camera.deactivate()
        self.camera = self.cameras[index]
        self.camera.camera.activate()
        self.camera.reset()
        time.sleep(CAMERA_ACTIVATION_TIME_SECONDS)

    def kill(self):
        self.running = False
        for cam in self.cameras:
            cam.camera.close()
        self.terminate()

def main():
    parser = argparse.ArgumentParser(description="UI utility for time lapse and HDR imagery.")
    parser.add_argument("devices", type=int, nargs="+", help="Device index. (0, 1, 2, ...)")
    parser.add_argument('--amscope', dest='use_amscope', action='store_true')
    parser.add_argument('--webcam', dest='use_amscope', action='store_false')
    args = parser.parse_args()

    app = QtGui.QApplication(['Camera Workbench'])

    if args.use_amscope:
        Camera = AmscopeCamera
    else:
        CAMERA_ACTIVATION_TIME_SECONDS = 0
        Camera = WebCamera

    cams = [CameraSettings(Camera(device), device) for device in args.devices]
    worker = Worker(cams)
    worker.start()
    mainWindow = MainWindow(worker)
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()