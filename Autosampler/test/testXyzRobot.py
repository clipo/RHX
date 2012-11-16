
##Imports
import logging

import communication
from Tkinter import *
from tkMessageBox import *
from tkColorChooser import askcolor
from tkFileDialog import askopenfilename
import time
from datetime import datetime
from datetime import timedelta
import sys
sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
import os
import io
import re
import serial
from ctypes import *
from time import sleep
import DataReadWrite
import xyzRobot
import math

begin=0
end=20
test=0
passed=0
print "-------------------------------------------------------"
print "bumpYMotorRight( 10 ) "
xyzRobot.bumpYMotorRight(10)

print "-------------------------------------------------------"
print "getAbsoluteXPosition()"

pos=xyzRobot.getAbsoluteXPosition()
print "xpos: ",pos
test += 1
if pos>-1:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
print "getAbsoluteYPosition()"

pos=xyzRobot.getAbsoluteYPosition()
print "ypos: ",pos
test += 1
if pos>-1:
   print "PASS"
   passed += 1
else:
   print "FAIL"
   
print "-------------------------------------------------------"
print "getXZero()"
pos=xyzRobot.getXZero()
print "x sensor pad: ",pos
test += 1
if pos>-1:
   print "PASS"
   passed += 1
else:
   print "FAIL"

print "-------------------------------------------------------"
print "getYZero()"
pos=xyzRobot.getXZero()
print "y sensor pad: ",pos
test += 1
if pos>-1:
   print "PASS"
   passed += 1
else:
   print "FAIL"


while begin < end:
   print "-------------------------------------------------------"

   print "getTemperature()"
   temp=xyzRobot.getTemperature()
   print "Temperature:",temp
   test += 1
   if temp>0:
      print "PASS"
      passed += 1
   else:
      print "FAIL"
   begin += 1


print "-------------------------------------------------------"

print "getHumidity()"
humidity=xyzRobot.getHumidity()
print "Humidity:",humidity
test += 1
if humidity>0:
    print "PASS"
    passed += 1
else:
    print "FAIL"

print "-------------------------------------------------------"
print "now testing going to various sample locations and returning to 0 point"

positionList = [1,4,6,8,9]
startAXpos=xyzRobot.getAbsoluteXPosition()
startAYpos=xyzRobot.getAbsoluteYPosition()
print "Initial Home Position:", startAXpos, " ", startAYpos
startXpos = xyzRobot.getXPosition()
startYpos = xyzRobot.getYPosition()


for position in positionList:
    value = xyzRobot.goToSamplePosition(position)
    currentAXpos=xyzRobot.getAbsoluteXPosition()
    currentAYpos=xyzRobot.getAbsoluteYPosition()
    print "Absolute sample position: ", position, "is:", currentAXpos, " ", currentAYpos
    currentXpos = xyzRobot.getXPosition()
    currentYpos = xyzRobot.getYPosition()
    print "Sample position: ", position, "is:", currentXpos, " ", currentYpos

    print "going home"
    value = xyzRobot.resetMotorsToZeroPosition()
    currentAXpos=xyzRobot.getAbsoluteXPosition()
    currentAYpos=xyzRobot.getAbsoluteYPosition()
    print "Absolute position ", currentAXpos, " ", currentAYpos
    currentXpos = xyzRobot.getXPosition()
    currentYpos = xyzRobot.getYPosition()
    diffAX = startAXpos - currentAXpos
    diffAY = startAYpos - currentAYpos
    print "Absolute Drift: ", diffAX, " ", diffAY
    diffX = startXpos - currentXpos
    diffY = startYpos - currentYpos
    print "Drift: ", diffX, " ", diffY
    print "----------------------------------------------"

print "going to balance..."
value=xyzRobot.goToOutsideBalanceFromOutside()
currentAXpos=xyzRobot.getAbsoluteXPosition()
currentAYpos=xyzRobot.getAbsoluteYPosition()
print "Absolute Position", currentAXpos, " ", currentAYpos
print "Position", xyzRobot.getXPosition(), " ", xyzRobot.getYPosition()

print "going home"
value = xyzRobot.resetMotorsToZeroPosition()
currentAXpos=xyzRobot.getAbsoluteXPosition()
currentAYpos=xyzRobot.getAbsoluteYPosition()
print "Absolute position at ", currentAXpos, " ", currentAYpos
print "Position", xyzRobot.getXPosition(), " ", xyzRobot.getYPosition()
diffAX = startAXpos - currentAXpos
diffAY = startAYpos - currentAYpos
print "Absolute Drift: ", diffAX, " ", diffAY
diffX = startXpos - xyzRobot.getXPosition()
diffY = startYpos - xyzRobot.getYPosition()
print " Drift: ", diffX, " ", diffY
print "----------------------------------------------------"
print "going to balance..."
value=xyzRobot.goToOutsideBalanceFromOutside()
currentAXpos=xyzRobot.getAbsoluteXPosition()
currentAYpos=xyzRobot.getAbsoluteYPosition()
print "Absolute Position", currentAXpos, " ", currentAYpos
print "Position", xyzRobot.getXPosition(), " ", xyzRobot.getYPosition()

print "going home"
value = xyzRobot.resetMotorsToZeroPosition()
currentAXpos=xyzRobot.getAbsoluteXPosition()
currentAYpos=xyzRobot.getAbsoluteYPosition()
print "Absolute position at ", currentAXpos, " ", currentAYpos
print "Position", xyzRobot.getXPosition(), " ", xyzRobot.getYPosition()
diffAX = startAXpos - currentAXpos
diffAY = startAYpos - currentAYpos
print "Absolute Drift: ", diffAX, " ", diffAY
diffX = startXpos - xyzRobot.getXPosition()
diffY = startYpos - xyzRobot.getYPosition()
print " Drift: ", diffX, " ", diffY

print "----------------------------------------------------"
print "going to balance..."
value=xyzRobot.goToOutsideBalanceFromOutside()
currentAXpos=xyzRobot.getAbsoluteXPosition()
currentAYpos=xyzRobot.getAbsoluteYPosition()
print "Absolute Position", currentAXpos, " ", currentAYpos
print "Position", xyzRobot.getXPosition(), " ", xyzRobot.getYPosition()

print "going home"
value = xyzRobot.resetMotorsToZeroPosition()
currentAXpos=xyzRobot.getAbsoluteXPosition()
currentAYpos=xyzRobot.getAbsoluteYPosition()
print "Absolute position at ", currentAXpos, " ", currentAYpos
print "Position", xyzRobot.getXPosition(), " ", xyzRobot.getYPosition()
diffAX = startAXpos - currentAXpos
diffAY = startAYpos - currentAYpos
print "Absolute Drift: ", diffAX, " ", diffAY
diffX = startXpos - xyzRobot.getXPosition()
diffY = startYpos - xyzRobot.getYPosition()
print " Drift: ", diffX, " ", diffY