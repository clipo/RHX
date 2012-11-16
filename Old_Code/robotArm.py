
# Filename: RobotController.py

#Basic imports
from ctypes import *
import os
import io
import serial
import sys
from time import sleep
import sched, time
import DataReadWrite


EOL = "\r";
command = "";

# Set the SSC-32 port - "COM1:" for Windows, "/dev/ttyS0" for Linux
SSC32_Port = "COM5:";


GripperChan=4;
GripperHome=1500;
Open=600;
Close=2400;

BalancePositionBaseInside=1060
BalancePositionBaseOutside=1214

BalancePositionUpShoulder=1210
BalancePositionDownShoulder=1020

BalancePositionDownElbow=1100
BalancePositionUpElbow=1280

BalancePositionUpWrist=810
BalancePositionDownWrist=600



# the alignment of the base to the sample position
# note that position 0 is the HOME position
SamplePositionBase=(1500,1240,1300,1324,1346,1370,1445,1445,1412,1379,1357,1379,1379,1379,1379,1379,1522,1500,1478,1467,1446,1687,1632,1544,1500)
SamplePositionUpShoulder=(1500,1644,1621,1604,1586,1558,1546,1586,1604,1638,1648,1558,1586,1610,1633,1648,1644,1621,1604,1586,1558,1558,1573,1598,1621)                                                                                                                                                                                                                                                  
SamplePositionUpElbow=(1500,1607,1602,1582,1575,1538,1518,1575,1591,1607,1607,1538,1575,1595,1606,1607,1607,1602,1591,1575,1538,1538,1560,1587,1602,1606)
SamplePositionUpWrist=(1500,810,810,810,810,810,810,810,810,810,810,810,810,810,810,810,810,810,810,810,810,810,810,810,810,810)

SamplePositionDownShoulder=(1500,1450,1360,1270,1352,1000,1312,1352,1370,1405,1415,1324,1352,1376,1399,1415,1410,1388,1370,1352,1324,1324,1340,1364,1388,1399)
                                                                                                                                                                                                                                                  
SamplePositionDownElbow=(1500,1786,1690,1560,1736,1000,1679,1736,1752,1768,1768,1699,1736,1756,1767,1768,1768,1763,1752,1736,1699,1699,1721,1747,1763,1767)
SamplePositionDownWrist=(1500,780,890,890,780,640,780,780,780,780,780,780,780,780,780,780,780,780,780,780,780,780,780,780,780,780)

def end():
	ssc32.close();


# Reads single characters until a CR is read
def Response (port):
   ich = "";
   resp = "";

   while (ich <> '\r'):
      ich = port.read(1);
      
      if (ich <> '\r'):
         resp = resp + ich;
   return resp;
      

# Converts a servo position in degrees to uS for the SSC-32
def To_Degrees (uS):
   result = 0;
   
   result = (uS - 1500) / 10;
   
   return result;

# Converts an SSC-32 servo position in uS to degrees
def To_uS (degrees):
   result = 0;
   
   result = (degrees * 10) + 1500;
   
   return result;

# Wait for a servo move to be completed
def Wait_for_Servos (port):
   ich = "";
   
   while (ich <> "."):
      Send_Command (port, "Q", True);
      
      ich = port.read(1);
   
   return;

# Send EOL to the SSC-32 to start a command executing
def Send_EOL (port):

   result = port.write(EOL);
   
   return result;

# Send a command to the SSC-32 with or without an EOL
def Send_Command (port, cmd, sendeol):
   
   result = port.write (cmd);
   
   if (sendeol):
      Send_EOL (port);
   
   return result;
   
#   Open the port at 115200 Bps - defaults to 8N1
ssc32 = serial.Serial(SSC32_Port, 115200);

def openGripper():
   print "now open gripper"
   #  Set the gripper to be open
   command = "#" + str(GripperChan) + " P" + str(Open);
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(2)

def closeGripper():
   print "now close gripper"
   #  Set the gripper to be open
   command = "#" + str(GripperChan) + " P" + str(Close);
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(2)

def goHome():
   print "now go home: "
   command = "#0 P" + str(SamplePositionBase[0]) + " #1 P"+str(SamplePositionUpShoulder[0]) 
   command = command + " #2 P" + str(SamplePositionUpElbow[0]) 
   command = command + " #3 P" + str(SamplePositionUpWrist[0])  
   command = command + " T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)

