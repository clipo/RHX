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
#import msvcrt
import os, sys
from Tkinter import *
from numpy import *
import math
import communication
import easygui

logger = logging.getLogger("AutoSampler-xyzRobot")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
today_date = datetime.today()
datestring = today_date.strftime("%Y-%m-%d-%H-%M")
debugfilename=""
if sys.platform=="darwin":
   debugfilename = "/Users/Clipo/Dropbox/Rehydroxylation/Logger/Logs/rhx-xyzRobot_" + datestring + "_debug.log"
else:
   debugfilename = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Logs/rhx-xyzRobot" + datestring + "_debug.log"

fh = logging.FileHandler(debugfilename)
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
## get the set of connections for reading the balance, etc.
import DataReadWrite
#import crucible_tracker

# object that tracks the XY position of the robot arm (encoders)
import Location

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs,OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Devices.Stepper import Stepper
from Phidgets.Devices.AdvancedServo import AdvancedServo
from Phidgets.Devices.Servo import ServoTypes
from Phidgets.Devices.InterfaceKit import InterfaceKit

########################################
## CONSTANTS ###########################
########################################
XTOLERANCE=5000    ## distance from recorded  X coordinates to actual coordinates to determine if the arm is too far
# away
YTOLERANCE=5000    ## distance from recorded Y coordinates to actual coordinates to determine if the arm is too far
# away

## interface number 8/8/8 for different sensors
HI_REZ_TEMPERATURE=4
TEMPERATURE = 6
HUMIDITY = 7
GRIPPERSENSOR = 3

XSTOPPER=2        ## interface for the x stop sensor
YSTOPPER=1        ## interface for the y stop sensor
ZSTOPPER=0        ## interface for the z stop sensor
#########################

XDISTANCE=-1
YDISTANCE=-1
COUNTS_FOR_STATS=3


# Absolute Positions of Zero, Zero
MINIMUM_X_VALUE  = 0
MINIMUM_Y_VALUE = 0

YMOTOR_OK_TO_CLOSE_DOOR = 160000  ## value of x for closing door

## Stepper Motor Numbers
XMOTOR=269450
YMOTOR=269153
ZMOTOR=269200



X=0
Y=1

STOPPED=1
MOVING=0

UP_SAMPLE_POSITION=0
UP_BALANCE_POSITION=0

#spaces betwen sample locations going along the length of the sampler (horizontal)
HORIZONTAL_SPACING = 8500

#space between sample locations going away from the sampler (vertical)
VERTICAL_SPACING = 8500

#how much to move in a "bump"
BUMP=2000

# coordinates for the gripper position
GRIPPER=0  ## servo number
GRIPPER_CLOSED = 5
GRIPPER_OPEN = 130
COUNTS_FOR_STATS = 3

# settings for light
LIGHT=1  ## servo number
LIGHT_ON = 220
LIGHT_OFF = 0

## Default values for the motor velocities
XMOTORVELOCITYLIMIT=10000
YMOTORVELOCITYLIMIT=10000
ZMOTORVELOCITYLIMIT=15000

## Default values for the motor velocities
XMOTORCURRENTLIMIT=2.0
YMOTORCURRENTLIMIT=2.0
ZMOTORCURRENTLIMIT=2.0

## Location Object (encoders)
myLocation=Location.Location()

def getXStepper():
   return xstepper

def getYStepper():
   return ystepper

def getZStepper():
   return zstepper

def getAdvancedServo():
   return advancedServo

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
      return False
   return True

def turnLasersOff():
   try:
      sensor=interfaceKit.setOutputState(5,False)
      sensor=interfaceKit.setOutputState(6,False)
   except PhidgetException as e:
      logger.critical("Error: %i: %s" % (e.code,e.details))
      return False;
   return True;

def atXZero():
   sensor=interfaceKit.getInputState(XSTOPPER)
   #print "Sensor X: ", sensor
   if sensor is False:
      return "FALSE"
   else:
      return "TRUE"

def atYZero():
   sensor=0
   sensor=interfaceKit.getInputState(YSTOPPER)
   #print "Sensor Y: ", sensor
   if sensor is False:
      return "FALSE"
   else:
      return "TRUE"

def atZZero():
   sensor=0
   sensor=interfaceKit.getInputState(ZSTOPPER)
   #print "Sensor Z: ", sensor
   if sensor is False:
      return "FALSE"
   else:
      return "TRUE"

def getXCoordinate():
   return myLocation.getXPosition()

def getYCoordinate():
   return myLocation.getYPosition()

def getCurrentXYCoordinates():
   X=getXCoordinate()
   Y=getYCoordinate()
   return X,Y

def setXYCoordinatesForPosition(position,X,Y):
   value=DataReadWrite.updateXYCoordinatesForSampleLocation(position,X,Y)
   return True

def getAbsoluteXPosition():
   return myLocation.getXPosition()

def getAbsoluteYPosition():
   return myLocation.getYPosition()

def getAbsoluteZPosition():
   return myLocation.getZPosition()

def getXZero():
   try:
      sensor = interfaceKit.getSensorValue(XSTOPPER)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))      
      return False
   return sensor

def getYZero():
   try:
      sensor = interfaceKit.getSensorValue(YSTOPPER)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))      
      return False
   return sensor

def getZZero():
   try:
      sensor = interfaceKit.getInputState(0)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))
      return False
   return sensor


def getTemperature():   
   try:
      value = interfaceKit.getSensorRawValue(HI_REZ_TEMPERATURE)/4.095
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))      
      return False
   sensor = double((value*0.222222222222)-61.1111111111+2.5) ## 2.5 added to match madgetech
   return sensor

def getZTopLimit():
   try:
      value = interfaceKit.getInputState(0)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))
      return False
   return value

def getHumidity():
   try:
      value = interfaceKit.getSensorRawValue(HUMIDITY)/4.095
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))
      return False
   sensor = double((value*0.1906)-40.20000-5.92) ## 5.22 added to match madgetech
   return sensor

def isGripperHoldingSomething():
   try:
      sensor2 = interfaceKit.getSensorValue(GRIPPERSENSOR)
   except PhidgetException as e:
      logger.critical("Error:  %i: %s" % (e.code,e.details))      
      sys.exit()
   if sensor2>0:
      return True
   else:
      return False

