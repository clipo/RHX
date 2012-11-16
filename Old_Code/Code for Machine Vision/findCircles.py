#!/usr/bin/python
# -*- coding: utf-8 -*-
import cv
from threading import Thread
#import serial

# create capture device
# start capturing form webcam
capture = cv.CreateCameraCapture(0)
if not capture:
   print "Could not open webcam"
   sys.exit(1)
    
frame = cv.QueryFrame(capture)

size=cv.GetSize(frame)

hsv_frame = cv.CreateImage(size, cv.IPL_DEPTH_8U, 3)
thresholded = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
thresholded2 = cv.CreateImage(size, cv.IPL_DEPTH_8U, 1)
#sv_min = cv.Scalar(0, 0, 0, 0)
#hsv_max = cv.Scalar(25, 1, 0, 0)
#hsv_min2 = cv.Scalar(200, 200, 255, 0)
#hsv_max2 = cv.Scalar(255, 255, 255, 0)
hsv_min = cv.Scalar(0, 50, 170, 0)
hsv_max = cv.Scalar(10, 180, 256, 0)
hsv_min2 = cv.Scalar(170, 50, 170, 0)
hsv_max2 = cv.Scalar(256, 180, 256, 0)

#storage = cv.CreateMemStorage(0)
storage = cv.CreateMat(frame.width, 1, cv.CV_32FC3)  
#CV windows
window=cv.NamedWindow( "Camera", cv.CV_WINDOW_AUTOSIZE );

   
def TrackBall(i):
   t = Thread(target=TrackBallThread, args=(i,))
   t.start()

def TrackBallThread(num_of_balls):
   
   while 1:
      # get a frame from the webcam
      frame = cv.QueryFrame(capture)
      print "grabbing frame..."
      if frame is not None:
         # convert to HSV for color matching
         # as hue wraps around, we need to match it in 2 parts and OR together
         cv.CvtColor(frame, hsv_frame, cv.CV_BGR2HSV)
         cv.InRangeS(hsv_frame, hsv_min, hsv_max, thresholded)
         cv.InRangeS(hsv_frame, hsv_min2, hsv_max2, thresholded2)
         cv.Or(thresholded, thresholded2, thresholded)
         # pre-smoothing improves Hough detector
         cv.Smooth(thresholded, thresholded, cv.CV_GAUSSIAN, 9, 9)
         cv.HoughCircles(thresholded, storage, cv.CV_HOUGH_GRADIENT, 2, thresholded.height/4, 100, 40, 20, 200)
         # find largest circle
         maxRadius = 0
         x = 0
         y = 0
         found = False
         for i in range(storage.width):
            circle = storage[i]
            if circle[2]   >  maxRadius:
               found = True
               maxRadius = circle[2]
               x = circle[0]
               y = circle[1]
         cvShowImage( "Camera", frame );
      
         if found:
            print "circle detected at position:",x, ",", y, " with radius:", maxRadius
            if x>420:
               # need to pan right
               #servoPos += 5
               #servoPos = min(140, servoPos)
               #servo(2, servoPos)
               ttt=1
            else:
               #elif x < 220:
               mmm=1
               #servoPos -= 5
               #servoPos = max(40, servoPos)
               #servo(2, servoPos)
               #print "servo position:", servoPos
         else:
            print "no ball"





TrackBallThread(1)
