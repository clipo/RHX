__author__ = 'Archy'
from SimpleCV import *

cam = Camera(2)
img = cam.getImage()
img.show()
img.findBlobs().show(autocolor=True)
