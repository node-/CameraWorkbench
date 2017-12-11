#!/usr/bin/python

"""
author: Jacob Kosberg
"""

import cv2
import sys
import numpy as np

def getCenter(bbox):
    return (int(bbox[0] + bbox[2]/2), int(bbox[1] + bbox[3]/2))

def main():
    # Instead of MIL, you can also use
    # BOOSTING, KCF, TLD, MEDIANFLOW or GOTURN
     
    tracker = cv2.TrackerKCF_create()

    # Read video
    video = cv2.VideoCapture(sys.argv[1])
 
    # Exit if video not opened.
    if not video.isOpened():
        print "Could not open video"
        sys.exit()
 
    # Read first frame.
    ok, frame = video.read()
    if not ok:
        print 'Cannot read video file'
        sys.exit()

    
    frames = []
    while True:
        ok, img = video.read()
        if not ok:
            break
        img = cv2.Canny(img, 200, 300)
        frames.append(cv2.cvtColor(img, cv2.COLOR_GRAY2RGB))
    #frames = list(reversed(frames))
    frame = frames[0]

    # Define an initial bounding box
    #bbox = (1160,396,98,16)
 
    # Uncomment the line below to select a different bounding box
    bbox = cv2.selectROI(frame, False)
    print bbox

    # Initialize tracker with first frame and bounding box
    ok = tracker.init(frame, bbox)
 
    center_i = np.array(getCenter(bbox), dtype=int)
    displacements = []
    for frame in frames:

        center_f = np.array(getCenter(bbox), dtype=int)
        displacements.append(center_f - center_i)

        # Update tracker
        ok, bbox = tracker.update(frame)
 
        # Draw bounding box
        if ok:
            p1 = (int(bbox[0]), int(bbox[1]))
            p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
            cv2.rectangle(frame, p1, p2, (0,0,255))
            cv2.circle(frame, getCenter(bbox), 4, (0,0,255), -1)
 
        # Display result
        cv2.imshow("Tracking", frame)
 
        # Exit if ESC pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27 : break

    #cv2.line(frame,center_i,center_f,(0,0,255),2)
    #cv2.imshow("Final", frame)

    print "Initial center: " + str(center_i)
    print "Final center: " + str(center_f)
    print "Displacement: " + str(np.linalg.norm(center_f-center_i))

if __name__ == "__main__":
    main()