
from datetime import date, datetime, time, timedelta
import DataReadWrite
import xyzRobot
from time import sleep
import scipy
from numpy import *
from Tkinter import *
import logging
import plotTest

#plotGraph= plotTest.Viewer()

# Pop up the windows for the two objects
#plotGraph.edit_traits()

logger=logging.getLogger("startRHX")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('rhx.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

robotStatus=Tk()
robotStatus.wm_title("Robot Status")
robotStatus.withdraw()
init = Toplevel()
LOGINT=5
M0EE1=IntVar()
M1EE1=IntVar()
M2EE1=IntVar()
MB1V1=IntVar()
MB2V1=IntVar()
RUNID=IntVar()
INITIALS=StringVar()
DURATION=IntVar()
NUMBEROFSAMPLES=IntVar()
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
HUMIDITY=DoubleVar()
REPS=IntVar()
INTERVAL=IntVar()
RUNID=IntVar()
DATEOFFIRING=StringVar()
TIMEOFFIRING=StringVar()
DURATIONOFFIRING=StringVar()
TEMPOFFIRING=StringVar()
CURRENTPOSITION=IntVar()
CURRENTREP=IntVar()
NAME=StringVar()
LOCATION=StringVar()
POSITION=IntVar()
MCOUNT=IntVar()
CURRENTSTEP=StringVar()
STATUS=StringVar()
DURATION=IntVar()
LOGGERINTERVAL=IntVar()
RUNID=IntVar()
NUMBEROFSAMPLES=IntVar()
TIMEREMAINING=IntVar()
TEMPERATURE=DoubleVar()
HUMIDITY=DoubleVar()
SAMPLENUM=IntVar()
RHTEMP2000TEMP=DoubleVar()
RHTEMP2000HUMIDITY=DoubleVar()

tempCorrection=0.0
rhCorrection=0.0

fileName="TEST"
dirname="/Users/Archy/Dropbox/Rehydroxylation/"


def go_initialize():
   DataReadWrite.initializeDatabase(dirname,fileName)
   DataReadWrite.openDatabase(dirname,fileName)
   numberOfSamples=int(NUMBEROFSAMPLES.get())
   duration=int(DURATION.get())
   startPosition=int(START_POSITION.get())
   #xyzRobot.resetValuesToZero()   
   setInitials=INITIALS.get()
   standardTemp=float(RHTEMP2000TEMP.get())
   standardRH = float(RHTEMP2000HUMIDITY.get())


   tempCorrection=standardTemp-float(xyzRobot.getTemperature())
   rhCorrection=standardRH-float(xyzRobot.getHumidity())
   logger.debug( "standardTemp: %f",standardTemp)
   logger.debug( "standardRH: %f",standardRH)
   logger.debug( "Temp: %f",xyzRobot.getTemperature())
   logger.debug( "RH: %f",xyzRobot.getHumidity())
   logger.debug( "tempCorrection: %f", tempCorrection)
   logger.debug( "rhCorrection: %f ",rhCorrection)
   
   runID = weighAllCrucibles(setInitials,numberOfSamples,LOGINT,duration,
   								startPosition,tempCorrection,rhCorrection,
          						robotStatus,POSITION,MCOUNT,CURRENTSTEP,
          						STATUS,DURATION,LOGGERINTERVAL,
          						RUNID,NUMBEROFSAMPLES,TIMEREMAINING)
   return True;
   
def weighAllCrucibles(initials,numberOfSamples,loggerInterval,
       duration,startPosition,tempCorrection,rhCorrection,robotStatus,
       POSITION,MCOUNT,CURRENTSTEP,STATUS,
       DURATION,LOGGERINTERVAL,RUNID,NUMBEROFSAMPLES,TIMEREMAINING):
   
   # Find elapsed time
   #first put robot back to zero
   logger.info("weightAllCrucibles: %s, %d, %d, %d, %d" % (initials,numberOfSamples,loggerInterval,duration,startPosition))
   position=int(startPosition)
   #HomePosition()
   listOfValues=()
   LOGGERINTERVAL.set(loggerInterval)
   DURATION.set(duration)
   POSITION.set(position)
   STATUS.set("Initializing")
   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")
   ### set up gui #########
   robotStatus.deiconify()
   Label(robotStatus,text="Run ID:").grid(row=0,column=0,sticky=W)
   Label(robotStatus,textvariable=RUNID).grid(row=0,column=1, sticky=W)
   Label(robotStatus,text="Current sample number:").grid(row=1,column=0,sticky=W)
   Label(robotStatus,textvariable=POSITION).grid(row=1,column=1, sticky=W)
   Label(robotStatus,textvariable=MCOUNT).grid(row=2,column=1,sticky=W)
   Label(robotStatus,text="Current measurement count:").grid(row=2,column=0,sticky=W)
   Label(robotStatus,text="Logging interval:").grid(row=3,column=0, sticky=W)
   Label(robotStatus,textvariable=LOGGERINTERVAL).grid(row=3,column=1,sticky=W)
   Label(robotStatus,text="Duration of Measurements:").grid(row=4,column=0, sticky=W)
   Label(robotStatus,textvariable=DURATION).grid(row=4,column=1,sticky=W)
   Label(robotStatus,text="Number of Samples:").grid(row=5,column=0,sticky=W)
   Label(robotStatus,textvariable=NUMBEROFSAMPLES).grid(row=5,column=1,sticky=W)
   Label(robotStatus,text="Time remaining for this sample:").grid(row=6,column=0,sticky=W)
   Label(robotStatus,textvariable=TIMEREMAINING).grid(row=6,column=1,sticky=W)
   Label(robotStatus,text="Status").grid(row=7,column=0, sticky=W)
   Label(robotStatus,textvariable=STATUS).grid(row=7,column=1,sticky=W)
   NUMBEROFSAMPLES.set(numberOfSamples)
   sleep(5)
   
   #first create a new run so we have an ID.
   logger.debug("DataReadWrite.insertRun( %s,%s,%d )" %(initials,today,numberOfSamples))
   runID=DataReadWrite.insertRun(initials,today,numberOfSamples)
   statustext = "Run ID is %d" % int(runID)
   logger.info( statustext)
   RUNID.set(int(runID))
   while position < numberOfSamples+1:
      POSITION.set(position)
      #statustext="Going to position: %d"% int(position)
      #logger.info( statustext)
      #set this crucible for this run
      logger.debug("DataReadWrite.insertInitialCrucible(%d,%d,%s)" % (runID,position,today))
      DataReadWrite.insertInitialCrucible(runID,position,today)
      # assume we start in position 1 -- which is the 0,0 point for the grid
      #logger.info( "going to sample position: %d ", position)
      STATUS.set(statustext)
      #goToSamplePosition(position)
      #statustext="Picking up sample %d" % int(position)
      #STATUS.set(statustext)
      #logger.info( "picking up sample.")
      #val = samplePickUp()
      #if val == False:
      #   return False;
      
      ## zero the balance for each sample
      logger.debug("going to zero balance...")
      DataReadWrite.zeroBalance()
      logger.debug( "opening balance door.")
      #DataReadWrite.openBalanceDoor()
      #statustext="Going to outside of balance x: %d y: %d" %( BALANCE_OUTSIDE[X], BALANCE_OUTSIDE[Y])
      #STATUS.set(statustext)
      logger.debug( "go to outside of balance.")
      #goToOutsideBalanceFromOutside()
      logger.debug( "go to inside balance")
      #statustext="Going to inside balance x: %d y: %d" %( BALANCE_INSIDE[X], BALANCE_INSIDE[Y])
      #STATUS.set(statustext)
      #goToInsideBalanceFromOutside()
      logger.debug( "put sample on balance")
      STATUS.set("Putting sample on balance")
      #val = putSampleOnBalance()
      #if val==False:
      #   STATUS.set("ERROR")
      #   robotStatus.quit()
      #   return False;
      STATUS.set("Moving to outside balance.")
      logger.info( "Move to outside balance.")
      #goToOutsideBalanceFromInside()
      ## may need to check to see if arm is clear of door.
      #DataReadWrite.closeBalanceDoor()
      durationOfLogging=int(duration)
      startTime=datetime.today()
      endPoint=timedelta(minutes=durationOfLogging)
      endTime=startTime+endPoint
      listOfValues=[]
      weight=float(0.0)
      count=0
      kcount=0
      tempHumidityArray=[]
      statustext="Weighing sample # %d"% position
      STATUS.set(statustext)
      a = array([])
      tempArray=array([])
      humidityArray=array([])

      averageTemp=0.0
      stdevTemp=0.0
      averageHumidity=0.0
      stdevHumidity=0.0

      while datetime.today() < endTime:
         timeLeft=endTime-datetime.today()
         TIMEREMAINING.set(int(timeLeft.seconds/60))
         result=[]
         (weight,status)=DataReadWrite.readWeightFromBalance()
         temp=xyzRobot.getTemperature()
         humidity=xyzRobot.getHumidity()
         if weight>0.0:
            #print "NOW GOING TO UPDATE PLOT"
            #plotGraph.add_data_point(1, 23.2323)

            listOfValues.append(weight)
            a=append(a,float(weight))
            averageWeight=mean(a)
            stdevWeight=std(a)
            averageTemp=0.0
            averageHumidity=0.0
            stdevTemp=0.0
            stdevHumidity=0.0

            logger.debug( "temp: %f humidity: %f " % (temp, humidity))
            temp=xyzRobot.getTemperature()
            humidity=xyzRobot.getHumidity()

            if (temp==""):
               temp=0.0     
            if temp>0:
               tempArray=append(tempArray,temp)
               if (tempArray.size > 2):
                  averageTemp=mean(tempArray)
                  stdevTemp=std(tempArray)
               else:
                  averageTemp=temp
                  stdevTemp=0.0
            if humidity>0:
               humidityArray=append(humidityArray,humidity)
               if humidityArray.size > 2:
                  averageHumidity=mean(humidityArray)
                  stdevHumidity=std(humidityArray)
               else:
                  averageHumidity=humidity
                  stdevHumidity=0.0
            
            print "position:",position,"averageWeight:",averageWeight,"stdevWeight:",stdevWeight,"averageTemp:",averageTemp,"stdevTemp:",stdevTemp,"averageHumidity:",averageHumidity,"stdevHumidity:",stdevHumidity,"today:",today,"run:",runID,"count:",count
            print "position=%d,averageWeight=%s,stdevWeight=%s,averageTemp=%s,stdevTemp=%s,averageHumidity=%s,stdevHumidity=%s,today=%s,runID=%d,count=%d" % (position,averageWeight,stdevWeight,averageTemp,stdevTemp,averageHumidity,stdevHumidity,today,runID,count)
            logger.debug( "Count: %d the average weight of crucible # %i is: %f with stdev of: %f" %(count, position,averageWeight,stdevWeight))
            ## now update crucible position record 
            now = datetime.today()
            today = now.strftime("%m-%d-%y %H:%M:%S")
            count += 1
            MCOUNT.set(count)

            ## kludge
            averageWeight=16
            DataReadWrite.updateCrucible(position,averageWeight,stdevWeight,averageTemp,stdevTemp,averageHumidity,stdevHumidity,today,runID,count)
            sleep(loggerInterval)
            statustext="Weight recorded #%d %f %f" %(count,averageWeight,stdevWeight)
            STATUS.set(statustext)
         if count==0:
            ## check to see if balance is giving anything
            (value,status)=DataReadWrite.readInstantWeightFromBalance()
            logger.info( "Balance current reads: %f ",float(value))
            if (value>0):
               logger.info( "Since this is >0 the balance is reading but not stable")
               logger.info( "resetting clock. Waiting for a valid entry before storing data...")
               startTime=datetime.today()
               endPoint=timedelta(minutes=durationOfLogging)
               endTime=startTime+endPoint
            else:
               STATUS.set("Error: nothing from balance. Checking to see if this resolves itself")
               logger.info( "There is a problem: no output from balance at all: Count: %d",int(kcount))
               kcount += 1
               if kcount==500:
                 logger.error( "There is a problem: no output for 500 counts -- quitting ")
                 xyzRobot.KillMotors()
                 exit(1)
      logger.info("Open the balance door")
      #DataReadWrite.openBalanceDoor()
      STATUS.set("Go back into balance to get sample.")
      logger.info( "enter balance")
      #goToInsideBalanceFromOutside()
      logger.info( "pick up sample")
      STATUS.set("Pick up sample from balance")
      #val = pickUpSampleFromBalance()
      #if val == False:
      #   STATUS.set("Error: missing sample")
      #   robotStatus.quit()
      #   return False
      logger.info( "leave balance . . . ")
      STATUS.set("Leave balance.")
      #goToOutsideBalanceFromInside()
      statustext="Return to position %d", int(position)
      STATUS.set(statustext)
      logger.info( "now return to position: %d ", int(position))
      STATUS.set("Put sample down.")
      #goToSamplePosition(position)
      logger.info( "put the sample down. . . ")
      #val=samplePutDown()
      #if val == False:
      #   STATUS.set("Error sample held when there shouldn't be one")
      #   robotStatus.quit()
      #   return False;
      logger.info( "close the balance door . . ")
      #DataReadWrite.closeBalanceDoor()
      STATUS.set("Now go to home position")
      #response=goHome()
      #if response==False:
      #   logger.error( "Home point not reached. Stopping.")
      #   return False;
      
      position += 1
      POSITION.set(position)
      statustext="Now starting next sample: %d",position
      STATUS.set(statustext)
      statustext="go on to the next position: %d", int(position)
      logger.info(statustext)
   STATUS.set("Done!")
   robotStatus.withdraw()
   return (runID)



init.wm_title("Initialize and Weigh Crucibles")
#Create Menus
menubar = Menu(init)
RHTEMP2000TEMP.set(18.0)
RHTEMP2000HUMIDITY.set(70.0)
INITIALS.set('CPL')
NUMBEROFSAMPLES.set(5)
DURATION.set(5)
INITIALSL = Label(init, text="Initials").grid(row=1, column=0, sticky=W)
INITIALSE = Entry(init, textvariable=INITIALS).grid(row=1, column=1, sticky=W)
  
NUMSAML = Label(init, text="Number of Samples").grid(row=3, column=0, sticky=W, padx=2, pady=2)
NUMSAME = Entry(init, textvariable=NUMBEROFSAMPLES).grid(row=3, column=1, sticky=W, padx=2, pady=2)

DURATIONL= Label(init, text="Duration of Measurements").grid(row=4, column=0, sticky=W, padx=2, pady=2)
DURATIONE = Entry(init, textvariable=DURATION).grid(row=4, column=1, sticky=W, padx=2, pady=2)
TEMPL=Label(init,text="Madge Tech Temperature:").grid(row=5,column=0,sticky=W,padx=2,pady=2)
TEMPE=Entry(init,textvariable=RHTEMP2000TEMP).grid(row=5,column=1,sticky=W,padx=2,pady=2)
RHL=Label(init,text="Madge Tech RH:").grid(row=6,column=0,sticky=W,padx=2,pady=2)
RHE=Entry(init,text=RHTEMP2000HUMIDITY).grid(row=6,column=1,sticky=W,padx=2,pady=2)


INITBUTTON = Button(init, text="Start Initialize", command=go_initialize).grid(row=7, column=1, sticky=W, padx=2, pady=2)
   
status="Initialize"

#logger.info("XMotor: %i  YMotor: %i" % (xyzRobot.getXMotorPosition(), xyzRobot.getYMotorPosition()))

#(xpos,ypos) = DataReadWrite.getLastPosition()
logger.info("Set the current position of motors to zero ... ")   
numberOfSamples=int(NUMBEROFSAMPLES.get())
duration=int(DURATION.get())
startPosition=int(START_POSITION.get())
setInitials=INITIALS.get()
logger.info ("Now going to move and measure each of the crucibles... ")
#logger.info("xyzRobot.weighAllCrucibles(%s,%d,%d,%d,%d)" % (setInitials,numberOfSamples,LOGINT,duration,startPosition))
init.mainloop()