def turnLightOff():
   logger.debug( "turnLightOn")
   #  Set the light to be on
   try:
      advancedServo.setPosition(LIGHT, LIGHT_OFF)
      while advancedServo.getStopped(LIGHT) !=STOPPED:
         pass
      advancedServo.setEngaged(LIGHT, False)
   except PhidgetException as e:
      logger.critical("Gripper Open Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   return True

def turnLightOn():
   logger.debug( "turnLightOff")
   #  Set the light to be on
   try:
      advancedServo.setEngaged(LIGHT, True)
      advancedServo.setPosition(LIGHT, LIGHT_ON)
      while advancedServo.getStopped(LIGHT) !=STOPPED:
         pass
   except PhidgetException as e:
      logger.critical("Gripper Open Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   return True

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
      sys.exit()
   return True;

def getGripperPosition():
   logger.debug( "openGripper:  now open gripper")
   #  Set the gripper to be open
   return advancedServo.getPosition(GRIPPER)

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
      sys.exit()
   sleep(1)
   return True;

def setAbsZeroXY():
   myLocation.setXZero()
   myLocation.setYZero()
   resetCoordinates(0,0)
   return True

def setXCoordinate(value):
   myLocation.setXPosition(value)
   return True

def setYCoordinate(value):
   myLocation.setYPosition(value)
   return True

def setZCoordinate(value):
   myLocation.setZPosition(value)
   return True

## home is defined as 0,0 -- the point in the far left corner        
def goHome():
   logger.debug("goHome:  Now going to the home position.")


   #####################################################################
   #####################################################################
   ## Z axis -- we need to make sure we are up to the top before trying
   ## to move anywhere - otherwise we will bump or drag
   ## first raise the gripper to the top
   #####################################################################

   if getZZero()==False:
      zstepper.setEngaged(0,True)
      try:
         zstepper.setTargetPosition(0,0)
         while zstepper.getStopped(0) !=STOPPED:
            pass
         sleep(1)
      except PhidgetException as e:
         logger.critical("Stepper 0: Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         return False

   ####################################################################
   ## go up until hit the zero switch. ideally we are there already
   #####################################################################
   # reset attempt counter. Only try this 30 times before giving up.
   attempts=0
   while atZZero()=="FALSE" and attempts < 50:
      moveZUntilZero()
      attempts += 1

   if atZZero()=="TRUE":
      myLocation.setZPosition(0)
      zstepper.setCurrentPosition(0,0)
   else:
      # stop -- couldnt find zero!
      return False

   ####################################################################
   ## First do the Y axis -- this way we can be certain to get back to
   ## the home axis before moving the X axis since the X can be
   ## blocked by the balance. Safer this way.
   ####################################################################
   ### Y Motor
   if getYZero()==False:
      try:
         ystepper.setEngaged(0,True)
         ystepper.setTargetPosition(0,0)
         while ystepper.getStopped(0) !=STOPPED:
            sleep(1)
            pass
         sleep(1)
         ystepper.setEngaged(0,False)
      except PhidgetException as e:
         logger.critical("Home Position - Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         sys.exit(1)

      ystepper.setEngaged(0,False)
      ystepper.setCurrentPosition(0,0)
      myLocation.setYPosition(0)

   ## Now iterate back along the Y axis until we hit the YZero switch
   ## ideally we will already be there. This just allows us
   ## to hopefully solve problems that arise if we are not at the
   ## Zero already
   #####################################################################
   ## check to see if we are as far as we can be in the Y axis (motor 2)
   #####################################################################

   # reset attempt counter. Only try this 30 times before giving up.
   attempts=0
   while (atYZero()=="FALSE") & (attempts < 30):
      moveYUntilZero()
      attempts+=1

   if atYZero()=="TRUE":
      ystepper.setCurrentPosition(0,0)
      myLocation.setYPosition(0)
   else:
      # stop -- couldnt find zero!
      return False


   ####################################################################
   ### Now do the X axis which is the axis perpendicular to the long axis
   ### This can be potentially blocked by the balance but we are now
   ### reasonably sure we are farther to the left than the balance location
   #####################################################################
   if getXZero()==False:
      try:
         xstepper.setEngaged(0,True)
         xstepper.setTargetPosition(0,0)
         while xstepper.getStopped(0) !=STOPPED:
            sleep(.5)
            pass
         sleep(1)
         xstepper.setEngaged(0,False)
      except PhidgetException as e:
         logger.critical("Home Position - Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         sys.exit()
      sleep(1)

   ####################################################################
   ## now check to see if weve reached the zero point of the x axis.
   ## if not, then move until we are there.
   ##################################
   # reset attempt counter. Only try this 30 times before giving up.

   attempts=0
   while (atXZero()=="FALSE") & (attempts < 30):
      moveXUntilZero()
      attempts+=1

   if atXZero()=="TRUE":
      xstepper.setCurrentPosition(0,0)
      myLocation.setXPosition(0)
   else:
      # stop -- couldnt find zero!
      return False

   logger.debug("Update the coordinates of the arm in terms of the motor")
   DataReadWrite.updatePosition(getXPosition(),getYPosition(),getZPosition())
   ## reset the Absolute Zero points
   logger.debug ("Reset the coordinates of the home position")
   ## set encoders to zero
   myLocation.setXYZero()

   value = setAbsZeroXY()
   value=setXMotorPosition(0)
   value=setYMotorPosition(0)
   value=setZMotorPosition(0)
   myLocation.setXPosition(0)
   myLocation.setYPosition(0)
   myLocation.setZPosition(0)

   return True

def moveMotorXToPosition(pos):
   try:
      xstepper.setEngaged( 0,True)
      xstepper.setTargetPosition(0,pos)
      while xstepper.getStopped(0) !=STOPPED and atXZero() == "FALSE":
         pass
      sleep(2)
      xstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   return pos

def moveMotorYToPosition(pos):
   try:
      ystepper.setEngaged( 0,True)
      ystepper.setTargetPosition(0,pos)
      while ystepper.getStopped(0) !=STOPPED and atYZero() == "FALSE":
         pass
      sleep(2)
      ystepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   return pos

def moveMotorZToPosition(pos):
   try:
      zstepper.setEngaged( 0,True)
      zstepper.setTargetPosition(0,pos)
      while zstepper.getStopped(0) !=STOPPED and atZZero() == "FALSE":
         pass
      sleep(2)
      zstepper.setCurrentPosition(0,pos)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   myLocation.setZPosition(pos)
   return pos

def moveZUntilZero():
   zstepper.setEngaged(0,True)
   try:
      zstepper.setTargetPosition(0,0)
      while zstepper.getStopped(0) !=STOPPED and atZZero() == "FALSE":
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical("Stepper 0: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      return False

   bump=1000
   ####################################################################
   attempts=0
   zstate=atZZero()
   while zstate == "FALSE" and attempts < 1000:
      #print "xstate:",xstate
      #print "At X Zero", atXZero()
      move=zstepper.getCurrentPosition(0)-bump
      attempts+=1
      #print "move: ",move
      try:
         zstepper.setTargetPosition(0,move)
         while zstepper.getStopped(0) !=STOPPED:
            pass
         zstate=atZZero()
         sleep(1)
      except PhidgetException as e:
         logger.critical("Stepper 0: Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         return False
      zstate=atZZero()
   #myLocation.setZZero()
   zstepper.setEngaged(0,False)

## home is defined as 0,0 -- the point in the far left corner
def moveXUntilZero():
   logger.debug("goHome:  Now moving until X is zero.")
   xstepper.setEngaged(0,True)
   ## check to see if we are as far as we can be in the X axis (motor 0)
   bump=2000

   ########################################
   attempts=0
   while (atXZero()=="FALSE") & (attempts < 30):
      #print "xstate:",xstate
      #print "At X Zero", atXZero()
      move=xstepper.getCurrentPosition(0)-bump
      attempts+=1
      #print "move: ",move
      try:
         xstepper.setTargetPosition(0,move)
         while xstepper.getStopped(0) !=STOPPED:
            pass
         sleep(1)
      except PhidgetException as e:
         logger.critical("Stepper 0: Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         return False
   xstepper.setEngaged(0, False)
   logger.debug ("Reset the coordinates of the X position")
   ## set encoders to zero
   value=setXMotorPosition(0)
   myLocation.setXZero()
   return True

def moveYUntilZero():
   logger.debug("goHome:  Now moving until Y is zero.")
   #####################################################################
   ystepper.setEngaged(0,True)
   ## check to see if we are as far as we can be in the Y axis (motor 2)

   attempts=0
   bump=2000
   while (atYZero()=="FALSE") & (attempts<500):
      #print "ystate:",ystate
      #print "At Y Zero", atYZero()
      move=ystepper.getCurrentPosition(0)-bump
      #print "move: ",move
      try:
         ystepper.setTargetPosition(0,move)
         while ystepper.getStopped(0) !=STOPPED:
            sleep(1)
            pass
         sleep(1)
      except PhidgetException as e:
         logger.critical("Stepper 0: Phidget Exception %i: %s" % (e.code, e.details))
         logger.critical("Exiting....")
         return False

   ystepper.setEngaged(0,False)
   logger.debug("Update the coordinates of the arm in terms of the motor")
   DataReadWrite.updatePosition(getXPosition(),getYPosition(),getZPosition())
   ## reset the Absolute Zero points
   logger.debug ("Reset the coordinates of the Y position")
   ## set encoders to zero
   myLocation.setYZero()
   value=setYMotorPosition(0)
   return True

def goToSamplePosition(position, startWindow):
   logger.debug("goToSamplePosition( %d) ",position)
   ## first go home -- or check to see we are there
   goHome()

   logger.debug("Now we are home... We are now going to go to sample position: %d",position)
   xpos=getXPosition()
   ypos=getYPosition()
   zpos=myLocation.getZPosition()
   if zpos>UP_SAMPLE_POSITION:  ### if not at top, then stop!!!
      return;
   newXpos=0
   newYpos=0
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))
   (newXpos,newYpos)=DataReadWrite.getXYForSampleLocation(position)
   logger.debug("Going to X: %d and Y: %d" %(newXpos,newYpos))

   if position<0:
      logger.error("Invalid position: %d ",position)
      return False

   ## now move to the position with the X and Y coordinates
   try:
      #print("Now move to X:  %d",newXpos)
      logger.debug("Now move to X:  %d",newXpos)
      xstepper.setEngaged(0,True)
      xstepper.setTargetPosition(0,newXpos)
      while xstepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      DataReadWrite.updatePosition(getXPosition(),getYPosition(),getZPosition())
      logger.debug("sleep to make sure this is complete..")
      xstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   sleep(2)
   try:
      ystepper.setEngaged(0,True)
      #print("Now move to Y: %d ",newYpos)
      logger.debug("Now move to Y: %d ",newYpos)
      ystepper.setTargetPosition(0,newYpos)
      while ystepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      ystepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   #print("We are now at x: %i and y: %i and z: %i" % (getXPosition(),getYPosition(),getZPosition()))
   logger.debug("We are now at x: %i and y: %i and z: %i" % (getXPosition(),getYPosition(),getZPosition()))
   DataReadWrite.updatePosition(getXPosition(),getYPosition(),getZPosition())
   ## for now only do the refine position for the crucibles in the rack -- not the balance
   if startWindow<>1:
      logger.debug("Now will refine the location based on difference in encoder locations")
      refineSamplePosition(position)
      logger.debug("Completed arm position refinement! whoohoo!")
   else:
      logger.debug("Since we are coming from the start window (startwindow=1), then do not do refinement")
      pass
   return True;

def refineSamplePosition(position):
   ####### NOTE TAKEN OUT FOR NOW #####
   return
   ####################################

   ## should only use this when the position is close
   logger.debug("refine the position over the crucible at position %d",position)
   xpos,ypos=myLocation.getPositions()
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))

   ## get the center of the crucible
   xCrucible,yCrucible=DataReadWrite.getXYCoordinatesForSampleLocation(position)
   xdiff=xpos-xCrucible  ## larger means to the left - so bump down
   ydiff=ypos-yCrucible ## larger means forward so bump right
   # x and y here are the pixels needed to move to get to the center of the crucibles.

   # first check to see if we are even close
   # if we are not within tolerance units in either direction
   # note: XTOLERANCE and YTOLERANCE are defined globally at the top of the file

   if xdiff > XTOLERANCE or ydiff > YTOLERANCE:
      logger.debug("Blargh! the arm is XDIFF: %d and YDIFF: %d which is greater than XTOLERANCE: %d or YTOLERANCE: %d "% (
         xdiff, ydiff, XTOLERANCE,YTOLERANCE ))
      alertWindow("Arm is too far away from the intended destination. Stopping...")
      sys.exit()


   ## first fix the X direction
   bump=1000
   if xdiff>0:
      while (abs(xpos-xCrucible)>0):
         bumpXMotorDown(bump)
         xpos,ypos=myLocation.getPositions()
         sleep(1)

   xpos,ypos=myLocation.getPositions()
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))
   xdiff=xpos-xCrucible  ## larger means to the left - so bump down
   ydiff=ypos-yCrucible ## larger means forward so bump right

   if xdiff<0:
      while (abs(xpos-xCrucible)>0):
         bumpXMotorUp(bump)
         xpos,ypos=myLocation.getPositions()
         sleep(1)

   xpos,ypos=myLocation.getPositions()
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))
   xdiff=xpos-xCrucible  ## larger means to the left - so bump down
   ydiff=ypos-yCrucible ## larger means forward so bump right

   ## now y
   if ydiff>0:
      while (abs(ypos-yCrucible)>0):
         bumpYMotorLeft(bump)
         xpos,ypos=myLocation.getPositions()
         sleep(1)

   xpos,ypos=myLocation.getPositions()
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))
   xdiff=xpos-xCrucible  ## larger means to the left - so bump down
   ydiff=ypos-yCrucible ## larger means forward so bump right

   if ydiff<0:
      while (abs(ypos-yCrucible)<0):
         bumpYMotorRight(bump)
         xpos,ypos=myLocation.getPositions()
         sleep(1)

   xpos,ypos=myLocation.getPositions()
   xdiff=xpos-xCrucible  ## larger means to the left - so bump down
   ydiff=ypos-yCrucible ## larger means forward so bump right
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))
   logger.debug("Difference in X: %d Y: %d" % (xdiff,ydiff))

   return True

