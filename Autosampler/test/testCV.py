import sys
sys.path.append("C:\\opencv\\build\\python\\2.7\\")

#import cv
from cv import *
#from highgui import *

NamedWindow("Example2", CV_WINDOW_AUTOSIZE)
capture = CaptureFromCAM(2)
loop = True
while(loop):
   frame = QueryFrame(capture)
   if (frame == None):
      break;
   ShowImage("Example2", frame)
   char = WaitKey(33)
   if (char != -1):
      if (ord(char) == 27):
         loop = False

#cvReleaseCapture(capture)
DestroyWindow("Example2")

#cv.NamedWindow("camera", 1)
#capture = cv.CaptureFromCAM(1)

#while True:
#   img = cv.QueryFrame(capture)
#   cv.ShowImage("camera", img)
#   if cv.WaitKey(10) == 27:
#      break
#cv.DestroyWindow("camera")


NamedWindow("window", CV_WINDOW_AUTOSIZE)
camera_index = 1
capture = CaptureFromCAM(camera_index)

def repeat():
   global capture #declare as globals since we are assigning to them now
   global camera_index
   frame = QueryFrame(capture)
   ShowImage("window", frame)
   c = WaitKey(10)
   if(c=="n"): #in "n" key is pressed while the popup window is in focus
      camera_index += 1 #try the next camera index
      capture = CaptureFromCAM(camera_index)
      if not capture: #if the next camera index didn't work, reset to 0.
         camera_index = 0
         capture = CaptureFromCAM(camera_index)

while True:
   repeat()

   __author__ = 'clipo'
