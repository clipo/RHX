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

def NumUp():
   global num
   num = num + 1

def StopUp():
   global stopCode
   stopCode = stopCode + 1

def StopZero():
   global stopCode
   stopCode = 0

def SampleNumUp():
   global sampleNumber
   sampleNumber=sampleNumber+1

def ItNumUp():
   global ItNum
   ItNum=ItNum+1
   global sampleNumber
   sampleNumber=1

def MoveThis():
   AutoStepper.GoToPosition()

def TimeWeigh():
   CTSec=raw_input("How long do you want to weigh the crucibles? (Minutes) ")
   CTMin=int(CTSec)*60
   global WaitTime
   WaitTime=CTMin
   MoveThis()

def StartWeighing():
   WeighSample()
   
def WeighSample():
   StopZero()
   scount = 1
   intervalsec=int(intervalseca)
   HackStep1=int(WaitTime/60)
   HackStep2 = 60//intervalsec
   HackSol = int(HackStep2*HackStep1)

def WeighCrucibles(runID,numberOfSamples,CTMinutes):
   CTMin=int(CTMinutes)*60
   global WaitTime
   WaitTime=CTMin
   MoveThis()

## some values
WaitTime=0
num = 1
stopCode=0
sampleNumber=1
ItNum=1

now = datetime.today()
today = now.strftime("%m-%d-%y %H:%M:%S")
todayString=now.strftime("%y%m%d%H%M%S")
print "The current time/date is: ", today
diffTime = now - now
endOfFiring = now

filename=""
fileokay=0
file=""
setInitials=""

preOrPost=2

status ="Post-fired"
# we want to just update the record during the post-fire phase
runID=""
while runID == "":
   runID = raw_input('Run ID: (e.g., 1): ')
   
locationCode=""
numberOfSamples=0
description=""
temperature=0.0
humidity=0.0   

(locationCode,numberOfSamples,description,temperature,humidity)=getRunInfo(runID)
            
setInitials=""
while setInitials == "":
   setInitials = raw_input( 'Researcher Initials (e.g., CPL): ')
    
dateTimeFiring=""
      
print "Enter date at which the firing started: "
startdate=""
while startdate=="":
   startdate = raw_input('Format: mm-dd-yyyy --> ')

sdate=startdate.split("-",3)
print "Enter start time of firing: "
starttime=""
while starttime=="":
   starttime = raw_input('Format (24 hours): hh:mm:ss -->')
stime=starttime.split(":",3)

startOfFiring = datetime(int(sdate[2]), int(sdate[0]), int(sdate[1]), int(stime[0]), int(stime[1]), int(stime[2]))

durationOfFiring=""
while durationOfFiring=="":
   durationOfFiring = raw_input('Duration of firing (minutes): ')
endOfFiring = startOfFiring + timedelta(minutes,durationOfFiring)
   
# minutes since firing ended
diffTime = now - endOfFiring
   
tempFiring=""
while tempFiring == "":
   tempFiring=raw_input('Temperature of firing (e.g., 600, 700): ') 

intervalsec=""
postMeasurementTimeInterval=""
while postMeasurementTimeInterval=="":
   postMeasurementTimeInterval=raw_input('How long to measure each sample (minutes, e.g., 60): ')

while intervalsec:
   intervalsec = raw_input('Sampling interval (how often to check balance, in seconds, e.g., 5,10,15,30,120): ')

repetitions=""
while repetitions="":
   repetitions=raw_input('How many times to repeat the cycle of measurements for all of the samples? (e.g., 1,5,10): ')


runID=DataReadWrite.updateRunPostFire(runID,setInitials,preOrPost,status,durationOfFiring,temperatureOfFiring,intervalsec,durationOfPostMeasurements,repetitions,endOfFiring)

count=0
repeat=0
 
while repeat < repetitions:
   xyzRobot.weighAllSamplesPostFire(runID,listOfSamples,duration,loggingInterval,numberOfSamples,startTime):
   repeat = repeat +1

   

