## Pre Fire Processing
## This consists of entering basic information for hte run
## Then sequentially weighing each sample and measuring change of weight through time. 
## What we want to see is no measureable change in direction for the weight.
## The weights of the samples then get used to calculate the "pre" weights

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

status="Pre-firing"

print "You should have already run zeroCrucibles.py to get the initial weights. "
print "This script should have also provided you the runID.  You will need it to continue. "

runID = ""
while runID=="":
	runID = raw_input('Enter the runID (e.g., 1)): ')      
      
setName=""
while setName=="":
   setName = raw_input( 'Enter name of sample set (e.g., Mississippian ): ')
   
setInitials=""
while setInitials == "":
   setInitials = raw_input( 'Researcher Initials (e.g., CPL): ')

setLocation=""
while setLocation == "":
   setLocation = raw_input( 'Sample Location (e.g., LMV): ')

numberOfSamples=""
while numberOfSamples=="":
   numberOfSamples = raw_input('How many samples? (e.g., 1,5,10): ')

preMeasurementTimeInterval=""
while preMeasurementTimeInterval=="":
   preMeasurementTimeInterval=raw_input('How long to measure each sample (minutes, e.g., 60): ')
   
intervalsec=""
while intervalsec=="":
   intervalsec = raw_input('Sampling interval (how often to check balance, in seconds, e.g., 5,10,15,30,120): ')
   
repetitions=""
while repetitions="":
   repetitions=raw_input('How many times to repeat the cycle of measurements for all of the samples? (e.g., 1,5,10): ')

setTemperature=""
while setTemperature == "":
   setTemperature = raw_input( 'Temperature for holding samples (e.g., 19.6): ')

setHumidity=""
while setHumidity == "":
   setHumidity = raw_input( 'Humidity for holding samples (e.g., 60.0): ')

runID=DataReadWrite.updateRunPreFire(runID,setInitials,setName,today,setLocation,preOrPost,intervalsec,setTemperature,setHumidity,status,preMeasurementTimeInterval,numberOfSamples,repetitions)

count=0
repeat=0

while count < numberOfSamples:
   # Get weight of empty crucible first. Then use this to subtract from balance reading.  
   #Now do an insert for tblSample for each sample include--- from here on we can then just update the record. 
    sampleID=DataReadWrite.insertNewSample(i_runID,i_crucibleID,v_description,d_dateTime,v_location,i_preOrPost,i_loggingInterval,f_temperature,f_humidity,v_status,i_preMeasurementTimeInterval,i_numberOfSamples)
   
   #make a list of the 
   listOfSamples.append(sampleID)
   count = count +1

while repeat < repetitions:
   xyzRobot.weighAllSamples(runID,listOfSamples,duration,loggingInterval,numberOfSamples)
   repeat = repeat +1
   	
		