#!/usr/bin/env python

"""
Modified from code posted here: http://forums.pimoroni.com/t/pan-tilt-hat-repo/3402/11
"""
import numpy as np
import cv2
import os
from pantilthat import *

os.system('sudo modprobe bcm2835-v4l2')

cascade = cv2.CascadeClassifier('./data/haarcascades/haarcascade_frontalface_default.xml')
#cascade = cv2.Load('/usr/share/opencv/lbpcascades/lbpcascade_frontalface.xml')

cam_pan = 90
cam_tilt = 45

# Turn the camera to the default position
pan(cam_pan-90)
tilt(cam_tilt-90)
light_mode(WS2812)

def lights(r,g,b,w):
    for x in range(18):
        set_pixel_rgbw(x,r if x in [3,4] else 0,g if x in [3,4] else 0,b,w if x in [0,1,6,7] else 0)
    show()

lights(0,0,0,50)

min_size = (15, 15)
image_scale = 5
haar_scale = 1.2
min_neighbors = 2
haar_flags = cv2.CASCADE_DO_CANNY_PRUNING

cap = cv2.VideoCapture(0)
# cv2.NamedWindow("Tracker", 1)
 
if cap:
    frame_copy = None
    
while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if frame is None:
        cv2.waitKey(0)
        break
    
   
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # small_img = cv2.CreateImage((cv2.Round(frame.width / image_scale),
    #                cv2.Round (frame.height / image_scale)), 8, 1)
 
    # convert color input image to grayscale
 
    # scale input image for faster processing
    # cv2.Resize(gray, small_img, cv2.CV_INTER_LINEAR)
 
    # cv2.EqualizeHist(small_img, small_img)

    midFace = None
 
    if(cascade):
        # HaarDetectObjects takes 0.02s
        faces = cascade.detectMultiScale(gray, scaleFactor = 1.5, minNeighbors = 5)
        if faces:
            lights(50 if len(faces) == 0 else 0, 50 if len(faces) > 0 else 0,0,50)

            for ((x, y, w, h), n) in faces:
                # the input to cv2.HaarDetectObjects was resized, so scale the
                # bounding box of each face and convert it to two CvPoints
                pt1 = (int(x * image_scale), int(y * image_scale))
                pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
                cv2.Rectangle(frame, pt1, pt2, cv2.RGB(100, 220, 255), 1, 8, 0)
                # get the xy corner co-ords, calc the midFace location
                x1 = pt1[0]
                x2 = pt2[0]
                y1 = pt1[1]
                y2 = pt2[1]

                midFaceX = x1+((x2-x1)/2)
                midFaceY = y1+((y2-y1)/2)
                midFace = (midFaceX, midFaceY)

                offsetX = midFaceX / float(frame.width/2)
                offsetY = midFaceY / float(frame.height/2)
                offsetX -= 1
                offsetY -= 1

                cam_pan -= (offsetX * 5)
                cam_tilt += (offsetY * 5)
                cam_pan = max(0,min(180,cam_pan))
                cam_tilt = max(0,min(180,cam_tilt))

                print(offsetX, offsetY, midFace, cam_pan, cam_tilt, frame.width, frame.height)

                pan(int(cam_pan-90))
                tilt(int(cam_tilt-90))
                break
                
    # Display the resulting frame
    cv2.imshow('Tracker',frame)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

# When everything done, release the capture
cv2.DestroyWindow("Tracker")