def gotoSamplePosition(position):
   print "now go to : ", position
   command = "#0 P" + str(SamplePositionBase[position]) + " #1 P"+str(SamplePositionUpShoulder[position]) 
   command = command + " #2 P" + str(SamplePositionUpElbow[position]) 
   command = command + " #3 P" + str(SamplePositionUpWrist[position])  
   command = command + " T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)

def samplePickUp(position):
   # first make sure gripper is open
   openGripper() 
   print "now go to : ", position
   command = "#0 P" + str(SamplePositionBase[position]) + " #1 P"+str(SamplePositionUpShoulder[position]) 
   command = command + " #2 P" + str(SamplePositionUpElbow[position]) 
   command = command + " #3 P" + str(SamplePositionUpWrist[position])  
   command = command + " T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   
   # now lower arm
   print "now lower arm to sample position : ", position
   command = "#1 P"+str(SamplePositionDownShoulder[position]) 
   command = command + " #2 P" + str(SamplePositionDownElbow[position]) 
   command = command + " #3 P" + str(SamplePositionDownWrist[position])  
   command = command + " T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1) 
   # close gripper
   closeGripper()
   # raise arm to moving position
   print "now raise arm "
   command = "#0 P" + str(SamplePositionBase[position]) + " #1 P"+str(SamplePositionUpShoulder[position]) 
   command = command + " #2 P" + str(SamplePositionUpElbow[position]) 
   command = command + " #3 P" + str(SamplePositionUpWrist[position])  
   command = command + " T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)
   
   
def samplePutDown(position):    
   ## start in up position
   command = "#0 P" + str(SamplePositionBase[position]) + " #1 P"+str(SamplePositionUpShoulder[position]) 
   command = command + " #2 P" + str(SamplePositionUpElbow[position]) 
   command = command + " #3 P" + str(SamplePositionUpWrist[position])  
   command = command + " T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   

   # now lower arm
   print "now lower arm to sample position : ", position
   command = " #1 P"+str(SamplePositionDownShoulder[position]) 
   command = command + " #2 P" + str(SamplePositionDownElbow[position]) 
   command = command + " #3 P" + str(SamplePositionDownWrist[position])  
   command = command + " T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   
   # open gripper
   openGripper()
   # raise arm to moving position
   ## start in up position
   command = "#1 P"+str(SamplePositionUpShoulder[position]) 
   command = command + " #2 P" + str(SamplePositionUpElbow[position]) 
   command = command + " #3 P" + str(SamplePositionUpWrist[position])  
   command = command + " T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)
   

def gotoOutsideBalanceFromInside():
   command = "#0 P" + str(BalancePositionBaseOutside) + " T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)  
    
def gotoOutsideBalanceFromOutside():
   #DataReadWrite.openBalanceDoor()
   
   command = "#0 P" + str(BalancePositionBaseOutside) + " #1 P"+str(BalancePositionUpShoulder) 
   command = command + " #2 P" + str(BalancePositionUpElbow) 
   command = command + " #3 P" + str(BalancePositionUpWrist)  
   command = command + " T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   
      

def putSampleOnBalance():
   gotoOutsideBalanceFromOutside()
   #DataReadWrite.zeroBalance()
   #DataReadWrite.openBalanceDoor()
   #move arm close and high
   print "move arm into balance area with sample up."
   command = "#0 P" + str(BalancePositionBaseInside) 
   command = command + " T3000"  
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   
   
   # lower arm arm to balance position
   print "lower arm in balance area"
   command = "#1 P"+str(BalancePositionDownShoulder) 
   command = command + " #2 P" + str(BalancePositionDownElbow) 
   command = command + " #3 P" + str(BalancePositionDownWrist)  
   command = command + " T3000"  
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)
   
   # open gripper
   openGripper()
   
   print "raise arm in balance area"
   command = " #1 P"+str(BalancePositionUpShoulder) 
   command = command + " #2 P" + str(BalancePositionUpElbow) 
   command = command + " #3 P" + str(BalancePositionUpWrist)  
   command = command + " T3000"  
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)
   print "move arm to outside of balance so I can shut the door"
   gotoOutsideBalanceFromInside()   
   #DataReadWrite.closeBalanceDoor()

