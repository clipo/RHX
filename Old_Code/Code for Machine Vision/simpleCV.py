
from SimpleCV.base import *
from SimpleCV.Camera import *
from SimpleCV.Color import *
from SimpleCV.Detection import *   
from SimpleCV.Features import *
from SimpleCV.ImageClass import *
from SimpleCV.Stream import *
from SimpleCV.Font import *
from SimpleCV.ColorModel import *
from SimpleCV.DrawingLayer import *
from SimpleCV.BlobMaker import *

#find the green ball
green_stuff = simpleCV.Camera().getImage().colorDistance(Color.GREEN)

green_blobs = simpleCV.green_channel.findBlobs()
#blobs are returned in order of area, smallest first

print "largest green blob at "
print "X: ", str(green_blobs[-1].x)
print "Y: ",str( green_blobs[-1].y)