def refineInsideBalancePosition():
   ####### NOTE TAKEN OUT FOR NOW #####
   return
   ####################################
   ## should only use this when the position is close
   logger.debug("refine the position over the crucible at the balance")
   xpos,ypos=myLocation.getPositions()
   logger.debug("We are now at these coordinates according to the encoders:  x: %d y: %d" % (xpos,ypos))
   ## get the center of the crucible
   xCrucible,yCrucible=DataReadWrite.getXYCoordinatesForBalance("inside")
   logger.debug("The balance is at x: %d y: %d" % (xCrucible,yCrucible))
   xdiff=xpos-xCrucible  ## larger means to the left - so bump down
   ydiff=ypos-yCrucible ## larger means forward so bump right
   # x and y here are the pixels needed to move to get to the center of the crucibles.
   logger.debug("The difference is x: %d y: %d" % (xdiff,ydiff))

   # first check to see if we are even close
   # if we are not within tolerance units in either direction
   # note: XTOLERANCE and YTOLERANCE are defined globally at the top of the file

   if xdiff > XTOLERANCE or ydiff > YTOLERANCE:
      logger.debug("Blargh! the arm is XDIFF: %d and YDIFF: %d which is greater than XTOLERANCE: %d or YTOLERANCE: %d "% (
         xdiff, ydiff, XTOLERANCE,YTOLERANCE ))
      alertWindow("Arm is too far away from the intended destination. Stopping...")
      sys.exit()
   logger.debug("now moving x to get to %d" % xdiff)
   ## first fix the X direction
   bump=500
   logger.debug("first check when xdiff is greater than zero. xdiff: %d " % xdiff)
   if xdiff>0:
      while (abs(xpos-xCrucible)>0):
         bumpXMotorDown(bump)
         xpos,ypos=myLocation.getPositions()
         logger.debug("now moving x from %d to %d" % (xpos,xCrucible))
         logger.debug("abs difference in x is %d ",abs(xpos-xCrucible))
         sleep(1)
   logger.debug("Done with X since we are: %d and the crucible is: %d" % (xpos,xCrucible))
   xpos,ypos=myLocation.getPositions()
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))
   xdiff=xpos-xCrucible  ## larger means to the left - so bump down
   ydiff=ypos-yCrucible ## larger means forward so bump right
   ogger.debug("now check when xdiff is less than zero. xdiff: %d " % xdiff)
   if xdiff<0:
      while (abs(xpos-xCrucible)>0):
         bumpXMotorUp(bump)
         xpos,ypos=myLocation.getPositions()
         logger.debug("now moving x from %d to %d" % (xpos,xCrucible))
         logger.debug("abs difference in x is %d ",abs(xpos-xCrucible))
         sleep(1)

   xpos,ypos=myLocation.getPositions()
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))
   xdiff=xpos-xCrucible  ## larger means to the left - so bump down
   ydiff=ypos-yCrucible ## larger means forward so bump right
   logger.debug("Now check y when ydiff is greater than zero. ydiff: %d " % ydiff)
   ## now y
   if ydiff>0:
      while (abs(ypos-yCrucible)>0):
         bumpYMotorLeft(bump)
         xpos,ypos=myLocation.getPositions()
         logger.debug("now moving y from %d to %d" % (ypos,yCrucible))
         logger.debug("abs difference in y is %d ",abs(ypos-yCrucible))
         sleep(1)

   xpos,ypos=myLocation.getPositions()
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))
   xdiff=xpos-xCrucible  ## larger means to the left - so bump down
   ydiff=ypos-yCrucible ## larger means forward so bump right
   logger.debug("Now check y when ydiff is less than zero. ydiff: %d " % ydiff)
   if ydiff<0:
      while (abs(ypos-yCrucible)<0):
         bumpYMotorRight(bump)
         xpos,ypos=myLocation.getPositions()
         logger.debug("now moving y from %d to %d" % (ypos,yCrucible))
         logger.debug("abs difference in y is %d ",abs(ypos-yCrucible))
         sleep(1)

   xpos,ypos=myLocation.getPositions()
   xdiff=xpos-xCrucible  ## larger means to the left - so bump down
   ydiff=ypos-yCrucible ## larger means forward so bump right
   logger.debug("We are now at x: %d y: %d" % (xpos,ypos))
   logger.debug("Difference in X: %d Y: %d" % (xdiff,ydiff))

   return True


