
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

COUNTS_FOR_STATS=3

postfire=Tk()
postfire.wm_title("Post Firing")
robotStatus=Toplevel()
alert= Toplevel()
alert.withdraw()
robotStatus.withdraw()

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
DATEOFFIRING.set("11-30-2011")
TIMEOFFIRING=StringVar()
TIMEOFFIRING.set("10:10:10")
DURATIONOFFIRING=IntVar()
DURATIONOFFIRING.set(540)
TEMPOFFIRING=IntVar()
TEMPOFFIRING.set(800)
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
TIMEELAPSED=IntVar()
TIMEREMAINING=IntVar()
TEMPERATURE=DoubleVar()
SAMPLENUM=IntVar()
RHTEMP2000TEMP=DoubleVar()
RHTEMP2000TEMP.set(18.0)
RHTEMP2000HUMIDITY=DoubleVar()
RHTEMP2000HUMIDITY.set(70.1)
CYCLE=IntVar()
CYCLE.set(3)
COUNTSFORSTATS=IntVar()
COUNTSFORSTATS.set(3)
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
   #Button(alert, text="Continue", command=backToMainWindow).grid(column=1,row=0)
   #Button(alert, text="Quit", command=KillProgram).grid(row=1,column=1)
   alert.mainloop()

def KillProgram():
   logger.debug("Quit has been requested by users. So quitting.")
   logger.debug("KillProgram!")
   alert.quit()
   #root.quit()
   #init.quit()
   prefire.quit()

   return True;

