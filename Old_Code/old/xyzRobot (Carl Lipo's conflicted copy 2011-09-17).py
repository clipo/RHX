
# Filename: xyzRobot.py

#Basic imports
from ctypes import *
import os
import io
import serial
import sys
from time import sleep
import sched, time

## get the set of connections for reading the balance, etc.
import DataReadWrite

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs
from Phidgets.Devices.Stepper import Stepper
from Phidgets.Devices.AdvancedServo import AdvancedServo
from Phidgets.Devices.Servo import ServoTypes

## CONSTANTS ###########################

## Stepper Motor Numbers
XMOTOR=0
YMOTOR=2

## Advanced Servo
ZMOTOR=0
GRIPPER=1

X=0
Y=1

#Movement List - Position 0 is motor 0 - Position 1 is motor 2 ... made sense ...
MOVE= (   [0,0],  [-400,0],     [-800,0],     [-1200,0],    [-1600,0],
	  [0,400],    [-400,400],   [-800,400],   [-1200,400],  [-1600,400],
	  [0,800],    [-400,800],   [-800,800],   [-1200,800],  [-1600,800],
	  [0, 1200],  [-400,1200],  [-800,1200],  [-1200,1200], [-1600,1200],
      [0,1600],   [-400,1600],  [-800,1600],  [-1200,1600], [-1600,1600]   )

# This is the relative position from the uppermost Z axis point (i.e., how far down to lower the arm)
DOWN_SAMPLE_POSITION = 130
DOWN_BALANCE_POSITION = 90

UP_SAMPLE_POSITION = 37
UP_BALANCE_POSITION=37

#spaces betwen sample locations going along the length of the sampler (horizontal)
HORIZONTAL_SPACING = -350

#space between sample locations going away from the sampler (vertical)
VERTICLE_SPACING = 400


# coordinates for the Balance
BALANCE_OUTSIDE = [  -1800, 775 ]
BALANCE_INSIDE = [ -2800, 775  ]

# coordinates for the gripper position
GRIPPER_CLOSED = 83
GRIPPER_OPEN = 5


def getStepper():
   return stepper
	
def getAdvancedServo():
   return advancedServo




#########################################################
###Event Handler Callback Functions
#Stepper Callbacks
def StepperAttached(e):
    attached = e.device
    print("Stepper %i Attached!" % (attached.getSerialNum()))

def StepperDetached(e):
    detached = e.device
    print("Stepper %i Detached!" % (detached.getSerialNum()))

def StepperError(e):
    source = e.device
    print("Stepper %i: Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))

def StepperCurrentChanged(e):
    source = e.device
    print("Stepper %i: Motor %i -- Current Draw: %6f" % (source.getSerialNum(), e.index, e.current))

def StepperInputChanged(e):
    source = e.device
    print("Stepper %i: Input %i -- State: %s" % (source.getSerialNum(), e.index, e.state))

def StepperPositionChanged(e):
    source = e.device
    print("Stepper %i: Motor %i -- Position: %f" % (source.getSerialNum(), e.index, e.position))

def StepperVelocityChanged(e):
    source = e.device
    print("Stepper %i: Motor %i -- Velocity: %f" % (source.getSerialNum(), e.index, e.velocity))

#Servo Callbacks
def Attached(e):
    attached = e.device
    print("Servo %i Attached!" % (attached.getSerialNum()))

def Detached(e):
    detached = e.device
    print("Servo %i Detached!" % (detached.getSerialNum()))

def Error(e):
    source = e.device
    print("Phidget Error %i: %s" % (source.getSerialNum(), e.eCode, e.description))

def CurrentChanged(e):
    global currentList
    currentList[e.index] = e.current

def PositionChanged(e):
    source = e.device
    print("AdvancedServo %i: Motor %i Position: %f - Velocity: %f - Current: %f" % (source.getSerialNum(), e.index, e.position,velocityList[e.index], currentList[e.index]))
    if advancedServo.getStopped(e.index) == True:
        print("Motor %i Stopped" % (e.index))

def VelocityChanged(e):
    global velocityList
    velocityList[e.index] = e.velocity
    
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

def Disengage():
   try:
      stepper.setEngaged(XMOTOR, False)
      advancedServo.setEngaged(ZMOTOR, False)
      advancedServo.setEngaged(GRIPPER,False)
      stepper.setEngaged(YMOTOR, False)
      sleep(2)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)

def Engage():
   try:
      stepper.setEngaged(XMOTOR, True)
      advancedServo.setEngaged(ZMOTOR, True)
      advancedServo.setEngaged(GRIPPER,True)
      stepper.setEngaged(YMOTOR, True)
      sleep(2)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)