def raiseToTop():
   logger.debug("raiseToTop")
   ## lower arm to sample
   logger.debug("now raising the arm down to the sample")
   newZpos = UP_SAMPLE_POSITION
   try:
      zstepper.setEngaged(0,True)
      logger.debug("Now move to Y: %d ",newZpos)
      zstepper.setTargetPosition(0,newZpos)
      while zstepper.getStopped(0) !=STOPPED and getZTopLimit() is False:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   return True;

def samplePickUp():
   logger.debug("samplePickUp")
   ## make sure grippers are open
   logger.debug("First make sure grippers are open...")
   openGripper()
   ## lower arm to sample
   logger.debug("now move the arm down to the sample")
   DOWN_SAMPLE_POSITION=int(DataReadWrite.getZForSampleLocation(1))
   try:
      zstepper.setEngaged(0,True)
      logger.debug("Now move to Z: %d ",DOWN_SAMPLE_POSITION)
      zstepper.setTargetPosition(0,DOWN_SAMPLE_POSITION)
      while zstepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()

   sleep(1)
   ## close grippper
   logger.debug ("Close gripper to value: %i ",GRIPPER_CLOSED)
   closeGripper()
   sleep(1)

   logger.debug ("Now raise the arm...")
   ## raise the arm

   try:
      zstepper.setEngaged( 0,True)
      logger.debug("Now move to Z: %d ",UP_SAMPLE_POSITION)
      zstepper.setTargetPosition(0,UP_SAMPLE_POSITION)
      while zstepper.getStopped(0) !=STOPPED and getZTopLimit() is False:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   sleep(2)
   return True

def samplePutDown():
   logger.debug("samplePutDown")
   DOWN_SAMPLE_POSITION=int(DataReadWrite.getZForSampleLocation(1))
   try:
      zstepper.setEngaged(0,True)
      logger.debug("Now move to Z: %d ",DOWN_SAMPLE_POSITION)
      zstepper.setTargetPosition(0,DOWN_SAMPLE_POSITION)
      while zstepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()

   #open gripper
   openGripper()
   sleep(2)

   #raise the arum
   try:
      zstepper.setEngaged(0,True)
      logger.debug("Now move to Z: %d ",UP_SAMPLE_POSITION)
      zstepper.setTargetPosition(0,UP_SAMPLE_POSITION)
      while zstepper.getStopped(0) !=STOPPED and getZTopLimit() is False:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   sleep(2)

   return True;

def goToOutsideBalanceFromInside():
   logger.debug("goToOutsideBalanceFromInside")
   ## make sure the door is open!!

   xBalance=0
   yBalance=0
   (xBalance,yBalance)=DataReadWrite.getXYForOutsideBalance()
   ## First Y

   try:
      ystepper.setEngaged(0,True)
      ystepper.setTargetPosition(0,yBalance)
      while ystepper.getStopped(0) !=STOPPED:
         pass
      sleep(1)
      ystepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   DataReadWrite.updatePosition(getXPosition(),getYPosition(),getZPosition())
   #set x axis -- move it to point outside...
   sleep(2)

   ## Then X
   try:
      xstepper.setEngaged(0,True)
      xstepper.setTargetPosition(0,xBalance)
      while xstepper.getStopped(0) !=STOPPED:
         pass
      sleep(1)
      xstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   DataReadWrite.updatePosition(getXPosition(),getYPosition(),getZPosition())
   sleep(2)

   if (getYMotorPosition() < YMOTOR_OK_TO_CLOSE_DOOR): ### Change this value
      DataReadWrite.closeBalanceDoor()
   return True;

def goToOutsideBalanceFromOutside():
   logger.debug("goToOutsideBalanceFromOutside")

   xBalance=0
   yBalance=0
   (xBalance,yBalance)=DataReadWrite.getXYForOutsideBalance()

   ## make sure the door is open!!
   DataReadWrite.openBalanceDoor()
   logger.debug("first move the y axis to %d", yBalance)
   ## first line up the Y axis arm 
   try:
      ystepper.setEngaged( 0,True)
      ystepper.setTargetPosition(0,yBalance)
      while ystepper.getStopped(0) != STOPPED:
         pass
      sleep(1)
      ystepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   sleep(2)
   logger.debug("now located at x: %d y: %d z: %d" % (getXPosition(),getYPosition(),getZPosition()))
   DataReadWrite.updatePosition(getXPosition(),getYPosition(),getZPosition())
   logger.debug("now move the x-asis to %d", xBalance)
   ## now move to the point just outside of the balance with the X axis
   try:
      xstepper.setEngaged(0,True)
      xstepper.setTargetPosition(0,xBalance)
      while xstepper.getStopped(0) !=STOPPED:
         pass
      sleep(1)
      xstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   logger.debug("now located at x: %d y: %d z: %d" % (getXPosition(),getYPosition(),getZPosition()))
   DataReadWrite.updatePosition(getXPosition(),getYPosition(),getZPosition())
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
   (xBalance,yBalance)=DataReadWrite.getXYForInsideBalance()

   logger.debug( "now moving x motor to position: %d", xBalance)
   try:
      xstepper.setEngaged( 0,True)
      xstepper.setTargetPosition(0,xBalance)
      while xstepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      xstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   sleep(2)
   logger.debug("now located at x: %d y: %d z: %d" % (getXPosition(),getYPosition(),getZPosition()))
   DataReadWrite.updatePosition(getXPosition(),getYPosition(),getZPosition())

   logger.debug("adjusting Y position to %d", yBalance)
   # make sure y position is correct
   try:
      ystepper.setEngaged(0,True)
      ystepper.setTargetPosition( 0,yBalance)
      while ystepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      ystepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   logger.debug("now located at x: %d y: %d z: %d" % (getXPosition(),getYPosition(),getZPosition()))
   DataReadWrite.updatePosition(getXPosition(),getYPosition(),getZPosition())
   sleep(1)

   logger.debug("Now will refine the location based on difference in encoder locations")
   refineInsideBalancePosition()
   logger.debug("Completed refinement")
   return True;   

def putSampleOnBalance():
   logger.debug("putSampleOnBalance")
   ##Zeroing the Balance
   DataReadWrite.zeroBalance()
   sleep(1)
   DOWN_BALANCE_POSITION_DROPOFF=int(DataReadWrite.getZForBalanceLocation())
   ## lower the arm
   logger.debug("Now lower the arm to %d", DOWN_BALANCE_POSITION_DROPOFF)
   #raise the arum
   try:
      zstepper.setEngaged( 0,True)
      logger.debug("Now move to Z: %d ",DOWN_BALANCE_POSITION_DROPOFF)
      zstepper.setTargetPosition(0,DOWN_BALANCE_POSITION_DROPOFF)
      while zstepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   sleep(2)

   logger.debug("open the gripper")
   # release the sample
   openGripper()
   sleep(1)
   logger.debug("raise the arm to position %d", UP_BALANCE_POSITION)
   ## raise the arm
   try:
      zstepper.setEngaged( 0,True)
      logger.debug("Now move to Z: %d ",UP_BALANCE_POSITION)
      zstepper.setTargetPosition(0,UP_BALANCE_POSITION)
      while zstepper.getStopped(0) !=STOPPED and getZTopLimit() is False:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   sleep(2)

   return True;

def getXYForSampleLocation(sampleLocation):
   if sampleLocation > 25 or sampleLocation < 0:
        return 0,0
   x=0
   y=0
   (x,y)=DataReadWrite.getXYForSampleLocation(sampleLocation)
   return (int(x),int(y))