def postFire():
   logger.debug("Now running postFire function")
   preOrPost=2
   status ="Post-fired"
   ##root.withdraw()
   postfire.deiconify()
   postfire.wm_title("Post-Fire")
   
   INITIALSL = Label(postfire, text="Initials").grid(row=1, column=0, sticky=W)
   INITIALSE = Entry(postfire, textvariable=INITIALS).grid(row=1, column=1, sticky=W)
  
   RUNIDL = Label(postfire, text="Run ID").grid(row=2, column=0, sticky=W, padx=2, pady=2)
   RUNIDE = Entry(postfire, textvariable=RUNID).grid(row=2, column=1, sticky=W,padx=2, pady=2)
   NUMSAML = Label(postfire, text="Number of Samples").grid(row=3, column=0, sticky=W, padx=2, pady=2)
   NUMSAME = Entry(postfire, textvariable=NUMBEROFSAMPLES).grid(row=3, column=1, sticky=W, padx=2, pady=2)
   STARTPOS= Label(postfire, text="Start Position").grid(row=4, column=0, sticky=W)
   STARTPOS= Entry(postfire, textvariable=START_POSITION).grid(row=4, column=1, sticky=W)

   DATEFIREL = Label(postfire, text="Date of Firing (mm-dd-yyyy)").grid(row=5, column=0, sticky=W, padx=2, pady=2)
   DATEFIREE = Entry(postfire, textvariable=DATEOFFIRING).grid(row=5, column=1, sticky=W,padx=2, pady=2)
   TIMEFIREL = Label(postfire, text="Start time of Firing (hh:mm:ss)").grid(row=6, column=0, sticky=W, padx=2, pady=2)
   TIMEFIREE = Entry(postfire, textvariable=TIMEOFFIRING).grid(row=6, column=1, sticky=W,padx=2, pady=2)
   TEMPFIREL = Label(postfire, text="Temperature of Firing (C)").grid(row=7, column=0, sticky=W, padx=2, pady=2)
   TEMPFIREE = Entry(postfire, textvariable=TEMPOFFIRING).grid(row=7, column=1, sticky=W, padx=2, pady=2)

   DURFIREL= Label(postfire, text="Duration of Firing (m)").grid(row=8, column=0, sticky=W, padx=2, pady=2)
   DURFIREE = Entry(postfire, textvariable= DURATIONOFFIRING).grid(row=8, column=1, sticky=W, padx=2, pady=2)
   DURATIONL= Label(postfire, text="Duration of Measurements").grid(row=9, column=0, sticky=W, padx=2, pady=2)
   DURATIONE = Entry(postfire, textvariable=DURATION).grid(row=9, column=1, sticky=W, padx=2, pady=2)
   INTERVALL= Label(postfire, text="Sampling interval (seconds)").grid(row=10, column=0, sticky=W, padx=2, pady=2)
   INTERVALE = Entry(postfire, textvariable=INTERVAL).grid(row=10, column=1, sticky=W, padx=2, pady=2)
   REPSL= Label(postfire, text="Repetitions").grid(row=11, column=0, sticky=W, padx=2, pady=2)
   REPSE = Entry(postfire, textvariable=REPS).grid(row=11, column=1, sticky=W, padx=2, pady=2)
   TEMPL= Label(postfire, text="Temperature (C)").grid(row=12, column=0, sticky=W, padx=2, pady=2)
   TEMPE = Entry(postfire, textvariable=TEMP).grid(row=12, column=1, sticky=W, padx=2, pady=2)
   HUMIDITYL= Label(postfire, text="Relative Humidity").grid(row=13, column=0, sticky=W, padx=2, pady=2)
   HUMIDITYE = Entry(postfire, textvariable=HUMIDITY).grid(row=13, column=1, sticky=W, padx=2, pady=2)
   TEMPL=Label(postfire,text="Madge Tech Temperature:").grid(row=14,column=0,sticky=W,padx=2,pady=2)
   TEMPE=Entry(postfire,textvariable=RHTEMP2000TEMP).grid(row=14,column=1,sticky=W,padx=2,pady=2)
   RHL=Label(postfire,text="Madge Tech RH:").grid(row=15,column=0,sticky=W,padx=2,pady=2)
   RHE=Entry(postfire,text=RHTEMP2000HUMIDITY).grid(row=15,column=1,sticky=W,padx=2,pady=2)

   DIRL=Label(postfire,text="Directory: ").grid(row=16,column=0,sticky=W,padx=2,pady=2)
   DIRE=Entry(postfire,textvariable=DBDIRECTORY).grid(row=16,column=1,sticky=W,padx=2,pady=2)

   DATAF=Label(postfire,text="Database filename to use:").grid(row=17,column=0,sticky=W)
   DATAL=Entry(postfire,textvariable=DATABASENAME).grid(row=17,column=1, sticky=W)

   INITBUTTON = Button(postfire, text="Start Post Fire", command=go_postFire).grid(row=18, column=1, padx=2, pady=2)
   postfire.mainloop()
   
