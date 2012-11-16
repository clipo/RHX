

#!/usr/bin/python
import cv
from cv import *
from threading import Thread
#import serial

class RobotVision:
   size=()
   def InitBallTracking(self):
      global size
      global hsv_frame
      global thresholded
      global thresholded2
      global hsv_min
      global hsv_max
      global hsv_min2
      global hsv_max2
      global capture
      global storage
      print "Initializing ball Tracking"
      size = (640, 480)
      hsv_frame = cv.CreateImage(size, IPL_DEPTH_8U, 3)
      thresholded = cv.CreateImage(size, IPL_DEPTH_8U, 1)
      thresholded2 = cv.CreateImage(size, IPL_DEPTH_8U, 1)
      hsv_min = cv.Scalar(0, 50, 170, 0)
      hsv_max = cv.Scalar(10, 180, 256, 0)
      hsv_min2 = cv.Scalar(170, 50, 170, 0)
      hsv_max2 = cv.Scalar(256, 180, 256, 0)
      storage = cv.CreateMemStorage(0)
      # start capturing form webcam
      capture = cv.CreateCameraCapture(-1)
      print "starting to capture"
      if not capture:
         print "Could not open webcam"
         sys.exit(1)
      #cv. windows
      cv.NamedWindow( "Camera", CV_WINDOW_AUTOSIZE );
   def TrackBall(self,i):
      t = Thread(target=self.TrackBallThread, args=(i,))
      t.start()
   def TrackBallThread(self,num_of_balls):
      global size
      global hsv_frame
      global thresholded
      global thresholded2
      global hsv_min
      global hsv_max
      global hsv_min2
      global hsv_max2
      global capture
      while 1:
         # get a frame from the webcam
         #frame = cv.QueryFrame(capture)
         hsv_frame=cv.LoadImageM("circles.jpg",1)   
         if hsv_frame is not None:
            # convert to HSV for color matching
            # as hue wraps around, we need to match it in 2 parts and OR together
            
            #cv.CvtColor(frame, hsv_frame, CV_BGR2HSV)
            #cv.InRangeS(hsv_frame, hsv_min, hsv_max, thresholded)
            #cv.InRangeS(hsv_frame, hsv_min2, hsv_max2, thresholded2)
            #cv.Or(thresholded, thresholded2, thresholded)
            # pre-smoothing improves Hough detector
            cv.Smooth(thresholded, thresholded, CV_GAUSSIAN, 9, 9)
            circles = cv.HoughCircles(thresholded, storage, CV_HOUGH_GRADIENT, 2, thresholded.height/4, 100, 40, 20, 200)
            # find largest circle
            maxRadius = 0
            x = 0
            y = 0
            found = False
            for i in range(circles.total):
               circle = circles[i]
               if circle[2] > maxRadius:
                  found = True
                  maxRadius = circle[2]
                  x = circle[0]
                  y = circle[1]
            cv.ShowImage( "Camera", frame );
            if found:
               print "ball detected at position:",x, ",", y, " with radius:", maxRadius
               if x > 420:
                  # need to pan right
                  servoPos += 5
                  servoPos = min(140, servoPos)
                  servo(2, servoPos)
               elif x > 220:
                  servoPos -= 5
                  servoPos = max(40, servoPos)
                  servo(2, servoPos)
               print "servo position:", servoPos
            else:
               print "no ball"
               
if __name__ == "__main__":
    robot= RobotVision()
    robot.InitBallTracking()
    robot.TrackBall(3)
 