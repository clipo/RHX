import sys
sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
import cv
import time

class Target:

   def __init__(self):
      self.capture = cv.CaptureFromCAM(0)
      cv.NamedWindow("Target", 1)

   def run(self):
      # Capture first frame to get size
      frame = cv.QueryFrame(self.capture)
      frame_size = cv.GetSize(frame)
      color_image = cv.CreateImage(cv.GetSize(frame), 8, 3)
      grey_image = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
      

      first = True

      while True:
         closest_to_left = cv.GetSize(frame)[0]
         closest_to_right = cv.GetSize(frame)[1]

         color_image = cv.QueryFrame(self.capture)

         # Smooth to get rid of false positives
         cv.Smooth(color_image, color_image, cv.CV_GAUSSIAN, 3, 0)

         
         # Convert the image to grayscale.
         cv.CvtColor(color_image, grey_image, cv.CV_RGB2GRAY)

         # Convert the image to black and white.
         #cv.Threshold(grey_image, grey_image, 70, 255, cv.CV_THRESH_BINARY)

         # Dilate and erode to get people blobs
         cv.Dilate(grey_image, grey_image, None, 18)
         cv.Erode(grey_image, grey_image, None, 10)
         maxradius=200
         minradius=100
         storage = cv.CreateMat(grey_image.width, 1, cv.CV_32FC3) 
         cv.HoughCircles(grey_image, storage, cv.CV_HOUGH_GRADIENT, 1, grey_image.height/4, 100, 40, minradius,maxradius)
         
         points = []
         Radius = 0
         x = 0
         y = 0
         i=0
         for i in range(storage.width):
            print(i)	
            if storage[i,2] >Radius:
               Radius = storage[i, 2]
               x = storage[i, 0]
               y = storage[i, 1]
               center=(x,y)
               print("circle x:", x,"y:", y,"radius:",Radius)
         else:
            print("no circle")
         cv.Circle(thresholded, center,Radius, (0, 0, 255), 3, 8, 0)
         cv.ShowImage( "result", grey_image)
         c = cv.WaitKey(7)
         if c==27: # Escape pressed
            False
            break

if __name__=="__main__":
    t = Target()
    t.run()