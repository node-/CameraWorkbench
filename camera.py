#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author: Jacob Kosberg
"""
import cv2
import Amscope
import numpy

class CameraError(Exception):
    """Camera error."""
class CameraTimeoutError(CameraError):
    """Camera timeout, probably due to bandwidth issue."""
class CameraDisconnectedError(CameraError):
    """Camera was disconnected."""
class CameraDeactivatedError(CameraError):
    """Camera is not activated."""

class AbstractCamera(object):
    """This Abstract class defines the interface for a generic camera."""
    def __init__(self, device):
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        raise NotImplementedError

    def get_frame(self):
        raise NotImplementedError

    def show_frame(self, title, scale=80.0):
        """
        Show current frames from cameras.

        ``wait`` is the wait interval in milliseconds before the window closes.
        """
        frame = self.get_frame()
        if frame.any():
            frame = cv2.resize(frame, None, 
                fx=scale/100.0, fy=scale/100.0, 
                interpolation=cv2.INTER_AREA) 
        cv2.imshow(title, frame)
        cv2.waitKey(1)

    def set_brightness(self, value):
        raise NotImplementedError

    def set_contrast(self, value):
        raise NotImplementedError

    def set_gain(self, value):
        raise NotImplementedError

    def set_exposure(self, value):
        raise NotImplementedError

    def set_rotation(self, value):
        self.rotation = value

    def set_parameter(self, key, value):
        raise NotImplementedError

    def rotate_bound(self, image, angle):
        # grab the dimensions of the image and then determine the
        # center
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)
     
        # grab the rotation matrix (applying the negative of the
        # angle to rotate clockwise), then grab the sine and cosine
        # (i.e., the rotation components of the matrix)
        M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = numpy.abs(M[0, 0])
        sin = numpy.abs(M[0, 1])
     
        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
     
        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY
     
        # perform the actual rotation and return the image
        return cv2.warpAffine(image, M, (nW, nH))


class AmscopeCamera(AbstractCamera):
    """Camera class impl for the Amscope cameras, which have more camera settings than webcams."""
    parameters = ["brightness", "contrast", "level_range", "exposure_time",
                "exposure_gain", "temperature_tint", "hue", "saturation", "gamma"]
    def __init__(self, device, fullRes=False):
        self.rotation = 0
        self.device = device
        self.capture = None
        self.disabled = False
        if not fullRes:
            self.resolution = 1
        else:
            self.resolution = 0

    def get_serial(self):
        return self.capture.get_serial() if not self.disabled else None

    def activate(self):
        #print "activating camera " + str(self.device)
        if self.capture:
            self.deactivate()
        try:
            self.capture = self.open_cam(self.device)
            self.capture.set_auto_exposure_enabled(False)
        except IOError as e:
            print(e)
            self.disabled = True
            print("Camera is disabled at index: %s" % self.device)

    def deactivate(self):
        #print "deactivating camera " + str(self.device)
        if self.capture:
            self.capture.close()
        self.capture = None

    def open_cam(self, device):
        cap = Amscope.ToupCamCamera(camIndex=device, resolution=self.resolution)
        if cap.open():
            return cap
        else:
            raise IOError('Could not find Amscope at index: ' + str(device))

    def get_frame(self):
        if not self.capture:
            #raise CameraDeactivatedError("You must activate the camera before snapping!")
            return None
        frame = self.rotate_bound(self.capture.get_np_image(), self.rotation)
        return frame

    def set_parameter(self, key, value):
        assert (key in self.parameters)
        #if not self.disabled:
        #getattr(self.capture, "set_" + key)(value)

    def close(self):
        self.deactivate()

    
    # Commented out since @deprecated decorator is not in this project
    def set_brightness(self, value):
        self.capture.set_brightness(value)

    def set_contrast(self, value):
        self.capture.set_contrast(value)

    def set_level_range(self, value):
        self.capture.set_level_range(value)

    def set_exposure(self, value):
        self.capture.set_exposure_time(value)

    def set_gain(self, value):
        self.capture.set_exposure_gain(value)

    def set_temp_tint(self, temp, tint):
        self.capture.set_temperature_tint(temp, tint)

    def set_hue(self, value):
        self.capture.set_hue(value)

    def set_saturation(self, value):
        self.capture.set_saturation(value)

    def set_gamma(self, value):
        self.capture.set_gamma(value)
    


class WebCamera(AbstractCamera):
    """Camera class impl for webcams that are supported by OpenCV3."""
    parameters = {"brightness" : cv2.CAP_PROP_BRIGHTNESS,
                    "contrast" : cv2.CAP_PROP_CONTRAST, 
                    "exposure_gain" : cv2.CAP_PROP_GAIN, 
                    "exposure_time" : cv2.CAP_PROP_EXPOSURE}
    def __init__(self, device, fullRes=True):
        self.rotation = 0
        self.device = device
        self.capture = cv2.VideoCapture(device)
        if fullRes:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920.0)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080.0)

    """Activation and deactivation are probably not required for webcams."""
    def activate(self):
        pass

    def deactivate(self):
        pass

    def get_frame(self):
        frame = self.rotate_bound(self.capture.read()[1], self.rotation)
        return frame

    def set_parameter(self, key, value):
        assert (key in self.parameters.keys())
        self.capture.set(self.parameters[key], value)


    def close(self):
        self.capture.release()
        cv2.destroyAllWindows()
    
    # Commented out since @deprecated decorator is not in this project

    def set_brightness(self, value):
        self.capture.set(cv2.CAP_PROP_BRIGHTNESS, value)

    def set_contrast(self, value):
        self.capture.set(cv2.CAP_PROP_CONTRAST, value)

    def set_gain(self, value):
        self.capture.set(cv2.CAP_PROP_GAIN, value)

    def set_exposure(self, value):
        self.capture.set(cv2.CAP_PROP_EXPOSURE, value)
    