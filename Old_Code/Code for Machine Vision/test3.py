import sys
sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
from SimpleCV.Display import Display

mycam =VirtualCamera("picture.png","image")

#find the green ball
green_stuff = mycam().getImage().colorDistance(Color.GREEN)

green_blobs = green_channel.findBlobs()
#blobs are returned in order of area, smallest first

print "largest green blob at " + str(green_blobs[-1].x) + ", " + str( green_blobs[-1].y)