## home is defined as 0,0 -- the point when the arm is right above the first sample        
def goHome():
   Engage()
   try:
      stepper.setTargetPosition(XMOTOR, 0)
      while stepper.getCurrentPosition(XMOTOR) !=0:
         pass
      sleep(8)
      stepper.setTargetPosition(YMOTOR, 0)
      while stepper.getCurrentPosition(YMOTOR) !=0:
         pass
      sleep(5)
      advancedServo.setPosition(ZMOTOR, UP_SAMPLE_POSITION)
      while advancedServo.getPosition(ZMOTOR) != UP_SAMPLE_POSITION:
            pass
      sleep(4)
   except PhidgetException as e:
      print("Home Position - Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   Disengage()

def gotoSamplePosition(position):
   Engage()
   if position<0 or position>25:
      print("Invalid position: ",position)
      exit(1)
   ## now move to the position with the X and Y coordinates
   try:
      stepper.setTargetPosition(XMOTOR, MOVE[position][X])
      while stepper.getCurrentPosition(XMOTOR) !=(MOVE[position][X]):
         pass
      sleep(8)
      stepper.setTargetPosition(YMOTOR, MOVE[position][Y])
      while stepper.getCurrentPosition(YMOTOR) !=MOVE[position][Y]:
         pass
      sleep(5)
   except PhidgetException as e:
      print("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   Disengage()
   sleep(5)
   
   
def samplePickUp():
   Engage()
   ## make sure grippers are open
   openGripper()
   ## lower arm to sample
   try:
      advancedServo.setPosition(XMOTOR, DOWN_SAMPLE_POSITION)
      while advancedServo.getPosition(XMOTOR) != DOWN_SAMPLE_POSITION:
         pass
      sleep(4)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   ## close grippper
   closeGripper()

   ## raise the arm
   try:
      advancedServo.setPosition(XMOTOR, UP_SAMPLE_POSITION)
      while advancedServo.getPosition(XMOTOR) != UP_SAMPLE_POSITION:
         pass
      sleep(4)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   
   Disengage()
   
def samplePutDown():
   Engage()
   C=(stepper.getCurrentPosition(XMOTOR))
   CC=int(C)
   TT=int(CC-DOWN_SAMPLE_POSITION)
   W=C+DOWN_SAMPLE_POSITION
   WW=int(W)
   try:
   	  #lower the arm
      advancedServo.setPosition(ZMOTOR, DOWN_SAMPLE_POSITION)
      while advancedServo.getPosition(ZMOTOR) != DOWN_SAMPLE_POSITION:
         pass
      sleep(4)
      #open gripper
      openGripper()
      
      #raise the arum
      advancedServo.setPosition(ZMOTOR, UP_SAMPLE_POSITION))
      while advancedServo.getPosition(ZMOTOR) != UP_SAMPLE_POSITION:
        pass
      sleep(4)
      
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   Disengage()
   
def gotoOutsideBalanceFromInside():
   ## make sure the door is open!!
   DataReadWrite.openBalanceDoor()
   Engage()
   #set x axis -- move it to point outside...
   try:
      stepper.setTargetPosition(XMOTOR, BALANCE_OUTSIDE[X])
      while stepper.getCurrentPosition(XMOTOR) !=BALANCE_OUTSIDE[X]:
         pass
      sleep(8)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)

   sleep(2)
   Disengage()
   
