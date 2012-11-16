# Filename: xyzRobot.py

#Basic imports
import logging
from ctypes import *
import os
import io
import serial
import sys
from time import sleep
import sched, time
from datetime import datetime
from datetime import timedelta
import msvcrt 
import os, sys
from Tkinter import *
from numpy import *
import math


## get the set of connections for reading the balance, etc.
import DataReadWrite
#import crucible_tracker

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs,OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Devices.Stepper import Stepper
from Phidgets.Devices.AdvancedServo import AdvancedServo
from Phidgets.Devices.Servo import ServoTypes
from Phidgets.Devices.InterfaceKit import InterfaceKit

## logging setup
logger=logging.getLogger("startRHX.xyzRobot")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('rhx.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
   

## CONSTANTS ###########################

# values of the infrared sensor channels
XDISTANCE=2
YDISTANCE=3

COUNTS_FOR_STATS=3

# Absolute Positions of Zero, Zero
MINIMUM_X_VALUE  = 0
MINIMUM_Y_VALUE = 0

## Stepper Motor Numbers
XMOTOR=0
YMOTOR=2

## Advanced Servo
ZMOTOR=0
GRIPPER=1

X=0
Y=1

STOPPED=1
MOVING=0

## remember the first position is 0! not a crucible ##

# This is the relative position from the uppermost Z axis point (i.e., how far down to lower the arm)
#DOWN_SAMPLE_POSITION = 93
#DOWN_BALANCE_POSITION_DROPOFF = 39
#DOWN_BALANCE_POSITION_PICKUP = 39

UP_SAMPLE_POSITION=0
UP_BALANCE_POSITION=0

#spaces betwen sample locations going along the length of the sampler (horizontal)
HORIZONTAL_SPACING = -350

#space between sample locations going away from the sampler (vertical)
VERTICAL_SPACING = 400

#how much to move in a "bump"
BUMP=10

# coordinates for the gripper position
GRIPPER_CLOSED = 80
GRIPPER_OPEN = 0

COUNTS_FOR_STATS = 3

def getStepper():
   return stepper

def getAdvancedServo():
   return advancedServo

## tracker is the object that we use to track the crucible via the webcam
### tracker = crucible_tracker.crucible_tracker((160, 120), debug=True, device=0)
#########################################################
###Event Handler Callback Functions
#Stepper Callbacks
def StepperAttached(e):
   attached = e.device
   logger.debug("Stepper %d Attached!" % (attached.getSerialNum()))

def StepperDetached(e):
   detached = e.device
   logger.debug("Stepper %d Detached!" % (detached.getSerialNum()))

def StepperError(e):
   source = e.device
   logger.debug("Stepper %d: Phidget Error %d: %s" % (source.getSerialNum(), e.eCode, e.description))

def StepperCurrentChanged(e):
   source = e.device
   logger.debug("Stepper %i: Motor %d -- Current Draw: %6f" % (source.getSerialNum(), e.index, e.current))

def StepperInputChanged(e):
   source = e.device
   logger.debug("Stepper %i: Input %d -- State: %s" % (source.getSerialNum(), e.index, e.state))

def StepperPositionChanged(e):
   source = e.device
   logger.debug("Stepper %i: Motor %d -- Position: %f" % (source.getSerialNum(), e.index, e.position))

def StepperVelocityChanged(e):
   source = e.device
   logger.debug("Stepper %i: Motor %d -- Velocity: %f" % (source.getSerialNum(), e.index, e.velocity))

#Servo Callbacks
def Attached(e):
   attached = e.device
   logger.debug("Servo %d Attached!" % (attached.getSerialNum()))

def Detached(e):
   detached = e.device
   logger.debug("Servo %d Detached!" % (detached.getSerialNum()))

def Error(e):
   source = e.device
   logger.error("Phidget Error %i: %d %s" % (source.getSerialNum(), e.eCode, e.description))

def CurrentChanged(e):
   global currentList
   currentList[e.index] = e.current

def PositionChanged(e):
   source = e.device
   logger.debug("AdvancedServo %i: Motor %i Position: %f - Velocity: %f - Current: %f" % (source.getSerialNum(), e.index, e.position,velocityList[e.index], currentList[e.index]))
   if advancedServo.getStopped(e.index) == True:
      logger.debug("Motor %i Stopped %s" % (e.index))

def VelocityChanged(e):
   global velocityList
   velocityList[e.index] = e.velocity

#Event Handler Callback Functions
def inferfaceKitAttached(e):
   attached = e.device
   logger.debug("InterfaceKit %i Attached!" % (attached.getSerialNum()))

def InterfaceKitDetached(e):
   detached = e.device
   logger.debug("InterfaceKit %i Detached!" % (detached.getSerialNum()))

def InterfaceKitError(e):
   try:
      source = e.device
      logger.debug("InterfaceKit %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))
   except PhidgetException as e:
      logger.error("Phidget Exception %i: %s" % (e.code, e.details))

def InterfaceKitInputChanged(e):
   source = e.device
   logger.debug("InterfaceKit %i: Input %i: %s" % (source.getSerialNum(), e.index, e.state))

def InterfaceKitSensorChanged(e):
   source = e.device
   logger.debug("InterfaceKit %i: Sensor %i: %i" % (source.getSerialNum(), e.index, e.value))

def InterfaceKitOutputChanged(e):
   source = e.device
   logger.debug("InterfaceKit %i: Output %i: %s" % (source.getSerialNum(), e.index, e.state))

##Script specific Definitions
def VALUp():
   global VAL
   VAL=VAL+1
def VALZero():
   global VAL
   VAL=0
def IttyUp():
   global Itty
   Itty=Itty+1

def turnLasersOn():
   try:
      sensor=interfaceKit.setOutputState(5,True)
      sensor=interfaceKit.setOutputState(6,True)
   except PhidgetException as e:
      logger.critical("Error: %i: %s" % (e.code,e.details))
      return False;
   return True;

def turnLasersOff():
   try:
      sensor=interfaceKit.setOutputState(5,False)
      sensor=interfaceKit.setOutputState(6,False)
   except PhidgetException as e:
      logger.critical("Error: %i: %s" % (e.code,e.details))
      return False;
   return True;


def getXDistance():
   try:
      sensor=interfaceKit.getSensorValue(XDISTANCE)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))
      return False;
   return sensor

def getYDistance():
   try:
      sensor=interfaceKit.getSensorValue(YDISTANCE)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))
      return False;
   return sensor

def getCurrentXYDistance():
   X=getXDistance()
   Y=getYDistance()
   return X,Y

def setDistanceXYForPosition(position,X,Y):
   value=DataReadWrite.updateDistanceXYForPosition(position,X,Y)
   return value

def getAbsoluteXPosition():
   try:
      sensor = interfaceKit.getSensorValue(0)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))      
      return False;
   return sensor

def getAbsoluteYPosition():
   try:
      sensor = interfaceKit.getSensorValue(1)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))      
      return False
   return sensor

def getXZero():
   try:
      sensor = interfaceKit.getSensorValue(2)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))      
      return False;
   return sensor

def getYZero():
   try:
      sensor = interfaceKit.getSensorValue(3)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))      
      return False;
   return sensor

def getTemperature():   
   try:
      value = interfaceKit.getSensorRawValue(4)/4.095
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))      
      return False;
   sensor = double((value*0.222222222222)-61.1111111111+2.5) ## 2.5 added to match madgetech
   return sensor

def getHumidity():
   try:
      value = interfaceKit.getSensorRawValue(7)/4.095
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))
      return False;
   sensor = double((value*0.1906)-40.20000-5.92) ## 5.22 added to match madgetech
   return sensor

def isGripperHoldingSomething():
   try:
      sensor2 = interfaceKit.getSensorValue(1)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))      
      exit(1)
   if sensor2>0:
      return True;
   else:
      return False;