def pickUpSampleFromBalance():
   logger.debug("pickUpSampleFromBalance")
   ## lower the arm
   DOWN_BALANCE_POSITION_PICKUP=int(DataReadWrite.getZForBalanceLocation())

   logger.debug("Lower the arm to %d ",DOWN_BALANCE_POSITION_PICKUP)
   try:
      zstepper.setEngaged( 0,True)
      logger.debug("Now move to Z: %d ",DOWN_BALANCE_POSITION_PICKUP)
      zstepper.setTargetPosition(0,DOWN_BALANCE_POSITION_PICKUP)
      while zstepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   logger.debug("Close the gripper.")
   sleep(2)
   ## grab the sample
   closeGripper()

   logger.debug("Gripper reports that it is holding a crucible. This is good.")

   ## raise the arm
   logger.debug("Raise the arm to %d", UP_BALANCE_POSITION)
   try:
      zstepper.setEngaged(0,True)
      logger.debug("Now move to Z: %d ",UP_BALANCE_POSITION)
      zstepper.setTargetPosition(0,UP_BALANCE_POSITION)
      while zstepper.getStopped(0) !=STOPPED and getZTopLimit() is False:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
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
   sys.exit()

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
   #Label(robotStatus,text="Run ID:").grid(row=0,column=0,sticky=W)
   #Label(robotStatus,textvariable=RUNID).grid(row=0,column=1, sticky=W)
   Label(robotStatus,text="Current crucible number:").grid(row=1,column=0,sticky=W)
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

   position=startPosition  ## set the position to start where we want it.
   if (position =="" or position ==0):  ## position must start at 1
      position=1

   statustext="Starting crucible weighing..."
   STATUS.set(statustext)
   robotStatus.update()
   ## x and y for the outside balance point. Use this to check to see if the arm is outside of the balance
   (outside_balance_x,outside_balance_y)=DataReadWrite.getXYCoordinatesForOutsideBalance()
   while position < (numberOfSamples+1):  # positions go from 1 to 25 (may need to fix one day)
      POSITION.set(position)
      statustext="Going to position: %d"% int(position)
      STATUS.set(statustext)
      robotStatus.update()
      logger.debug( statustext)
      logger.debug( "Sample position: %d ", position)
      STATUS.set(statustext)
      robotStatus.update()
      goToSamplePosition(position,0)
      statustext="Picking up sample %d" % int(position)
      STATUS.set(statustext)
      #logger.debug( "picking up sample.")
      robotStatus.update()
      val = samplePickUp()
      if val is False:
         return False;

      ## zero the balance for each sample
      #logger.debug("going to zero balance...")
      DataReadWrite.zeroBalance()
      #logger.debug( "opening balance door.")
      DataReadWrite.openBalanceDoor()
      statustext="Going to outside of balance x: %d y: %d" %( DataReadWrite.getXYForOutsideBalance())
      robotStatus.update()
      STATUS.set(statustext)
      #logger.debug( "go to outside of balance.")
      goToOutsideBalanceFromOutside()
      #logger.debug( "go to inside balance")
      statustext="Going to inside balance x: %d y: %d" %( DataReadWrite.getXYForInsideBalance())
      STATUS.set(statustext)
      robotStatus.update()
      goToInsideBalanceFromOutside()
      #logger.debug( "put sample on balance")
      STATUS.set("Putting sample on balance")
      robotStatus.update()
      val = putSampleOnBalance()
      if val is False:
         STATUS.set("ERROR")
         robotStatus.quit()
         return False;
      STATUS.set("Moving to outside balance.")
      robotStatus.update()
      #logger.debug( "Move to outside balance.")
      goToOutsideBalanceFromInside()
      ## may need to check to see if arm is clear of door.
      (pos_x,pos_y)=getCurrentXYCoordinates()
      if pos_y < outside_balance_y: ### Change this value!!
         DataReadWrite.closeBalanceDoor()

      logger.debug("Go Home and Park the Arm. Reset to Zero. Relax and wait while samples are measured.")
      goHome()

      ## Now calculate the duration
      durationOfLogging=int(duration)
      startTime=datetime.today()
      endPoint=timedelta(minutes=durationOfLogging)
      endTime=startTime+endPoint
      listOfValues=[]
      weight=float(0.0)
      count=0
      kcount=0
      tempHumidityArray=[]
      statustext="Weighing crucible # %d"% position
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
      sleep(30)
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
            
            ##measurementID=DataReadWrite.insertCrucibleMeasurement(runID,position,weight,status,temperature,humidity,count,today)
            DataReadWrite.updateChamberCrucible(position,averageWeight,stdevWeight,today,count)
            sleep(loggingInterval)
            statustext="Weight recorded for crucible #%d with %d counts %f weight %f stddev" %(position, count,averageWeight,stdevWeight)
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
               robotStatus.update()
               logger.debug( "There is a problem: no output from balance at all: Count: %d",int(kcount))
               kcount += 1
               if kcount==500:
                  logger.error( "There is a problem: no output for 500 counts -- quitting ")
                  KillMotors()
                  sys.exit()

      STATUS.set("Go back into balance to get sample.")
      robotStatus.update()
      logger.debug("Now go to area outside of balance ")
      goToOutsideBalanceFromOutside()
      logger.debug("Open the balance door")
      DataReadWrite.openBalanceDoor()
      logger.debug( "enter balance")
      goToInsideBalanceFromOutside()
      logger.debug( "pick up crucible")
      STATUS.set("Pick up crucible from balance")
      robotStatus.update()
      val = pickUpSampleFromBalance()
      if val is False:
         STATUS.set("Error: missing crucible")
         robotStatus.quit()
         return False
      robotStatus.update()
      logger.debug( "leave balance . . . ")
      STATUS.set("Leave balance.")
      robotStatus.update()
      goToOutsideBalanceFromInside()
      logger.debug("Go home to reset position")
      goHome()
      statustext="Return to position %d", int(position)
      STATUS.set(statustext)
      robotStatus.update()
      logger.debug( "now return to position: %d ", int(position))
      STATUS.set("Put sample down.")
      goToSamplePosition(position,0)
      logger.debug( "put the sample down. . . ")
      val=samplePutDown()
      if val is False:
         STATUS.set("Error sample held when there shouldn't be one")
         robotStatus.quit()
         return False;
      logger.debug( "close the balance door . . ")
      (pos_x,pos_y)=getCurrentXYCoordinates()

      if pos_y < outside_balance_y:
         logger.debug("closing balance door.")
         DataReadWrite.closeBalanceDoor()
      STATUS.set("Now go to home position")
      robotStatus.update()
      response=goHome()
      if response is False:
         logger.error( "Home point not reached. Stopping.")
         return False;
      position += 1   # increment the position to the next one...
      POSITION.set(position)
      statustext="Now starting next sample: %d",position
      STATUS.set(statustext)
      statustext="go on to the next position: %d", int(position)
      robotStatus.update()
   logger.debug(statustext)
   STATUS.set("Done!")
   robotStatus.update()
   robotStatus.withdraw()
   return True


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
      robotStatus.update()
      logger.debug("Now on position: %d ", int(position))
      statustext="Go to position %d",int(position)
      STATUS.set(statustext)
      robotStatus.update()
      goToSamplePosition(position,0)
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
      robotStatus.update()
      logger.debug("Go to outside balance.")
      goToOutsideBalanceFromOutside()
      statustext="Going into the balance."
      STATUS.set(statustext)
      robotStatus.update()
      logger.debug("go to inside balance.")
      goToInsideBalanceFromOutside()
      logger.debug("put sample on balance.")
      statustext="Putting sample on balance."
      STATUS.set(statustext)
      robotStatus.update()
      val = putSampleOnBalance()
      if val is False:
         return False
      ## may need to check to see if arm is clear of door.
      logger.debug("go to outsisde balance from the inside.")
      statustext="Going to outside of balance"
      STATUS.set(statustext)
      robotStatus.update()
      goToOutsideBalanceFromInside()
      logger.debug("close balance door")
      if (getXMotorPosition() > -2800):
         DataReadWrite.closeBalanceDoor()
      ## go home to park arm
      STATUS.set("Going home to park arm")
      robotStatus.update()
      goHome()
      crucibleWeight=double(DataReadWrite.getChamberCrucibleWeight(position))
      if (crucibleWeight is False):
         alertWindow("getCrucibleWeight returned an error.")
         sys.exit()

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
               alertWindow("insertPreFireMeasurement returned an error.")
               sys.exit()

            ### check to see if enough measurements have been made. First at least 100 must have been done
            if (count > COUNTS_FOR_STATS):
               (mean,stdev,variance,tempMean,tempStdev,humidityMean,humidityStdev)=DataReadWrite.getStatsForPrefireWeightOfSample(runID,sampleID,count)
               MEAN.set(mean)
               STDEV.set(stdev)
               VARIANCE.set(variance)
               logger.debug("Mean: %d  Stdev: %d  Variance: %d TempMean: %d  TempStDev: %d HumidityMean: %d HumidityStdDev: %d" % (mean,stdev,variance,tempMean,tempStdev,humidityMean,humidityStdev))
               value=DataReadWrite.updateSamplePreFire(runID,sampleID,position,mean,stdev,tempMean,tempStdev,humidityMean,humidityStdev)
            sleep(loggingInterval)

      goToOutsideBalanceFromOutside()
      DataReadWrite.openBalanceDoor()
      statustext="Going into balance."
      STATUS.set(statustext)
      robotStatus.update()
      goToInsideBalanceFromOutside()
      statustext="Picking up sample."
      STATUS.set(statustext)
      robotStatus.update()
      val=pickUpSampleFromBalance()
      if val is False:
         return False
      statustext="Going to outside of balance."
      STATUS.set(statustext)
      robotStatus.update()
      goToOutsideBalanceFromInside()
      ## first go home then go to the position
      goHome()
      statustext="Going to position %d." % position
      STATUS.set(statustext)
      robotStatus.update()
      goToSamplePosition(position,0)
      statustext="Putting sample down."
      STATUS.set(statustext)
      robotStatus.update()
      val=samplePutDown()
      if val == False:
         return False
      statustext="Going to home position."
      STATUS.set(statustext)
      robotStatus.update()
      response=goHome()
      if response is False:
         logger.error( "Home point not reached. Stopping.")
         STATUS.set("Error: home point not reached.")
         robotStatus.update()
         return False
      if (getXMotorPosition() > -2800):
         DataReadWrite.closeBalanceDoor()
      position += 1  ## increment the position to the next sample
      POSITION.set(int(position))

      statustext= "Now moving to the next sample %d." % position
      STATUS.set(statustext)
      robotStatus.update()
   STATUS.set("Done!")
   STATUS.set(statustext)
   robotStatus.update()
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
   robotStatus.update()
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
      goToSamplePosition(position,0)
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

      # go home and park arm
      goHome()

      ## check that there is something on the balance
      crucibleWeight=double(DataReadWrite.getChamberCrucibleWeight(position))
      if (crucibleWeight is False):
         alertWindow("getChamberCrucibleWeight returned an error.")
         sys.exit()

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
      robotStatus.update()
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
            robotStatus.update()
            temperature=getTemperature()  ###+tempCorrection
            humidity=getHumidity()        ###rhCorrection
            ##logger.debug( "TMP:  temp: %s, humidity: %s" % (temperature,humidity))

            standard_weight=float(DataReadWrite.readStandardBalance())
            timeElaspedMin=0.0
            timeDiff=now - endOfFiring
            timeElapsedMin=timeDiff.seconds/60
            TIMEELAPSEDMIN.set(timeElapsedMin)
            robotStatus.update()
            ## timeElapsedQuarterPower=double(pow(timeElapsedMin,0.25))

            value=DataReadWrite.insertPostFireMeasurement(runID,sampleID,position,
                                                          weight,status,temperature,humidity,endOfFiring,
                                                          crucibleWeight,standard_weight,now,total_count,repetition,repetition_count,count)
            if (value is False):
               alertWindow("insertPostFireMeasurement returned with an error.")
               sys.exit()
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
      robotStatus.update()
      goToOutsideBalanceFromOutside()
      DataReadWrite.openBalanceDoor()
      goToInsideBalanceFromOutside()
      statustext="Picking up sample from balance."
      STATUS.set(statustext)
      robotStatus.update()

      val=pickUpSampleFromBalance()
      if val is False:
         return False
      STATUS.set("Going outside balance from inside")
      robotStatus.update()

      goToOutsideBalanceFromInside()
      goHome()
      statustext="Going to position %d" % int(position)
      STATUS.set(statustext)
      robotStatus.update()

      goToSamplePosition(position,0)
      STATUS.set("Putting sample down")
      robotStatus.update()

      val=samplePutDown()
      if val is False:
         return False
      STATUS.set("Now going to home position.")
      response=goHome()
      if (getYMotorPosition() < YMOTOR_OK_TO_CLOSE_DOOR):
         DataReadWrite.closeBalanceDoor()
      if response is False:
         logger.error( "Was unable to go home. Quitting.")
         return False
      position += 1 ## increment position to go to next sample
      POSITION.set(int(position))
      statustext="Now on position %d" % position
      STATUS.set(statustext)
      robotStatus.update()
   STATUS.set("Done!")
   robotStatus.withdraw()
   return runID