def gotoOutsideBalanceFromOutside():
   Engage()
   ## make sure the door is open!!
   DataReadWrite.openBalanceDoor()

   ## first line up the Y axis arm 
   try:
      stepper.setTargetPosition(YMOTOR, BALANCE_OUTSIDE[Y])
      while stepper.getCurrentPosition(YMOTOR) != BALANCE_OUTSIDE[Y]:
         pass
      sleep(4)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)

   

   ## now move to the point just outside of the balance with the X axis
   try:
      stepper.setTargetPosition(XMOTOR, BALANCE_OUTSIDE[X])
      while stepper.getCurrentPosition(XMOTOR) !=BALANCE_OUTSIDE[X]:
         pass
      sleep(8)
      
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
  
   Disengage()

def gotoInsideBalanceFromOutside():
   Engage()
   ## make sure the door is open!!
   DataReadWrite.openBalanceDoor()

   # make sure y position is correct
   try:
      stepper.setTargetPosition(YMOTOR, BALANCE_INSIDE[Y])
      while stepper.getCurrentPosition(YMOTOR) !=BALANCE_INSIDE[Y]:
         pass
      sleep(4)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
          
   
   #set x axis -- move it to point outside...
   try:
      stepper.setTargetPosition(XMOTOR, BALANCE_INSIDE[0])
      while stepper.getCurrentPosition(XMOTOR) !=BALANCE_INSIDE[0]:
         pass
      sleep(5)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   
   Disengage()

def putSampleOnBalance():
   
   ##Zeroing the Balance
   DataReadWrite.zeroBalance()
   sleep(1)
   ##Opening the door
   DataReadWrite.openBalanceDoor()
   
   ## go to the area outside the balance
   gotoOutsideBalanceFromOutside()
   
   gotoInsideBalanceFromOutside()
   ## lower the arm
   Engage()
   try:
      advancedServo.setPosition(ZMOTOR, DOWN_BALANCE_POSITION)
      while advancedServo.getPosition(ZMOTOR) != DOWN_BALANCE_POSITION:
         pass
      sleep(4)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   
   # release the sample
   openGripper()
   
   ## raise the arm
   try:
      advancedServo.setPosition(ZMOTOR, UP_BALANCE_POSITION)
      while advancedServo.getPosition(ZMOTOR) != UP_BALANCE_POSITION:
         pass
      sleep(4)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)

   ## now leave the balance area
   
   gotoOutsideBalanceFromInside
   sleep(2)
   ##Closing the Door
   DataReadWrite.closeBalanceDoor()
   Disengage()

def pickUpSampleFromBalance(): 
   Engage()
   sleep(2)
   ## first make sure that the arm is lined up in the Y axis
   try:
      stepper.setTargetPosition(YMOTOR, BALANCE_INSIDE_POSITION[Y])
      while stepper.getCurrentPosition(YMOTOR) !=BALANCE_INSIDE_POSITION[Y]:
         pass
      sleep(4)
   except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

   ##Opening the door
   DataReadWrite.openBalanceDoor()

   ## now move the sample into the balance
   try:
      stepper.setTargetPosition(XMOTOR, BALANCE_INSIDE_POSITION[0])
      while stepper.getCurrentPosition(XMOTOR) !=BALANCE_INSIDE_POSITION[0]:
         pass
      sleep(8)
   except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

   ## lower the arm
   try:
      advancedServo.setPosition(ZMOTOR,DOWN_BALANCE_POSITION)
      while advancedServo.getPosition(ZMOTOR) != DOWN_BALANCE_POSITION:
         pass
      sleep(4)
   except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

   ## release the sample
   openGripper()
   ## raise the arm
   try:
      advancedServo.setPosition(ZMOTOR, UP_BALANCE_POSITION)
      while advancedServo.getPosition(ZMOTOR) != UP_BALANCE_POSITION:
         pass
      sleep(4)
   except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

   ## move the arm outside of balance area
   try:
      stepper.setTargetPosition(XMOTOR, BALANCE_OUTSIDE_POSITION[X])
      while stepper.getCurrentPosition(XMOTOR) !=BALANCE_OUTSIDE_POSITION[X]:
         pass
      sleep(8)
   except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
   
   ##Close the Door
   DataReadWrite.closeBalanceDoor()
   Disengage()

