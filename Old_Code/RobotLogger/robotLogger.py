import MySQLdb
import serial
import time
from datetime import datetime
from datetime import timedelta
import msvcrt
from pyExcelerator import *  
import os, sys
from select import select
import signal
import sys
import random
import csv
import re


## Create Connection to the Database
conn = MySQLdb.connect (host = "134.139.125.220",
                           user = "rhx",
                           passwd = "rhx",
                           db = "rhx")
                           
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

# open the serial port for the temperature and humidity controller
tempHumidity = serial.Serial(port='COM1', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=1, rtscts=0)
tempHumidity.write("x\n")

# open the serial port for the balance
balance = serial.Serial(port='COM9', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10, xonxoff=0, rtscts=0)

now = datetime.today()
today = now.strftime("%m-%d-%y %H:%M:%S")
todayString=now.strftime("%y%m%d%H%M%S")
print "The current time/date is: ", today
diffTime = now - now
endOfFiring = now

#Ask Set Name (e.g., Mississippian)
setName = raw_input( 'Enter set name (e.g., Mississippian ): ')
filename=""
fileokay=0
file=""

#Ask Sample Run Name/Number (NEAR1, NEAR2)
runName = raw_input( 'Enter run name (e.g., NEAR1 ): ')

#Location
runLocation = raw_input( 'Enter run name (e.g., NEAR1 ): ')

#Operator Name
operatorName = raw_input( 'Enter operator name (e.g., CPL ): ')


#Ask # of samples - N
numberOfSamples = raw_input( 'Enter Number of Samples (e.g., 25): ')
numberOfSamples=int(numberOfSamples)

#Ask Logging interval
intervalsec = raw_input('Enter sampling interval (in seconds, e.g., 5,10,15,30,120): ')
intervalsec=int(intervalsec)

#Temperature of firing
temperatureOfFiring = raw_input( 'Temperature of Firing (e.g., 500): ')
temperatureOfFiring=int(temperatureOfFiring)

#Description
description = raw_input( 'Description of samples: ')

while fileokay==0:
   filename = raw_input('Enter name for output file (e.g., output):  ')
   file=filename+".xls"
   response=""
   if (os.path.isfile(file)):
      response = raw_input('File exits! Do you want to overwrite the file (y/n)?:')
      if response == "y":
         fileokay=1
   else:
      print "you entered: ", file, "\n"
      fileokay=1
      break

preOrPost = raw_input('Pre firing weight determination (0) or Post firing (1) ')

if preOrPost=="1":
   print "Enter date at which the firing started "
   istartdate = raw_input('Format: mm-dd-yyyy --> ')
   isdate=startdate.split("-",3)
   print "Enter time at which the firing started "
   istarttime = raw_input('Format (24 hours): hh:mm:ss -->')
   istime=starttime.split(":",3)
   startOfFiring = datetime(int(sdate[2]), int(sdate[0]), int(sdate[1]), int(stime[0]), int(stime[1]), int(stime[2]))
   duration = raw_input('Enter duration of firing finished (minutes):')
   duration=int(duration)
   endOfFiring = startOfFiring + duration
   diffTime = now - endOfFiring
   
   
   #print diffTime.seconds
   print "Seconds elapsed since firing ", diffTime.seconds
   print "Minutes elapsed since firing ", diffTime.minutes

#open a backup text file
csvFile = "./"+todayString+".csv"
#f = open(csvFile, 'w')
fileWriter = csv.writer(open(csvFile, 'wb'), delimiter=',')


# OPEN FILE
curpath = os.path.dirname(__file__)   
workbook = Workbook()
worksheet2=workbook.add_sheet("summary")


cursor = conn.cursor ()
cursor.execute ("""
	   INSERT INTO tblRun (v_locationCode, i_numberOfSamples, d_dateTime, v_operatorName,
	   		i_equilibrationDuration,d_dateTimeFiring,i_durationOfFiring,i_temperatureOfFiring,
	   		i_logginInterval,v_description)
       VALUES
         (%s, %s, %s, %s, %s
         , (location, numberOfSamples, today, operatorName,duration,startOfFiring ),
         ('frog', 'amphibian'),
         ('tuna', 'fish'),
         ('racoon', 'mammal')
     """)


