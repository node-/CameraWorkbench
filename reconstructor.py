#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    This module is only available on Windows.
    author: Jacob Kosberg
"""

import os
import subprocess
import cv2

def runCMPMVS(workingDir):
    cmpmvsDir = "C:\\cmpmvs"
    sfmCommand = [os.path.join(cmpmvsDir, "visualSfM_CMPMVS.bat")]
    sfmCommand += [os.path.join(cmpmvsDir, "VisualSFM.exe")]
    sfmCommand += [os.path.join(cmpmvsDir, "CMPMVS.exe")]
    sfm = subprocess.Popen(sfmCommand + [workingDir], stdout=subprocess.PIPE)
    sfm.communicate()

def convertPngsToJpgs(inputPngs, outputDir):
    for imgpath in inputPngs:
        img = cv2.imread(imgpath)
        newfilename = os.path.splitext(os.path.basename(imgpath))[0] + ".jpg"
        outputPath = os.path.join(outputDir, newfilename)
        cv2.imwrite(outputPath, img)