def go_postFire():
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
      Message(alert,text="You must have a RunID to continue.", bg='red', fg='ivory', relief=GROOVE).grid(row=0, column=0, sticky=W+E+N+S)
      #Button(alert, text="Continue", command=backToMainWindow).grid(row=1,column=0)
      #Button(alert, text="Quit", command=KillProgram).grid(row=2,column=1)
      logger.debug("You must have a RunID entered in order to continue.")
      return False;
   
   setInitials=str(INITIALS.get())
   startPosition=int(START_POSITION.get())
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
   temperatureOfFiring=int(TEMPOFFIRING.get())
   durationOfFiring=DURATIONOFFIRING.get()*60
   preOrPost=2
   status="postfire"
 

   startPosition=START_POSITION.get()
   now = datetime.today()
   ## (locationCode,numberOfSamples,description,temperature,humidity,endOfFiring,durationOfFiring)=DataReadWrite.getRunInfo(runID)
   startdate=DATEOFFIRING.get()
   starttime=TIMEOFFIRING.get()
   sdate=startdate.split("-",3)
   stime=starttime.split(":",3)

   startOfFiring = datetime(int(sdate[2]), int(sdate[0]), int(sdate[1]), int(stime[0]), int(stime[1]), int(stime[2]))
   
   end = timedelta(minutes=durationOfFiring)
   endOfFiring = startOfFiring + end
   
   # minutes since firing ended
   diffTime = now - endOfFiring
  
   ## d_endOfFiring = endOfFiring.strftime("%m-%d-%y %H:%M:%S")
   intervalsec=int(INTERVAL.get())
   postMeasurementTimeInterval=int(DURATION.get()) 
   repetitions=int(REPS.get())
   #print runID,setInitials,status,durationOfFiring,temperatureOfFiring,postMeasurementTimeInterval,duration,repetitions,endOfFiring,startPosition,intervalsec
   logger.debug("updateRunPostFire( %d,%s,%s,%s,%d,%d,%d,%d,%d,%s,%d,%d )" % 
   							(runID,setInitials,status,startOfFiring,
       						durationOfFiring,temperatureOfFiring,intervalsec,
      						duration,repetitions,endOfFiring,startPosition,intervalsec))

   value=DataReadWrite.updateRunPostFire(runID,setInitials,
               status,startOfFiring,durationOfFiring,temperatureOfFiring,intervalsec,
               duration,repetitions,endOfFiring, startPosition,intervalsec)
   if (value is False):
      logger.error("There has been an error since updateRunPostFire returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. The arm has returned to Home.", bg='red', fg='ivory', relief=GROOVE).pack(padx=1,pady=1)
     # Button(alert, text="Continue", command=backToMainWindow)
     # Button(alert, text="Quit", command=KillProgram)

   count=0
   repeat=1
   ## print runID,"-",duration,"-",intervalsec,"-",numberOfSamples,"-",startPosition,"-",endOfFiring,"-",tempCorrection,"-",rhCorrection,"-",repeat
 
   while repeat < (repetitions+1):
      CYCLE.set(repeat)
      weighAllSamplesPostFire(runID,duration,
               intervalsec,numberOfSamples,startPosition,
               endOfFiring,tempCorrection,rhCorrection,repeat,
               robotStatus,POSITION,MCOUNT,
               CURRENTSTEP,STATUS,DURATION,
               LOGGERINTERVAL,RUNID,NUMBEROFSAMPLES,
               TIMEREMAINING,TIMEELAPSED,REPS,CYCLE)
      repeat += 1
      #  update_windows()
   #postfire.update()
   #postfire.deiconify()
   #postfire.withdraw()
   return True;
   
