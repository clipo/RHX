
# Filename: RobotController.py

#Basic imports
from ctypes import *
import os
import io
import serial
import sys
from time import sleep
import sched, time
import DataReadWrite
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs
from Phidgets.Devices.Stepper import Stepper
from Phidgets.Devices.AdvancedServo import AdvancedServo
from Phidgets.Devices.Servo import ServoTypes


#Movement List - Position 0 is motor 0 - Position 1 is motor 2 ... made sense ...
MOVE= (   [0,-1450],     [-400,-1450],   [-750,-1450],  [-1100,-1535], [-1450,-1535],
		  [-50, -1135],  [-450,-1135],   [-850,-1135],  [-1250,-1135], [-1650,-1135],
		  [-50, -735],   [-450,-735],    [-850,-735],   [-1250,-735],  [-1650,-735],
		  [-50, -335],   [-450,-335],    [-850,-335],   [-1250,-335],  [-1650,-335],
          [-50, 35],     [-450,35],      [-850,35],     [-1250,35],    [-1650,35]   ]

# This is the relative position from the uppermost Z axis point (i.e., how far down to lower the arm)
DOWN_POSITION = 100

#spaces betwen sample locations going along the length of the sampler (horizontal)
HORIZONTAL_SPACING = 400

#space between sample locations going away from the sampler (vertical)
VERTICAL_SPACING = 300

BALANCE_OUTSIDE = [  XXX, YYYY ]
BALANCE_INSIDE = [ XXXX, YYYY  ]

def getStepper():
	return stepper
	
def getAdvancedServo():
	return advancedServo

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
print("Opening phidget object (stepper motor)....")

try:
    advancedServo.openPhidget()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

print("Waiting for Arm to attach (linear actuator)....")

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
try:
    stepper.openPhidget()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

print("Waiting for Motors to attach....")

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
try:
    advancedServo.setAcceleration(0, 50.00)
    sleep(2)
    
    advancedServo.setVelocityLimit(0, 50.00)
    sleep(2)
    
    advancedServo.setPositionMin(0)=60
    advancedServo.setPositionMax(0)=1000
    
    advancedServo.setPositionMin(1)=50
    advancedServo.setPositionMax(1)=1000
    
except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

#Set Current position as Start Position    
print ("Set Positions")
try:
   stepper.setCurrentPosition(0, 0)
   stepper.setCurrentPosition(2, 0)
   sleep(1)
except PhidgetException as e:
   print("Phidget Exception %i: %s" % (e.code, e.details))
   print("Exiting....")
   exit(1)

#Engage Motors
try:
   print("Set the motor as engaged...")
   stepper.setEngaged(0, True)
   stepper.setEngaged(2, True)
   sleep(1)
except PhidgetException as e:
   print("Phidget Exception %i: %s" % (e.code, e.details))
   print("Exiting....")
   exit(1)


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
        stepper.setEngaged(0, False)
        advancedServo.setEngaged(0, False) 
        stepper.setEngaged(2, False)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

def Engage():
    try:
        stepper.setEngaged(0, True)
        advancedServo.setEngaged(0, True)
        stepper.setEngaged(2, True)
        sleep(5)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
        
