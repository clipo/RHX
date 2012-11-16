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
import enhancedserial

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
tempHumidity = enhancedserial.EnhancedSerial(port='COM11', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2, xonxoff=1, rtscts=0)
time.sleep(1)
 
# open the serial port for the balance
balance = serial.Serial(port='COM9', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10, xonxoff=0, rtscts=0)

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

intervalsec = raw_input('Enter sampling interval (in seconds, e.g., 5,10,15,30,120): ')
#startingweight = raw_input('Enter approx. starting weight (g): ')

setName = raw_input( 'Enter set name (e.g., Mississippian ): ')
filename=""
fileokay=0
file=""

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


# continue...
#open a backup text file
csvFile = "./"+todayString+".csv"
#f = open(csvFile, 'w')
fileWriter = csv.writer(open(csvFile, 'wb'), delimiter=',')

intervalsec=int(intervalsec)

# OPEN FILE
curpath = os.path.dirname(__file__)   
workbook = Workbook()
worksheet2=workbook.add_sheet("summary")


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

sampleNumber=raw_input('Enter first sample number to begin (e.g., 1): ')

sampleName=setName+"-"+sampleNumber
sampleNum=int(sampleNumber)
keyPress=""
print "Press 'n' to enter a new sample or 'x' to exit"
random.seed()
non_decimal = re.compile(r'[^\d.]+')

while stopCode==0:
   if msvcrt.kbhit():
      keyPress = msvcrt.getch()
   time.sleep(intervalsec)
   
 
   if scount == 50:
      #workbook.save(file)
      scount=0  ## this line saves the file after 50 entries. I assumed it would
				## just "save the file" -- but it creates a new one
				## so its only 49 lines long. crap.
				## that was to make it not lose all the data in the case of a ctrl-break
				## Hmmm. Can get rid of that. at least for now...
				## its possible that it scount is somehow being misused so that it start writing
				## on line scount -- back to the beginning. that shouldnt be happening though
				## as scount is simply the save count. will have to see
				##
   ## balance read
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
   #print "The current time/date is: ", today
##This appears to be where the elapsed minutes function breaks down ...
##I would wager this is caused by a conflict between this diffTime being a local
##variable and the global diffTime variable - changing to diffTime2
   diffTime2 = now - endOfFiring

   diffSeconds = diffTime2.seconds
   diffMinutes = float(diffSeconds/60)
   #print "Seconds elapsed since firing ", diffTime.seconds
   #print "Minutes elapsed since firing ", diffTime.minutes
   diffMinutesQuarterPower = pow(diffMinutes,0.25)
   print "Logged: " + str(num) + " - " + str(sampleName) + " - " + str(weight) + " - " + str(tempC) + " - " + str(humidity)
   if sheetName == "prefire":
      worksheet.write(num,0,num)
      worksheet.write(num,1,sampleName)
      worksheet.write(num,2,today)
      worksheet.write(num,3,float(weight))
      worksheet.write(num,4,tempC)
      worksheet.write(num,5,humidity)
      worksheet.write(num,6,pressure)
      worksheet.write(num,7,light)
      fileWriter.writerow([num,sampleName,today,float(weight),tempC,humidity,pressure,light])
   else:
      worksheet.write(num,0, num)
      worksheet.write(num,1, sampleName)
      worksheet.write(num,2, today)
      worksheet.write(num,3, diffMinutes)
      worksheet.write(num,4, float(weight))
      worksheet.write(num,5, diffMinutesQuarterPower)
      worksheet.write(num,6, tempC)
      worksheet.write(num,7, humidity)
      worksheet.write(num,8, pressure)
      worksheet.write(num,9, light)
      fileWriter.writerow([num,sampleName,today,diffMinutes,float(weight),diffMinutesQuarterPower,tempC,humidity,pressure,light])   
   if keyPress == "x":
      sWeightAverage = average(listOfWeightValues)
      sWeightStdev = std(listOfWeightValues)
      sHumidityAverage = average(listOfHumidityValues)
      sHumidityStdev = std(listOfHumidityValues)
      sTempAverage = average(listOfTempValues)
      sTempStdev = std(listOfTempValues)
      sPressureAverage = average(listOfPressureValues)
      sPressureStdev = std(listOfPressureValues)
      worksheet2.write(int(sampleNum),0,sampleNumber)
      worksheet2.write(int(sampleNum),1,sampleName)
      worksheet2.write(int(sampleNum),2,str(snum))
      worksheet2.write(int(sampleNum),3,str(today))
      worksheet2.write(int(sampleNum),4,str(sWeightAverage))
      worksheet2.write(int(sampleNum),5,str(sWeightStdev))
      worksheet2.write(int(sampleNum),6,str(sTempAverage))
      worksheet2.write(int(sampleNum),7,str(sTempStdev))
      worksheet2.write(int(sampleNum),8,str(sHumidityAverage))
      worksheet2.write(int(sampleNum),9,str(sHumidityStdev))
      worksheet2.write(int(sampleNum),10,str(sPressureAverage))
      worksheet2.write(int(sampleNum),11,str(sPressureStdev))
      tempHumidity.close()
      balance.close()
      workbook.save(file)
      break
      stopCode=1
      
   ## if we want a new sample to be started   
   if keyPress == "n": 
      sWeightAverage = average(listOfWeightValues)
      sWeightStdev = std(listOfWeightValues)
      sHumidityAverage = average(listOfHumidityValues)
      sHumidityStdev = std(listOfHumidityValues)
      sTempAverage = average(listOfTempValues)
      sTempStdev = std(listOfTempValues)
      sPressureAverage = average(listOfPressureValues)
      sPressureStdev = std(listOfPressureValues)
      worksheet2.write(int(sampleNum),0,sampleNumber)
      worksheet2.write(int(sampleNum),1,sampleName)
      worksheet2.write(int(sampleNum),2,str(snum))
      worksheet2.write(int(sampleNum),3,str(today))
      worksheet2.write(int(sampleNum),4,str(sWeightAverage))
      worksheet2.write(int(sampleNum),5,str(sWeightStdev))
      worksheet2.write(int(sampleNum),6,str(sTempAverage))
      worksheet2.write(int(sampleNum),7,str(sTempStdev))
      worksheet2.write(int(sampleNum),8,str(sHumidityAverage))
      worksheet2.write(int(sampleNum),9,str(sHumidityStdev))
      worksheet2.write(int(sampleNum),10,str(sPressureAverage))
      worksheet2.write(int(sampleNum),11,str(sPressureStdev))
      # save worksheet
      workbook.save(file)
	  ## it saves the file here too - everytime a new sample gets entered. I havent seen this cause a 
	  ## a problem yet -- it seems to retain all of the samples. Have you?
	  ##I haven't got to press "n" yet... 
	  ## all of my testing showed this worked -- but its something to consider (look at). 
	  ## let me try to fix the read thing -- to get it synced up correctly...
	  
      # now clear the variables and get the next sample number      
      listOfWeightValues=[]
      listOfTempValues=[]
      listOfHumidityValues=[]
      listOfPressureValues=[]
      sampleNum=sampleNum+1
      textS="Enter next sample number (e.g., " + str(sampleNum) + ") "
      if textS=="":
      	textS=str(sampleNum)
      snum=0
      sampleNum=raw_input(textS)
      sampleName=setName+"-"+sampleNum
      sampleNum=int(sampleNum)
      keyPress=""
   num = num + 1
   #print num
   snum = snum +1
   
   ## count how many mesurements before save
   ## save after 50 recordings
   scount = scount + 1

# in case it gets here   
tempHumidity.close()
balance.close()
workbook.save(os.path.join(curpath, file))
exit
