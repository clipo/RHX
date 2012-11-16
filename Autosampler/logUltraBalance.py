__author__ = 'clipo'
#Basic imports
#sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")

import easygui
import sqlite3 as sqlite
import sys
import logging
from ctypes import *
import os
import io
import re
import serial
from time import sleep
import sched, time
from datetime import datetime
from datetime import timedelta
import msvcrt
import os, sys
from Tkinter import *
from numpy import *
import math
import ComPorts
from Tkinter import *
import tkFileDialog
from tkMessageBox import *
from tkColorChooser import askcolor
from tkFileDialog import askopenfilename
from msvcrt import kbhit,getch

#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs,OutputChangeEventArgs, SensorChangeEventArgs
from Phidgets.Devices.Stepper import Stepper
from Phidgets.Devices.AdvancedServo import AdvancedServo
from Phidgets.Devices.Servo import ServoTypes
from Phidgets.Devices.InterfaceKit import InterfaceKit


## interface number 8/8/8 for different sensors
HI_REZ_TEMPERATURE=4
TEMPERATURE = 6
HUMIDITY = 7
GRIPPERSENSOR = 3

balance = serial.Serial(port=ComPorts.UltraBalance, baudrate=9600, bytesize=8, parity='N', stopbits=1,
                                 timeout=1, xonxoff=0)
non_decimal = re.compile(r'[^\d.]+')
f = open('c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Logs/UltraBalanceBalanceLog.txt', 'w')

def getTemperature():
   try:
      value = interfaceKit.getSensorRawValue(HI_REZ_TEMPERATURE)/4.095
   except PhidgetException as e:

      return False
   sensor = double((value*0.222222222222)-61.1111111111+2.5) ## 2.5 added to match madgetech
   return sensor


def getHumidity():
   try:
      value = interfaceKit.getSensorRawValue(HUMIDITY)/4.095
   except PhidgetException as e:

      return False
   sensor = double((value*0.1906)-40.20000-5.92) ## 5.22 added to match madgetech
   return sensor

def readWeightFromStandardBalance():
   standard_balance.write('P\n\r')
   out = standard_balance.readline()
   #print "Balance reports: ", out

   #print "how many gs", out.count(' g')
   if out.count(' g')==1:
      out = out.replace('g', '')
      out = out.replace(' ', '')
      out = out.rstrip()
      return float(out)
   else:
      return False

def readWeightFromUltraBalance():
   ## balance read
   status = ""
   balance.write("S\n\r")
   bline = balance.readline()
   code = []
   if (len(bline) > 4):
      code.append(bline[0])
      code.append(bline[1])
      code.append(bline[2])
      string = ''.join(code)
      if (string == "S S"):
         status = "Stable"
      elif (string == "S D"):
         status = "Unstable"
      elif(string == "S I"):
         status = "Busy"
   else:
      status = "Error"


   weight = float(0.0)
   result = []
   if len(bline) == 18:
      bbline = bline.lstrip("S S   ")
      weights = bbline.replace(" g", "")
      weights = weights.rstrip(" ")
      weights = weights[:-1]
      weights = weights.rstrip("\n")
      weights = weights.rstrip("\r")
      weight = non_decimal.sub('', weights)
      #weight=re.search(float_pat,weights)
      if weight == "":
         weight = 0.0
         #if weight.count('.')>1:
      #   weight=0.0
      result.append(weight)
      result.append(status)
      return result
   else:
      return (weight, "Unstable");


def weighSample():
   listOfValues = []
   weight = float(0.0)
   count = 0
   kcount = 0
   averageWeight = 0.0
   stdevWeight = 0.0
   a = array([])
   count=0
   stop = False

   while not stop:
      if kbhit(): stop = getch()=='q'
      weight,status = readWeightFromUltraBalance()
      #print "weight: ",weight
      if weight is FALSE:
         print "."
      elif weight>0.0:
         count += 1
         humidity=getHumidity()
         temp=getTemperature()
         print count, "\t", temp, "\t", humidity,"\t",weight,"\n"
         stringvar= str(count)+"\t"+str(temp)+"\t"+str(humidity)+"\t"+str(weight)+"\n"
         f.write(stringvar)
      sleep(1)
   return


try:
   interfaceKit = InterfaceKit()
except RuntimeError as e:
   print "error %i: %s" % (e.code, e.details)

try:
   interfaceKit.openPhidget()
except PhidgetException as e:
   print "error %i: %s" % (e.code, e.details)

try:
   interfaceKit.waitForAttach(10000)
except PhidgetException as e:
   print("Phidget Exception %i: %s" % (e.code, e.details))




weighSample()