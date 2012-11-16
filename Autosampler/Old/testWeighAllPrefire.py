
from datetime import date, datetime, time, timedelta
import DataReadWrite
import xyzRobot
from time import sleep
import scipy
from datetime import datetime
from datetime import timedelta
from numpy import *
from Tkinter import *
import logging

logger=logging.getLogger("startRHX")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('rhx.log')
fh.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)

prefire=Tk()
prefire.wm_title("Pre Firing")
robotStatus=Toplevel()
alert= Toplevel()
alert.withdraw()
robotStatus.withdraw()
COUNTS_FOR_STATS = 3
LOGINT=5
M0EE1=IntVar()
M1EE1=IntVar()
M2EE1=IntVar()
MB1V1=IntVar()
MB2V1=IntVar()
RUNID=IntVar()
RUNID.set(1)
INITIALS=StringVar()
INITIALS.set("CPL")
DURATION=IntVar()
DURATION.set(3)
NUMBEROFSAMPLES=IntVar()
NUMBEROFSAMPLES.set(5)
START_POSITION=IntVar()
MV=IntVar()
AV=DoubleVar()
XMOTORPOSITION=StringVar()
YMOTORPOSITION= StringVar()
BALANCEWEIGHT=DoubleVar()
BALANCESTATUS=StringVar()
ABSOLUTEXPOSITION=StringVar()
CRUCIBLEYESNO=StringVar()
MOTORSTEP=StringVar()
MOTORSTEP.set("10")
BALANCEDOOR=StringVar()
SAMPLEPOSITION=StringVar()
POSITION=IntVar()
START_POSITION.set("1")
TEMP=DoubleVar()
TEMP.set(18)
HUMIDITY=DoubleVar()
HUMIDITY.set(70.0)
REPS=IntVar()
REPS.set(3)
INTERVAL=IntVar()
INTERVAL.set(5)
RUNID=IntVar()
RUNID.set(1)
DATEOFFIRING=StringVar()
TIMEOFFIRING=StringVar()
DURATIONOFFIRING=StringVar()
TEMPOFFIRING=StringVar()
CURRENTPOSITION=IntVar()
CURRENTREP=IntVar()
NAME=StringVar()
NAME.set("Mississippi")
LOCATION=StringVar()
LOCATION.set("LMV")
POSITION=IntVar()
MCOUNT=IntVar()
CURRENTSTEP=StringVar()
STATUS=StringVar()
DURATION=IntVar()
DURATION.set(2)
LOGGERINTERVAL=IntVar()
TIMEREMAINING=IntVar()
TEMPERATURE=DoubleVar()
SAMPLENUM=IntVar()
RHTEMP2000TEMP=DoubleVar()
RHTEMP2000HUMIDITY=DoubleVar()
CYCLE=IntVar()
CYCLE.set(3)
MEAN=DoubleVar()
STDEV=DoubleVar()
VARIANCE=DoubleVar()
tempCorrection=0.0
rhCorrection=0.0
DATABASENAME=StringVar()
DATABASENAME.set("TEST")
DBDIRECTORY=StringVar()
DBDIRECTORY.set("c:/Users/Archy/Dropbox/Rehydroxylation/")
PRECISIONTEMP=DoubleVar()


def alertWindow(message):
   logger.error(message)
   alert.deiconify()
   Message(alert,text=message, bg='red', fg='ivory', relief=GROOVE).grid(row=0,column=0,sticky=W+E+N+S)
   ##Button(alert, text="Continue", command=backToMainWindow).grid(column=1,row=0)
   ##Button(alert, text="Quit", command=KillProgram).grid(row=1,column=1)
   alert.mainloop()

def KillProgram():
   logger.debug("Quit has been requested by users. So quitting.")
   logger.debug("KillProgram!")
   alert.quit()

   #init.quit()
   prefire.quit()

   return True;

