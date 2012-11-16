__author__ = 'clipo'
#!/usr/bin/env python


#Basic imports
from ctypes import *
import sys
from time import sleep
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, EncoderPositionChangeEventArgs, InputChangeEventArgs
from Phidgets.Devices.Stepper import Stepper

# constants
XPOSITION=0  # X axis
YPOSITION=0  # Y axis
ZPOSITION=0

## set to 1 if you want to debug
DEBUG = 0

class Motors:

   #Create the stepper objects
   try:
      xstepper = Stepper()
   except RuntimeError as e:
      print("Runtime Exception: %s" % e.details)
      print("Exiting....")
      exit(1)

   try:
      ystepper = Stepper()
   except RuntimeError as e:
      print("Runtime Exception: %s" % e.details)
      print("Exiting....")
      exit(1)

   try:
      zstepper = Stepper()
   except RuntimeError as e:
      print("Runtime Exception: %s" % e.details)
      print("Exiting....")
      exit(1)

   def getXPosition(self):
      return XPOSITION

   def getXPosition(self):
      return YPOSITION

   def getZPosition(self):
      return ZPOSITION

   def getPositions(self):
      return XPOSITION,YPOSITION,ZPOSITION

   def setXZero(self):
      XPOSITION=0
      self.xstepper.setCurrentPosition(0,0)

   def setYZero(self):
      YPOSITION=0
      self.ystepper.setCurrentPosition(0,0)

   def setZZero(self):
      ZPOSITION=0
      self.zstepper.setCurrentPosition(0,0)

   def setXYZZero(self):
      self.setXZero()
      self.setYZero()
      self.setZZero()

   def close(self):
      try:
         self.xstepper.closePhidget()
      except PhidgetException as e:
         print("Phidget Error %i: %s" % (e.code, e.details))
      try:
         self.ystepper.closePhidget()
      except PhidgetException as e:
         print("Phidget Error %i: %s" % (e.code, e.details))
      try:
         self.zstepper.closePhidget()
      except PhidgetException as e:
         print("Phidget Error %i: %s" % (e.code, e.details))
      exit(1)

   def setXPosition(self,location):
      self.xstepper.setCurrentPosition(0,location)

   def setYPosition(self,location):
      self.ystepper.setCurrentPosition(0,location)

   def setZPosition(self,location):
      self.zstepper.setCurrentPosition(0,location)

   def setXYZPositions(self,X,Y,Z):
         self.xstepper.setCurrentPosition(0,X)
         self.ystepper.setCurrentPosition(0,Y)
         self.zstepper.setCurrentPosition(0,Z)

   def moveXToPosition(pos):
      try:
         xstepper.setEngaged( 0,True)
         xstepper.setTargetPosition(0,pos)
         while xstepper.getStopped(0) !=STOPPED:
            pass
         sleep(2)
         xstepper.setEngaged(0,False)
      except PhidgetException as e:
         logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         sys.exit()
      XPOSITION=pos
      return pos

   def moveYToPosition(pos):
      try:
         ystepper.setEngaged( 0,True)
         ystepper.setTargetPosition(0,pos)
         while ystepper.getStopped(0) !=STOPPED:
            pass
         sleep(2)
         ystepper.setEngaged(0,False)
      except PhidgetException as e:
         logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         sys.exit()
      YPOSITION=pos
      return pos

   def moveZToPosition(pos):
      try:
         zstepper.setEngaged( 0,True)
         zstepper.setTargetPosition(0,pos)
         while ystepper.getStopped(0) !=STOPPED:
            pass
         sleep(2)
         zstepper.setEngaged(0,False)
      except PhidgetException as e:
         logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         sys.exit()
      ZPOSITION=pos
      return pos

   def bumpZMotorDown(bump):
      logger.debug("bumpZMotorDown")
      move = int(zstepper.getCurrentPosition(0))+int(bump)
      zstepper.setEngaged(0,True)
      try:
         zstepper.setTargetPosition(0,move)
         while zstepper.getStopped(0) != STOPPED and atZZero() == "FALSE":
            print "continuing.. not stopped and not true"
            pass
         sleep(1)
      except PhidgetException as e:
         logger.critical("Servo Z: Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         sys.exit(1)
      print "NEW POSITION:  getCurrentPosition for Z:  ", zstepper.getCurrentPosition(0)
      setZMotorPosition(move)
      print "now setting position to its new location... move"
      zstepper.setEngaged(0,False)
      return move




   #### X
   try:
      xstepper.openPhidget()
   except PhidgetException as e:
      print("Phidget Error %i: %s" % (e.code, e.details))
      exit(1)
   try:
      xstepper.waitForAttach(10000)
   except PhidgetException as e:
      print("Phidget Error %i: %s" % (e.code, e.details))
      try:
         xstepper.closePhidget()
      except PhidgetException as e:
         print("Phidget Error %i: %s" % (e.code, e.details))
         exit(1)
      exit(1)

   ### Y
   try:
      ystepper.openPhidget()
   except PhidgetException as e:
      print("Phidget Error %i: %s" % (e.code, e.details))
      exit(1)

   try:
      ystepper.waitForAttach(10000)
   except PhidgetException as e:
      print("Phidget Error %i: %s" % (e.code, e.details))
      try:
         ystepper.closePhidget()
      except PhidgetException as e:
         print("Phidget Error %i: %s" % (e.code, e.details))
         exit(1)
      exit(1)

   ### Z
   try:
      ystepper.openPhidget()
   except PhidgetException as e:
      print("Phidget Error %i: %s" % (e.code, e.details))
      exit(1)
   try:
      zstepper.waitForAttach(10000)
   except PhidgetException as e:
      print("Phidget Error %i: %s" % (e.code, e.details))
      try:
         zstepper.closePhidget()
      except PhidgetException as e:
         print("Phidget Error %i: %s" % (e.code, e.details))
         exit(1)
      exit(1)

   xstepper.setCurrentPosition(0,0)
   ystepper.setCurrentPosition(0,0)
   zstepper.setCurrentPosition(0,0)

### main body

if DEBUG is 1:
   myLocation = Location()

   #while True:
   print "X Location: ", myLocation.getXPosition()
   print "Y Location: ", myLocation.getYPosition()
   ##   sleep(1)

   print "Set X Location to 100: "
   myLocation.setXPosition(100)

   print "Set Y Location to 1000: "
   myLocation.setYPosition(1000)

   print "X Location: ", myLocation.getXPosition()
   print "Y Location: ", myLocation.getYPosition()


   myLocation.close()