def weighAllCrucibles(initials,numberOfSamples,loggingInterval,duration):
   # Find elapsed time
   #first put robot back to zero
   position=0
   #HomePosition()
   listOfValues=()
   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")

   #first create a new run so we have an ID.
   runID=DataReadWrite.insertRun(initials,today,numberOfSamples)
 
   while position < numberOfSamples:
      goToSamplePosition(position)
      samplePickUp()
      ## zero the balance for each sample
      DataReadWrite.zeroBalance()
      DataReadWrite.openBalanceDoor()
      gotoOutsideBalanceFromOutside()

      putSampleOnBalance()
      
      ## may need to check to see if arm is clear of door.
      DataReadWrite.closeBalanceDoor()
      
      startTime=datetime.today()
      endPoint=timeDelta(minutes=duration)
      endTime=startTime+endPoint
      while datetime.today < endTime:
         weight=readWeightFromBalance()
         listOfValues.append(weight)
         averageWeight=average(listOfValues)
         stdevWeight=stdev(listOfValues)
         print( "The average weight of crucible #", position, " is: ", averageWeight, " with stdev of: ", stdevWeight)
         ## now update crucible position record 
         now = datetime.today()
         today = now.strftime("%m-%d-%y %H:%M:%S")
         DataReadWrite.updateCrucible(runID,position,averageWeight,stdevWeight,today)
         sleep(loggingInterval)          
      DataReadWrite.openBalanceDoor()
      pickUpSampleFromBalance()
      gotoSamplePosition(position)
      samplePutDown()
      DataReadWrite.closeBalanceDoor()
      position=position+1
   return (runID)
	  
def weighAllSamplesPreFire(runID,listOfSamples,duration,loggingInterval,numberOfSamples):
   # Find elapsed time
   #first put robot back to zero
   position=0
   #HomePosition()
   listOfValues=()
   crucibleWeight=0.0
    
   startTime=datetime.today()
   endPoint=timeDelta(minutes=duration)
   endTime=startTime+endPoint

   while position < numberOfSamples:
     
      goToSamplePosition(position)
      samplePickUp()
      ## zerothe balance for each sample
      DataReadWrite.zeroBalance()
      DataReadWrite.openBalanceDoor()
      gotoOutsideBalanceFromOutside()
      putSampleOnBalance()
       ## may need to check to see if arm is clear of door.
      DataReadWrite.closeBalanceDoor()
      crucibleWeight=getCrucibleWeight(runID,position)
      sampleID=getSampleID(runID,position)
      startTime=datetime.today()
      endPoint=timeDelta(minutes=duration)
      endTime=startTime+endPoint
      while datetime.today < endTime:
         weight=readWeightFromBalance()
         sampleWeight=weight-crucibleWeight
         (temp,humidity,pressure,light)=readTempHumidity()
         ## now update crucible position record
         now = datetime.today()
         today = now.strftime("%m-%d-%y %H:%M:%S")
         DataReadWrite.insertPostFireMeasurement(runID,sampleID,position,weightMeasurement,temperature,humidity,pressure,light,crucibleWeight,today)
         sleep(loggingInterval)
      DataReadWrite.openBalanceDoor()
      pickUpSampleFromBalance()
      goToSamplePosition(position)
      samplePutDown()
      DataReadWrite.closeBalanceDoor()
      position=position+1

