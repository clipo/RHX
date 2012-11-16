import time
from datetime import datetime
from datetime import timedelta
import msvcrt
from pyExcelerator import *  
import os, sys
from select import select
import sys
import serial
import random
import csv
import re
import AutoStepper

# open the serial port for the temperature and humidity controller
tempHumidity = serial.Serial(port='COM11', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=1, rtscts=0)

# open the serial port for the balance
balance = serial.Serial(port='COM9', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10, xonxoff=0, rtscts=0)

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

WaitTime=0
num = 1
stopCode=0
sampleNumber=1
ItNum=1
# OPEN FILE
curpath = os.path.dirname(__file__)   
workbook = Workbook()
worksheet2=workbook.add_sheet("summary")


now = datetime.today()
today = now.strftime("%m-%d-%y %H:%M:%S")
todayString=now.strftime("%y%m%d%H%M%S")
print "The current time/date is: ", today
diffTime = now - now
endOfFiring = now

preOrPost = raw_input('Pre firing weight determination (0) or Post firing (1) ')

if preOrPost=="1":
   print "Enter date at which the firing finished "
   startdate = raw_input('Format: mm-dd-yyyy --> ')
   sdate=startdate.split("-",3)
   print "Enter time at which the firing finished "
   starttime = raw_input('Format (24 hours): hh:mm:ss -->')
   stime=starttime.split(":",3)
   endOfFiring = datetime(int(sdate[2]), int(sdate[0]), int(sdate[1]), int(stime[0]), int(stime[1]), int(stime[2]))

   diffTime = now - endOfFiring

   #print diffTime.seconds

   print "Seconds elapsed since firing ", diffTime.seconds
   #print "Minutes elapsed since firing ", diffTime.minutes

intervalseca = raw_input('Enter sampling interval (in seconds, e.g., 5,10,15,30,120): ')

setName = raw_input( 'Enter set name (e.g., Mississippian ): ')
setNameCSV=str(setName)
filename = raw_input('Enter name for output file (e.g., output):  ')
# continue...
#open a backup text file
csvFile = "./"+todayString+"_"+filename+".csv"
#f = open(csvFile, 'w')
fileWriter = csv.writer(open(csvFile, 'wb'), delimiter=',')
if preOrPost == "0":
   fileWriter.writerow(['Point','Set Name','Sample','Iteration','Date','Weight','Temp','Humidity','Pressure','Light'])
else:
   fileWriter.writerow(['Point','Set Name','Sample','Iteration','Date','ElapsedMin','Weight','ElaspedMin^0.25','Temp','Humidity','Pressure','Light'])
def NumUp():
   global num
   num = num + 1
   print "NumUp: ",num
def StopUp():
   global stopCode
   stopCode = stopCode + 1
   print "StopCode: ",stopcode
def StopZero():
   global stopCode
   stopCode = 0
   print "StopCode: ",stopcode
def SampleNumUp():
   global sampleNumber
   sampleNumber=sampleNumber+1
   print "sampleNumber: ",stopcode
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

   # number of measurements for this sample. Resets to 0 when a new sample is included
   snum = 1
   listOfValues=[]
   listOfWeightValues=[]
   listOfTempValues=[]
   listOfPressureValues=[]
   listOfHumidityValues=[]

   sampleNumberstr=str(sampleNumber)

   sampleName=setName+"-"+sampleNumberstr
   sampleNum=int(sampleNumber)
   random.seed()
   non_decimal = re.compile(r'[^\d.]+')


#### Main Loop     
   while stopCode<=HackSol:
      time.sleep(intervalsec)
      
      if scount == 50:
         scount=0
         
##      balance read
      balance.write("S\n\r")
      bline = balance.readline()
      print "Balance Ouput:  ", bline
      weight=0.0
      if len(bline) == 18:	
         bbline = bline.lstrip("S S   ")
         weight = bbline.replace(" g", "")
         weight=weight.rstrip()
         weight = non_decimal.sub('', weight)
         if weight=="":
            weight=0.0
         if weight.count('.')>1:
            weight=0.0
      else:
         weight=0.0
      
      if weight==0.0:
         continue
         
      ## temp Humidity Read
      
      tline=" "
      readOne=""
      ## Example string:  $,57.8,79,51.4,1009.48,0.0,0.0,-1,0.00,0.00,*
      ##                  $,57.8,79,51.5,1009.28,0.0,0.0,-1,0.00,0.00,*
      time.sleep(1)
      tempHumidity.write("\n")
      while(readOne <> "$"):
         readOne =tempHumidity.read(1)
      tline = "$"+tempHumidity.read(46)
      while( tline.find("$") <> 0 and tline.find("*") < 44 ):
         print "Incorrect string. try again."
         time.sleep(0.5*random.random())
         print "TempHumidity Reading: ", tline
         tline="$".tempHumidity.read(46)
      ## print "Weather: ",tline

      listOfWeightValues.append(weight)
      listOfValues=tline.split(",",10)
      humidity=listOfValues[1]
      tempC=0.0
      tempF=listOfValues[2]
      tempC=(float(tempF)-32)*5/9
      pressure=listOfValues[4]
      light=listOfValues[5]

      listOfTempValues.append(tempC)
      listOfHumidityValues.append(humidity)
      listOfPressureValues.append(pressure)

      # Find elapsed time
      now = datetime.today()
      today = now.strftime("%m-%d-%y %H:%M:%S")
      diffTime2 = now - endOfFiring

      diffSeconds = diffTime2.seconds
      diffMinutes = float(diffSeconds/60)
      diffMinutesQuarterPower = pow(diffMinutes,0.25)
      print "Logged: " + str(num) + " - " + str(sampleName) + " - " + str(weight) + " - " + str(tempC) + " - " + str(humidity)
      if preOrPost == "0":
         fileWriter.writerow([num,setNameCSV,sampleName,ItNum,today,float(weight),tempC,humidity,pressure,light]) ##Elapsed Time and the standard weight from second balance and iteration number
      else:
         fileWriter.writerow([num,setNameCSV,sampleName,ItNum,today,diffMinutes,float(weight),diffMinutesQuarterPower,tempC,humidity,pressure,light])
      NumUp()
      StopUp()
      snum = snum +1
      
##Saving the File
       
   # now clear the variables and get the next sample number      
   listOfWeightValues=[]
   listOfTempValues=[]
   listOfHumidityValues=[]
   listOfPressureValues=[]
   sampleNum=sampleNum+1
   snum=0
   sampleNumstr=str(sampleNum)
   sampleName=setName+"-"+sampleNumstr
   sampleNum=int(sampleNum)
   
   ## count how many mesurements before save
   ## save after 50 recordings
   scount = scount + 1
   print ("DJ! Flip that Shit!")
   SampleNumUp()
   AutoStepper.MoveBack()

##   # in case it gets here   
##   tempHumidity.close()
##   balance.close()
##   workbook.save(os.path.join(curpath, file))
##   exit(0)
