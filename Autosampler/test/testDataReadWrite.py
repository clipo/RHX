import DataReadWrite
import time
from datetime import datetime
from datetime import timedelta
from Tkinter import *
import tkMessageBox
import sys
sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
import os
import io
import re
import serial
import math
from ctypes import *

passed=0
test=1
runID=1
positionNumber=1
tempCorrection=22
rhCorrection=67

initials="CPL"
numberOfSamples=3

print "-------------------------------------------------------"
print "Initializing Database: initializeDatabase()"
filename = "TEST"
dirname="c:/Users/Archy/Dropbox/Rehydroxylation/"
value = DataReadWrite.initializeDatabase(dirname,filename)
test += 1
if (value==True):
   print "Database opened. PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"

print "Close Database: closeDatabase()"
value = DataReadWrite.closeDatabase()
test += 1
if (value==True):
   print "Database closed. PASS"
   passed += 1
else:
   print "FAIL"

print "-------------------------------------------------------"
print "Open newly created Database: initializeDatabase()"
filename = "TEST"
dirname="c:/Users/Archy/Dropbox/Rehydroxylation/"
test += 1
value = DataReadWrite.openDatabase(dirname,filename)
if (value==True):
   print "Database opened. PASS"
   passed += 1
else:
   print "FAIL"

print "-------------------------------------------------------"
value=DataReadWrite.BDOpen()
print "BDOpen() result->",value
test += 1
if value==True:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
value=DataReadWrite.BDClose()
print "BDClose() result->",value
test += 1
if value==True:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
value=DataReadWrite.BZero()
print "BZero() result->",value
test += 1
if value==True:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"

weight=float(DataReadWrite.getCrucibleWeight(runID,positionNumber))
print "getCrucibleWeight(",runID,",",positionNumber,")"
print "result-->",weight
test += 1
if weight>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"

xpos=10
ypos=10
print "-------------------------------------------------------"
value=DataReadWrite.updatePosition(xpos,ypos)
print "updatePosition(",xpos,",",ypos,") result ->",value
test += 1
if value==True:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
DataReadWrite.zeroBalance()
print "zeroBalance() result ->",value
xpos=20
ypos=20
test += 1
if value==True:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
DataReadWrite.setPosition(xpos,ypos)
print "setPosition(",xpos,",",ypos,") result ->",value
test += 1
if value==True:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"

(xpos,ypos) = DataReadWrite.getLastPosition()
print "getLastPosition() result -> xpos: ",xpos, "ypos: ", ypos
test += 1
if (xpos>0 and ypos>0):
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"

value=DataReadWrite.openBalanceDoor()
print "openBalanceDoor() result ->",value
test += 1
if value==True:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"

value=DataReadWrite.closeBalanceDoor()
print "closeBalanceDoor() result ->",value
test += 1
if value==True:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"

value=DataReadWrite.isBalanceDoorOpen()
print "isBalanceDoorOpen() result ->",value
test += 1
if (value=="OPEN" or value=="CLOSED"):
   print "PASS"
   passed += 1
else:
   print "FAIL"
runID=1
position=1
print "-------------------------------------------------------"

value=DataReadWrite.getMaxPreFireCount(runID,position)
print "getMaxPreFireCount(",runID,",",position,") result ->",value
test += 1
if value==True:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"

value=DataReadWrite.getMaxPostFireCount(runID,position)
print "getMaxPostFireCount(",runID,",",position,") result ->",value
test += 1
if value==True:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"

i_runID=1
i_positionNumber=1
v_description="Mississippian"
v_locationCode="LMV"
d_datetime= datetime.today()
i_preOrPost=1
i_loggingInterval=5
f_temperature=18.0
f_humidity=70.1
v_status="Crucible"
i_preMeasurementInterval=3
i_repetitions=3
f_pressure=1010.1
f_light=21.1
f_weight=10.23208232
standard_weight=23.1
total_count=10
repetition=3
repetition_count=2
i_preMeasurementTimeInterval=3
weightMeasurement=22.1215
crucibleWeight=10.232
total_count=15

print "-------------------------------------------------------"
print "DataReadWrite.insertCrucibleMeasurement()"
value = DataReadWrite.insertCrucibleMeasurement(i_runID,i_positionNumber,f_weight,v_status,f_temperature,f_humidity,f_pressure,f_light, total_count,d_datetime)

test += 1
if value is False:
   print "FAIL"
else:
    print "PASS"
    passed += 1

print "-------------------------------------------------------"
v_status="Prefire"
# Now do an insert for tblSample for each sample include--- from here on we can then just update the record. 
sampleID = DataReadWrite.insertNewSample(i_runID,i_positionNumber,v_description,d_datetime,
					v_locationCode,i_preOrPost,i_loggingInterval,f_temperature,
					f_humidity,v_status,i_preMeasurementTimeInterval,i_repetitions)
       
print ("insertNewSample(",i_runID,",",i_positionNumber,",",v_description,",",d_datetime,",",
					v_locationCode,",",i_preOrPost,",",i_loggingInterval,",",f_temperature,",",
					f_humidity,",",v_status,",",i_preMeasurementTimeInterval,",",i_repetitions,")")
print "insertNewSample() -- results: Sample ID: ",sampleID

