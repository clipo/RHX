import cv

#cv.NamedWindow("camera", 1)
#capture = cv.CaptureFromCAM(0)

img = cv.LoadImageM("circles.jpg", 1)
#img = cv.QueryFrame(capture)
gray = cv.CreateImage(cv.GetSize(img), 8, 1)

edges = cv.CreateImage(cv.GetSize(img), 8, 1)

cv.CvtColor(img, gray, cv.CV_BGR2GRAY)
cv.Canny(gray, edges, 50, 200, 3)
cv.Smooth(gray, gray, cv.CV_GAUSSIAN, 9, 9)

cv.ShowImage("gray", gray)
storage = cv.CreateMat(1, 2, cv.CV_32FC3)

#This is the line that throws the error
cv.HoughCircles(edges, storage, cv.CV_HOUGH_GRADIENT, 2, gray.height/4, 200, 100)
Radius = 0
x = 0
y = 0
print "storage width:", storage.width
for i in range(storage.width):

   print i
   if storage[i,2] >Radius:
      Radius = storage[i, 2]
      x = storage[i, 0]
      y = storage[i, 1]
      center=(x,y)
      print x,y,Radius
   else:
      print "no circle"

#cv.Circle(thresholded, center,Radius, (0, 0, 255), 3, 8, 0)

#cv.ShowImage("camera", img)
