
from datetime import date, datetime, time, timedelta
import DataReadWrite
from time import sleep
import scipy
from numpy import *


listOfValues=[]
duration=5
startTime=datetime.today()
endPoint=timedelta(minutes=duration)
endTime=startTime+endPoint
loggingInterval=1

print "Current time: ",startTime
print "endPoint: ", endPoint
print "endTime: ", endTime
position =1
runID=1
startTime=datetime.today()
endPoint=timedelta(minutes=duration)
endTime=startTime+endPoint
count=0
weight=float(0.0)
value=float(0.0)
a = array([])


DataReadWrite.closeBalanceDoor()
while datetime.today() < endTime:
   timeLeft=endTime-datetime.today()
   print "Time left: ", (int(timeLeft.seconds/60))
   weight=DataReadWrite.readStandardBalance()
   print "Weight: %f" % (float(weight))
   if weight>0:
      a=append(a,float(weight))
      print "Length: ",a.size
      averageWeight=mean(a)
      stdevWeight=std(a)
      print( "The average weight of crucible #%d is: %f with stdev of: %f" % (position, averageWeight,stdevWeight))
   ## now update crucible position record 
   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")
   
   sleep(loggingInterval)    
DataReadWrite.openBalanceDoor()
position=position+1