def preFire():

   status="Pre-firing"


   prefire.wm_title("Pre-Fire")

   RHTEMP2000TEMP.set(xyzRobot.getTemperature())
   RHTEMP2000HUMIDITY.set(xyzRobot.getHumidity())
   PRECISIONTEMP.set(xyzRobot.getTemperature())

   INITIALSL = Label(prefire, text="Initials").grid(row=1, column=0, sticky=W)
   INITIALSE = Entry(prefire, textvariable=INITIALS).grid(row=1, column=1, sticky=W)

   RUNIDL = Label(prefire, text="Run ID").grid(row=2, column=0, sticky=W, padx=2, pady=2)
   RUNIDE = Entry(prefire, textvariable=RUNID).grid(row=2, column=1, sticky=W,padx=2, pady=2)
   NAMEL = Label(prefire, text="Name of sample set (e.g., Mississippian ):").grid(row=3, column=0, sticky=W, padx=2, pady=2)
   NAMEE = Entry(prefire, textvariable=NAME).grid(row=3, column=1, sticky=W,padx=2, pady=2)
   Label(prefire, text="Sample Location (e.g., LMV):").grid(row=4, column=0, sticky=W, padx=2, pady=2)
   Entry(prefire, textvariable=LOCATION).grid(row=4, column=1, sticky=W,padx=2, pady=2)

   NUMSAML = Label(prefire, text="Number of Samples").grid(row=5, column=0, sticky=W, padx=2, pady=2)
   NUMSAME = Entry(prefire, textvariable=NUMBEROFSAMPLES).grid(row=5, column=1, sticky=W, padx=2, pady=2)
   STARTPOS= Label(prefire, text="Start Position").grid(row=6, column=0, sticky=W)
   STARTPOS= Entry(prefire, textvariable=START_POSITION).grid(row=6, column=1, sticky=W)

   DURATIONL= Label(prefire, text="Duration of Measurements").grid(row=7, column=0, sticky=W, padx=2, pady=2)
   DURATIONE = Entry(prefire, textvariable=DURATION).grid(row=7, column=1, sticky=W, padx=2, pady=2)
   INTERVALL= Label(prefire, text="Sampling interval (seconds)").grid(row=8, column=0, sticky=W, padx=2, pady=2)
   INTERVALE = Entry(prefire, textvariable=INTERVAL).grid(row=8, column=1, sticky=W, padx=2, pady=2)
   REPSL= Label(prefire, text="Repetitions").grid(row=9, column=0, sticky=W, padx=2, pady=2)
   REPSE = Entry(prefire, textvariable=REPS).grid(row=9, column=1, sticky=W, padx=2, pady=2)
   TEMPL= Label(prefire, text="Temperature (C)").grid(row=10, column=0, sticky=W, padx=2, pady=2)
   TEMPE = Entry(prefire, textvariable=TEMP).grid(row=10, column=1, sticky=W, padx=2, pady=2)
   HUMIDITYL= Label(prefire, text="Relative Humidity").grid(row=11, column=0, sticky=W, padx=2, pady=2)
   HUMIDITYE = Entry(prefire, textvariable=HUMIDITY).grid(row=11, column=1, sticky=W, padx=2, pady=2)

   TEMPL=Label(prefire,text="Madge Tech Temperature:").grid(row=12,column=0,sticky=W,padx=2,pady=2)
   TEMPE=Entry(prefire,textvariable=RHTEMP2000TEMP).grid(row=12,column=1,sticky=W,padx=2,pady=2)
   RHL=Label(prefire,text="Madge Tech RH:").grid(row=13,column=0,sticky=W,padx=2,pady=2)
   RHE=Entry(prefire,text=RHTEMP2000HUMIDITY).grid(row=13,column=1,sticky=W,padx=2,pady=2)

   PTEMP1=Label(prefire,text="Precision Temp").grid(row=14,column=0,sticky=W)
   PTEMP2=Label(prefire,textvariable=PRECISIONTEMP).grid(row=14,column=1,sticky=W)
   HUMIDITY1=Label(prefire,text="Humidity").grid(row=15,column=0,sticky=W)
   HUMIDITY2=Label(prefire,textvariable=HUMIDITY).grid(row=15,column=1,sticky=W)


   DIRL=Label(prefire,text="Directory: ").grid(row=16,column=0,sticky=W,padx=2,pady=2)
   DIRE=Entry(prefire,textvariable=DBDIRECTORY).grid(row=16,column=1,sticky=W,padx=2,pady=2)

   DATAF=Label(prefire,text="Database filename to use:").grid(row=17,column=0,sticky=W)
   DATAL=Entry(prefire,textvariable=DATABASENAME).grid(row=17,column=1, sticky=W)

   INITBUTTON = Button(prefire, text="Start Pre Fire", command=go_preFire).grid(row=18, column=2, padx=2, pady=2)

   prefire.mainloop()