def resetXYValuesToZero():
   logger.debug("resetValuesToZero")
   #Set Current position as Start Position    
   logger.debug("Set Positions of SERVOs and STEPPER MOTORS to 0")
   try:
      xstepper.setCurrentPosition(0,0)
      ystepper.setCurrentPosition(0,0)
      #zstepper.setCurrentPosition(0,0)
      #myLocation.setZZero()
      advancedServo.setPosition(GRIPPER,GRIPPER_OPEN)
      DataReadWrite.updatePosition(0,0,getZPosition())
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()


def resetCoordinates(x,y):
   logger.debug("resetCoordinates")
   if x=="":
      x=0
   if y=="":
      y=0
   #Set Current position as Start Position    
   logger.debug("Set Positions of SERVOs and STEPPER MOTORS to 0")
   try:
      xstepper.setCurrentPosition(0,x)
      ystepper.setCurrentPosition(0,y)
      #z=myLocation.getZPosition()
      DataReadWrite.updatePosition(x,y,getZPosition())
      advancedServo.setPosition(GRIPPER,GRIPPER_OPEN)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()

def setYMotorPosition(pos):
   try:
      ystepper.setCurrentPosition(0,pos)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   return True

def setXMotorPosition(pos):
   try:
      xstepper.setCurrentPosition(0,pos)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   return True

def setZMotorPosition(pos):
   try:
      zstepper.setCurrentPosition(0,pos)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   myLocation.setZPosition(pos)
   return True

def getMotorPositions():
   logger.debug("getMotorPositions")
   xpos=0
   ypos=0
   try:
      xpos=int(xstepper.getCurrentPosition(0))
      ypos=int(ystepper.getCurrentPosition(0))
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   return (xpos,ypos)

def getZPosition():
   logger.debug("getZPosition")
   #get current postiopn
   zpos=0
   try:
      zpos=int(zstepper.getCurrentPosition(0))
   except PhidgetException as e:
      logger.debug("Phidget Exception %i: %s" % (e.code, e.details))
      logger.debug("No value means that the servo has not been set to some value. Will assume 0 at this point.")
   return zpos

def getXPosition():
   logger.debug("getXPosition")
   #get current postiopn
   xpos=0
   try:
      xpos=int(xstepper.getCurrentPosition(0))
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit()
   return xpos  



def getYPosition():
   logger.debug("getYPosition")
   #get current postiopn
   ypos=0
   try:
      ypos=int(ystepper.getCurrentPosition(0))
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   return ypos

