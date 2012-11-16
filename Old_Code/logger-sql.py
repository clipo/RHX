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
import AutoStepper
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

preOrPost=""
while preOrPost=="":
	preOrPost = raw_input(' Crucible zero (0), Pre firing weight determination (1) or Post firing (2) : ')

# POST firing value for preOrPost is 2
if preOrPost=="2":
   status ="Post-fired"
   # we want to just update the record during the post-fire phase
   runID=""
   while runID == "":
      runID = raw_input('Run ID from prefiring (e.g., 1): ')
   locationCode=""
   numberOfSamples=0
   description=""
   temperature=0.0
   humidity=0.0   
   c = conn.cursor()
   c.execute('select * from tblRun where i_runID = ?',runID)
   for row in cur.fetchall():
      locationCode=row[1]
      numberOfSamples=row[2]
      description=row[14]
      temperature=row[17]
      humidity=row[18]
      
   setInitials=""
   while setInitials == "":
      setInitials = raw_input( 'Researcher Initials (e.g., CPL): ')
      
   print "Enter date at which the firing started: "
   startdate = raw_input('Format: mm-dd-yyyy --> ')
   sdate=startdate.split("-",3)
   print "Enter start time of firing: "
   starttime = raw_input('Format (24 hours): hh:mm:ss -->')
   stime=starttime.split(":",3)
   startOfFiring = datetime(int(sdate[2]), int(sdate[0]), int(sdate[1]), int(stime[0]), int(stime[1]), int(stime[2]))
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

   t=(setInitials,description,today,locationCode,1,interval,temperature,humidity,status,numberOfSamples,runID,postMeasurementTimeInterval,runID) 
   
   # Insert initial data for the run
   c.execute('update tblRun SET v_operatorName=?,v_description=?,d_dateTime=?,v_locationCode=?,i_preOrPost=?,i_loggingInterval=?,f_temperature=?,f_humidity=?,v_status=?,i_numberOfSamples=?,i_linkedRun=?,i_postMeasurementTimeInterval=? where i_runID=?',t) 
   # Save (commit) the changes
   conn.commit()
   # Now get the id for the run so we can update with other info as we ask...
   runID = c.lastrowid
   print "RUN ID = ",runID, " <WRITE THIS DOWN>"
   raw_input('Press any key to continue')
   WeighSamples

# must mean pre-firing
else if preOrPost==1:
   status="Pre-firing"

   # we want to just update the record during the post-fire phase (after zeroing)
   runID=""
   while runID == "":
      runID = raw_input('Run ID from crucible zero step (e.g., 1): ')
      
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
   while numberOfSamples:
      numberOfSamples = raw_input('How many samples? (e.g., 1,5,10): ')

   preMeasurementTimeInterval=""
   while preMeasurementTimeInterval=="":
      preMeasurementTimeInterval=raw_input('How long to measure each sample (minutes, e.g., 60): ')
   
   intervalsec=""
   while intervalsec:
      intervalsec = raw_input('Sampling interval (how often to check balance, in seconds, e.g., 5,10,15,30,120): ')

   setTemperature=""
   while setTemperature == "":
      setTemperature = raw_input( 'Temperature for holding samples (e.g., 19.6): ')

   setHumidity=""
   while setHumidity == "":
      setHumidity = raw_input( 'Humidity for holding samples (e.g., 60.0): ')
   
   t=(setInitials,setName,today,setLocation,preOrPost,intervalsec,setTemperature,setHumidity,status,preMeasurementTimeInterval,numberOfSamples)
   # create a cursor to the database
   c = conn.cursor()
   # Insert initial data for the run
   c.execute('update tblRun SET v_operatorName=?,v_description=?,d_dateTime=?,v_locationCode=?,i_preOrPost=?,i_loggingInterval=?,f_temperature=?,f_humidity=?,v_status=?,i_preMeasurementTimeInterval=?,i_numberOfSamples=? where i_runID=?',t)
   # Save (commit) the changes
   conn.commit()
   # Now get the id for the run so we can update with other info as we ask...
   runID = c.lastrowid
   raw_input('Press any key to continue')
   
else:
   # get the weight of the crucibles - empty. 
   setInitials=""
   while setInitials == "":
      setInitials = raw_input( 'Researcher Initials (e.g., CPL): ')

   numberOfSamples=""
   while numberOfSamples:
      numberOfSamples = raw_input('How many crucibles? (e.g., 1,5,10): ')
      intervalsec=""
   while intervalsec:
      intervalsec = raw_input('Sampling interval (how often to check balance, in seconds, e.g., 5,10,15,30,120): ')

   measurementTimeInterval=""
   while measurementTimeInterval=="":
      preMeasurementTimeInterval=raw_input('How long to measure each crucible (minutes, e.g., 60): ')
   
   runID=""
   while runID == "":
      runID = raw_input('Sample ID from prefiring (e.g., 1): ')
   c=conn.cursor()
   t=(numberOfSamples,setInitials)
   c.execute('insert into tblRun (i_numberOfSamples,v_operatorName,i_preOrPost,v_status) VALUES (?,?,0,"Initial Insert")',t)
   # Save (commit) the changes
   conn.commit()
   # Now get the id for the run so we can update with other info as we ask...
   runID = c.lastrowid
   print "RUN ID = ",runID, " <WRITE THIS DOWN>"
   raw_input('Press any key to continue')
   RobotController.weighCrucibles(runID,numberOfSamples,measurementTimeInterval)
   
# continue...
#open a backup text file
csvFile = "./"+todayString+".csv"
#f = open(csvFile, 'w')
fileWriter = csv.writer(open(csvFile, 'wb'), delimiter=',')

intervalsec=int(intervalsec)


# value to look for to end loop
stopCode=0
# total number of measurements
num = 1



      # Find elapsed time
      now = datetime.today()
      today = now.strftime("%m-%d-%y %H:%M:%S")
      diffTime2 = now - endOfFiring

      diffSeconds = diffTime2.seconds
      diffMinutes = float(diffSeconds/60)
      diffMinutesQuarterPower = pow(diffMinutes,0.25)
      print "Logged: " + str(num) + " - " + str(sampleName) + " - " + str(weight) + " - " + str(tempC) + " - " + str(humidity)
      if preOrPost == "0":
         fileWriter.writerow([num,setNameCSV,sampleName,ItNum,today,float(weight),tempC,humidity,pressure,light]) 
         ##Elapsed Time and the standard weight from second balance and iteration number
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

   ## increment the sampel umber
   SampleNumUp()
   AutoStepper.MoveBack()
   
   
====================================
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
