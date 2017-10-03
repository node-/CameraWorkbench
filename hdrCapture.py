#!/usr/bin/python

"""
author: Jacob Kosberg
"""

from __future__ import division
from os.path import join

import time
import numpy as np
import cv2

def timelapse(seconds):
    starttime=time.time()
    while True:
        snapAll()
        time.sleep(seconds - ((time.time() - starttime) % seconds))

def snapAll():
    for i in [0]:
        snap(i)

def mergeImgs(imgs, expos):
    # Debevec = name of the HDR algorithm used for merging
    merge_debvec = cv2.createMergeDebevec()
    hdr_debvec = merge_debvec.process(imgs, times=np.array(expos, dtype=np.float32))
    tonemap1 = cv2.createTonemapDurand(gamma=2.2)
    res_debvec = tonemap1.process(hdr_debvec.copy())
    res_debvec_8bit = np.clip(res_debvec*255, 0, 255).astype('uint8')
    return res_debvec_8bit

def snap(device):
    # this maps the relationship between
    # DSHOW's arbitrary driver parameters and exposure in seconds.
    expo_relation = [(0, 1/512), (-1, 1/256), (-2, 1/128), (-3, 1/64), (-4, 1/32), (-5, 1/16)]

    cap = cv2.VideoCapture(device)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920.0)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080.0)

    imgs = []
    expos = []
    for param, sec in expo_relation:
        cap.set(cv2.CAP_PROP_EXPOSURE, param-1)
        spendTime(1, cap.read)
        img = cap.read()[1]
        imgs.append(img)
        expos.append(sec)

        # debugging info
        #print str(k) + " =? " + str(cap.get(cv2.CAP_PROP_EXPOSURE))
        #cv2.imshow(str(k) + " seconds", img)
        #cv2.imwrite(join("test", str(v)) + ".png", img)

    mergedImg = mergeImgs(imgs, expos)
    filename = "HDR_" + str(device) + "_" + str(time.time()) + ".jpg"
    cv2.imwrite(join("test", filename), mergedImg)

    # When everything done, release the capture
    cap.release()

def spendTime(seconds, function):
    t_end = time.time() + seconds
    while time.time() < t_end:
        function()

def main():
    timelapse(5)

if __name__ == "__main__":
    main()