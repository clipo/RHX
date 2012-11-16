#Basic imports
from ctypes import *
import sys
from time import sleep
import sched, time
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs
from Phidgets.Devices.Stepper import Stepper
from Phidgets.Devices.AdvancedServo import AdvancedServo
from Phidgets.Devices.Servo import ServoTypes


#Movement List - Position 0 is motor 0 - Position 1 is motor 1 ... made sense ...
MOVE=[[100,1650],[-475,1650],[-850,1650],[-1225,1650],[-1600,1650],[-100, 1250],[-475,1250],[-850,1250],\
      [-1225,1250],[-1600,1250],[-100, 850],[-475,850],[-850,850],[-1225,850],[-1600,850],[-100, 450],\
      [-475,450],[-850,450],[-1225,450],[-1600,450],[-100, 50],[-475,50],[-850,50],[-1225,50],[-1600,50]]

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