def goHome():
    try:
        stepper.setTargetPosition(0, 0)
        while stepper.getCurrentPosition(0) !=0:
            pass
        sleep(2)
        stepper.setTargetPosition(2, 0)
        while stepper.getCurrentPosition(2) !=0:
            pass
        advancedServo.setPosition(0, advancedServo.getPositionMin(0))
        while advancedServo.getPosition(0) != advancedServo.getPositionMin(0):
            pass
        sleep(2)
    except PhidgetException as e:
        print("Home Position - Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

def gotoSamplePosition(position):
   Engage()
   if position<0 or position>25:
      print("Invalid position: ",position)
      exit(1)
   try:
      stepper.setTargetPosition(0, MOVE[position][0])
      while stepper.getCurrentPosition(0) !=(MOVE[position][0]):
         pass
      sleep(2)
      stepper.setTargetPosition(2, MOVE[position][1])
      while stepper.getCurrentPosition(2) !=MOVE[position][1]:
         pass
      sleep(2)
   except PhidgetException as e:
      print("GoToPosition:  Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   sleep(5)
   
def samplePickUp(position):
    Z=(stepper.getCurrentPosition(0))
    Q=Z-DOWN_POSITION
    QQ=int(Q)
    try:
        advancedServo.setPosition(0, advancedServo.getPositionMax(0))
        while advancedServo.getPosition(0) != advancedServo.getPositionMax(0):
            pass
        sleep(8)
        stepper.setTargetPosition(0, QQ)
        while stepper.getCurrentPosition(0) !=QQ:
            pass
        sleep(1)
        advancedServo.setPosition(0, advancedServo.getPositionMin(0))
        while advancedServo.getPosition(0) != advancedServo.getPositionMin(0):
            pass
        sleep(8)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
   
def samplePutDown(position):    
    C=(stepper.getCurrentPosition(0))
    CC=int(C)
    TT=int(CC-DOWN_POSITION)
    W=C+DOWN_POSITION
    WW=int(W)
    try:
        stepper.setTargetPosition(0, TT)
        while stepper.getCurrentPosition(0) !=TT:
            pass
        sleep(2)
        advancedServo.setPosition(0, advancedServo.getPositionMax(0))
        while advancedServo.getPosition(0) != advancedServo.getPositionMax(0):
            pass
        sleep(8)
        stepper.setTargetPosition(0, MOVE[VAL][0])
        while stepper.getCurrentPosition(0) !=(MOVE[VAL][0]):
            pass
        sleep(2)
        advancedServo.setPosition(0, advancedServo.getPositionMin(0))
        while advancedServo.getPosition(0) != advancedServo.getPositionMin(0):
            pass
        sleep(8)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

def gotoOutsideBalanceFromInside():
   DataReadWrite.openBalanceDoor()
   try:
      stepper.setTargetPosition(2, -750)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)

   while stepper.getCurrentPosition(2) !=-750:
      pass
   sleep(2)
   
def gotoOutsideBalanceFromOutside():
   DataReadWrite.openBalanceDoor()
   try:
      stepper.setTargetPosition(2, -750)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)

   while stepper.getCurrentPosition(2) !=-750:
      pass
   sleep(2)

	
   stepper.setTargetPosition(0, -3100)
   while stepper.getCurrentPosition(0) !=-3100:
      pass
   sleep(2)
   advancedServo.setPosition(0, 118.00)
   while advancedServo.getPosition(0) != 118.00:
      pass
   sleep(8)
      

def putSampleOnBalance():
   ##Zeroing the Balance
   DataReadWrite.zeroBalance()
   sleep(1)
   ##Opening the door
   DataReadWrite.openBalanceDoor()
   try:
      stepper.setTargetPosition(0,-2900)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   gotoOutsideBalanceFromOutside()

   while stepper.getCurrentPosition(0) !=-2900:
      pass
   sleep(2)
   advancedServo.setPosition(0, advancedServo.getPositionMin(0))
   while advancedServo.getPosition(0) != advancedServo.getPositionMin(0):
      pass
   sleep(4)
   stepper.setTargetPosition(0,0)
   while stepper.getCurrentPosition(0) !=0:
      pass
   sleep(2)
   stepper.setTargetPosition(2, 0)
   while stepper.getCurrentPosition(2) !=0:
      pass
   sleep(2)
   ##Closing the Door
   DataReadWrite.closeBalanceDoor()
    
   advancedServo.setEngaged(0, False)
   sleep(2)
   Disengage()

def pickUpSampleFromBalance(): 
   Engage()
   sleep(5)
   try:
      stepper.setTargetPosition(2, -750)
   except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

   while stepper.getCurrentPosition(2) !=-750:
         pass
      
   sleep(2)
   ##Opening the door
   DataReadWrite.openBalanceDoor()
   advancedServo.setPosition(0,118.00)
   while advancedServo.getPosition(0) != 118.00:
      pass
   sleep(8)
   stepper.setTargetPosition(0, -3150)
   while stepper.getCurrentPosition(0) !=-3150:
      pass
   sleep(2)
   advancedServo.setPosition(0, advancedServo.getPositionMin(0))
   while advancedServo.getPosition(0) != advancedServo.getPositionMin(0):
      pass
   sleep(2)
   stepper.setTargetPosition(0, 0)
   while stepper.getCurrentPosition(0) !=0:
      pass
   sleep(1)
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
      samplePickUp(position)
      ## zerothe balance for each sample
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
      samplePutDown(position)
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
      samplePickUp(position)
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
      samplePutDown(position)
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
      samplePickUp(position)
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
      samplePutDown(position)
      DataReadWrite.closeBalanceDoor()
      position=position+1

def openGripper():
   print "now open gripper"
   try:
      advancedServo.setPosition(1, advancedServo.getPositionMax(1))
   except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
   time.sleep(2)

def closeGripper():
   print "now close gripper"
   #  Set the gripper to be open
   try:
      advancedServo.setPosition(1, advancedServo.getPositionMin(1))
   except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)  
   time.sleep(2)