def openGripper():
   logger.debug( "openGripper:  now open gripper")
   #  Set the gripper to be open
   try:
      advancedServo.setEngaged(GRIPPER, True)
      advancedServo.setPosition(GRIPPER, GRIPPER_OPEN)
      while advancedServo.getStopped(GRIPPER) !=STOPPED:
         pass
      sleep(2)
      advancedServo.setEngaged(GRIPPER, False)
   except PhidgetException as e:
      logger.critical("Gripper Open Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   sleep(1)
   return True;

def closeGripper():
   logger.debug("closeGripper:  now close gripper")
   #  Set the gripper to be open
   try:
      advancedServo.setEngaged(GRIPPER, True)
      advancedServo.setPosition(GRIPPER, GRIPPER_CLOSED)
      while advancedServo.getStopped(GRIPPER) !=STOPPED:
         pass
      sleep(2)
      advancedServo.setEngaged(GRIPPER, False)
   except PhidgetException as e:
      logger.critical("Gripper Close Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   sleep(1)
   return True;

def setAbsZeroXY( xVal, yVal ):
    MINIMUM_X_VALUE  = xVal
    MINIMUM_Y_VALUE = yVal
    return True;

## home is defined as 0,0 -- the point in the far left corner        
def goHome():
   logger.debug("goHome:  Now going to the home position.")
   # first find Home using the absolute sensors
   # value = resetMotorsToZeroPosition()
   # now move to zero if it couldnt be found. Should really do nothing.
   #if value == False:
   #    alertWindow("Error could not find the home position")

   try:
      stepper.setEngaged(XMOTOR, True)
      stepper.setTargetPosition(XMOTOR, 0)
      while stepper.getStopped(XMOTOR) !=STOPPED:
         pass
      sleep(2)
      stepper.setEngaged(XMOTOR, False)
   except PhidgetException as e:
       logger.critical("Home Position - Phidget Exception %i: %s" % (e.code, e.details))
       logger.critical("Exiting....")
       exit(1)
   sleep(2)
   ### Y Motor
   try:
      stepper.setEngaged(YMOTOR, True)      
      stepper.setTargetPosition(YMOTOR, 0)
      while stepper.getStopped(YMOTOR) !=STOPPED:
         pass
      sleep(2)
   except PhidgetException as e:
      logger.critical("Home Position - Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   stepper.setEngaged(YMOTOR, False)

   stepper.setEngaged(XMOTOR, True)
   ## check to see if we are as far as we can be in the X axis (motor 0)
   bump=10
   move=stepper.getCurrentPosition(XMOTOR)+bump
   preAbsX=getAbsoluteXPosition()
   sleep(2)
   try:
      stepper.setTargetPosition(XMOTOR,move)
      postAbsX=getAbsoluteXPosition()
      while stepper.getStopped(XMOTOR) !=STOPPED:
         pass
      while preAbsX < postAbsX:
         preAbsX=getAbsoluteXPosition()
         while stepper.getStopped(XMOTOR) !=STOPPED:
            pass
         sleep(2)
         stepper.setTargetPosition(XMOTOR,move)
         postAbsX=getAbsoluteXPosition()
         sleep(1)
   except PhidgetException as e:
      logger.critical("Stepper 0: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      return False
   stepper.setEngaged(XMOTOR, False)

   stepper.setEngaged(YMOTOR, True)
   ## check to see if we are as far as we can be in the Y axis (motor 2)
   bump=10
   move=stepper.getCurrentPosition(YMOTOR)-bump
   preAbsY=getAbsoluteYPosition()
   sleep(2)
   try:
      stepper.setTargetPosition(YMOTOR,move)
      postAbsY=getAbsoluteYPosition()
      while stepper.getStopped(YMOTOR) !=STOPPED:
         pass
      sleep(2)
      while preAbsY < postAbsY:
         preAbsY=getAbsoluteYPosition()
         while stepper.getStopped(YMOTOR) !=STOPPED:
            pass
         sleep(2)
         stepper.setTargetPosition(YMOTOR,move)
         sleep(1)
         postAbsX=getAbsoluteYPosition()
   except PhidgetException as e:
      logger.critical("Stepper 0: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      return False
   stepper.setEngaged(YMOTOR, False)

   newpos= getAbsoluteXPosition()
   #if newpos <>92:
   #   logger.error( "Moved to Home position but not at ZERO!  Going to wait for instructions")
   #  return False;
   DataReadWrite.updatePosition(getXPosition(),getYPosition(),getZPosition())
   ## reset the Absolute Zero points
   value = setAbsZeroXY(getAbsoluteXPosition(),getAbsoluteYPosition())
   value=M0SetP()
   value=M2SetP()
   sleep(2)
   return True;

def goToSamplePosition(position, startWindow=1):
   logger.debug("goToSamplePosition( %d) ",position)
   logger.debug("We are now going to go to sample position: %d",position)
   xpos=getXPosition()
   ypos=getYPosition()
   zpos=getZPosition()
   if zpos>70:
      return False
   newXpos=0
   newYpos=0
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))
   (newXpos,newYpos)=DataReadWrite.getXYForSampleLocation(position)
   logger.debug("Going to X: %d and Y: %d" %(newXpos,newYpos))

   if position<0 or position>25:
      logger.error("Invalid position: %d ",position)
      return False;

   ## now move to the position with the X and Y coordinates
   try:
      logger.debug("Now move to X:  %d",newXpos)
      stepper.setEngaged(XMOTOR, True)
      stepper.setTargetPosition(XMOTOR, newXpos)
      while stepper.getStopped(XMOTOR) !=STOPPED:
         pass
      sleep(2)
      DataReadWrite.updatePosition(getXPosition(),getYPosition())
      logger.debug("sleep to make sure this is complete..")
      stepper.setEngaged(XMOTOR, False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)

   try:
      stepper.setEngaged(YMOTOR, True)
      logger.debug("Now move to Y: %d ",newYpos)
      stepper.setTargetPosition(YMOTOR, newYpos)
      while stepper.getStopped(YMOTOR) !=STOPPED:
         pass
      sleep(2)
      stepper.setEngaged(YMOTOR,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   logger.debug("We are now at x: %i and y: %i" % (getXPosition(),getYPosition()))
   DataReadWrite.updatePosition(getXPosition(),getYPosition())
   ## for now only do the refine position for the crucibles in the rack -- not the balance
   #if position<26 and startWindow==0:
      #refinePosition(position)
   return True;

def refinePosition(position):
   ## should only use this when the position is close
   logger.debug("refine the position over the crucible at position %d",position)
   xpos=getXDistance()
   ypos=getYDistance()
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))
   ## get the center of the crucible
   xCrucible,yCrucible=DataReadWrite.getXYDistanceForSampleLocation(position)
   xdiff=xpos-xCrucible  ## larger means to the left - so bump down
   ydiff=ypos-yCrucible ## larger means forward so bump right
   # x and y here are the pixels needed to move to get to the center of the crucibles.
   ## first fix the X direction
   bump=5
   if xdiff>=0:
      while (abs(xCrucible-xpos)<bump):
         bumpXMotorUp(bump)
         xpos,ypos=getCurrentXYDistance()
         sleep(1)
   elif xdiff>0:
      while (abs(xCrucible-xpos)<bump):
         bumpXMotorDown(bump)
         xpos,ypos=getCurrentXYDistance()
         sleep(1)
   ## now y
   if ydiff<=0:
      while (abs(yCrucible-ypos)>bump):
         bumpYMotorLeft(bump)
         xpos,ypos=getCurrentXYDistance()
         sleep(1)
   elif ydiff>0:
      while (abs(yCrucible-ypos)>bump):
         bumpYMotorRight(bump)
         xpos,ypos=getCurrentXYDistance()
         sleep(1)
   return True

def raiseToTop():
   logger.debug("raiseToTop")
   ## lower arm to sample
   logger.debug("now raising the arm down to the sample")
   try:
      advancedServo.setEngaged(ZMOTOR, True)
      advancedServo.setPosition(ZMOTOR, UP_SAMPLE_POSITION)
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         #print "...waiting for the zmotor to stop..."
         pass
      sleep(2)
      advancedServo.setEngaged(ZMOTOR,False)
   except PhidgetException as e:
      logger.critical("samplePickUp Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   sleep(2)
   return True;

def samplePickUp():
   logger.debug("samplePickUp")
   ## make sure grippers are open
   logger.debug("First make sure grippers are open...")
   openGripper()
   ## lower arm to sample
   logger.debug("now move the arm down to the sample")
   DOWN_SAMPLE_POSITION=DataReadWrite.getZForSampleLocation(1)
   advancedServo.setEngaged(ZMOTOR,True)
   logger.debug("move sample to %d",DOWN_SAMPLE_POSITION)
   try:
      advancedServo.setPosition(ZMOTOR, DOWN_SAMPLE_POSITION)
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         #print "...waiting for the zmotor to stop..."
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical("samplePickUp Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   advancedServo.setEngaged(ZMOTOR,False)
   sleep(2)
   ## close grippper
   logger.debug ("Close gripper to value: %i ",GRIPPER_CLOSED)

   closeGripper()
   sleep(2)
   logger.debug ("Checking to see if gripper is holding something")
   #if isGripperHoldingSomething() == False:
      #logger.error( "There is a problem. Gripper reports no crucible. Going to home position.")
      #logger.error( "Open Gripper.")
      #openGripper()
      #logger.error( "Raise arm to top.")
      #raiseToTop()
      #response=goHome()
      #val = raw_input("Continue ( c ) or quit ( q )?")
      #if val=="q": 
         #KillMotors()
         #exit(1)
      #else:
         #return False;

   logger.debug ("Gripper reports that it is holding a crucible.")
   logger.debug ("Now raise the arm...")

   ## raise the arm
   try:
      advancedServo.setEngaged(ZMOTOR,True)
      advancedServo.setPosition(ZMOTOR, UP_SAMPLE_POSITION)
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         #print ". . . waiting for the zmotor to stop . . ."
         sleep(1)
         pass
      sleep(2)
      advancedServo.setEngaged(ZMOTOR, False)
   except PhidgetException as e:
      logger.critical("samplePickUp Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   sleep(2)
   return True;

def samplePutDown():
   logger.debug("samplePutDown")
   DOWN_SAMPLE_POSITION=DataReadWrite.getZForSampleLocation(1)
   try:
      #lower the arm
      advancedServo.setEngaged(ZMOTOR, True)
      advancedServo.setPosition(ZMOTOR, DOWN_SAMPLE_POSITION)
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         #print ". . . waiting for the zmotor to stop . . ."
         pass
      sleep(1)
      advancedServo.setEngaged(ZMOTOR, False)
      sleep(2)
      #open gripper
      openGripper()
      sleep(2)
      #raise the arum
      advancedServo.setEngaged(ZMOTOR, True)
      advancedServo.setPosition(ZMOTOR, UP_SAMPLE_POSITION)
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         #print ". . . waiting for the zmotor to stop . . ."
         pass
      sleep(2)
      advancedServo.setEngaged(ZMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   sleep(2)
   #if isGripperHoldingSomething() == True:
      #logger.error ("Gripper reports that it is NOT holding a crucible.")
      #logger.error( "There is a problem. Gripper reports holding a crucible when it should be empty.")
      #logger.error( "Open Gripper.")
      #openGripper()
      #logger.error( "Raise arm to top.")
      #raiseToTop()
      #response=goHome()
      #val = raw_input("Continue ( c ) or quit ( q )?")
      #if val=="q": 
         #KillMotors()
         #exit(1)
      #else:
         #return False;
   return True;

def goToOutsideBalanceFromInside():
   logger.debug("goToOutsideBalanceFromInside")
   ## make sure the door is open!!
   xBalance=0
   yBalance=0
   (xBalance,yBalance)=DataReadWrite.getXYForBalance("outside")
   ## First in the X direction
   try:
      stepper.setEngaged(XMOTOR, True)
      stepper.setTargetPosition(XMOTOR, xBalance)
      while stepper.getStopped(XMOTOR) !=STOPPED:
         pass
      sleep(1)
      stepper.setEngaged(XMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   DataReadWrite.updatePosition(getXPosition(),getYPosition())
   sleep(2)
   ## Then Y

   try:
      stepper.setEngaged(YMOTOR, True)
      stepper.setTargetPosition(YMOTOR, yBalance)
      while stepper.getStopped(YMOTOR) !=STOPPED:
         pass
      sleep(1)
      stepper.setEngaged(YMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   DataReadWrite.updatePosition(getXPosition(),getYPosition())
   #set x axis -- move it to point outside...
   sleep(2)
   if (getXMotorPosition() > -2800):
      DataReadWrite.closeBalanceDoor()
   return True;

def goToOutsideBalanceFromOutside():
   logger.debug("goToOutsideBalanceFromOutside")
   xBalance=0
   yBalance=0
   (xBalance,yBalance)=DataReadWrite.getXYForBalance("outside")

   ## make sure the door is open!!
   DataReadWrite.openBalanceDoor()
   logger.debug("first move the y axis to %d", yBalance)
   ## first line up the Y axis arm 
   try:
      stepper.setEngaged(YMOTOR, True)
      stepper.setTargetPosition(YMOTOR, yBalance)
      while stepper.getStopped(YMOTOR) != STOPPED:
         pass
      sleep(1)
      stepper.setEngaged(YMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   sleep(2)
   logger.debug("now located at x: %d y: %d" % (getXPosition(),getYPosition()))
   DataReadWrite.updatePosition(getXPosition(),getYPosition())
   logger.debug("now move the x-asis to %d", xBalance)
   ## now move to the point just outside of the balance with the X axis
   try:
      stepper.setEngaged(XMOTOR, True)
      stepper.setTargetPosition(XMOTOR, xBalance)
      while stepper.getStopped(XMOTOR) !=STOPPED:
         pass
      sleep(1)
      stepper.setEngaged(XMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   logger.debug("now located at x: %d y: %d" % (getXPosition(),getYPosition()))
   DataReadWrite.updatePosition(getXPosition(),getYPosition())
   sleep(2)
   return True;

def goToInsideBalanceFromOutside():
   logger.debug("goToInsideBalanceFromOutside")
   ## make sure the door is open!!
   ## DataReadWrite.openBalanceDoor()
   #set x axis -- move it to point outside...

   value=DataReadWrite.openBalanceDoor()

   xBalance=0
   yBalance=0
   (xBalance,yBalance)=DataReadWrite.getXYForBalance("inside")

   logger.debug( "now moving x motor to position: %d", xBalance)
   try:
      stepper.setEngaged(XMOTOR, True)
      stepper.setTargetPosition(XMOTOR, xBalance)
      while stepper.getStopped(XMOTOR) !=STOPPED:
         pass
      sleep(2)
      stepper.setEngaged(XMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   sleep(2)
   logger.debug("now located at x: %d y: %d" % (getXPosition(),getYPosition()))
   DataReadWrite.updatePosition(getXPosition(),getYPosition())

   logger.debug("adjusting Y position to %d", yBalance)
   # make sure y position is correct
   try:
      stepper.setEngaged(YMOTOR, True)
      stepper.setTargetPosition(YMOTOR, yBalance)
      while stepper.getStopped(YMOTOR) !=STOPPED:
         pass
      sleep(2)
      stepper.setEngaged(YMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   logger.debug("now located at x: %d y: %d" % (getXPosition(),getYPosition()))
   DataReadWrite.updatePosition(getXPosition(),getYPosition())
   sleep(2)
   return True;   

def putSampleOnBalance():
   logger.debug("putSampleOnBalance")
   ##Zeroing the Balance
   DataReadWrite.zeroBalance()
   sleep(1)
   DOWN_BALANCE_POSITION_DROPOFF=DataReadWrite.getZForBalanceLocation()
   ## lower the arm
   logger.debug("Now lower the arm to %d", DOWN_BALANCE_POSITION_DROPOFF)
   try:
      advancedServo.setEngaged(ZMOTOR, True)
      advancedServo.setPosition(ZMOTOR, DOWN_BALANCE_POSITION_DROPOFF)
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         #print ". . . waiting for the zmotor to stop . . ."
         pass
      sleep(2)
      advancedServo.setEngaged(ZMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   sleep(2)
   logger.debug("open the gripper")
   # release the sample
   openGripper()
   sleep(1)
   logger.debug("raise the arm to position %d", UP_BALANCE_POSITION)
   ## raise the arm
   try:
      advancedServo.setEngaged(ZMOTOR, True)
      advancedServo.setPosition(ZMOTOR, UP_BALANCE_POSITION)
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         #print ". . . waiting for the zmotor to stop . . ."
         pass
      sleep(2)
      advancedServo.setEngaged(ZMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   sleep(2)
   #if isGripperHoldingSomething() == True:
      #logger.error ("Gripper reports that it is holding a crucible (when it shouldnt).")
      #logger.error ("There is a problem. Gripper reports holding a crucible. Stopping.")
      #logger.error("FIRST -- Check to see if there is something on the balance")
      #logger.error("if there is something on the balance then its okay")
      #results=[]
      #(weight,status)=DataReadWrite.readWeightFromBalance()

      #if (weight>1.0):
         #logger.error("There is %f g on the balance. Since this is >1g, the sensor must be wrong.", weight)
      #else:
         #logger.error("There is just %f g on the balance. This is too close to zero. Error.",weight)
         #logger.error ("First open Gripper.")
         #openGripper()
         #logger.error( "Raise arm to top.")
         #goToOutsideBalanceFromInside()
         #raiseToTop()
         #response=goHome()
         #val = raw_input("Continue ( c ) or quit ( q )?")
         #if val=="q": 
            #KillMotors()
            #exit(1)
         #else:
            #return False;
   return True;

def getXYForSampleLocation(sampleLocation):
   if sampleLocation > 25 or sampleLocation < 0:
        return 0,0
   x=0
   y=0
   (x,y)=DataReadWrite.getXYForSampleLocation(sampleLocation)
   return (x,y)

def pickUpSampleFromBalance():
   logger.debug("pickUpSampleFromBalance")
   ## lower the arm
   DOWN_BALANCE_POSITION_PICKUP=DataReadWrite.getZForBalanceLocation()

   logger.debug("Lower the arm to %d ",DOWN_BALANCE_POSITION_PICKUP)
   try:
      advancedServo.setEngaged(ZMOTOR, True)
      advancedServo.setPosition(ZMOTOR,DOWN_BALANCE_POSITION_PICKUP)
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         #print "... Waiting for the zmotor to stop ..."
         pass
      sleep(2)
      advancedServo.setEngaged(ZMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   logger.debug("Close the gripper.")
   sleep(2)
   ## grab the sample
   closeGripper()

   logger.debug("Gripper reports that it is holding a crucible. This is good.")

   ## raise the arm
   logger.debug("Raise the arm to %d", UP_BALANCE_POSITION)
   try:
      advancedServo.setEngaged(ZMOTOR, True)
      advancedServo.setPosition(ZMOTOR, UP_BALANCE_POSITION)
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         pass
      sleep(2)
      advancedServo.setEngaged(ZMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
   return True;

def nextSample():
   position = POSITION.get()+1   # increment the position to the next one...
   POSITION.set(position)
   statustext="Next sample: %d",position
   STATUS.set(statustext)
   statustext="go on to the next position: %d", int(position)
   logger.debug(statustext)
   STATUS.set("Done!")
   runID=RUNID.get()
   return (runID)

def quitProgram():
   exit()

def weighAllCrucibles(initials,numberOfSamples,loggingInterval,
                      duration,startPosition,tempCorrection,rhCorrection,robotStatus,
                      POSITION,MCOUNT,CURRENTSTEP,STATUS,
                      DURATION,LOGGERINTERVAL,RUNID,NUMBEROFSAMPLES,TIMEREMAINING,alert):
   #global robotStatus

   # Find elapsed time
   #first put robot back to zero
   logger.debug("weightAllCrucibles: %s, %d, %d, %d, %d" % (initials,numberOfSamples,loggingInterval,duration,startPosition))
   position=int(startPosition)
   #HomePosition()
   listOfValues=()
   LOGGERINTERVAL.set(loggingInterval)
   DURATION.set(duration)
   POSITION.set(position)
   STATUS.set("Initializing")
   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")
   ### set up gui #########
   robotStatus.deiconify()
   Label(robotStatus,text="Run ID:").grid(row=0,column=0,sticky=W)
   Label(robotStatus,textvariable=RUNID).grid(row=0,column=1, sticky=W)
   Label(robotStatus,text="Current sample number:").grid(row=1,column=0,sticky=W)
   Label(robotStatus,textvariable=POSITION).grid(row=1,column=1, sticky=W)
   Label(robotStatus,textvariable=MCOUNT).grid(row=2,column=1,sticky=W)
   Label(robotStatus,text="Current measurement count:").grid(row=2,column=0,sticky=W)
   Label(robotStatus,text="Logging interval:").grid(row=3,column=0, sticky=W)
   Label(robotStatus,textvariable=LOGGERINTERVAL).grid(row=3,column=1,sticky=W)
   Label(robotStatus,text="Duration of Measurements:").grid(row=4,column=0, sticky=W)
   Label(robotStatus,textvariable=DURATION).grid(row=4,column=1,sticky=W)
   Label(robotStatus,text="Number of Samples:").grid(row=5,column=0,sticky=W)
   Label(robotStatus,textvariable=NUMBEROFSAMPLES).grid(row=5,column=1,sticky=W)
   Label(robotStatus,text="Time remaining for this sample:").grid(row=6,column=0,sticky=W)
   Label(robotStatus,textvariable=TIMEREMAINING).grid(row=6,column=1,sticky=W)
   Label(robotStatus,text="Status").grid(row=7,column=0, sticky=W)
   Label(robotStatus,textvariable=STATUS).grid(row=7,column=1,sticky=W)
   Button(robotStatus,text="Next Sample", command=nextSample).grid(row=8, column=0, padx=2, pady=2)
   Button(robotStatus,text="Quit", command=quitProgram).grid(row=8, column=1, padx=2, pady=2)
   NUMBEROFSAMPLES.set(numberOfSamples)
   sleep(5)

   #first create a new run so we have an ID.
   logger.debug("DataReadWrite.insertRun( %s,%s,%d )" %(initials,today,numberOfSamples))
   runID=DataReadWrite.insertRun(initials,today,numberOfSamples)
   if (runID is False):
      alertWindow("insertRun returned an error.", alert)
      exit(1)
   #global runID
   statustext = "Run ID is %d" % int(runID)
   logger.debug( statustext)
   RUNID.set(int(runID))
   position=startPosition  ## set the position to start where we want it.
   if (position =="" or position ==0):  ## position must start at 1
      position=1

   while position < (numberOfSamples+1):  # positions go from 1 to 25
      POSITION.set(position)
      statustext="Going to position: %d"% int(position)
      logger.debug( statustext)
      #set this crucible for this run
      logger.debug("DataReadWrite.insertInitialCrucible(%d,%d,%s)" % (runID,position,today))
      value=DataReadWrite.insertInitialCrucible(runID,position,today)
      if (value is False):
         alertWindow("insertInitialCrucible returned an error.", alert)
         exit(1)
      # assume we start in position 1 -- which is the 0,0 point for the grid
      logger.debug( "going to sample position: %d ", position)
      STATUS.set(statustext)
      goToSamplePosition(position)
      statustext="Picking up sample %d" % int(position)
      STATUS.set(statustext)
      logger.debug( "picking up sample.")
      val = samplePickUp()
      if val is False:
         return False;

      ## zero the balance for each sample
      logger.debug("going to zero balance...")
      DataReadWrite.zeroBalance()
      logger.debug( "opening balance door.")
      DataReadWrite.openBalanceDoor()
      statustext="Going to outside of balance x: %d y: %d" %( DataReadWrite.getXYForBalance("outside"))
      STATUS.set(statustext)
      logger.debug( "go to outside of balance.")
      goToOutsideBalanceFromOutside()
      logger.debug( "go to inside balance")
      statustext="Going to inside balance x: %d y: %d" %( DataReadWrite.getXYForBalance("inside"))
      STATUS.set(statustext)
      goToInsideBalanceFromOutside()
      logger.debug( "put sample on balance")
      STATUS.set("Putting sample on balance")
      val = putSampleOnBalance()
      if val is False:
         STATUS.set("ERROR")
         robotStatus.quit()
         return False;
      STATUS.set("Moving to outside balance.")
      logger.debug( "Move to outside balance.")
      goToOutsideBalanceFromInside()
      ## may need to check to see if arm is clear of door.
      if (getXMotorPosition() > -2800):
         DataReadWrite.closeBalanceDoor()
      durationOfLogging=int(duration)
      startTime=datetime.today()
      endPoint=timedelta(minutes=durationOfLogging)
      endTime=startTime+endPoint
      listOfValues=[]
      weight=float(0.0)
      count=0
      kcount=0
      tempHumidityArray=[]
      statustext="Weighing sample # %d"% position
      STATUS.set(statustext)
      a = array([])
      tempArray=array([])
      humidityArray=array([])
      averageTemp=0.0
      stdevTemp=0.0
      averageHumidity=0.0
      stdevHumidity=0.0
      averagePressure=0.0
      averageLight=0.0
      robotStatus.update()
      ## sleep for 120 seconds -- dont record the first two minutes of data - let the balance recover
      sleep(120)
      while datetime.today() < endTime:
         timeLeft=endTime-datetime.today()
         TIMEREMAINING.set(int(timeLeft.seconds/60))
         result=[]
         (weight,status)=DataReadWrite.readWeightFromBalance()
         robotStatus.update()
         if weight>0.0:
            listOfValues.append(weight)
            a=append(a,double(weight))
            averageWeight=a.mean()
            averageTemp=0.0
            averageHumidity=0.0
            stdevTemp=0.0
            stdevHumidity=0.0
            averagePressure=0.0
            averageLight=0.0
            stdevWeight=a.std()
            humidity=getHumidity()    ###+rhCorrection
            temperature=getTemperature()   ###+tempCorrection
            if (temperature is ""):
               temperature=0.0
            if temperature>0:
               tempArray=append(tempArray,temperature)
               if (tempArray.size > 1):
                  averageTemp=tempArray.mean()
                  stdevTemp=tempArray.std()
               else:
                  averageTemp=temperature
                  stdevTemp=0.0
            if humidity>0:
               humidityArray=append(humidityArray,humidity)
               if humidityArray.size > 1:
                  averageHumidity=humidityArray.mean()
                  stdevHumidity=humidityArray.std()
               else:
                  averageHumidity=humidity
                  stdevHumidity=0.0
            count += 1
            logger.debug( "Count: %d the average weight of crucible # %i is: %f with stdev of: %f" %(count, position,averageWeight,stdevWeight))
            ## now update crucible position record 
            now = datetime.today()
            today = now.strftime("%m-%d-%y %H:%M:%S")

            MCOUNT.set(count)
            
            measurementID=DataReadWrite.insertCrucibleMeasurement(runID,position,weight,status,temperature,humidity,count,today)
            DataReadWrite.updateCrucible(position,averageWeight,stdevWeight,averageTemp,stdevTemp,averageHumidity,stdevHumidity,today,runID,count)
            sleep(loggingInterval)
            statustext="Weight recorded #%d %f %f" %(count,averageWeight,stdevWeight)
            STATUS.set(statustext)
            
         if count is 0:
            ## check to see if balance is giving anything
            (value,status)=DataReadWrite.readInstantWeightFromBalance()
            logger.debug( "Balance current reads: %f ",float(value))
            if (value>0):
               logger.debug( "Since this is >0 the balance is reading but not stable")
               logger.debug( "resetting clock. Waiting for a valid entry before storing data...")
               startTime=datetime.today()
               endPoint=timedelta(minutes=durationOfLogging)
               endTime=startTime+endPoint
            else:
               STATUS.set("Error: nothing from balance. Checking to see if this resolves itself")
               logger.debug( "There is a problem: no output from balance at all: Count: %d",int(kcount))
               kcount += 1
               if kcount==500:
                  logger.error( "There is a problem: no output for 500 counts -- quitting ")
                  KillMotors()
                  exit(1)
      logger.debug("Open the balance door")
      DataReadWrite.openBalanceDoor()
      STATUS.set("Go back into balance to get sample.")
      logger.debug( "enter balance")
      goToInsideBalanceFromOutside()
      logger.debug( "pick up sample")
      STATUS.set("Pick up sample from balance")
      val = pickUpSampleFromBalance()
      if val is False:
         STATUS.set("Error: missing sample")
         robotStatus.quit()
         return False
      logger.debug( "leave balance . . . ")
      STATUS.set("Leave balance.")
      goToOutsideBalanceFromInside()
      statustext="Return to position %d", int(position)
      STATUS.set(statustext)
      logger.debug( "now return to position: %d ", int(position))
      STATUS.set("Put sample down.")
      goToSamplePosition(position)
      logger.debug( "put the sample down. . . ")
      val=samplePutDown()
      if val is False:
         STATUS.set("Error sample held when there shouldn't be one")
         robotStatus.quit()
         return False;
      logger.debug( "close the balance door . . ")
      if (getXMotorPosition() > -2800):
          DataReadWrite.closeBalanceDoor()
      STATUS.set("Now go to home position")
      response=goHome()
      if response is False:
         logger.error( "Home point not reached. Stopping.")
         return False;

      position += 1   # increment the position to the next one...
      POSITION.set(position)
      statustext="Now starting next sample: %d",position
      STATUS.set(statustext)
      statustext="go on to the next position: %d", int(position)
      logger.debug(statustext)
   STATUS.set("Done!")
   robotStatus.withdraw()
   return (runID)


def weighAllSamplesPreFire(runID,duration,loggingInterval,
                           numberOfSamples,startPosition,
                           tempCorrection,rhCorrection,repetition,
                           robotStatus,POSITION,MCOUNT,CURRENTSTEP,
                           STATUS,DURATION,LOGGERINTERVAL,RUNID,
                           NUMBEROFSAMPLES,TIMEREMAINING,CYCLE,MEAN,STDEV,VARIANCE, alert):
   # Find elapsed time
   #first put robot back to zero
   position=int(startPosition)
   if position=="":
      position=1
   logger.debug("weighAllSamplesPreFire( %d,%d,%d,%d,%d )" % (runID,duration,loggingInterval,numberOfSamples,startPosition))

   status="prefire"
   preOrPost=1
   #HomePosition()
   listOfValues=()
   RUNID.set(runID)
   NUMBEROFSAMPLES.set(numberOfSamples)
   DURATION.set(duration)
   POSITION.set(position)
   CYCLE.set(repetition)
   MCOUNT.set(0)
   STATUS.set("Initializing")
   LOGGERINTERVAL.set(loggingInterval)
   crucibleWeight=0.0
   startTime=datetime.today()
   endPoint=timedelta(minutes=duration)
   endTime=startTime+endPoint
   robotStatus.deiconify()
   Label(robotStatus,text="Run ID:").grid(row=0,column=0,sticky=W)
   Label(robotStatus,textvariable=RUNID).grid(row=0,column=1, sticky=W)
   Label(robotStatus,text="Current sample number:").grid(row=1,column=0,sticky=W)
   Label(robotStatus,textvariable=POSITION).grid(row=1,column=1, sticky=W)
   Label(robotStatus,text="Total Number of Samples:").grid(row=2,column=0,sticky=W)

   Label(robotStatus,textvariable=NUMBEROFSAMPLES).grid(row=2,column=1,sticky=W)
   Label(robotStatus,text="Cycle Number:").grid(row=3,column=0,sticky=W)
   Label(robotStatus,textvariable=CYCLE).grid(row=3,column=1,sticky=W)
   Label(robotStatus,textvariable=MCOUNT).grid(row=4,column=1,sticky=W)
   Label(robotStatus,text="Current measurement count:").grid(row=4,column=0,sticky=W)
   Label(robotStatus,text="Logging interval:").grid(row=5,column=0, sticky=W)
   Label(robotStatus,textvariable=LOGGERINTERVAL).grid(row=5,column=1,sticky=W)
   Label(robotStatus,text="Duration of Measurements:").grid(row=6,column=0, sticky=W)
   Label(robotStatus,textvariable=DURATION).grid(row=6,column=1,sticky=W)
   Label(robotStatus,text="Number of Samples:").grid(row=7,column=0,sticky=W)
   Label(robotStatus,textvariable=NUMBEROFSAMPLES).grid(row=7,column=1,sticky=W)
   Label(robotStatus,text="Time remaining for this sample:").grid(row=8,column=0,sticky=W)
   Label(robotStatus,textvariable=TIMEREMAINING).grid(row=8,column=1,sticky=W)
   Label(robotStatus,text="Status").grid(row=9,column=0, sticky=W)
   Label(robotStatus,textvariable=STATUS).grid(row=9,column=1,sticky=W)
   sleep(5)
   robotStatus.update()
   while (position < (numberOfSamples+1)):
      robotStatus.update()
      statustext="Now on sample %d",int(position)
      STATUS.set(statustext)
      logger.debug("Now on position: %d ", int(position))
      statustext="Go to position %d",int(position)
      STATUS.set(statustext)
      goToSamplePosition(position)
      val = samplePickUp()
      if val == False:
         return False
      ## zero the balance for each sample
      logger.debug("Zero balance")
      DataReadWrite.zeroBalance()
      logger.debug("Open balance door")
      DataReadWrite.openBalanceDoor()
      statustext="Going to outside of balance"
      STATUS.set(statustext)
      logger.debug("Go to outside balance.")
      goToOutsideBalanceFromOutside()
      statustext="Going into the balance."
      STATUS.set(statustext)
      logger.debug("go to inside balance.")
      goToInsideBalanceFromOutside()
      logger.debug("put sample on balance.")
      statustext="Putting sample on balance."
      STATUS.set(statustext)
      val = putSampleOnBalance()
      if val is False:
         return False
      ## may need to check to see if arm is clear of door.
      logger.debug("go to outsisde balance from the inside.")
      statustext="Going to outside of balance"
      STATUS.set(statustext)
      goToOutsideBalanceFromInside()
      logger.debug("close balance door")
      if (getXMotorPosition() > -2800):
         DataReadWrite.closeBalanceDoor()
      crucibleWeight=double(DataReadWrite.getCrucibleWeight(runID,position))
      if (crucibleWeight is False):
         alertWindow("getCrucibleWeight returned an error.", alert)
         exit(1)

      sampleID=int(DataReadWrite.getSampleID(runID,position))
      startTime=datetime.today()
      durationOfLogging=int(duration)
      endPoint=timedelta(minutes=durationOfLogging)
      endTime=startTime+endPoint
      repetition_count=0
      kcount=0
      standard_weight=double(0.0)

      #get the latest count for this sample
      total_count = int(DataReadWrite.getMaxPreFireCount(runID,position))
      if (total_count==0 or total_count==""):
         total_count=0
      listOfValues=[]
      a = array([])
      weight=double(0.0)
      statustext="Weighing sample # %d"% position
      STATUS.set(statustext)
      count=0
      robotStatus.update()
      ## sleep for 120 seconds -- dont record the first two minutes of data - let the balance recover
      sleep(120)
      while datetime.today() < endTime:
         robotStatus.update()
         timeLeft=endTime-datetime.today()
         TIMEREMAINING.set(int(timeLeft.seconds/60))
         result=[]
         (measurement,status)=DataReadWrite.readWeightFromBalance()
         weight=double(measurement)-double(crucibleWeight)
         if weight>0.0:
            a=append(a,double(weight))
            averageWeight=a.mean()
            stdevWeight=a.std()
            count += 1
            logger.debug( "Count: %d the average weight of sample # %d is %f with stdev of %f" % (count,position,averageWeight,stdevWeight))
            ## now update crucible position record 
            now = datetime.today()
            today = now.strftime("%m-%d-%y %H:%M:%S")
            repetition_count += 1
            total_count += 1
            MCOUNT.set(count)

            temperature=getTemperature()   ## +tempCorrection
            humidity=getHumidity()        ##+rhCorrection
            logger.debug( "TMP:  temp: %s, humidity: %s" % (temperature,humidity))
            
            standard_weight=float(DataReadWrite.readStandardBalance())
            if (temperature==""):
               temperature=0.0
            if (humidity==""):
               humidity=0.0

            value=DataReadWrite.insertPreFireMeasurement(runID,sampleID,position,weight,status,
                                                         temperature,humidity,crucibleWeight,
                                                         standard_weight,today,total_count,
                                                         repetition,repetition_count,count)

            if (value is False):
               alertWindow("insertPreFireMeasurement returned an error.", alert)
               exit(1)

            ### check to see if enough measurements have been made. First at least 100 must have been done
            if (count > COUNTS_FOR_STATS):
               (mean,stdev,variance,tempMean,tempStdev,humidityMean,humidityStdev)=DataReadWrite.getStatsForPrefireWeightOfSample(runID,sampleID,count)
               MEAN.set(mean)
               STDEV.set(stdev)
               VARIANCE.set(variance)
               logger.debug("Mean: %d  Stdev: %d  Variance: %d TempMean: %d  TempStDev: %d HumidityMean: %d HumidityStdDev: %d" % (mean,stdev,variance,tempMean,tempStdev,humidityMean,humidityStdev))
               value=DataReadWrite.updateSamplePreFire(runID,sampleID,position,mean,stdev,tempMean,tempStdev,humidityMean,humidityStdev)
            sleep(loggingInterval)
      DataReadWrite.openBalanceDoor()
      statustext="Going into balance."
      STATUS.set(statustext)
      goToInsideBalanceFromOutside()
      statustext="Picking up sample."
      STATUS.set(statustext)
      val=pickUpSampleFromBalance()
      if val is False:
         return False
      statustext="Going to outside of balance."
      STATUS.set(statustext)
      goToOutsideBalanceFromInside()
      statustext="Going to position %d." % position
      STATUS.set(statustext)
      goToSamplePosition(position)
      statustext="Putting sample down."
      val=samplePutDown()
      if val == False:
         return False
      statustext="Going to home position."
      response=goHome()
      if response is False:
         logger.error( "Home point not reached. Stopping.")
         STATUS.set("Error: home point not reached.")
         return False
      if (getXMotorPosition() > -2800):
         DataReadWrite.closeBalanceDoor()
      position += 1  ## increment the position to the next sample
      POSITION.set(int(position))

      statustext= "Now moving to the next sample %d." % position
      STATUS.set(statustext)
   STATUS.set("Done!")
   robotStatus.withdraw()
   return runID;

def weighAllSamplesPostFire(runID,duration,
                            loggingInterval,numberOfSamples,startPosition,endOfFiring,
                            tempCorrection,rhCorrection,repetition,robotStatus,
                            POSITION,MCOUNT,CURRENTSTEP,STATUS,DURATION,
                            LOGGERINTERVAL,RUNID,NUMBEROFSAMPLES,TIMEREMAINING,TIMEELAPSEDMIN,REPS,CYCLE, alert):
   logging.debug("weighAllSamplesPostFire( %d,%d,%d,%d,%d,%s,%f,%f,%d)" %(runID,duration,
                                                                          loggingInterval,numberOfSamples,startPosition,endOfFiring,tempCorrection,rhCorrection,repetition))
   # Find elapsed time
   #first put robot back to zero
   position=int(startPosition)
   if (position == "" or position==0):
      position=1

   #HomePosition()
   listOfValues=()
   STATUS.set("Initializing")
   crucibleWeight=0.0
   robotStatus.deiconify()
   preOrPost=2
   status="postfire"
   now = datetime.today()
   timeLapsedSinceFiring= now - endOfFiring
   Label(robotStatus,text="Run ID:").grid(row=0,column=0,sticky=W)
   Label(robotStatus,textvariable=RUNID).grid(row=0,column=1, sticky=W)
   Label(robotStatus,text="Current sample number:").grid(row=1,column=0,sticky=W)
   Label(robotStatus,textvariable=POSITION).grid(row=1,column=1, sticky=W) 
   Label(robotStatus,text="Cycle Number:").grid(row=3,column=0,sticky=W)
   Label(robotStatus,textvariable=CYCLE).grid(row=3,column=1,sticky=W)

   Label(robotStatus,textvariable=MCOUNT).grid(row=4,column=1,sticky=W)
   Label(robotStatus,text="Current measurement count:").grid(row=4,column=0,sticky=W)
   Label(robotStatus,text="Time elapsed since firing (min):").grid(row=5,column=0,sticky=W)
   Label(robotStatus,textvariable=TIMEELAPSEDMIN).grid(row=5,column=1,sticky=W)
   Label(robotStatus,text="Logging interval:").grid(row=6,column=0, sticky=W)
   Label(robotStatus,textvariable=LOGGERINTERVAL).grid(row=6,column=1,sticky=W)
   Label(robotStatus,text="Duration of Measurements:").grid(row=7,column=0, sticky=W)
   Label(robotStatus,textvariable=DURATION).grid(row=7,column=1,sticky=W)
   Label(robotStatus,text="Number of Samples:").grid(row=8,column=0,sticky=W)
   Label(robotStatus,textvariable=NUMBEROFSAMPLES).grid(row=8,column=1,sticky=W)
   Label(robotStatus,text="Time remaining for this sample:").grid(row=9,column=0,sticky=W)
   Label(robotStatus,textvariable=TIMEREMAINING).grid(row=9,column=1,sticky=W)
   Label(robotStatus,text="Status").grid(row=10,column=0, sticky=W)
   Label(robotStatus,textvariable=STATUS).grid(row=10,column=1,sticky=W)
   ### note: this wont work for sets of samples where the start point is not one..
   maxPosition=position+numberOfSamples
   startTime=datetime.today()
   endPoint=timedelta(minutes=duration)
   endTime=startTime+endPoint
   POSITION.set(int(position))
   NUMBEROFSAMPLES.set(int(numberOfSamples))
   DURATION.set(duration)
   LOGGERINTERVAL.set(loggingInterval)
   CYCLE.set(repetition)
   repetition_count=0
   sleep(5)
   while (position < maxPosition):
      robotStatus.update()
      repetition_count += 1
      logging.debug("Now on position: %d",int(position))
      goToSamplePosition(position)
      val=samplePickUp()
      if val == False:
         return False
      ## zerothe balance for each sample
      DataReadWrite.zeroBalance()
      DataReadWrite.openBalanceDoor()
      goToOutsideBalanceFromOutside()
      goToInsideBalanceFromOutside()
      val=putSampleOnBalance()
      if val is False:
         return False
      ## may need to check to see if arm is clear of door.
      goToOutsideBalanceFromInside()
      if (getXMotorPosition() > -2800):
         DataReadWrite.closeBalanceDoor()
      crucibleWeight=double(DataReadWrite.getCrucibleWeight(runID,position))
      if (crucibleWeight is False):
         alertWindow("getCrucibleWeight returned an error.", alert)
         exit(1)

      sampleID=int(DataReadWrite.getSampleID(runID,position))
      startTime=datetime.today()
      durationOfLogging=int(duration)
      endPoint=timedelta(minutes=durationOfLogging)

      endTime=startTime+endPoint
      count=0
      kcount=0
      standard_weight=float(DataReadWrite.readStandardBalance())
      listOfValues=[]
      a=array([])
      statustext="Weighing sample # %d"% position
      STATUS.set(statustext)
      total_count=int(DataReadWrite.getMaxPostFireCount(runID,position))
      if (total_count==0 or total_count==""):
         total_count=0
      count=0
      robotStatus.update()
      ## sleep for 120 seconds -- dont record the first two minutes of data - let the balance recover
      sleep(120)
      while datetime.today() < endTime:
         robotStatus.update()
         timeLeft=endTime-datetime.today()
         TIMEREMAINING.set(int(timeLeft.seconds/60))

         kcount=0
         standard_weight=0.0
         measurement=double(0.0)
         weight=double(0.0)
         temperature=double(0.0)
         humidity=double(0.0)
         result=[]
         (measurement,status)=DataReadWrite.readWeightFromBalance()
         weight=double(measurement)-double(crucibleWeight)
         if weight>0.0:
            a=append(a,double(weight))
            averageWeight=double(a.mean())
            stdevWeight=double(a.std())
            count += 1
            logger.debug( "Count: %i the average weight of sample # %i is %f with stdev of %f" % (count, position, averageWeight,stdevWeight))
            ## now update crucible position record
            now = datetime.today()
            today = now.strftime("%m-%d-%y %H:%M:%S")
            total_count += 1

            MCOUNT.set(count)

            temperature=getTemperature()  ###+tempCorrection
            humidity=getHumidity()        ###rhCorrection
            logger.debug( "TMP:  temp: %s, humidity: %s" % (temperature,humidity))

            standard_weight=float(DataReadWrite.readStandardBalance())
            timeElaspedMin=0.0
            timeDiff=now - endOfFiring
            timeElapsedMin=timeDiff.seconds/60
            TIMEELAPSEDMIN.set(timeElapsedMin)
            ## timeElapsedQuarterPower=double(pow(timeElapsedMin,0.25))

            value=DataReadWrite.insertPostFireMeasurement(runID,sampleID,position,
                                                          weight,status,temperature,humidity,endOfFiring,
                                                          crucibleWeight,standard_weight,now,total_count,repetition,repetition_count,count)
            if (value is False):
               alertWindow("insertPostFireMeasurement returned with an error.", alert)
               exit(1)
               ### check to see if enough measurements have been made. First at least 100 must have been done
            if (count > COUNTS_FOR_STATS):
               (mean,stdev,variance,tempMean,tempStdev,humidityMean,humidityStdev)=DataReadWrite.getStatsForPostFireWeightOfSample(runID,sampleID,count)
               if mean is None:
                  mean=0.0
               if variance is None:
                  variance=0.0
               if tempMean is None:
                  tempMean=0.0
               if tempStdev is None:
                  tempStdev=0.0
               if humidityMean is None:
                  humidityMean=0.0
               if humidityStdev is None:
                  humidityStdev=0.0
               logger.debug("Mean: %d  Stdev: %d  Variance: %d TempMean: %d  TempStDev: %d HumidityMean: %d HumidityStdDev: %d" % (mean,stdev,variance,tempMean,tempStdev,humidityMean,humidityStdev))
               value=DataReadWrite.updateSamplePostFire(runID,sampleID,position,tempMean,tempStdev,humidityMean,humidityStdev,count,repetition,timeElapsedMin)
            sleep(loggingInterval)

      statustext="Done! Going to retrieve sample from balance."
      STATUS.set(statustext)
      DataReadWrite.openBalanceDoor()
      goToInsideBalanceFromOutside()
      statustext="Picking up sample from balance."
      STATUS.set(statustext)
      val=pickUpSampleFromBalance()
      if val is False:
         return False
      STATUS.set("Going outside balance from inside")
      goToOutsideBalanceFromInside()
      statustext="Going to position %d" % int(position)
      STATUS.set(statustext)
      goToSamplePosition(position)
      STATUS.set("Putting sample down")
      val=samplePutDown()
      if val is False:
         return False
      STATUS.set("Now going to home position.")
      response=goHome()
      if (getXMotorPosition() > -2800):
         DataReadWrite.closeBalanceDoor()
      if response is False:
         logger.error( "Was unable to go home. Quitting.")
         return False
      position += 1 ## increment position to go to next sample
      POSITION.set(int(position))
      statustext="Now on position %d" % position
      STATUS.set(statustext)
   STATUS.set("Done!")
   robotStatus.withdraw()
   return runID;

def resetValuesToZero():
   logger.debug("resetValuesToZero")
   #Set Current position as Start Position    
   logger.debug("Set Positions of SERVOs and STEPPER MOTORS to 0")
   try:
      stepper.setCurrentPosition(XMOTOR, 0)
      stepper.setCurrentPosition(YMOTOR, 0)
      advancedServo.setPosition(ZMOTOR,UP_SAMPLE_POSITION)
      advancedServo.setPosition(GRIPPER,GRIPPER_OPEN)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   DataReadWrite.updatePosition(0,0)

def resetCoordinates(x,y):
   logger.debug("resetCoordinates")
   if x=="":
      x=0
   if y=="":
      y=0
   #Set Current position as Start Position    
   logger.debug("Set Positions of SERVOs and STEPPER MOTORS to 0")
   try:
      stepper.setCurrentPosition(XMOTOR, x)
      stepper.setCurrentPosition(YMOTOR, y)
      advancedServo.setPosition(ZMOTOR,UP_SAMPLE_POSITION)
      advancedServo.setPosition(GRIPPER,GRIPPER_OPEN)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   DataReadWrite.updatePosition(x,y)


def getMotorPositions():
   logger.debug("getMotorPositions")
   xpos=0
   ypos=0
   try:
      xpos=int(stepper.getCurrentPosition(XMOTOR))
      ypos=int(stepper.getCurrentPosition(YMOTOR))
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   return (xpos,ypos)

def getZPosition():
   logger.debug("getXPosition")
   #get current postiopn
   zpos=0
   try:
      zpos=int(advancedServo.getPosition(ZMOTOR))
   except PhidgetException as e:
      logger.debug("Servo Phidget Exception %i: %s" % (e.code, e.details))
      logger.debug("No value means that the servo has not been set to some value. Will assume 0 at this point.")
   return zpos

def getXPosition():
   logger.debug("getXPosition")
   #get current postiopn
   xpos=0
   try:
      xpos=int(stepper.getCurrentPosition(XMOTOR))
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   return xpos  

def getYPosition():
   logger.debug("getYPosition")
   #get current postiopn
   ypos=0
   try:
      ypos=int(stepper.getCurrentPosition(YMOTOR))
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   return ypos

def raiseArm(zup):
   logger.debug("raiseArm: %d",zup)
   ## raise the arm
   zpos=int(advancedServo.getCurrentPosition(ZMOTOR))
   newz=zpos-zup
   try:
      advancedServo.setEngaged(ZMOTOR,True)
      advancedServo.setPosition(ZMOTOR,newz )
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         # print ". . . waiting for the zmotor to stop . . ."
         pass
      sleep(2)
      advancedServo.setEngaged(ZMOTOR, False)
   except PhidgetException as e:
      logger.critical("samplePickUp Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   return newz

def physicallyResetArm():
   logger.debug("physicallyResetArm")
   openGripper()
   ## raise the arm
   try:
      advancedServo.setEngaged(ZMOTOR,True)
      advancedServo.setPosition(ZMOTOR, UP_SAMPLE_POSITION)
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         # print ". . . waiting for the zmotor to stop . . ."
         pass
      sleep(2)
      advancedServo.setEngaged(ZMOTOR, False)
   except PhidgetException as e:
      logger.critical("samplePickUp Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   #set move back to 0
   # need to move current_x - new amount
   try:
      stepper.setEngaged(XMOTOR, True)
      stepper.setTargetPosition(XMOTOR, 0)
      while stepper.getStopped(XMOTOR) !=STOPPED:
         pass
      sleep(2)
      stepper.setEngaged(XMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)

   # make sure y position is correct
   try:
      stepper.setEngaged(YMOTOR, True)
      stepper.setTargetPosition(YMOTOR, 0)
      while stepper.getStopped(YMOTOR) !=STOPPED:
         pass
      sleep(2)
      stepper.setEngaged(YMOTOR, False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)

def lowerArmToSample():
   logger.debug("Lowering arm to sample")
   DOWN_SAMPLE_POSITION=DataReadWrite.getZForSampleLocation(1)
   try:
      advancedServo.setEngaged(0, True)
      advancedServo.setPosition(0,DOWN_SAMPLE_POSITION )
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         pass
      sleep(2)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   try:
      advancedServo.setEngaged(0, False)
      sleep(1)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   sleep(2)

def raiseArmToTop():
   logger.debug("raiseArmToTop")
   try:
      advancedServo.setEngaged(0, True)
      advancedServo.setPosition(0,UP_SAMPLE_POSITION )
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         pass
      sleep(2)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)

   try:
      advancedServo.setEngaged(0, False)
      sleep(1)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   sleep(2)

def lowerArmToBalance():
   logger.debug("lowerArmToBalance")
   DOWN_BALANCE_POSITION_PICKUP=DataReadWrite.getZForBalanceLocation()
   try:
      advancedServo.setEngaged(0, True)
      advancedServo.setPosition(0,DOWN_BALANCE_POSITION_PICKUP )
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         pass
      sleep(2)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)

   try:
      advancedServo.setEngaged(0, False)
      sleep(1)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)


def getMotorPositions():
   logger.debug("getMotorPositions")
   xpos=0
   ypos=0
   try:
      xpos=stepper.getCurrentPosition(XMOTOR)
      ypos=stepper.getCurrentPosition(YMOTOR)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   return xpos,ypos

def getXMotorPosition():
   logger.debug("getXMotorPosition")
   #get current postion
   xpos=0
   try:
      xpos=stepper.getCurrentPosition(XMOTOR)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   return xpos  

def getYMotorPosition():
   logger.debug("getYMotorPosition")
   #get current postiopn
   ypos=0
   try:
      ypos=stepper.getCurrentPosition(YMOTOR)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   return ypos

def armToTop():
   logger.debug("armToTop")
   try:
      advancedServo.setEngaged(0, True)
      advancedServo.setPosition(0, advancedServo.getPositionMax(0))
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         pass
      sleep(2)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   try:
      advancedServo.setEngaged(0, False)
      sleep(1)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)

def bumpXMotorUp(bump):
   logger.debug("bumpXmotorUp")
   currentpos=getAbsoluteXPosition()
   move = stepper.getCurrentPosition(XMOTOR)-int(bump)
   stepper.setEngaged(XMOTOR, True)
   try:
      stepper.setTargetPosition(XMOTOR,move)
      while stepper.getStopped(XMOTOR) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical("Servo 0: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   newpos= getAbsoluteXPosition()
   ###HACKHACKHACKHACK#####
   newpos += 1
   ## right now the turns on the resistor only get about 2/3 of the way before
   ## topping out at 1000. Thus, the numbers get to 0 going forward without any
   ## progress. So Ill take this out for now
   ###HACKHACK##################
   if currentpos==newpos:
      # then there has been no movement
      # so current position hasnt changed
      # so go back to original setting
      logger.debug("No movement so setting the position back...")
      move = stepper.getCurrentPosition(XMOTOR)+int(bump)
      try:
         stepper.setTargetPosition(XMOTOR,move)
         while stepper.getStopped(XMOTOR) != STOPPED:
            pass
         sleep(1)
      except PhidgetException as e:
         logger.critical("Servo 0: Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         exit(1)
   stepper.setEngaged(XMOTOR, False)
   return int(move);

def bumpYMotorLeft(bump):
   logger.debug("bumpYMotorLeft")
   move = stepper.getCurrentPosition(YMOTOR)-int(bump)
   stepper.setEngaged(YMOTOR, True)
   try:
      stepper.setTargetPosition(YMOTOR,move)
      while stepper.getStopped(YMOTOR) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical("Servo 2: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   stepper.setEngaged(YMOTOR, False)
   return move;   

def bumpXMotorDown(bump):
   logger.debug("bumpXMotorDown")
   currentpos= getAbsoluteXPosition()
   stepper.setEngaged(XMOTOR, True)
   logger.debug("start here: %d", int(stepper.getCurrentPosition(XMOTOR)))
   move = stepper.getCurrentPosition(XMOTOR)+int(bump)
   logger.debug( "move to here: %i", move)

   try:
      stepper.setTargetPosition(XMOTOR,move)
      while stepper.getStopped(XMOTOR) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical("Servo 0: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   stepper.setEngaged(XMOTOR, False)
   ### hack -- the clock turns over at 1000 so I have to check to see where the previous position"
   newpos= getAbsoluteXPosition()+1
   ### so removing this function by adding 1
   if (newpos==0):
      logger.debug( "new position is 0: so set this to the 0 point")
      # then there has been no movement
      # so current position hasnt changed
      # so set to 0 position
      M0SetP()
   return move;

def bumpYMotorRight(bump):
   logger.debug("bumpYMotorRight")
   move = stepper.getCurrentPosition(YMOTOR)+int(bump)
   stepper.setEngaged(YMOTOR, True)
   try:
      stepper.setTargetPosition(YMOTOR,move)
      while stepper.getStopped(YMOTOR) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical("Servo 2: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   stepper.setEngaged(YMOTOR, False)
   return move; 

def bumpYMotorNE(bump):
   move = stepper.getCurrentPosition(YMOTOR)+int(bump)
   stepper.setEngaged(YMOTOR, True)
   try:
      stepper.setTargetPosition(YMOTOR,move)
      while stepper.getStopped(YMOTOR) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical("Servo 2: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   stepper.setEngaged(YMOTOR, False)
   return move; 


###Arm Controls
def moveArmToPosition(value):
   logger.debug("moveArmToPosition")
   try:
      advancedServo.setEngaged(0, True)
      advancedServo.setPosition(0, value)
      while advancedServo.getStopped(ZMOTOR) != STOPPED:
         pass
      sleep(2)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   try:
      advancedServo.setEngaged(0, False)
      sleep(1)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)

def KillMotors():
   logger.debug ("Killing Motors and Phidget Objects")
   try:
      stepper.setEngaged(0, False)
      sleep(1)
      stepper.setEngaged(1, False)
      sleep(1)
      stepper.setEngaged(2, False)
      sleep(1)
      advancedServo.setEngaged(0, False)
      stepper.closePhidget()
      advancedServo.closePhidget()
      interfaceKit.closePhidget()
      robotStatus.quit()
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
   return
def Mover(motorNumber,position):
   try:
      MotorMove(motorNumber,position)
   except:
      pass

##Motor Movers
##+numbers go away from the balance    
def M0Mover(val):
   logger.debug ("The input value is: %d", int(val))
   try:
      Mover(0,val)
   except:
      pass
##+numbers go towards the motors    
def M1Mover(val):
   logger.debug ("The input value is: %d", int(val))
   MV.set(val)
   try:
      Mover(1,val)
   except:
      pass
##+numbers go up
def M2Mover(val):
   logger.debug ("The input value is: %d", int(val))
   try:
      Mover(2,val)
   except:
      pass

#0 out Position
def M0SetP():
   logger.debug ("Current position of Motor 0 is now start position")
   try:
      MotorPosition(0)
   except:
      pass

def M1SetP():
   logger.debug ("Current position of Motor 1 is now start position")
   try:
      MotorPosition(1)
   except:
      pass

def M2SetP():
   logger.debug ("Current position of Motor 2 is now start position")  
   try:
      MotorPosition(2)
   except:
      pass

def MotorPosition(motorNumber):
   logger.debug("MotorPosition: %d", int(motorNumber))
   try:
      logger.debug("Set as start position for motor %d", int(motorNumber))
      stepper.setCurrentPosition(motorNumber, 0)
      sleep(1)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)

def MotorMove(motorNumber,movePosition):
   if movePosition>1500:
      value=DataReadWrite.openBalanceDoor()

   try:
      logger.debug("Set the motor as engaged...")
      stepper.setEngaged(int(motorNumber), True)
      sleep(1)
      stepper.setTargetPosition(int(motorNumber),int(movePosition))
      while stepper.getStopped(int(motorNumber)) != STOPPED:
         pass
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   logger.debug ("Finished Move...")

def backToMainWindow():
   return

def KillProgram():
   return

def alertWindow(message, alert):
   logger.error(message)
   alert.deiconify()
   Message(alert,text=message, bg='red', fg='ivory', relief=GROOVE).grid(row=0,column=0,sticky=W+E+N+S)
   Button(alert, text="Continue", command=backToMainWindow).grid(row=1,column=0)
   Button(alert, text="Quit", command=KillProgram).grid(row=1,column=1)
   exit(1)

def resetMotorsToZeroPosition():
   currentAbsXPosition= getAbsoluteXPosition()
   currentAbsYPosition= getAbsoluteYPosition()
   xMotor=stepper.getCurrentPosition(XMOTOR)
   yMotor=stepper.getCurrentPosition(YMOTOR)
   oldxpos=0
   oldypos=0
   newxpos=0
   newypos=0
   stepper.setEngaged(XMOTOR, True)
   bump=10
   diff=1
   move=stepper.getCurrentPosition(XMOTOR)+bump

   logger.debug("Current Motors at X: %d Y: %d" %(xMotor,yMotor))
   logger.debug("Current Abs Position at X: %d Y: %d " % (currentAbsXPosition,currentAbsYPosition))
   try:
      stepper.setTargetPosition(XMOTOR,move)
      while stepper.getStopped(XMOTOR) != STOPPED:
         pass
      sleep(1)
      while (getAbsoluteXPosition()-1 > MINIMUM_X_VALUE):
         oldxpos=getAbsoluteXPosition()
         logger.debug("Now X Motor at X: %d Y: %d" %(stepper.getCurrentPosition(XMOTOR),stepper.getCurrentPosition(YMOTOR)))
         logger.debug("Now Abs Position at X: %d Y: %d " % (getAbsoluteXPosition(),getAbsoluteYPosition()))
         move=stepper.getCurrentPosition(XMOTOR)+bump

         logger.debug("Bumping XMOTOR: %d" % (move))
         stepper.setTargetPosition(XMOTOR,move)
         while stepper.getStopped(XMOTOR) != STOPPED:
            pass
         sleep(1)
         newxpos=getAbsoluteXPosition()
         diff = abs(newxpos - oldxpos)
         logger.debug("Now at X: %d Y: %d" %(stepper.getCurrentPosition(XMOTOR),stepper.getCurrentPosition(YMOTOR)))
         logger.debug("Now Abs Position at X: %d Y: %d " % (getAbsoluteXPosition(),getAbsoluteYPosition()))
   except PhidgetException as e:
      logger.critical("Stepper 0: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      return False
   stepper.setEngaged(XMOTOR, False)
   
   logger.debug("Current Motors at X: %d Y: %d" %(xMotor,yMotor))
   logger.debug("Current Abs Position at X: %d Y: %d " % (currentAbsXPosition,currentAbsYPosition))
   diff=1
   move=stepper.getCurrentPosition(YMOTOR)-bump
   stepper.setEngaged(YMOTOR, True)
   try:
      stepper.setTargetPosition(YMOTOR,move)
      while stepper.getStopped(YMOTOR) != STOPPED:
         pass
      sleep(1)
      while (getAbsoluteYPosition()-1 > MINIMUM_Y_VALUE):
         oldypos=getAbsoluteYPosition()
         logger.debug("Now Y Motor at X: %d Y: %d" %(stepper.getCurrentPosition(XMOTOR),stepper.getCurrentPosition(YMOTOR)))
         logger.debug("Now Abs Position at X: %d Y: %d " % (getAbsoluteXPosition(),getAbsoluteYPosition()))         
         move=stepper.getCurrentPosition(YMOTOR)-bump
         while stepper.getStopped(YMOTOR) != STOPPED:
            pass
         sleep(1)
         logger.debug("Bumping YMOTOR: %d" % (move))
         stepper.setTargetPosition(YMOTOR,move)
         newypos=getAbsoluteYPosition()
         diff = abs(newypos - oldypos)
         logger.debug("Now Y Motor at X: %d Y: %d" %(stepper.getCurrentPosition(XMOTOR),stepper.getCurrentPosition(YMOTOR)))
         logger.debug("Now Abs Position at X: %d Y: %d " % (getAbsoluteXPosition(),getAbsoluteYPosition()))
   except PhidgetException as e:
      logger.critical("Stepper Y: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      return False
   stepper.setEngaged(YMOTOR, False)
   ## reset the Absolute Zero points
   value = setAbsZeroXY(getAbsoluteXPosition(),getAbsoluteYPosition())
   ## now set the stepper motors to 0
   value = resetValuesToZero()
   
   return True;

def initializeRobot():
   global advancedServo
   global stepper
   global interfaceKit
   ############INITIALIZATION########################
   ###Create Stepper and Servo Objects
   try:
      advancedServo = AdvancedServo()
   except RuntimeError as e:
      logger.critical("Runtime Exception: %s" % e.details)
      logger.critical("Exiting....")
      return False;
   try:
      stepper = Stepper()
   except RuntimeError as e:
      logger.critical("Runtime Exception: %s" % e.details)
      logger.critical("Exiting....")
      return False;
   #stack to keep current values in
   currentList = [0,0,0,0,0,0,0,0]
   velocityList = [0,0,0,0,0,0,0,0]
   
   try:
      advancedServo.openPhidget()
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      return False;
   
   logger.debug("Waiting for Arm to attach....")
   
   try:
      advancedServo.waitForAttach(10000)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      try:
         advancedServo.closePhidget()
      except PhidgetException as e:
         logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         return False;
      logger.critical("Exiting....")
      return False;
   
   logger.debug("Opening phidget object for steppers...")
   try:
      stepper.openPhidget()
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      return False;
   
   logger.debug("Waiting for stepper motors to attach....")
   
   try:
      stepper.waitForAttach(1000)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
   
   try:
      logger.debug("Setting the servo type for motor 0 to PHIDGET_SERVO_FIRGELLI_L12_100_100_06_R ")
      advancedServo.setServoType(ZMOTOR, 17 )
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      return False;
   
   try:
      logger.debug("Setting the servo type for motor 1 to PHIDGET_SERVO_HITEC_HS422")
      advancedServo.setServoType(GRIPPER, ServoTypes.PHIDGET_SERVO_HITEC_HS422)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      return False;
   
   logger.debug("Create an interfacekit object")
   try:
      interfaceKit = InterfaceKit()
   except RuntimeError as e:
      logger.critical("Runtime Exception: %s" % e.details)
      logger.critical("Exiting....")
      return False;      
   
   logger.debug("Opening phidget (sensor) object....")
   
   try:
      interfaceKit.openPhidget()
   except PhidgetException as e:
      logger.critical("Sensor Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      return False;
  
   logger.debug("Waiting for attach....")
   
   try:
       interfaceKit.waitForAttach(10000)
   except PhidgetException as e:
       print("Phidget Exception %i: %s" % (e.code, e.details))
       try:
           interfaceKit.closePhidget()
       except PhidgetException as e:
           print("Phidget Exception %i: %s" % (e.code, e.details))
           print("Exiting....")
           exit(1)
       print("Exiting....")
       exit(1)

initializeRobot()