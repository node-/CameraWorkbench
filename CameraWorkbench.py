#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author: Jacob Kosberg
"""


from SaveState import guisave, guirestore
from PyQt4 import QtGui, QtCore, uic

import cv2
import time
import os
import argparse
import sys


class MainWindow(QtGui.QMainWindow):
    def __init__(self, camera, worker):
        QtGui.QMainWindow.__init__(self)
        self.ui = uic.loadUi('ui/main.ui', self)
        self.setWindowTitle("Camera Workbench")
        self.setFixedSize(self.size())
        self.settings = QtCore.QSettings('ui/main.ini', QtCore.QSettings.IniFormat)
        guirestore(self)
        self.worker = worker

        worker.scale = self.viewportScaleSpinBox.value()
        worker.interval = self.intervalSpinBox.value()
        worker.intervalEnabled = self.intervalEnabled.isChecked()

        self.settingsWindow = CameraSettings(camera)
        self.worker.setImagesPath(str(self.capturePath.text()))

        # Camera Settings
        self.parametersButton.clicked.connect(lambda: self.settingsWindow.show())
        # Viewport Scale
        self.viewportScaleSpinBox.valueChanged.connect(
            lambda: self.worker.setScale(self.viewportScaleSpinBox.value()))
        self.capturePath.textChanged.connect(
            lambda: self.worker.setImagesPath(str(self.capturePath.text())))

        # Capture Image
        self.captureButton.clicked.connect(lambda: self.worker.captureImage())
        # Interval
        self.intervalSpinBox.valueChanged.connect(
            lambda: self.worker.setInterval(self.intervalSpinBox.value()))
        self.intervalEnabled.stateChanged.connect(
            lambda: self.worker.setIntervalEnabled(self.intervalEnabled.isChecked()))

    def closeEvent(self, event):
        self.worker.running = False
        self.settingsWindow.closeEvent(event)
        guisave(self)
        event.accept()


class CameraSettings(QtGui.QWidget):
    def __init__(self, camera):
        QtGui.QWidget.__init__(self)
        self.ui = uic.loadUi('ui/parameters.ui', self)
        self.camera = camera

        self.setFixedSize(self.size())

        # wiring sliders and spin boxes
        self.connectObjs((self.brightnessSlider, self.brightnessSpinBox), self.setBrightness)
        self.connectObjs((self.contrastSlider, self.contrastSpinBox), self.setContrast)
        self.connectObjs((self.gainSlider, self.gainSpinBox), self.setGain)
        self.connectObjs((self.exposureSlider, self.exposureSpinBox), self.setExposure)
        self.connectObjs((self.rotationSlider, self.rotationSpinBox), self.setRotation)

        # restore settings
        self.settings = QtCore.QSettings('ui/parameters.ini', QtCore.QSettings.IniFormat)
        guirestore(self)

    def connectObjs(self, objTuple, setFunction):
        first, second = objTuple
        first.valueChanged.connect(
            lambda: self.changeValue(first, second, setFunction))
        second.valueChanged.connect(
            lambda: self.changeValue(second, first, setFunction))

    def changeValue(self, fromObj, toObj, setFunction):
        toObj.setValue(fromObj.value())
        setFunction()

    def setBrightness(self):
        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, self.brightnessSpinBox.value())

    def setContrast(self):
        self.camera.set(cv2.CAP_PROP_CONTRAST, self.contrastSpinBox.value())

    def setGain(self):
        self.camera.set(cv2.CAP_PROP_GAIN, self.gainSpinBox.value())

    def setExposure(self):
        # the -1 fixes weird off-by-one openCV bug
        self.camera.set(cv2.CAP_PROP_EXPOSURE, self.exposureSpinBox.value()-1)

    def setRotation(self):
        #self.camera.set_rotation(self.isLeft, self.rotationSpinBox.value())
        pass

    def closeEvent(self, event):
        guisave(self)
        event.accept()


class Worker(QtCore.QThread):
    def __init__(self, camera):
        QtCore.QThread.__init__(self)
        self.camera = camera
        self.running = True
        self.intervalEnabled = False

    def run(self):
        while self.running:
            if self.intervalEnabled:
                start = time.time()
                while time.time() < start + self.interval:
                    self.show_frame()
                self.captureBoth()
            else:
                self.show_frame()

        self.kill()

    def verifyPathExists(self, path):
        if path in [None, ""]:
            raise ValueError("Path cannot be empty!")

    def get_frame(self):
        return self.camera.get_frame()

    def show_frame(self):
        # rotate and scale this
        frame = self.get_frame()
        cv2.imshow("Preview", frame)

    def captureBoth(self):
        for i in [0, 1]:
            self.captureImage(i)

    def captureImage(self):
        cv2.imwrite(self.getImageFilepath(self.imagesPath), self.get_frame())

    def getImageFilepath(self, path):
        self.verifyPathExists(path)
        date_string = time.strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join(path, date_string + ".png")

    def setIntervalEnabled(self, enabled):
        self.intervalEnabled = enabled

    def setImagesPath(self, path):
        self.imagesPath = path

    def setScale(self, scale):
        self.scale = scale

    def setInterval(self, interval):
        self.interval = interval

    def kill(self):
        self.running = False
        self.terminate()


class Camera(object):
    def __init__(self, device):
        self.capture = cv2.VideoCapture(device)

    def get_frame(self):
        return self.capture.read()[1]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.capture.release()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description="UI utility for time lapse imagery.")
    parser.add_argument("device", type=int, help="Camera's device index for OpenCV. (0, 1, 2, ...)")
    args = parser.parse_args()

    with Camera(args.device) as camera:
        app = QtGui.QApplication(['Camera Workbench'])
        thread = Worker(camera)
        thread.start()
        mainWindow = MainWindow(camera, thread)
        mainWindow.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