def raiseArm(zup):
   logger.debug("raiseArm: %d",zup)
   ## raise the arm
   zpos=int(myLocation.getZPosition())
   newz=zpos-zup
      ## raise the arm
   logger.debug("Raise the arm to %d", zup)
   try:
      zstepper.setEngaged( 0,True)
      logger.debug("Now move to Z: %d ",zup)
      zstepper.setTargetPosition(0,zup)
      while zstepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("raiseArm: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   myLocation.setZPosition(newz)
   return newz

def lowerArmToSample():
   logger.debug("Lowering arm to sample")
   DOWN_SAMPLE_POSITION=int(DataReadWrite.getZForSampleLocation(1))
   #print "moving arm to position: ", DOWN_SAMPLE_POSITION
   try:
      zstepper.setEngaged( 0,True)
      logger.debug("Now move to Z: %d ", DOWN_SAMPLE_POSITION)
      zstepper.setTargetPosition(0,DOWN_SAMPLE_POSITION)
      while zstepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("raiseArm: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   try:
      advancedServo.setEngaged(0, False)
      sleep(1)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   myLocation.setZPosition(DOWN_SAMPLE_POSITION)
   return True

def raiseArmToTop():
   logger.debug("raiseArmToTop")
   try:
      zstepper.setEngaged( 0,True)
      logger.debug("Now move to Z: %d ",UP_SAMPLE_POSITION)
      zstepper.setTargetPosition(0,UP_SAMPLE_POSITION)
      while zstepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("raiseArm: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   myLocation.setZZero()
   zstepper.setCurrentPosition(0,0)
   return True

def lowerArmToBalance():
   logger.debug("lowerArmToBalance")
   DOWN_BALANCE_POSITION_PICKUP=int(DataReadWrite.getZForBalanceLocation())
   try:
      zstepper.setEngaged( 0,True)
      logger.debug("Now move to Z: %d ",DOWN_BALANCE_POSITION_PICKUP)
      zstepper.setTargetPosition(0,DOWN_BALANCE_POSITION_PICKUP)
      while zstepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("raiseArm: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   myLocation.setZPosition(DOWN_BALANCE_POSITION_PICKUP)
   return True;

## UNUSED?
def getXYMotorPositions():
   logger.debug("getXYMotorPositions")
   xpos=0
   ypos=0
   try:
      xpos=xstepper.getCurrentPosition(0)
      ypos=ystepper.getCurrentPosition(0)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   return xpos,ypos

def getXMotorPosition():
   logger.debug("getXMotorPosition")
   #get current postion
   xpos=0
   try:
      xpos=xstepper.getCurrentPosition(0)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   return xpos


def getYMotorPosition():
   logger.debug("getYMotorPosition")
   #get current position
   ypos=0
   try:
      ypos=ystepper.getCurrentPosition(0)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   return ypos

def getZMotorPosition():
   logger.debug("getZMotorPosition")
   #get current position
   zpos=0
   try:
      zpos=zstepper.getCurrentPosition(0)
      #print "Current Z Position: ", zpos
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   #zpos = myLocation.getZPosition()
   return zpos


def armToTop():
   logger.debug("armToTop")
   try:
      zstepper.setEngaged(0,True)
      logger.debug("Now move to Z: %d ",UP_SAMPLE_POSITION)
      zstepper.setTargetPosition(0,UP_SAMPLE_POSITION)
      while zstepper.getStopped(0) !=STOPPED:
         pass
      sleep(2)
      zstepper.setCurrentPosition(0,0)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("raiseArm: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      exit(1)
   myLocation.setZZero()
   return True

def disengageMotors():
   xstepper.setEngaged(0,False)
   ystepper.setEngaged(0,False)
   zstepper.setEngaged(0,False)
   return True

def bumpXMotorUp(bump):
   logger.debug("bumpXmotorUp")
   currentAbsPosition=getAbsoluteXPosition()
   currentMotorPosition=xstepper.getCurrentPosition(0)
   move = currentMotorPosition+int(bump)
   xstepper.setEngaged(0,True)
   try:
      xstepper.setTargetPosition(0,move)
      while xstepper.getStopped(0) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical("Servo 0: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   newAbsPosition= getAbsoluteXPosition()

   if currentAbsPosition==newAbsPosition:
      # then there has been no movement
      # so current position hasnt changed
      # so go back to original setting
      logger.debug("No movement so setting the position back...")
      xstepper.setCurrentPosition(0,currentMotorPosition)
   xstepper.setEngaged(0,False)
   return int(move);

def bumpYMotorLeft(bump):
   logger.debug("bumpYMotorLeft")
   move = ystepper.getCurrentPosition(0)-int(bump)
   ystepper.setEngaged(0,True)
   try:
      ystepper.setTargetPosition(0,move)
      while ystepper.getStopped(0) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical("Y Stepper: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   ystepper.setEngaged(0,False)
   return True


def bumpZMotorDown(bump):
   logger.debug("bumpZMotorDown")
   moveVal = int(int(myLocation.getZPosition()) + int(bump))
   #print "Current position for Z:  %d "% myLocation.getZPosition()
   #print "moving to %d" % moveVal
   zstepper.setEngaged(0,True)
   try:
      zstepper.setTargetPosition(0,moveVal)
      while zstepper.getStopped(0) != STOPPED:
         #print "continuing.. not stopped and not true"
         pass
      sleep(1)
      zstepper.setEngaged(0,False)

   except PhidgetException as e:
      logger.critical("Stepper Z: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)

   #print "now setting position to its new location... move"
   myLocation.setZPosition(moveVal)
   #print "Zposition is now:  %d "% myLocation.getZPosition()

   return True

def bumpZMotorUp(bump):
   logger.debug("bumpZMotorUp")
   moveVal = int(int(myLocation.getZPosition()) - int(bump))
   #print "current position for Z: %d"% myLocation.getZPosition()
   #print "moving to: %d" % moveVal
   if atZZero() == "TRUE":
      return True
   zstepper.setEngaged(0,True)
   try:
      zstepper.setTargetPosition(0,moveVal)
      while zstepper.getStopped(0) != STOPPED:
         #print "continuing..."
         pass
      sleep(1)
      zstepper.setEngaged(0,False)
   except PhidgetException as e:
      logger.critical("Servo Z: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   myLocation.setZPosition(moveVal)
   #print "Zposition is now:  ", myLocation.getZPosition()
   return True

def bumpXMotorDown(bump):
   logger.debug("bumpXMotorDown")
   currentpos= getAbsoluteXPosition()
   xstepper.setEngaged(0,True)
   logger.debug("start here: %d", int(xstepper.getCurrentPosition(0)))
   moveVal = xstepper.getCurrentPosition(0)-int(bump)
   #print( "move to here: %i", moveVal)

   try:
      xstepper.setTargetPosition(0,moveVal)
      while xstepper.getStopped(0) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical("Servo 0: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   xstepper.setEngaged(0,False)
   ### hack -- the clock turns over at 1000 so I have to check to see where the previous position"
   newpos= getAbsoluteXPosition()+1
   ### so removing this function by adding 1
   if (newpos==0):
      logger.debug( "new position is 0: so set this to the 0 point")
      # then there has been no movement
      # so current position hasnt changed
      # so set to 0 position
      setXMotorPosition(0)
   return True

def bumpYMotorRight(bump):
   logger.debug("bumpYMotorRight")
   move = ystepper.getCurrentPosition(0)+int(bump)
   ystepper.setEngaged(0,True)
   try:
      ystepper.setTargetPosition(0,move)
      while ystepper.getStopped(0) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical("Servo 2: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   ystepper.setEngaged(0,False)
   return move; 

def bumpYMotorNE(bump):
   move = ystepper.getCurrentPosition(0)+int(bump)
   ystepper.setEngaged(0,True)
   try:
      ystepper.setTargetPosition(0,move)
      while ystepper.getStopped(0) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical(" Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   ystepper.setEngaged(0,False)


   move = xstepper.getCurrentPosition(0)+int(bump)
   xstepper.setEngaged(0,True)
   try:
      xstepper.setTargetPosition(0,move)
      while xstepper.getStopped(0) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical(" Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   xstepper.setEngaged(0,False)

   return True;


###Arm Controls
def moveArmToPosition(value):
   logger.debug("moveArmToPosition")
   zstepper.setEngaged(0,True)
   try:
      zstepper.setTargetPosition(0,value)
      while zstepper.getStopped(0) != STOPPED:
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical(" Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
      zstepper.setEngaged(0,False)
   myLocation.setZPosition(value)
   return True;

def KillMotors():
   logger.debug ("Killing Motors and Phidget Objects")
   try:
      xstepper.setEngaged(0,False)
      sleep(1)
      ystepper.setEngaged(0,False)
      sleep(1)
      zstepper.setEngaged(0,False)
      sleep(1)
      advancedServo.setEngaged(0, False)
      sleep(1)
      xstepper.closePhidget(0)
      ystepper.closePhidget(0)
      zstepper.closePhidget(0)
      advancedServo.closePhidget()
      interfaceKit.closePhidget()
      sys.exit(1)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   return True


def backToMainWindow():
   return

def KillProgram():
   return

def setXMotorCurrentLimit(current):
   xstepper.setCurrentLimit(0,current)
   return True

def setYMotorCurrentLimit(current):
   ystepper.setCurrentLimit(0,current)
   return True

def setZMotorCurrentLimit(current):
   zstepper.setCurrentLimit(0,current)
   return True

def setXMotorVelocityLimit(maxvelocity):
   xstepper.setVelocityLimit(0,maxvelocity)
   return True

def setYMotorVelocityLimit(maxvelocity):
   ystepper.setVelocityLimit(0,maxvelocity)
   return True

def setZMotorVelocityLimit(maxvelocity):
   zstepper.setVelocityLimit(0,maxvelocity)
   return True

def getXMotorVelocityLimit():
   return xstepper.getVelocityLimit(0)

def getYMotorVelocityLimit():
   return ystepper.getVelocityLimit(0)

def getZMotorVelocityLimit():
   return zstepper.getVelocityLimit(0)

def alertWindow(message):
   title = "RHX ERROR!"
   communication.sendEmail(title,message)
   while 1:
      easygui.msgbox(message, title, ok_button="Exit")     # show a Continue/Cancel dialog
   return

def resetZMotorToZeroPosition():
   logger.debug("resetZMotorToZeroPosition")
   zstepper.setEngaged(0,True)
   aVerySmallValue = -500000
   try:
      zstepper.setTargetPosition(0,aVerySmallValue)
      while zstepper.getStopped(0) != STOPPED and atZZero() == "FALSE":
         pass
      sleep(1)
   except PhidgetException as e:
      logger.critical(" Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   zstepper.setCurrentPosition(0,0)
   zstepper.setEngaged(0,False)
   myLocation.setZPosition(0)
   return True;

def resetZToZero():
   zstepper.setCurrentPosition(0,0)
   myLocation.setZPosition(0)
   return True

def resetXYMotorsToZeroPosition():
   currentAbsXPosition= getAbsoluteXPosition()
   currentAbsYPosition= getAbsoluteYPosition()
   xMotor=xstepper.getCurrentPosition(0)
   yMotor=ystepper.getCurrentPosition(0)
   #zMotor=myLocation.setZZero()
   oldxpos=0
   oldypos=0
   newxpos=0
   newypos=0
   xstepper.setEngaged(0, True)
   bump=500
   diff=1
   move=xstepper.getCurrentPosition(0)+bump

   logger.debug("Current Motors at X: %d Y: %d" %(xMotor,yMotor))
   logger.debug("Current Abs Position at X: %d Y: %d " % (currentAbsXPosition,currentAbsYPosition))
   try:
      xstepper.setTargetPosition(0,move)
      while xstepper.getStopped(0) != STOPPED:
         pass
      sleep(1)
      while (getAbsoluteXPosition()-1 > MINIMUM_X_VALUE):
         oldxpos=getAbsoluteXPosition()
         logger.debug("Now X Motor at X: %d Y: %d" %(xstepper.getCurrentPosition(0),ystepper.getCurrentPosition(0)))
         logger.debug("Now Abs Position at X: %d Y: %d " % (getAbsoluteXPosition(),getAbsoluteYPosition()))
         move=xstepper.getCurrentPosition(0)+bump

         logger.debug("Bumping XMOTOR: %d" % (move))
         xstepper.setTargetPosition(0,move)
         while xstepper.getStopped(0) != STOPPED:
            pass
         sleep(1)
         newxpos=getAbsoluteXPosition()
         diff = abs(newxpos - oldxpos)
         logger.debug("Now at X: %d Y: %d" %(xstepper.getCurrentPosition(0),ystepper.getCurrentPosition(0)))
         logger.debug("Now Abs Position at X: %d Y: %d " % (getAbsoluteXPosition(),
                                                                         getAbsoluteYPosition()))
   except PhidgetException as e:
      logger.critical("Stepper 0: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   xstepper.setEngaged(0,False)
   
   logger.debug("Current Motors at X: %d Y: %d" %(xMotor,yMotor))
   logger.debug("Current Abs Position at X: %d Y: %d " % (currentAbsXPosition,currentAbsYPosition))
   diff=1
   move=ystepper.getCurrentPosition(0)-bump
   ystepper.setEngaged( 0,True)
   try:
      ystepper.setTargetPosition(0,move)
      while ystepper.getStopped(0) != STOPPED:
         pass
      sleep(1)
      while (getAbsoluteYPosition()-1 > MINIMUM_Y_VALUE):
         oldypos=getAbsoluteYPosition()
         logger.debug("Now Y Motor at X: %d Y: %d" %(xstepper.getCurrentPosition(0),ystepper.getCurrentPosition(0)))
         logger.debug("Now Abs Position at X: %d Y: %d " % (getAbsoluteXPosition(),getAbsoluteYPosition()))
         move=ystepper.getCurrentPosition(0)-bump
         while ystepper.getStopped(0) != STOPPED:
            pass
         sleep(1)
         logger.debug("Bumping YMOTOR: %d" % (move))
         ystepper.setTargetPosition(0,move)
         newypos=getAbsoluteYPosition()
         diff = abs(newypos - oldypos)
         logger.debug("Now Y Motor at X: %d Y: %d" %(xstepper.getCurrentPosition(0),ystepper.getCurrentPosition(0)))
         logger.debug("Now Abs Position at X: %d Y: %d " % (getAbsoluteXPosition(),getAbsoluteYPosition()))
   except PhidgetException as e:
      logger.critical("Stepper Y: Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   ystepper.setEngaged(0,False)
   ## reset the Absolute Zero points
   value = setAbsZeroXY()
   ## now set the stepper motors to 0
   value = reseXYValuesToZero()

   
   return True;

def initializeRobot():
   global advancedServo
   global xstepper
   global ystepper
   global zstepper
   global interfaceKit

   ############INITIALIZATION########################
   ###Create Stepper and Servo Objects

   #print "create servo"
   try:
      advancedServo = AdvancedServo()
   except RuntimeError as e:
      logger.critical("Runtime Exception: %s" % e.details)
      logger.critical("Exiting....")
      return False;
   #print "create steppers"
   try:
      xstepper = Stepper()
      ystepper = Stepper()
      zstepper = Stepper()
   except RuntimeError as e:
      logger.critical("Runtime Exception: %s" % e.details)
      logger.critical("Exiting....")
      return False;

   #print "open servo"
   try:
      advancedServo.openPhidget()
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)

   logger.debug("Waiting for Arm to attach....")

   #print "wait for servo to attach"
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
      sys.exit(1)
   #set the gripper to 0 (jaws wide open)
   advancedServo.setPosition(GRIPPER,0)
   ### get the motors connected and attached
   logger.debug("Opening phidget object for xsteppers...")
   try:
      xstepper.openPhidget(XMOTOR)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   logger.debug("Waiting for ystepper motors to attach....")
   try:
      xstepper.waitForAttach(1000)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))


   logger.debug("Opening phidget object for ysteppers...")
   try:
      ystepper.openPhidget(YMOTOR)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   logger.debug("Waiting for ystepper motors to attach....")
   try:
      ystepper.waitForAttach(1000)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))

   logger.debug("Opening phidget object for zsteppers...")
   try:
      zstepper.openPhidget(ZMOTOR)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))
      logger.critical("Exiting....")
      sys.exit(1)
   logger.debug("Waiting for zstepper motors to attach....")
   try:
      zstepper.waitForAttach(1000)
   except PhidgetException as e:
      logger.critical("Phidget Exception %i: %s" % (e.code, e.details))

   logger.debug("Setting Default values for the motor velocity limits")
   setYMotorVelocityLimit(YMOTORVELOCITYLIMIT)
   setXMotorVelocityLimit(XMOTORVELOCITYLIMIT)
   setZMotorVelocityLimit(ZMOTORVELOCITYLIMIT)

   setXMotorCurrentLimit(XMOTORCURRENTLIMIT)
   setYMotorCurrentLimit(YMOTORCURRENTLIMIT)
   setZMotorCurrentLimit(ZMOTORCURRENTLIMIT)

   try:
      logger.debug("Setting the servo type for motor 0 to PHIDGET_SERVO_HITEC_HS422")
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
           sys.exit(1)
       print("Exiting....")
       sys.exit(1)


initializeRobot()