def go_preFire():
   dbName=DATABASENAME.get()
   dbDir=DBDIRECTORY.get()

   value=DataReadWrite.openDatabase(dbDir,dbName)
   if value is False:
      logger.error("There has been an error since openDatabase returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. Cannot create database", bg='red', fg='ivory', relief=GROOVE)

   runID=int(RUNID.get())
   if (runID<1):
      alert.deiconify()
      alert.title("Alert: No RunID Number!")
      Message(alert,text="You must have a RunID to continue.", bg='red', fg='ivory', relief=GROOVE).grid(row=0,column=0,sticky=E+W+N+S)
      ##Button(alert, text="Continue", command=backToMainWindow).grid(row=1,column=0)
      ##Button(alert, text="Quit", command=KillProgram).grid(row=1,column=1)
      logger.debug("You must have a RunID entered in order to continue.")
      return False;
   preOrPost=1
   status="prefire"
   setInitials=str(INITIALS.get())
   startPosition=int(START_POSITION.get())
   setName=str(NAME.get())
   setLocation=str(LOCATION.get())
   intervalsec=int(INTERVAL.get())
   numberOfSamples=int(NUMBEROFSAMPLES.get())
   repetitions=int(REPS.get())
   duration=int(DURATION.get())
   setTemperature=float(TEMP.get())
   setHumidity=float(HUMIDITY.get())
   standardTemp=float(RHTEMP2000TEMP.get())
   standardRH=float(RHTEMP2000HUMIDITY.get())

   temp=xyzRobot.getTemperature()
   humidity=xyzRobot.getHumidity()
   tempCorrection=standardTemp-temp
   rhCorrection=standardRH-humidity

   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")

   if (startPosition==""):
      startPosition=1
      
   runID=DataReadWrite.updateRunPreFire(runID,setInitials,setName,today,
   setLocation,preOrPost,intervalsec,setTemperature,setHumidity,
   status,duration,numberOfSamples,repetitions,startPosition)
   
   if (runID == False):
      logger.error("There has been an error since updateRunPreFire returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. The arm has returned to Home.", bg='red', fg='ivory', relief=GROOVE).grid(row=0,column=0,sticky=W+E+N+S)
      ##Button(alert, text="Continue", command=backToMainWindow).grid(column=1,row=0)
      ##Button(alert, text="Quit", command=KillProgram).grid(row=1,column=1)
   count=1
   repeat=0

   while (count < (numberOfSamples+1)):

      (meanWeight, stdevWeight) = DataReadWrite.getCrucibleWeightStats(runID,count)
      # Now do an insert for tblSample for each sample include--- from here on we can then just update the record.
      sampleID = DataReadWrite.insertNewSample(runID,count,setName,now,setLocation,preOrPost,intervalsec,setTemperature,setHumidity,status,duration,repetitions,meanWeight,stdevWeight)

    
      if (sampleID is False):
         logger.error("There has been an error since insertNewSample returned FALSE")
         alert.deiconify()
         Message(alert,text="There has been a problem. The arm has returned to Home.", bg='red', fg='ivory', relief=GROOVE).grid(row=0,column=0,sticky=W+E+N+S)
         ##Button(alert, text="Continue", command=backToMainWindow).grid(column=1,row=0)
         ##Button(alert, text="Quit", command=KillProgram).grid(row=1,column=1)
         break
      count += 1

   repeat=0      
   ## repeat as many times as asked (all of the crucibles)
   while repeat < repetitions:
      weighAllSamplesPreFire(runID,duration,intervalsec,
            numberOfSamples,startPosition,standardTemp,
            standardRH,repeat,
            robotStatus,POSITION,MCOUNT,CURRENTSTEP,
            STATUS,DURATION,LOGGERINTERVAL,RUNID,
            NUMBEROFSAMPLES,TIMEREMAINING,CYCLE,MEAN,STDEV,VARIANCE)
      repeat += 1
      #prefire.update_windows()
   

   prefire.withdraw()
   return True
   
