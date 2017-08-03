#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    author: Jacob Kosberg
"""
import cv2
import Amscope

class AbstractCamera(object):
    """This Abstract class defines the interface for a generic camera."""
    def __init__(self, device):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, type, value, traceback):
        raise NotImplementedError

    def get_frame(self):
        raise NotImplementedError

    def show_frame(self, scale=80.0):
        """
        Show current frames from cameras.

        ``wait`` is the wait interval in milliseconds before the window closes.
        """
        frame = self.get_frame()
        if frame.any():
            frame = cv2.resize(frame, None, 
                fx=scale/100.0, fy=scale/100.0, 
                interpolation=cv2.INTER_AREA) 
        cv2.imshow("Preview", frame)
        cv2.waitKey(1)

    def set_brightness(self, value):
        raise NotImplementedError

    def set_contrast(self, value):
        raise NotImplementedError

    def set_gain(self, value):
        raise NotImplementedError

    def set_exposure(self, value):
        raise NotImplementedError


class AmscopeCamera(AbstractCamera):
    """Implementatin of the Abstract Camera class for the Amscope cameras"""
    def __init__(self, device):
        cap = Amscope.ToupCamCamera(camIndex=device)
        if cap.open():
            self.capture = cap
        else:
            raise IOError('Could not find Amscope at index: ' + str(i))

    def get_frame(self):
        frame = self.capture.get_np_image()
        return frame

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.capture.close()


class WebCamera(AbstractCamera):
    """Implements the Abstract Camera for webcams that support OpenCV3"""
    def __init__(self, device):
        self.capture = cv2.VideoCapture(device)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920.0)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080.0)

    def get_frame(self):
        frame = self.capture.read()[1]
        return frame

    def set_brightness(self, value):
        self.capture.set(cv2.CAP_PROP_BRIGHTNESS, value)

    def set_contrast(self, value):
        self.capture.set(cv2.CAP_PROP_CONTRAST, value)

    def set_gain(self, value):
        self.capture.set(cv2.CAP_PROP_GAIN, value)

    def set_exposure(self, value):
        self.capture.set(cv2.CAP_PROP_EXPOSURE, value)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.capture.release()
        cv2.destroyAllWindows()