if preOrPost == "0":
   sheetName="prefire"
   worksheet = workbook.add_sheet(sheetName)
   worksheet.write(0,0, 'Point Number')
   worksheet.write(0,1, 'Sample')
   worksheet.write(0,2, 'Date')
   worksheet.write(0,3, 'Weight')
   worksheet.write(0,4, 'Temperature (C)')
   worksheet.write(0,5, 'Humidity (%RH)')
   worksheet.write(0,6, 'Pressure (Pascals)')
   worksheet.write(0,7, 'Light')

   fileWriter.writerow(['Point','Sample','Date','Weight','Temp','Humidity','Pressure','Light'])
   
   worksheet2.write(0,0,'Sample Num')
   worksheet2.write(0,1,'Sample')
   worksheet2.write(0,2,'Number of Measurements')
   worksheet2.write(0,3,'Date')
   worksheet2.write(0,4,'Mean Weight')
   worksheet2.write(0,5,'StdDev Weight')
   worksheet2.write(0,6,'Mean Temp')
   worksheet2.write(0,7,'StdDev Temp')
   worksheet2.write(0,8,'Mean RH')
   worksheet2.write(0,9,'StdDev RH')
   worksheet2.write(0,10,'Mean Pressure')
   worksheet2.write(0,11,'StdDev Pressure')
else:
   sheetName="postfire"
   worksheet = workbook.add_sheet(sheetName)
   worksheet.write(0,0, 'Point Number')
   worksheet.write(0,1, 'Sample')
   worksheet.write(0,2, 'Date')
   worksheet.write(0,3, 'Elapsed Minutes')
   worksheet.write(0,4, 'Weight')
   worksheet.write(0,5, 'Elapsed Minutes^0.25')
   worksheet.write(0,6, 'Temperature (C)')
   worksheet.write(0,7, 'Humidity (%RH)')
   worksheet.write(0,8, 'Pressure (Pascals)')
   worksheet.write(0,9, 'Light')
  
   fileWriter.writerow(['Point','Sample','Date','ElapsedMin','Weight','ElaspedMin^0.25','Temp','Humidity','Pressure','Light'])
   
   worksheet2.write(0,0,'Sample Num')
   worksheet2.write(0,1,'Sample')
   worksheet2.write(0,2,'Number of Measurements')
   worksheet2.write(0,3,'Date')
   worksheet2.write(0,4,'Mean Weight')
   worksheet2.write(0,5,'StdDev Weight')
   worksheet2.write(0,6,'Mean Temp')
   worksheet2.write(0,7,'StdDev Temp')
   worksheet2.write(0,8,'Mean RH')
   worksheet2.write(0,9,'StdDev RH')
   worksheet2.write(0,10,'Mean Pressure')
   worksheet2.write(0,11,'StdDev Pressure')

# value to look for to end loop
stopCode=0
# total number of measurements
num = 1
# number of times before save
scount =1

# number of measurements for this sample. Resets to 0 when a new sample is included
snum = 1
listOfValues=[]
listOfWeightValues=[]
listOfTempValues=[]
listOfPressureValues=[]
listOfHumidityValues=[]




If prefire -- record empty crucible weight
	Create file Sample Run Number with -pre suffix (excel and csv)
	Create log file for run (or mysql?)
		-- named by time
		-- data include:  # of samples, intervals, etc.
		-- start weights of crucibles.
		-- end/equilbrated weights of samples.
	Ask equilibration time
	notify user that rack must be installed and loaded with X crucibles 
	go through each of the crucibles (1-N)
	bring to scale and weigh for X minutes
	
	Pause -- tell user to add sherds to rack, reinsert
	
	Pause for X minutes to let samples equilibrate
	(( plot data? ))
	
	Once X minutes is complete, load N samples
	Allow each to be weighed for X minutes
	Logger stuff
	
	Notify user the equilibration is done... and sherds are ready for firing
	
If post-fire 
	get log file for run
		-- load # of samples
		-- empty weights
		-- equilibrated weights /std deviations
	Create file Sample Run Number with -post suffix (excel and csv)
	Ask firing date/time (start)
	Ask firing duration (minutes)
	Calculate firing finish time
	
	Load first sample
		motors on
		door open
		door check
		sample loaded
		door close
		logger on, weather on
		log data at Y intervals
		repeat for X minutes
	Load next sample...
		motors off
	 	logger on -weight
	 		
	repeat... N times
	
Summarize? Graph?