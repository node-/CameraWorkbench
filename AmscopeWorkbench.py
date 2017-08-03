#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
author: Jacob Kosberg
"""

import argparse
import Amscope
import os
import time
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="UI utility for Amscope camera imagery.")
    parser.add_argument("count", type=int, help="Number of connected Amscope cameras.")
    args = parser.parse_args()
    initTimelapse(args.count)

def getCams(numCams):
    cams = []
    for i in range(numCams):
        cam = Amscope.ToupCamCamera(camIndex=i)
        if cam.open():
            cams.append(cam)
        else:
            print "Could not open cam #" + str(i)

    return cams

def initTimelapse(numCams):
    assert(numCams > 0)
    cams = getCams(numCams)
"""
    starttime = time.time()
    while True:
        datestr = str(datetime.now().strftime("%Y-%m-%d_%H.%M.%S"))
        i = 0

    	path = os.path.join("images", "cam" + str(i), ".bmp")

    	print "snapping to " + path

    	if not take_image(cam, path):
    		print "snap failed! reloading drivers"
    		cam.close()
    		del(cam)
    		reload(camera)
    		cam = camera.ToupCamCamera(camIndex=i)
    		cam.open()

    	time.sleep(300.0 - ((time.time() - starttime) % 300))
"""
    for cam in cams:
        cam.close()

def take_image(cam, path):
	cam.save(path)
	time.sleep(5)
	if not os.path.exists(path):
		print "NO IMAGE OUTPUT!"
		return False
	return True


if __name__ == '__main__':
    main()
