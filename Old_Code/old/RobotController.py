#!/usr/bin/python
# Filename: RobotController.py

#Basic imports
from ctypes import *
import os
import io
import serial
import sys
from time import sleep
import sched, time
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs
from Phidgets.Devices.Stepper import Stepper
from Phidgets.Devices.AdvancedServo import AdvancedServo
from Phidgets.Devices.Servo import ServoTypes
import DataReadWrite

#Movement List - Position 0 is motor 0 - Position 1 is motor 2 ... made sense ...
MOVE=[[0,-1450],[-400,-1450],[-750,-1450],[-1100,-1535],[-1450,-1535],[-50, -1135],[-450,-1135],[-850,-1135],[-1250,-1135],[-1650,-1135],[-50, -735],[-450,-735],[-850,-735],[-1250,-735],[-1650,-735],[-50, -335],[-450,-335],[-850,-335],[-1250,-335],[-1650,-335],[-50, 35],[-450,35],[-850,35],[-1250,35],[-1650,35]]

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
print("Opening phidget object....")

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

def HomePosition():
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
        sleep(8)
    except PhidgetException as e:
        print("Home Position - Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

def Killswitch():
    try:
        print ("Killswitch engaged")
        stepper.setTargetPosition(0, 0)
        while stepper.getCurrentPosition(0) !=0:
            pass
        sleep(2)
        stepper.setTargetPosition(2, 0)
        while stepper.getCurrentPosition(2) !=0:
            pass
        sleep(2)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    Disengage()
    exit(1)
    
##Picks Crucible up off of the tray
def samplePickUp():
    Z=(stepper.getCurrentPosition(0))
    Q=Z-150
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

##Places Crucible back down on the tray
def samplePutDown():
    C=(stepper.getCurrentPosition(0))
    CC=int(C)
    TT=int(CC-150)
    W=C+150
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

#MotorMovers
def goToSamplePosition(1,position):
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
   ## Now pick up the crucible
   collectSample()
            
##Begin the Program
def moveSampleToBalance():
   stepper.setTargetPosition(2, -750)
   while stepper.getCurrentPosition(2) !=-750:
      pass
   sleep(2)
   ##Zeroing the Balance
   DataReadWrite.zeroBalance()
   sleep(1)
   ##Opening the door
	
   DataReadWrite.openBalanceDoor()
	
   stepper.setTargetPosition(0, -3100)
   while stepper.getCurrentPosition(0) !=-3100:
      pass
   sleep(2)
   advancedServo.setPosition(0, 118.00)
   while advancedServo.getPosition(0) != 118.00:
      pass
   sleep(8)
   stepper.setTargetPosition(0,-2900)
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
   DataWriteWrite.closeBalanceDoor()
    
   advancedServo.setEngaged(0, False)
   sleep(2)
   Disengage()

##Moves the Crucible from the balance back to its home position
def moveSampleBack(position):
   Engage()
   sleep(5)
   try:
      stepper.setTargetPosition(2, -750)
      while stepper.getCurrentPosition(2) !=-750:
         pass
      
      sleep(2)
      ##Opening the door
      DataWriteWrite.openBalanceDoor()
      
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
      sleep(8)
      stepper.setTargetPosition(0, 0)
      while stepper.getCurrentPosition(0) !=0:
         pass
      sleep(1)
      ##Closing the Door
      DataWriteWrite.closeBalanceDoor()
      
      stepper.setTargetPosition(2, 0)
      while stepper.getCurrentPosition(2) !=0:
         pass
      sleep(2)
      ##Return to the samples home XY position
      stepper.setTargetPosition(0, MOVE[VAL][0])
      while stepper.getCurrentPosition(0) !=MOVE[position][0]:
         pass
      stepper.setTargetPosition(2, MOVE[VAL][1])
      while stepper.getCurrentPosition(2) !=MOVE[position][1]:
         pass
      sleep(2)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   DataWriteWrite.zeroBalance()

def weighAllCrucibles(initials,numberOfSamples,measurementTimeInterval,duration):
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
      goToSamplePosition(1,position)
      moveSampleToBalance(position)
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
                
      MoveSampleBack(position)
      Deposit()
      position=position+1
   return (runID)
	  
def weighAllSamplesPreFire(runID,listOfSamples,duration,loggingInterval,numberOfSamples):
   # Find elapsed time
   #first put robot back to zero
   position=0
   #HomePosition()
   listOfValues=()
   crucibleWeight=0.0
   while position < numberOfSamples:
      crucibleWeight=getCrucibleWeight(runID,position)
      sampleID=getSampleID(runID,position)
      goToSamplePosition(1,position)
      moveSampleToBalance(position)
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
         	        
      moveSampleBack(position)
      Deposit()
      position=position+1

def weighAllSamplesPostFire(runID,listOfSamples,duration,loggingInterval,numberOfSamples,timeOfFiring):
   # Find elapsed time
   #first put robot back to zero
   position=0
   #HomePosition()
   listOfValues=()
   crucibleWeight=0.0
   while position < numberOfSamples:
      crucibleWeight=getCrucibleWeight(runID,position)
      sampleID=getSampleID(runID,position)
      goToPosition(position)
      moveSampleToBalance(position)
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
      	 timeElapsed= now - timeOfFiring
      	 timeElapsedQuarterPower = pow(timeElapsed,0.25)
	     DataReadWrite.insertPostFireMeasurement(runID,sampleID,position,weightMeasurement,temperature,humidity,pressure,light,endOfFiring,crucibleWeight,today,timeElapsed,timeElapsedQuarterPower)
	     
         sleep(loggingInterval)
         	        
      moveSampleBack(position)
      Deposit()
      position=position+1