test += 1
if sampleID>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"

weight=12.2091
status="Stable"
print "-------------------------------------------------------"
          
count=10

value=DataReadWrite.insertPreFireMeasurement(i_runID,sampleID,i_positionNumber,weightMeasurement,status,
     f_temperature,f_humidity,f_pressure,f_light,crucibleWeight,standard_weight,d_datetime,total_count,repetition,repetition_count,count)

print ("insertPreFireMeasurement: ",i_runID,",",sampleID,",",i_positionNumber,",",weightMeasurement,",",status,",",
     f_temperature,",",f_humidity,",",f_pressure,",",f_light,",",crucibleWeight,",",standard_weight,",",
     d_datetime,",",total_count,",",repetition,",",repetition_count,",",count)
     
print "insertPreFireMeasurement() -- result: ",value
test += 1
if value>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
print "readWeightFromBalance() "
(weight,status)=DataReadWrite.readWeightFromBalance()
print "readWeightFromBalance() -- results:",weight,",",status
test += 1
if weight>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"

print "readInstantWeightFromBalance()"
(weight,status)=DataReadWrite.readInstantWeightFromBalance()
print "readInstantWeightFromBalance() -- results:",weight,",",status
test += 1
if weight>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
print "insertRun(",initials,",",d_datetime,",",numberOfSamples,")"
value=DataReadWrite.insertRun(initials,d_datetime,numberOfSamples)
print "Result-->",value
test += 1
if value>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"

print "-------------------------------------------------------"
print "getRunInfo(",runID,")"
row=[]
(status, row)=DataReadWrite.getRunInfo(runID)
if (status==True):
   (locationCode,numberOfSamples,description,temperature,humidity,endOfFiring,durationOfFiring)=row
   print "locationCode:",locationCode
   print "numberOfSamples:",numberOfSamples
   print "description:",description
   print "temperature:",temperature
   print "humidity:",humidity
   print "endOfFiring:",endOfFiring
   print "durationOfFiring:",durationOfFiring
else:
  print "status: ", status
test += 1
if status==True:
   print "PASS"
   passed += 1
else:
   print "FAIL"
   
print "-------------------------------------------------------"
print "readTempHumidity(",tempCorrection,",",rhCorrection,")"
(temp,humidity,dewpoint,pressure,light)=DataReadWrite.readTempHumidity(tempCorrection,rhCorrection)
print "Temp:",temp
print "Humidity:",humidity
print "Dewpoint:",dewpoint
print "Pressure:",pressure
print "Light:",light
test += 1
if temp>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
print "getSampleID(",runID,",",i_positionNumber,")"
value=DataReadWrite.getSampleID(runID,position)
print "Result-->",value
test += 1
if value>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
print "getEndOfFiring(",runID,")"
value=DataReadWrite.getEndOfFiring(runID)
print "Result-->",value
test += 1
if value>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
print "insertInitialCrucible(",runID,",",i_positionNumber,",",d_datetime,")"
value=DataReadWrite.insertInitialCrucible(runID,i_positionNumber,d_datetime)
print "Result-->",value
test += 1
if value>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
print "getCrucibleWeight(",runID,",",i_positionNumber,")"
value=DataReadWrite.getCrucibleWeight(runID,i_positionNumber)
print "Result-->",value
test += 1
if value>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"

print "-------------------------------------------------------"
length=10
values=DataReadWrite.getStatsForPrefireWeightOfSample(runID,i_positionNumber,length)
if (values==False):
   print "No stats possible"
else:
   (average,stdev,variance)=values
   print "Result: Average:",average,"Stdev:",stdev,"Variance:",variance
test += 1
if average>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
print "getStatsForPostFireWeightOfSample(",runID,",",i_positionNumber,",",length,")"
values=DataReadWrite.getStatsForPostFireWeightOfSample(runID,i_positionNumber,length)
if (values==False):
   print "No stats possible"
else:
   (average,stdev,variance)=values
   print "Result: Average:",average,"Stdev:",stdev,"Variance:",variance
test += 1
if average>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"
startdate="10-10-2011"
starttime="10:10:10"
sdate=startdate.split("-",3)
stime=starttime.split(":",3)
startOfFiring = datetime(int(sdate[2]), int(sdate[0]), int(sdate[1]), int(stime[0]), int(stime[1]), int(stime[2]))
durationOfFiring=540
endOfFiring = startOfFiring + timedelta(minutes=durationOfFiring)
now = datetime.today()
today = now.strftime("%m-%d-%y %H:%M:%S")
timeDiff=now - endOfFiring
timeElapsed=timeDiff.seconds/60
timeElapsedQuarterPower=pow(timeElapsed,0.25)
temperature=18.1
humidity=19.2
pressure=1031
light=32
total_count=10
repetition=1
repetition_count=13
count=45
value=DataReadWrite.insertPostFireMeasurement(runID,sampleID,position,weight,status,temperature,humidity,pressure,light,endOfFiring,crucibleWeight,standard_weight,now,total_count,repetition,repetition_count,count)
test += 1
if value>0:
   print "PASS"
   passed += 1
else:
   print "FAIL"
print "-------------------------------------------------------"


print "Number of tests: ",test
print "Number of tests PASSED: ",passed
