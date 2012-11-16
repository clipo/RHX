#!/usr/bin/python
import time, webbrowser
import sys
sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")


import cv #Import functions from OpenCV
cv.NamedWindow('a_window', cv.CV_WINDOW_AUTOSIZE)
image=cv.LoadImage('picture.png', cv.CV_LOAD_IMAGE_COLOR) #Load the image
font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 3, 8) #Creates a font
x = 30
y = 50
#cv.PutText('a_window',"Hello World!!!", (x,y),font, 255) #Draw the text
cv.ShowImage('a_window', image) #Show the image
time.sleep(5)
cv.SaveImage('image.png', image) #Saves the image