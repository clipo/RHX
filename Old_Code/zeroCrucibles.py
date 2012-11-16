
## Crucible weighing, etc.

import serial
import time
from datetime import datetime
from datetime import timedelta
import msvcrt 
import os, sys
from select import select
import signal
import sys
import random
import csv
import re
import xyzRobot
import DataReadWrite

def average(myList):
   newList=[]
   for n in myList[:]:
      newList.append(float(n))
      
   summy = sum(newList)
   averages = float(summy)/len(newList)
   return averages

def std(myList):
   newList=[]
   for n in myList[:]:
      newList.append(float(n))
   summy = sum(newList)
   a = float(summy)/len(newList)
   r =len(newList)
   b = []
   for n in range(r-1):
      if newList[n] > a:
         b.append((newList[n] - a)**2)
      if newList[n] < a:
         b.append((a - newList[n])**2)
   SD = (float(sum(b)/r))**0.5 
   return SD

status="Initialize"

print "There are three major steps in doing an RHX run.  "
print "The first is to set up the crucibles and get their empty weights."
print "This script (zeroCrucibles) does this job. "  
print "Note that this step will produce a runID -- the index number "
print "that links runs to samples to measurements and crucibles. "
print "You will want to write this number down as you will be asked for it "
print "in the subsequent setps (preFire.py and postFire.py) "


   

# get the weight of the crucibles - empty. 
setInitials=""
while setInitials == "":
   setInitials = raw_input( 'Researcher Initials (e.g., CPL): ')

numberOfSamples=""
while numberOfSamples=="":
   numberOfSamples = raw_input('How many crucibles? (e.g., 1,5,10): ')
   
duration=""
while duration=="":
   duration=raw_input('How long to measure each crucible (minutes, e.g., 60): ')

(xpos,ypos) = DataReadWrite.getLastPosition()

print "-------------------------------------------"
print "According to the database, the arm is current at X: ",xpos , " and Y: ",ypos
newposition=""
while newposition<>"Y" and newposition<>"N":
   newposition = raw_input("Reset coordinates to 0,0? (Y/N)")
   
if newposition == "Y":
   DataReadWrite.setPosition(0,0)

newposition=""
print "Reset coordinates of motors to X: ",xpos, "Y: ",ypos
while newposition<>"Y" and newposition<>"N":
   newposition = raw_input("Y/N: ")
   
if newposition == "Y":
   xyzRobot.resetCoordinates(xpos,ypos)

resetArm=""
while resetArm<>"Y" and resetArm<>"N":
   resetArm=raw_input("Attempt to move back to its 0,0 point? (Y/N)")

if resetArm=="Y":
   xyzRobot.physicallyResetArm()

xyzRobot.resetValuesToZero()   
print "Now going to move and measure each of the crucibles... "   
   
runID = xyzRobot.weighAllCrucibles(setInitials,numberOfSamples,2,duration)

print "Done!  The next script to run will be preFire.py "
print "The runID is ", runID, ". Save this number. "