def pickUpSampleFromBalance(): 
   print "go to area outside of balance"
   gotoOutsideBalanceFromOutside()
   #DataReadWrite.openBalanceDoor  
   print "open the gripper"
   openGripper()
   #move arm close and high
   print "move arm inside balance but keep it above the sample"
   command = "#0 P" + str(BalancePositionBaseInside)
   command = command + " T3000"  
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   
   # lower arm arm to balance position
   print "now lower the arm on to sample"
   command = " #1 P"+str(BalancePositionDownShoulder) 
   command = command + " #2 P" + str(BalancePositionDownElbow) 
   command = command + " #3 P" + str(BalancePositionDownWrist)
   command = command + " T3000" 
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)
   
   print "close the gripper on the sample"
   closeGripper()

   print "now pick up the sample and raise arm "
   command = "#1 P"+str(BalancePositionUpShoulder) 
   command = command + " #2 P" + str(BalancePositionUpElbow) 
   command = command + " #3 P" + str(BalancePositionUpWrist)  
   command = command + " T3000"  
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   
   
   print "go to area outside of balance"
   gotoOutsideBalanceFromInside()
	
def weighAllCrucibles(initials,numberOfSamples,loggingInterval,duration):
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
      goToSamplePosition(position)
      samplePickUp(position)
      ## zerothe balance for each sample
      DataReadWrite.zeroBalance()
      DataReadWrite.openBalanceDoor()
      gotoOutsideBalanceFromOutside()
      putSampleOnBalance()
      
      ## may need to check to see if arm is clear of door.
      DataReadWrite.closeBalanceDoor()
      
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
         sleep(loggingInterval)          
      DataReadWrite.openBalanceDoor()
      pickUpSampleFromBalance()
      gotoSamplePosition(position)
      samplePutDown(position)
      DataReadWrite.closeBalanceDoor()
      position=position+1
   return (runID)
	  
def weighAllSamplesPreFire(runID,listOfSamples,duration,loggingInterval,numberOfSamples):
   # Find elapsed time
   #first put robot back to zero
   position=0
   #HomePosition()
   listOfValues=()
   crucibleWeight=0.0
    
   startTime=datetime.today()
   endPoint=timeDelta(minutes=duration)
   endTime=startTime+endPoint

   while position < numberOfSamples:
     
      goToSamplePosition(position)
      samplePickUp(position)
      ## zerothe balance for each sample
      DataReadWrite.zeroBalance()
      DataReadWrite.openBalanceDoor()
      gotoOutsideBalanceFromOutside()
      putSampleOnBalance()
       ## may need to check to see if arm is clear of door.
      DataReadWrite.closeBalanceDoor()
      crucibleWeight=getCrucibleWeight(runID,position)
      sampleID=getSampleID(runID,position)
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
      DataReadWrite.openBalanceDoor()
      pickUpSampleFromBalance()
      goToSamplePosition(position)
      samplePutDown(position)
      DataReadWrite.closeBalanceDoor()
      position=position+1

def weighAllSamplesPostFire(runID,listOfSamples,duration,loggingInterval,numberOfSamples,startTime):
   # Find elapsed time
   #first put robot back to zero
   position=0
   #HomePosition()
   listOfValues=()
   crucibleWeight=0.0
    
   startTime=datetime.today()
   endPoint=timeDelta(minutes=duration)
   endTime=startTime+endPoint

   while position < numberOfSamples:
     
      goToSamplePosition(position)
      samplePickUp(position)
      ## zerothe balance for each sample
      DataReadWrite.zeroBalance()
      DataReadWrite.openBalanceDoor()
      gotoOutsideBalanceFromOutside()
      putSampleOnBalance()
       ## may need to check to see if arm is clear of door.
      DataReadWrite.closeBalanceDoor()
      crucibleWeight=getCrucibleWeight(runID,position)
      sampleID=getSampleID(runID,position)
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
         timeElapsed= now - startTime
         timeElapsedQuarterPower = pow(timeElapsed,0.25)
         DataReadWrite.insertPostFireMeasurement(runID,sampleID,position,weightMeasurement,temperature,humidity,pressure,light,endOfFiring,crucibleWeight,today,timeElapsed,timeElapsedQuarterPower)
         sleep(loggingInterval)
      DataReadWrite.openBalanceDoor()
      pickUpSampleFromBalance()
      goToSamplePosition(position)
      samplePutDown(position)
      DataReadWrite.closeBalanceDoor()
      position=position+1