def weighAllSamplesPostFire(runID,duration,
      		intervalsec,numberOfSamples,startPosition,endOfFiring,
      		tempCorrection,rhCorrection,repeat,robotStatus,
      		POSITION,MCOUNT,CURRENTSTEP,STATUS,DURATION,
      		LOGGERINTERVAL,RUNID,NUMBEROFSAMPLES,TIMEREMAINING,TIMEELAPSED,REPS,CYCLE):
   ## print runID,"-",duration,"-",intervalsec,"-",numberOfSamples,"-",startPosition,"-",endOfFiring,"-",tempCorrection,"-",rhCorrection,"-",repeat
   logging.debug("weighAllSamplesPostFire( %d,%d,%d,%d,%d,%s,%f,%f,%d)" %
   				(runID,
   				duration,
      		intervalsec,
      		numberOfSamples,
      		startPosition,
      		endOfFiring,
      		tempCorrection,
      		rhCorrection,
      		repeat))
   # Find elapsed time
   #first put robot back to zero
   position=int(startPosition)

   if position=="":
      position=1

   #HomePosition()
   listOfValues=()
   STATUS.set("Initializing")
   crucibleWeight=0.0
   robotStatus.deiconify()
   preOrPost=2
   status="postfire"
   now = datetime.today()
   timeLapsedSinceFiring= now - endOfFiring
   Label(robotStatus,text="Run ID:").grid(row=0,column=0,sticky=W)
   Label(robotStatus,textvariable=RUNID).grid(row=0,column=1, sticky=W)
   Label(robotStatus,text="Current sample number:").grid(row=1,column=0,sticky=W)
   Label(robotStatus,textvariable=POSITION).grid(row=1,column=1, sticky=W) 
   Label(robotStatus,text="Cycle Number:").grid(row=3,column=0,sticky=W)
   Label(robotStatus,textvariable=CYCLE).grid(row=3,column=1,sticky=W)

   Label(robotStatus,textvariable=MCOUNT).grid(row=4,column=1,sticky=W)
   Label(robotStatus,text="Current measurement count:").grid(row=4,column=0,sticky=W)
   Label(robotStatus,text="Time elapsed since firing (min):").grid(row=5,column=0,sticky=W)
   Label(robotStatus,textvariable=TIMEELAPSED).grid(row=5,column=1,sticky=W)
   Label(robotStatus,text="Logging interval:").grid(row=6,column=0, sticky=W)
   Label(robotStatus,textvariable=LOGGERINTERVAL).grid(row=6,column=1,sticky=W)
   Label(robotStatus,text="Duration of Measurements:").grid(row=7,column=0, sticky=W)
   Label(robotStatus,textvariable=DURATION).grid(row=7,column=1,sticky=W)
   Label(robotStatus,text="Number of Samples:").grid(row=8,column=0,sticky=W)
   Label(robotStatus,textvariable=NUMBEROFSAMPLES).grid(row=8,column=1,sticky=W)
   Label(robotStatus,text="Time remaining for this sample:").grid(row=9,column=0,sticky=W)
   Label(robotStatus,textvariable=TIMEREMAINING).grid(row=9,column=1,sticky=W)
   Label(robotStatus,text="Status").grid(row=10,column=0, sticky=W)
   Label(robotStatus,textvariable=STATUS).grid(row=10,column=1,sticky=W)
   startTime=datetime.today()
   endPoint=timedelta(minutes=duration)
   endTime=startTime+endPoint
   POSITION.set(int(position))
   NUMBEROFSAMPLES.set(int(numberOfSamples))
   DURATION.set(duration)
   LOGGERINTERVAL.set(intervalsec)
   CYCLE.set(repeat)
  
   sleep(5)
   while position < numberOfSamples+1:
      
      logging.debug("Now on position: %d",int(position))
      ##goToSamplePosition(position)
      ##val=samplePickUp()
      ##if val == False:
      ##   return False
      ## zerothe balance for each sample
      ##DataReadWrite.zeroBalance()
      ##DataReadWrite.openBalanceDoor()
      ##goToOutsideBalanceFromOutside()
      ##goToInsideBalanceFromOutisde()
      ##val=putSampleOnBalance()
      ##if val == False:
      ##   return False
      ## may need to check to see if arm is clear of door.
      #goToOutsideBalanceFromInside()
      #DataReadWrite.closeBalanceDoor()
      crucibleWeight=double(DataReadWrite.getCrucibleWeight(runID,position))
      if (crucibleWeight is False):
         alertWindow("getCrucibleWeight returned an error.")
         exit(1)
      
      sampleID=int(DataReadWrite.getSampleID(runID,position))
      startTime=datetime.today()
      durationOfLogging=int(duration)
      endPoint=timedelta(minutes=durationOfLogging)
      
      endTime=startTime+endPoint
      count=0
      kcount=0
      repetition_count=0
      standard_weight=float(0.0)
      listOfValues=[]
      a=array([])
      statustext="Weighing sample # %d"% position
      STATUS.set(statustext)
      total_count=int(DataReadWrite.getMaxPostFireCount(runID,position))
      if (total_count==0 or total_count==""):
         total_count=0
      while datetime.today() < endTime:
         timeLeft=endTime-datetime.today()
         TIMEREMAINING.set(int(timeLeft.seconds/60))
         kcount=0
         standard_weight=0.0
         measurement=double(0.0)
         weight=double(0.0)
         result=[]
         (measurement,status)=DataReadWrite.readWeightFromBalance()
         weight=double(measurement)-double(crucibleWeight)
         if weight>0.0:
            a=append(a,double(weight))
            averageWeight=a.mean()
            stdevWeight=a.std()
            logger.debug( "Count: %i the average weight of sample # %i is %f with stdev of %f" % (count, position, averageWeight,stdevWeight))
            ## now update crucible position record 
            now = datetime.today()
            today = now.strftime("%m-%d-%y %H:%M:%S")
            total_count += 1
            count += 1
            repetition_count += 1
            MCOUNT.set(count)
            temperature=xyzRobot.getTemperature()
            humidity=xyzRobot.getHumidity()
            logger.debug( "TMP:  temp: %s, humidity: %s" % (temperature,humidity))
            
            standard_weight=0.0
            
            timeDiff=now - endOfFiring
            timeElapsed=int(timeDiff.seconds/60)
            TIMEELAPSED.set(timeElapsed)
            timeElapsedQuarterPower=double(pow(abs(timeElapsed),0.25))
 
            value=DataReadWrite.insertPostFireMeasurement(runID,sampleID,position,
          				weight,status,temperature,humidity,endOfFiring,
          				crucibleWeight,standard_weight,now,total_count,repeat,repetition_count,count)
            if (value is False):
               alertWindow("insertPostFireMeasurement returned with an error.")
               exit(1)
               ### check to see if enough measurements have been made. First at least 100 must have been done
            if (count > COUNTS_FOR_STATS):
               (mean,stdev,variance,tempMean,tempStdev,humidityMean,humidityStdev)=DataReadWrite.getStatsForPostFireWeightOfSample(runID,sampleID,count)
               logger.debug("TempMean: %d  TempStDev: %d HumidityMean: %d HumidityStdDev: %d" % (tempMean,tempStdev,humidityMean,humidityStdev))

               value=DataReadWrite.updateSamplePostFire(runID,sampleID,position,tempMean,tempStdev,humidityMean,humidityStdev,count,repeat,timeElapsed)

            sleep(intervalsec)
            if count==0:
               ## check to see if balance is giving anything
               (value,status)=DataReadWrite.readInstantWeightFromBalance()
               logger.debug( "Instant value from balance (unstable):  %f",float(value))
               if (value>0):
                  STATUS.set("Resetting clock")
                  logger.warning( "Since this is >0 the balance is reading but not stable")
                  logger.warning( "resetting clock. Waiting for a valid entry before storing data...")
                  startTime=datetime.today()
                  endPoint=timedelta(minutes=durationOfLogging)
                  endTime=startTime+endPoint
               else:
                  STATUS.set("Error. No output from balance. Trying again.")
                  logger.warning("There is a problem: no output from balance at all: Count: %d",int(kcount))
                  kcount += 1
                  if kcount==500:
                     STATUS.set("Tried 500 times but nothing from balance. Quitting")
                     logger.error( "There is a problem: no output for 500 counts -- quitting ")
                     ##KillMotors()
                     exit(1)
         sleep(intervalsec)
      statustext="Done! Going to retrieve sample from balance."
      STATUS.set(statustext)
      ##DataReadWrite.openBalanceDoor()
      ##goToInsideBalanceFromOutside()
      statustext="Picking up sample from balance."
      STATUS.set(statustext)
      #val=pickUpSampleFromBalance()
      #if val == False:
      #   return False
      STATUS.set("Going outside balance from inside")
      ##goToOutsideBalanceFromInside()
      statustext="Going to position %d" % int(position)
      STATUS.set(statustext)
      ##goToSamplePosition(position)
      STATUS.set("Putting sample down")
      ##val=samplePutDown()
      ##if val == False:
      ##   return False
      STATUS.set("Now going to home position.")
      #response=goHome()
      ##DataReadWrite.closeBalanceDoor()
      ##if response==False:
      ##   logger.error( "Was unable to go home. Quitting.")
      ##   return False
      position +=1
      POSITION.set(int(position))
      statustext="Now on position %d" % position
      STATUS.set(statustext)
   STATUS.set("Done!")
   #robotStatus.withdraw()
   return runID;

postFire()