def weighAllSamplesPostFire(runID,listOfSamples,duration,loggingInterval,numberOfSamples,startTime):
   # Find elapsed time
   #first put robot back to zero
   position=0
   #HomePosition()
   listOfValues=()
   crucibleWeight=0.0
    
   startTime=datetime.today()
   endPoint=timeDelta(minutes=duration)
   endTime=startTime+endPoint

   while position < numberOfSamples:
     
      goToSamplePosition(position)
      samplePickUp()
      ## zerothe balance for each sample
      DataReadWrite.zeroBalance()
      DataReadWrite.openBalanceDoor()
      gotoOutsideBalanceFromOutside()
      putSampleOnBalance()
       ## may need to check to see if arm is clear of door.
      DataReadWrite.closeBalanceDoor()
      crucibleWeight=getCrucibleWeight(runID,position)
      sampleID=getSampleID(runID,position)
      startTime=datetime.today()
      endPoint=timeDelta(minutes=duration)
      endTime=startTime+endPoint
      while datetime.today < endTime:
         weight=readWeightFromBalance()
         sampleWeight=weight-crucibleWeight
         (temp,humidity,pressure,light)=readTempHumidity()
         ## now update crucible position record 
         now = datetime.today()
         today = now.strftime("%m-%d-%y %H:%M:%S")
         timeElapsed= now - startTime
         timeElapsedQuarterPower = pow(timeElapsed,0.25)
         DataReadWrite.insertPostFireMeasurement(runID,sampleID,position,weightMeasurement,temperature,humidity,pressure,light,endOfFiring,crucibleWeight,today,timeElapsed,timeElapsedQuarterPower)
         sleep(loggingInterval)
      DataReadWrite.openBalanceDoor()
      pickUpSampleFromBalance()
      goToSamplePosition(position)
      samplePutDown()
      DataReadWrite.closeBalanceDoor()
      position=position+1

def openGripper():
   Engage()
   print "now open gripper"
   #  Set the gripper to be open
   try:
      advancedServo.setPosition(GRIPPER, GRIPPER_OPEN)
      while advancedServo.getPosition(GRIPPER) !=GRIPPER_OPEN:
         pass
      sleep(3)
   except PhidgetException as e:
        print("Servo Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)   
   Disengage()
   
def closeGripper():
   Engage()
   print "now close gripper"
   #  Set the gripper to be open
   try:
      advancedServo.setPosition(GRIPPER, GRIPPER_CLOSED)
      while advancedServo.getPosition(GRIPPER) != GRIPPER_CLOSED:
         pass
      sleep(3)
   except PhidgetException as e:
        print("Servo Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)   
   Disengage()


############INITIALIZATION########################
###Create Stepper and Servo Objects
try:
    advancedServo = AdvancedServo()
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)
    
try:
    stepper = Stepper()
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)
#stack to keep current values in
currentList = [0,0,0,0,0,0,0,0]
velocityList = [0,0,0,0,0,0,0,0]
   
###Open Phidgets
print("Opening phidget object for Servos....")

try:
    advancedServo.openPhidget()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

print("Waiting for Arm to attach....")

try:
    advancedServo.waitForAttach(10000)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    try:
        advancedServo.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    print("Exiting....")
    exit(1)

print("Opening phidget object for Steppers…")
try:
    stepper.openPhidget()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

print("Waiting for stepper motors to attach....")

try:
    stepper.waitForAttach(1000)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    try:
        stepper.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    print("Exiting....")
    exit(1)

#Set Current position as Start Position    
print ("Set Positions of SERVOs to 0")
try:
   stepper.setCurrentPosition(XMOTOR, 0)
   stepper.setCurrentPosition(YMOTOR, 0)
   sleep(1)
except PhidgetException as e:
   print("Phidget Exception %i: %s" % (e.code, e.details))
   print("Exiting....")
   exit(1)

