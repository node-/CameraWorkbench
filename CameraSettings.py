#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author: Jacob Kosberg
"""

from SaveState import guisave, guirestore, guidebug
from PyQt4 import QtGui, QtCore, uic
from camera import AmscopeCamera, WebCamera

import time

class AbstractCameraSettings(QtGui.QWidget):
    def __init__(self, camera, device, change_signal):
        self.change_detected = change_signal
        self.setWindowTitle("Camera Settings")
        self.camera = camera
        self.deviceId = device
        self.settingsFuncs = [self.setBrightness, self.setContrast,
                            self.setExposure, self.setRotation, self.setGain]
        self.setFixedSize(self.size())

    def setDeviceName(self):
        deviceName = str(self.deviceName.text())
        self.deviceNameStr = deviceName if deviceName else self.deviceId

    def wireUiElements(self):
        self.saveButton.clicked.connect(lambda: self.save())
        self.connectObjs((self.brightnessSlider, self.brightnessSpinBox), self.setBrightness)
        self.connectObjs((self.contrastSlider, self.contrastSpinBox), self.setContrast)
        self.connectObjs((self.exposureSlider, self.exposureSpinBox), self.setExposure)
        self.connectObjs((self.gainSlider, self.gainSpinBox), self.setGain)
        self.connectObjs((self.rotationSlider, self.rotationSpinBox), self.setRotation)
        self.deviceName.textChanged.connect(self.setDeviceName)
        self.wireSpecialUi()

    def wireSpecialUi(self):
        raise NotImplementedError

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
        try:
            setFunction()
        except AttributeError as e:
            # FIXME shouldn't give this error on boot if connectObjs() doesn't call setFunction()
            print("Capture object is empty; normal if booting.")

    def setBrightness(self):
        self.camera.set_brightness(self.brightnessSpinBox.value())

    def setContrast(self):
        self.camera.set_contrast(self.contrastSpinBox.value())

    def setExposure(self):
        self.camera.set_exposure(self.exposureSpinBox.value())

    def setGain(self):
        self.camera.set_gain(self.gainSpinBox.value())

    def setRotation(self):
        self.camera.set_rotation(self.rotationSpinBox.value())

    def applySettings(self):
        for func in self.settingsFuncs:
            func()
        guidebug(self)

    def save(self):
        guisave(self)
        self.change_detected.emit()

    def reset(self, waitTime):
        guirestore(self)
        self.wait(waitTime)
        self.applySettings()
        
    def closeEvent(self, event):
        guisave(self)
        event.accept()

class WebCameraSettings(AbstractCameraSettings):
    def __init__(self, camera, device, change_signal):
        QtGui.QWidget.__init__(self)
        AbstractCameraSettings.__init__(self, camera, device, change_signal)
        ui_path = "ui/parameters"
        self.ui = uic.loadUi(ui_path + '.ui', self)

        self.settings = QtCore.QSettings(
            ui_path + '_' +str(self.deviceId) + '.ini',
            QtCore.QSettings.IniFormat)

        self.setDeviceName()
        self.wireUiElements()
        time.sleep(5)
        guirestore(self)

    def reset(self, waitTime):
        pass

    def setDeviceSerial(self):
        # OpenCV does not support vendor details of VideoCapture objects
        pass

    def setDeviceId(self):
        # No deviceId label in UI
        pass

    def wireSpecialUi(self):
        # could implement zoom, position, etc.
        pass

    def wait(self, waitTime):
        #time.sleep(waitTime)
        pass

class AmscopeCameraSettings(AbstractCameraSettings):
    def __init__(self, camera, device, change_signal):
        QtGui.QWidget.__init__(self)
        AbstractCameraSettings.__init__(self, camera, device, change_signal)
        ui_path = "ui/amscope_parameters"
        self.ui = uic.loadUi(ui_path + '.ui', self)
        self.serial = self.initDeviceSerial()

        self.settings = QtCore.QSettings(
            ui_path + '_' +str(self.serial) + '.ini',
            QtCore.QSettings.IniFormat)
        
        self.setDeviceName()
        self.wireUiElements()
        guirestore(self)

    def initDeviceSerial(self):
        self.camera.activate()
        serial = str(self.camera.get_serial())
        self.camera.deactivate()
        return serial

    def setDeviceSerial(self):
        self.serialLabel.setText(self.serial)

    def setDeviceId(self):
        self.deviceIdLabel.setText(str(self.deviceId))

    def wait(self, waitTime):
        time.sleep(waitTime)

    def wireSpecialUi(self):
        self.settingsFuncs.extend([self.setTempTint, self.setHue,
                                self.setGamma, self.setSaturation])
        self.connectObjs((self.gammaSlider, self.gammaSpinBox), self.setGamma)
        self.connectObjs((self.saturationSlider, self.saturationSpinBox), self.setSaturation)
        self.connectObjs((self.tempSlider, self.tempSpinBox), self.setTempTint)
        self.connectObjs((self.tintSlider, self.tintSpinBox), self.setTempTint)
        self.connectObjs((self.hueSlider, self.hueSpinBox), self.setHue)

    def setTempTint(self):
        self.camera.capture.set_temperature_tint(self.tempSpinBox.value(), self.tintSpinBox.value())

    def setHue(self):
        self.camera.set_parameter("hue", self.hueSpinBox.value())

    def setGamma(self):
        self.camera.set_parameter("gamma", self.gammaSpinBox.value())

    def setSaturation(self):
        self.camera.set_parameter("saturation", self.saturationSpinBox.value())