def weighAllSamplesPreFire(runID,duration,loggingInterval,
            numberOfSamples,startPosition,
            tempCorrection,rhCorrection,repetition,
   			robotStatus,POSITION,MCOUNT,CURRENTSTEP,
   			STATUS,DURATION,LOGGERINTERVAL,RUNID,
   			NUMBEROFSAMPLES,TIMEREMAINING,CYCLE,MEAN,STDEV,VARIANCE):
   # Find elapsed time
   #first put robot back to zero
   position=int(startPosition)
   if position=="":
      position=1
   logger.debug("weighAllSamplesPreFire( %d,%d,%d,%d,%d )" % (runID,duration,loggingInterval,numberOfSamples,startPosition))
   
   status="prefire"
   preOrPost=1
   #HomePosition()
   listOfValues=()
   RUNID.set(runID)
   NUMBEROFSAMPLES.set(numberOfSamples)
   DURATION.set(duration)
   POSITION.set(position)
   CYCLE.set(repetition)
   MCOUNT.set(0)
   STATUS.set("Initializing")
   LOGGERINTERVAL.set(loggingInterval)
   crucibleWeight=0.0
   startTime=datetime.today()
   endPoint=timedelta(minutes=duration)
   endTime=startTime+endPoint
   robotStatus.deiconify()
   Label(robotStatus,text="Run ID:").grid(row=0,column=0,sticky=W)
   Label(robotStatus,textvariable=RUNID).grid(row=0,column=1, sticky=W)
   Label(robotStatus,text="Current sample number:").grid(row=1,column=0,sticky=W)
   Label(robotStatus,textvariable=POSITION).grid(row=1,column=1, sticky=W)
   Label(robotStatus,text="Total Number of Samples:").grid(row=2,column=0,sticky=W)
   Label(robotStatus,textvariable=NUMBEROFSAMPLES).grid(row=2,column=1,sticky=W)
   Label(robotStatus,text="Cycle Number:").grid(row=3,column=0,sticky=W)
   Label(robotStatus,textvariable=CYCLE).grid(row=3,column=1,sticky=W)
   Label(robotStatus,textvariable=MCOUNT).grid(row=4,column=1,sticky=W)
   Label(robotStatus,text="Current measurement count:").grid(row=4,column=0,sticky=W)
   Label(robotStatus,text="Logging interval:").grid(row=5,column=0, sticky=W)
   Label(robotStatus,textvariable=LOGGERINTERVAL).grid(row=5,column=1,sticky=W)
   Label(robotStatus,text="Duration of Measurements:").grid(row=6,column=0, sticky=W)
   Label(robotStatus,textvariable=DURATION).grid(row=6,column=1,sticky=W)
   Label(robotStatus,text="Number of Samples:").grid(row=7,column=0,sticky=W)
   Label(robotStatus,textvariable=NUMBEROFSAMPLES).grid(row=7,column=1,sticky=W)
   Label(robotStatus,text="Time remaining for this sample:").grid(row=8,column=0,sticky=W)
   Label(robotStatus,textvariable=TIMEREMAINING).grid(row=8,column=1,sticky=W)
   Label(robotStatus,text="Status").grid(row=9,column=0, sticky=W)
   Label(robotStatus,textvariable=STATUS).grid(row=9,column=1,sticky=W)
   sleep(5)

   while position < numberOfSamples+1:
      statustext="Now on sample %d",int(position)
      STATUS.set(statustext)
      logger.debug("Now on position: %d ", int(position))
      statustext="Go to position %d",int(position)
      STATUS.set(statustext)
      #goToSamplePosition(position)
      #val = samplePickUp()
      #if val == False:
      #   return False
      ## zero the balance for each sample
      logger.debug("Zero balance")
      #DataReadWrite.zeroBalance()
      logger.debug("Open balance door")
      #DataReadWrite.openBalanceDoor()
      statustext="Going to outside of balance"
      STATUS.set(statustext)
      #logger.debug("Go to outside balance.")
      #goToOutsideBalanceFromOutside()
      statustext="Going into the balance."
      STATUS.set(statustext)
      logger.debug("go to inside balance.")
      #goToInsideBalanceFromOutside()
      logger.debug("put sample on balance.")
      statustext="Putting sample on balance."
      STATUS.set(statustext)
      #val = putSampleOnBalance()
      #if val == False:
      #   return False
      ## may need to check to see if arm is clear of door.
      logger.debug("go to outsisde balance from the inside.")
      statustext="Going to outside of balance"
      STATUS.set(statustext)
      #goToOutsideBalanceFromInside()
      logger.debug("close balance door")
      #DataReadWrite.closeBalanceDoor()
      
      crucibleWeight=double(DataReadWrite.getCrucibleWeight(runID,position))
      if crucibleWeight==False:
         alertWindow("get Crucible Weight returned an error")
         
      sampleID=DataReadWrite.getSampleID(runID,position)
      startTime=datetime.today()
      durationOfLogging=int(duration)
      endPoint=timedelta(minutes=durationOfLogging)
      endTime=startTime+endPoint
      repetition_count=0
      kcount=0
      standard_weight=float(0.0)
      count=0
      
      #get the latest count for this sample
      total_count = int(DataReadWrite.getMaxPreFireCount(runID,position))
      if (total_count == 0 or total_count == ""):
         total_count=0
      listOfValues=[]
      a = array([])
      weight=double(0.0)
      statustext="Weighing sample # %d"% position
      STATUS.set(statustext)
      while datetime.today() < endTime:
         timeLeft=endTime-datetime.today()
         TIMEREMAINING.set(int(timeLeft.seconds/60))
         result=[]
         (measurement,status)=DataReadWrite.readWeightFromBalance()
         
         weight=double(crucibleWeight)-double(measurement)
         
         if weight>0.0:
            a=append(a,double(weight))
            averageWeight=a.mean()
            
            stdevWeight=a.std()
            logger.debug( "Count: %d the average weight of sample # %d is %f with stdev of %f" % (count,position,float(averageWeight),float(stdevWeight)))
            ## now update crucible position record 
            now = datetime.today()
            today = now.strftime("%m-%d-%y %H:%M:%S")
            repetition_count += 1
            total_count += 1
            MCOUNT.set(count)
            temperature=xyzRobot.getTemperature()
            humidity=xyzRobot.getHumidity()

            logger.debug( "TMP:  temp: %s, humidity: %s" % (temperature,humidity))

            standard_weight=0.0
            if (temperature==""):
               temperature=0.0
            if (humidity==""):
               humidity=0.0
               
            value=DataReadWrite.insertPreFireMeasurement(runID,sampleID,position,weight,status,
                     temperature,humidity,crucibleWeight,
                     standard_weight,today,total_count,repetition,repetition_count,count)
            if value==False:
               alertWindow("insertPreFireMeasurement has returned an error")

            count += 1
            ### check to see if enough measurements have been made. First at least 100 must have been done
            if (count > COUNTS_FOR_STATS):
               (mean,stdev,variance,tempMean,tempStdev,humidityMean,humidityStdev)=DataReadWrite.getStatsForPrefireWeightOfSample(runID,sampleID,count)
               MEAN.set(mean)
               STDEV.set(stdev)
               VARIANCE.set(variance)
               logger.debug("Mean: %d  Stdev: %d  Variance: %d TempMean: %d  TempStDev: %d HumidityMean: %d HumidityStdDev: %d" % (mean,stdev,variance,tempMean,tempStdev,humidityMean,humidityStdev))
               value=DataReadWrite.updateSamplePreFire(runID,sampleID,position,mean,stdev,tempMean,tempStdev,humidityMean,humidityStdev)
            sleep(loggingInterval)
         if count==0:
            ## check to see if balance is giving anything
            (value,status)=DataReadWrite.readInstantWeightFromBalance()
            logger.debug( "Instant value from balance (unstable): %f ",float(value))
            if (value>0):
               logger.debug( "Since this is >0 the balance is reading but not stable")
               logger.debug( "resetting clock. Waiting for a valid entry before storing data...")
               startTime=datetime.today()
               endPoint=timedelta(minutes=durationOfLogging)
               endTime=startTime+endPoint
            else:
               logger.error( "There is a problem: no output from balance at all: Count: %d ",int(kcount))
               kcount += 1
               if kcount==500:
                 logger.error( "There is a problem: no output for 500 counts -- quitting ")
                 KillMotors()
                 exit(1)   
      #DataReadWrite.openBalanceDoor()
      statustext="Going into balance."
      STATUS.set(statustext)
      #goToInsideBalanceFromOutside()
      statustext="Picking up sample."
      STATUS.set(statustext)
      #val=pickUpSampleFromBalance()
      #if val == False:
      #   return False
      statustext="Going to outside of balance."
      STATUS.set(statustext)
      #goToOutsideBalanceFromInside()
      statustext="Going to position %d." % position
      STATUS.set(statustext)
      #goToSamplePosition(position)
      statustext="Putting sample down."
      #val=samplePutDown()
      #if val == False:
      #   return False
      statustext="Going to home position."
      #response=goHome()
      #if response==False:
      #   logger.error( "Home point not reached. Stopping.")
      #   STATUS.set("Error: home point not reached.")
      #   return False
      #DataReadWrite.closeBalanceDoor()
      position += 1
      POSITION.set(int(position))
      statustext= "Now moving to the next sample %d." % position
      STATUS.set(statustext)
   STATUS.set("Done!")
   robotStatus.withdraw()
   return runID;

preFire()


