import sys
#sys.path.append("C:\\Users\\Eamon Gaffney\\Downloads\\opencv\\build\\python\\2.7") ##cv refuses to install properly for me, this allows python to find the library
from cv import *
from time import sleep

##class CaptureError(Exception):
##    def __init__(self, is_file):
##        self.f = is_file
##
##    def __str__(self):
##        return 'CaptureError: the ' + 'file ' if self.f else 'camera ' + 'could not be opened successfully'

Debug=False
## height = 240
## width = 320

class crucible_tracker():
   ##supply either filename or device, which is device number
   ##if debeg is true, the video will be played with the circles that have been found
   ##center is x,y tuple
   def __init__(self, center, filename=False, device=0, debug=False):
   ##        if filename: ##filename defaults to false if none is provided, signifying that a camera feed will be used instead
   ##            if VideoCaptrue.open(filename): ##raises exception if opening fails
   ##                vc = VideoCapture(filename)
   ##            else:
   ##                raise CaptrueError(True)
   ##        else:
   ##            if VideoCaptrue.open(device):
   ##                vc = VideoCapture(device)
   ##            else:
   ##                raise CaptrueError(False)
      if filename:
         self.vc = CaptureFromFile(filename)
      else:
         self.vc = CreateCameraCapture(device)
         #self.vc = CaptureFromCAM(device)
      self.debug = debug
      self.window = NamedWindow('window')
      self.center = center

   def show_image(self, image, delay=83):
      ShowImage('window', image)
      WaitKey(delay)

   def get_relative_position(self, frame, debug=False):
      gframe = CreateImage(GetSize(frame), IPL_DEPTH_8U, 1)
      CvtColor(frame, gframe, CV_BGR2GRAY)
      #Threshold(gframe, gframe, 200, 255, CV_THRESH_BINARY)
      #ShowImage('window',gframe)
      circles = CreateMat(1, 10000, CV_32FC3)
      HoughCircles(gframe, circles, CV_HOUGH_GRADIENT, 2, 100)
      ##last two params are thresholds, first is stricter with higher values, second
      ##is stricter with lower ones; 2, 100 worked with the cup but failed on the pictures
      ##        self.show_image(gframe)
      ##        wcirc = CloneImage(frame)
      ##        for i in range(circles.cols):
      ##            a = circles[0, i]
      ##            Circle(wcirc, Point_(a[0], a[1]), a[2], CvScalar(255, 0, 0, 0))
      ##        ShowImage('window', wcirc)
      ##turns matrix into native python list of tuples for better data analysis
      circlist = []
      for i in range(circles.cols):
         circlist.append(circles[0, i])
      circlist = filter(lambda a: a[2] > 52, filter(lambda a: a[2] < 56, circlist)) ##filter by size
      if debug: ##draw circles
         if len(circlist) >= 1:
            for i in circlist:
               Circle(frame, (int(i[0]), int(i[1])), int(i[2]),
                      CV_RGB(0, 255, 0) if len(circlist) == 1 else CV_RGB(255, 0, 0), 4)
               Circle(frame, (int(i[0]), int(i[1])), 3,
                      CV_RGB(0, 255, 0) if len(circlist) == 1 else CV_RGB(255, 0, 0), 5)
         self.show_image(frame, 1500)
      if len(circlist):
         #print "radius: ", circlist[0][2]
         return circlist[0][0] - self.center[0], circlist[0][1] - self.center[1]

   def analyze_video_stream(self):
      position = (0, 0)
      while True: ##a bit hackish, but cv leaves me few choices
         img = QueryFrame(self.vc)
         #ShowImage('robot view',frame)
         position = self.get_relative_position(img, self.debug)
         #sleep(1)
         print position

   def analyze_video_frame(self):
      img = QueryFrame(self.vc)
      if Debug: ## print the height/width of image frame
         print "height", img.height, "width", img.width
      #ShowImage('robot view',frame)
      position = self.get_relative_position(img, self.debug)
      return position



##Testing code

##f = LoadImage('C:\\Users\\Eamon Gaffney\\Downloads\\0001.jpg')
##g = LoadImage('C:\\Users\\Eamon Gaffney\\Downloads\\0002.jpg')
##h = LoadImage('C:\\Users\\Eamon Gaffney\\Downloads\\0003.jpg')
##i = LoadImage('C:\\Users\\Eamon Gaffney\\Downloads\\0004.jpg')
##video = 'C:\\Users\\Eamon Gaffney\\Downloads\\robot.avi'

if Debug:
   t = crucible_tracker((160, 120), debug=True, device=0)
   position = (0, 0)
   while True:
      position = t.analyze_video_frame()
      sleep(1)
      print position

#print(t.get_relative_position(f, True))
#print(t.get_relative_position(g, True))
#print(t.get_relative_position(h, True))
#print(t.get_relative_position(i, True))
