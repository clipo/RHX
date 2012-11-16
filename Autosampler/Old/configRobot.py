###Simple program that moves the motors and the arms - used for finding positions.


##Imports
import sys
import easygui
# comment while on Mac OS X
#sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
import logging
import communication
from Tkinter import *
import tkFileDialog
from tkMessageBox import *
from tkColorChooser import askcolor
from tkFileDialog import askopenfilename
import time
from datetime import datetime
from datetime import timedelta
import os
import io
import re
import serial
from ctypes import *
from time import sleep
import DataReadWriteNoBalance
import xyzRobot
import math
import communication

LOGINT=5
logger = logging.getLogger("AutoSampler-configRobot")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
today_date = datetime.today()
datestring = today_date.strftime("%Y-%m-%d-%H-%M")

## Mac OS X
debugfilename = "/Users/Clipo/Dropbox/Rehydroxylation/Logger/Autosampler/logs/rhx-configRobot" + datestring + "_debug.log"
## debugfilename = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Autosampler/logs/rhx-startRHX" + datestring +\
##                "_debug.log"
fh = logging.FileHandler(debugfilename)
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

##Establish GUI ### make these global

root = Tk()
root.wm_title("RHX Measurement")
init = Toplevel()
init.withdraw()
prefire= Toplevel()
prefire.withdraw()
postfire= Toplevel()
postfire.withdraw()
alert=Toplevel()
alert.withdraw()
robotStatus=Toplevel()
robotStatus.wm_title("Robot Status")
robotStatus.withdraw()
moveArm=Toplevel()
moveArm.wm_title("Move Arm")
moveArm.withdraw()
setupCrucibles= Toplevel()
setupCrucibles.withdraw()


#### These are all variables for the displays. Ive made them global so that I can access them anywhere here. Kludgy

XZERO=StringVar()
YZERO=StringVar()
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
START_POSITION.set(1)
MV=IntVar()
AV=DoubleVar()
XMOTORPOSITION=StringVar()
YMOTORPOSITION= StringVar()
BALANCEWEIGHT=DoubleVar()
BALANCESTATUS=StringVar()
ABSOLUTEXPOSITION=StringVar()
ABSOLUTEYPOSITION=StringVar()
CRUCIBLEYESNO=StringVar()
MOTORSTEP=StringVar()
MOTORSTEP.set("20")
BALANCEDOOR=StringVar()
SAMPLEPOSITION=StringVar()
POSITION=IntVar()
TEMP=DoubleVar()
HUMIDITY=DoubleVar()
REPS=IntVar()
INTERVAL=IntVar()
INTERVAL.set(5)
RUNID=IntVar()
RUNID.set(1)
DATEOFFIRING=StringVar()
TIMEOFFIRING=StringVar()
DURATIONOFFIRING=IntVar()
RATEOFHEATING=IntVar()
TEMPOFFIRING=IntVar()
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
STANDARD_BALANCE=DoubleVar()
TIMEREMAINING=IntVar()
TIMEELAPSEDMIN=DoubleVar()
TEMPERATURE=DoubleVar()
HUMIDITY=DoubleVar()
SAMPLENUM=IntVar()
FILENAME=StringVar()
RHTEMP2000TEMP=DoubleVar()
RHTEMP2000HUMIDITY=DoubleVar()
CYCLE=IntVar()
PRECISIONTEMP=DoubleVar()
DATABASENAME=StringVar()
DBDIRECTORY=StringVar()
DBDIRECTORY.set("c:/Users/Archy/Dropbox/Rehydroxylation/")
tempCorrection=0.0
rhCorrection=0.0
fileName="RHX.sqlite"
dirname="/Users/Archy/Dropbox/Rehydroxylation/"
CRUCIBLEWEIGHT=DoubleVar()
CRUCIBLEWEIGHTSTDDEV=DoubleVar()
SAMPLEWEIGHT=DoubleVar()
CURRENTSAMPLE=IntVar()
ABSOLUTEXZERO=IntVar()
ABSOLUTEYZERO=IntVar()
ABSOLUTEXZERO.set(3)
ABSOLUTEYZERO.set(230)

COUNTSFORSTATS=IntVar()
COUNTSFORSTATS.set(3)
MEAN=DoubleVar()
STDEV=DoubleVar()
VARIANCE=DoubleVar()
SETRUNID=IntVar()
POSTFIREWEIGHT=DoubleVar()
POSTFIREWEIGHTSTDDEV=DoubleVar()
CURRENTSAMPLE=IntVar()
INITIALWEIGHT=DoubleVar()
INITIALWEIGHTSTDDEV=DoubleVar()

INITIALSHERDWEIGHTSTDDEV=DoubleVar()
INITIALWEIGHTSTDDEV=DoubleVar()
SAMPLEWEIGHTSTDDEV=DoubleVar()
SAMPLEZPOSITION=IntVar()
BALANCEZPOSITION=IntVar()
MAXXMOTORVELOCITY=DoubleVar()
MAXYMOTORVELOCITY=DoubleVar()

def quit():
   value=DataReadWriteNoBalance.closeDatabase()
   if (value == False):
      logger.error("There has been an error since closeDatabase returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. Cannot close database", bg='red', fg='ivory', relief=GROOVE)
   alert.quit()
   prefire.quit()
   postfire.quit()
   init.quit()
   root.quit()
   exit(1);

def callback():
   askopenfilename()

def printValues():
   print "XMotor: ",xyzRobot.getXMotorPosition(), " YMotor: ",xyzRobot.getYMotorPosition()
   print "Absolute X Position: ", xyzRobot.getAbsoluteXPosition()
   print "-------------------------------------------------"
   return True;

#Program Controls

def restart_program():
   try:
      xyzRobot.KillMotors()
   except:
      pass
   python = sys.executable
   os.execl(python, python, * sys.argv)
   return True;

def KillProgram():
   logger.debug("Quit has been requested by users. So quitting.")
   logger.debug("KillProgram!")
   try:
      xyzRobot.KillMotors()
   except:
      pass

   alert.quit()
   root.quit()
   init.quit()
   prefire.quit()
   postfire.quit()
   return True;

def update_windows():
   XMOTORPOSITION.set(xyzRobot.getXMotorPosition())
   YMOTORPOSITION.set(xyzRobot.getYMotorPosition())

   XZERO.set(xyzRobot.atXZero())
   YZERO.set(xyzRobot.atYZero())
   PRECISIONTEMP.set(xyzRobot.getTemperature())
   results=[]
   XZERO.set(xyzRobot.atXZero())
   YZERO.set(xyzRobot.atYZero())
   if (XZERO.get()=="TRUE") & (YZERO.get()=="TRUE"):
      value = xyzRobot.setAbsZeroXY()

   ABSOLUTEXPOSITION.set(xyzRobot.getAbsoluteXPosition())
   ABSOLUTEYPOSITION.set(xyzRobot.getAbsoluteYPosition())

   print "X encoder: ", xyzRobot.getAbsoluteXPosition()
   print "Y encoder: ", xyzRobot.getAbsoluteYPosition()
   vals=[]
   value=0
   if XZERO.get()=="TRUE":
      ## reset the Absolute Zero points
      value=xyzRobot.setXMotorPosition(0)

   if YZERO.get()=="TRUE":
      value=xyzRobot.setYMotorPosition(0)

   #logger.debug("Going to read the temp and humidity")
   TEMPERATURE.set(xyzRobot.getTemperature())
   HUMIDITY.set(xyzRobot.getHumidity())
   value = xyzRobot.isGripperHoldingSomething()
   if value is True:
      CRUCIBLEYESNO.set("Yes")
   else:
      CRUCIBLEYESNO.set("No")
   xlimit=xyzRobot.getXMotorVelocityLimit()
   ylimit=xyzRobot.getYMotorVelocityLimit()
   MAXXMOTORVELOCITY.set(xlimit)
   MAXYMOTORVELOCITY.set(ylimit)

def initialize():
   root.withdraw()
   init.deiconify()
   init.wm_title("Initialize and Weigh Crucibles")

   ## assume starting point is 0
   setMotorXToZero()
   setMotorYToZero()
   setAbsZeroXY()
   #Create Menus
   menubar = Menu(init)
   #File Bar 
   filemenu = Menu(menubar, tearoff=0)
   filemenu.add_command(label="New", command=restart_program)
   filemenu.add_separator()
   filemenu.add_command(label="Exit", command=KillProgram)
   menubar.add_cascade(label="File", menu=filemenu)
   RHTEMP2000TEMP.set(xyzRobot.getTemperature())
   RHTEMP2000HUMIDITY.set(xyzRobot.getHumidity())
   PRECISIONTEMP.set(xyzRobot.getTemperature())
   #Help Menu
   helpmenu = Menu(menubar, tearoff=0)
   menubar.add_cascade(label="Help", menu=helpmenu)
   #Display the Menus
   START_POSITION.set(1)
   init.config(menu=menubar)
   INITIALSL = Label(init, text="Initials").grid(row=1, column=0, sticky=W)
   INITIALSE = Entry(init, textvariable=INITIALS).grid(row=1, column=1, sticky=W)

   NUMSAML = Label(init, text="Number of Crucibles").grid(row=3, column=0, sticky=W, padx=2, pady=2)
   NUMSAME = Entry(init, textvariable=NUMBEROFSAMPLES).grid(row=3, column=1, sticky=W, padx=2, pady=2)

   STARTPOS2= Label(init, text="Start Position").grid(row=4, column=0, sticky=W)
   STARTPOS2= Entry(init, textvariable=START_POSITION).grid(row=4, column=1, sticky=W)

   DURATIONL= Label(init, text="Duration of Measurements").grid(row=5, column=0, sticky=W, padx=2, pady=2)
   DURATIONE = Entry(init, textvariable=DURATION).grid(row=5, column=1, sticky=W, padx=2, pady=2)

   TEMPL=Label(init,text="Madge Tech Temperature:").grid(row=6,column=0,sticky=W,padx=2,pady=2)
   TEMPE=Entry(init,textvariable=RHTEMP2000TEMP).grid(row=6,column=1,sticky=W,padx=2,pady=2)
   RHL=Label(init,text="Madge Tech RH:").grid(row=7,column=0,sticky=W,padx=2,pady=2)
   RHE=Entry(init,text=RHTEMP2000HUMIDITY).grid(row=7,column=1,sticky=W,padx=2,pady=2)

   PTEMP1=Label(init,text="Precision Temp").grid(row=8,column=0,sticky=W)
   PTEMP2=Label(init,textvariable=PRECISIONTEMP).grid(row=8,column=1,sticky=W)

   HUMIDITY1=Label(init,text="Humidity").grid(row=9,column=0,sticky=W)
   HUMIDITY2=Label(init,textvariable=HUMIDITY).grid(row=9,column=1,sticky=W)

   # The next lines are removed because the weight of the crucibles will be recorded in the tblCrucibleXY
   # rather than special crucible chamber. This way the values can be reused
   # if the numbers/crucibles dont change.  Running this function allows the
   # plastic crucibles to be reweighed and recorded.

   ## DIRL=Label(init,text="Directory: ").grid(row=10,column=0,sticky=W,padx=2,pady=2)
   ## DIRE=Entry(init,textvariable=DBDIRECTORY).grid(row=10,column=1,sticky=W,padx=2,pady=2)

   ## DATAF=Label(init,text="Database filename to use:").grid(row=11,column=0,sticky=W)
   ## DATAL=Entry(init,textvariable=DATABASENAME).grid(row=11,column=1, sticky=W)

   INITBUTTON = Button(init, text="Start Initialize", command=go_initialize).grid(row=12, column=2, sticky=W, padx=2, pady=2)
   QUITBUTTON = Button(init, text="Quit", command=quit_init).grid(row=12, column=0, sticky=W, padx=2, pady=2)
   update_windows()

def quit_init():
   root.deiconify()
   init.withdraw()

def go_initialize():
   status="Initialize"
   logger.debug('go_initialize: initialize function running. pre-weigh crucibles')

   logger.debug("XMotor: %i  YMotor: %i" % (xyzRobot.getXMotorPosition(), xyzRobot.getYMotorPosition()))
   logger.debug("Set the current position of motors to zero ... ")
   standardTemp=float(RHTEMP2000TEMP.get())
   standardRH=float(RHTEMP2000HUMIDITY.get())

   ## initially use the 0,0 as the correction to see what we need to adjust to match the MadgeTech 2000
   ## Note these are GLOBAL so that we can read the corrections when running the other stuff
   temp=xyzRobot.getTemperature()
   tempCorrection=standardTemp-temp
   rhCorrection=standardRH-xyzRobot.getHumidity()

   numberOfSamples=int(NUMBEROFSAMPLES.get())
   duration=int(DURATION.get())
   startPosition=int(START_POSITION.get())
   xyzRobot.resetXYValuesToZero()
   setInitials=INITIALS.get()

   timeToCompletion = (duration*numberOfSamples)+numberOfSamples
   end = timedelta(minutes=timeToCompletion)

   now = datetime.today()
   endOfRunTime = now + end
   endOfRun = endOfRunTime.strftime("%m-%d-%y %H:%M:%S")

   print "This run will end ca. ", endOfRun

   logger.debug ("Now going to move and measure each of the crucibles... ")
   logger.debug("xyzRobot.weighAllCrucibles(%s,%d,%d,%d,%d)" % (setInitials,numberOfSamples,LOGINT,duration,startPosition))
   runID = xyzRobot.weighAllCrucibles(setInitials,numberOfSamples,LOGINT,duration,startPosition,tempCorrection,rhCorrection,
      robotStatus,POSITION,MCOUNT,CURRENTSTEP,STATUS,DURATION,LOGGERINTERVAL,RUNID,NUMBEROFSAMPLES,TIMEREMAINING,alert)

   if runID is False:
      logger.error("There has been an error since weighAllCrucibles returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. The arm has returned to Home.", bg='red', fg='ivory', relief=GROOVE)
      communication.sendEmail ("RHX Error","An error has occurred with weighAllCrucibles!")
   RUNID.set(int(runID))

   DataReadWriteNoBalance.updateTempRHCorrection(tempCorrection,rhCorrection,runID)

   logger.debug( "Init: Done!   ")
   #logger.debug("The runID is %i Save this number. ", runID)
   init.withdraw()
   root.update()
   root.deiconify()
   value=DataReadWriteNoBalance.closeDatabase()

   communication.sendEmail ("RHX Status Change","Initialization is complete!")

   return True;

def setup():
   root.withdraw()
   init.deiconify()
   init.wm_title("Setup and Data Entry")
   #Create Menus
   menubar = Menu(init)
   #File Bar
   filemenu = Menu(menubar, tearoff=0)
   filemenu.add_command(label="New", command=restart_program)
   filemenu.add_separator()
   filemenu.add_command(label="Exit", command=KillProgram)
   menubar.add_cascade(label="File", menu=filemenu)
   RHTEMP2000TEMP.set(xyzRobot.getTemperature())
   RHTEMP2000HUMIDITY.set(xyzRobot.getHumidity())
   PRECISIONTEMP.set(xyzRobot.getTemperature())
   #Help Menu
   helpmenu = Menu(menubar, tearoff=0)
   menubar.add_cascade(label="Help", menu=helpmenu)
   #Display the Menus
   START_POSITION.set(1)
   init.config(menu=menubar)
   INITIALSL = Label(init, text="Initials").grid(row=1, column=0, sticky=W)
   INITIALSE = Entry(init, textvariable=INITIALS).grid(row=1, column=1, sticky=W)
   NAMEL = Label(init, text="Name of sample set (e.g., Mississippian ):").grid(row=2, column=0, sticky=W, padx=2,
      pady=2)
   NAMEE = Entry(init, textvariable=NAME).grid(row=2, column=1, sticky=W,padx=2, pady=2)
   Label(init, text="Sample Location (e.g., LMV):").grid(row=3, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=LOCATION).grid(row=3, column=1, sticky=W,padx=2, pady=2)

   NUMSAML = Label(init, text="Number of Samples").grid(row=4, column=0, sticky=W, padx=2, pady=2)
   NUMSAME = Entry(init, textvariable=NUMBEROFSAMPLES).grid(row=4, column=1, sticky=W, padx=2, pady=2)

   STARTPOS2= Label(init, text="Start Position").grid(row=5, column=0, sticky=W)
   STARTPOS2= Entry(init, textvariable=START_POSITION).grid(row=5, column=1, sticky=W)

   TEMPL=Label(init,text="Madge Tech Temperature:").grid(row=6,column=0,sticky=W,padx=2,pady=2)
   TEMPE=Entry(init,textvariable=RHTEMP2000TEMP).grid(row=6,column=1,sticky=W,padx=2,pady=2)
   RHL=Label(init,text="Madge Tech RH:").grid(row=7,column=0,sticky=W,padx=2,pady=2)
   RHE=Entry(init,text=RHTEMP2000HUMIDITY).grid(row=7,column=1,sticky=W,padx=2,pady=2)

   PTEMP1=Label(init,text="Precision Temp").grid(row=8,column=0,sticky=W)
   PTEMP2=Label(init,textvariable=PRECISIONTEMP).grid(row=8,column=1,sticky=W)
   HUMIDITY1=Label(init,text="Humidity").grid(row=9,column=0,sticky=W)
   HUMIDITY2=Label(init,textvariable=HUMIDITY).grid(row=9,column=1,sticky=W)

   DIRL=Label(init,text="Directory: ").grid(row=10,column=0,sticky=W,padx=2,pady=2)
   DIRE=Entry(init,textvariable=DBDIRECTORY).grid(row=10,column=1,sticky=W,padx=2,pady=2)

   DATAF=Label(init,text="Database filename to use:").grid(row=11,column=0,sticky=W)
   DATAL=Entry(init,textvariable=DATABASENAME).grid(row=11,column=1, sticky=W)

   INITBUTTON = Button(init, text="Setup Run", command=go_setup).grid(row=12, column=2, sticky=W, padx=2,
      pady=2)
   QUITBUTTON = Button(init, text="Quit", command=quit_init).grid(row=12, column=0, sticky=W, padx=2, pady=2)
   update_windows()

def go_setup():
   status="Setup"
   logger.debug('go_setup: initialize function running. pre-weigh crucibles')
   dbName=DATABASENAME.get()
   dbDir=DBDIRECTORY.get()

   value=DataReadWriteNoBalance.openDatabase(dbDir,dbName)
   if value is False:
      logger.error("There has been an error since openDatabase returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. Cannot read database", bg='red', fg='ivory', relief=GROOVE)
      alert.update()

   standardTemp=float(RHTEMP2000TEMP.get())
   standardRH=float(RHTEMP2000HUMIDITY.get())

   ## initially use the 0,0 as the correction to see what we need to adjust to match the MadgeTech 2000
   ## Note these are GLOBAL so that we can read the corrections when running the other stuff
   temp=xyzRobot.getTemperature()
   tempCorrection=standardTemp-temp
   rhCorrection=standardRH-xyzRobot.getHumidity()

   numberOfSamples=int(NUMBEROFSAMPLES.get())
   startPosition=int(START_POSITION.get())
   setInitials=INITIALS.get()

   #first create a new run so we have an ID.
   #logger.debug("DataReadWrite.insertRun( %s,%s,%d )" %(initials,today,numberOfSamples))
   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")
   runID=DataReadWriteNoBalance.getLastRunID()
   if runID is False:
      logger.error("There has been an error since getLastRunID returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. Cannot find a run. Must set up measures ahead of time.", bg='red', fg='ivory',
         relief=GROOVE)
      exit(1)
   statustext = "Run ID is %d" % int(runID)
   DataReadWriteNoBalance.updateTempRHCorrection(tempCorrection,rhCorrection,runID)
   logger.debug( statustext)
   RUNID.set(int(runID))
   CURRENTSAMPLE.set(1)
   init.update()

   go_setupPart2()

def go_setupPart2():
   count=CURRENTSAMPLE.get()
   if count>NUMBEROFSAMPLES.get():
      quit_setup()

   runID=int(RUNID.get())
   if (runID<1):
      alert.deiconify()
      alert.title("Alert: No RunID Number!")
      Message(alert,text="You must have a RunID to continue.", bg='red', fg='ivory', relief=GROOVE)
      logger.debug("You must have a RunID entered in order to continue.")
      return False;

   preOrPost=1
   setInitials=str(INITIALS.get())
   startPosition=int(START_POSITION.get())
   setName=str(NAME.get())
   setLocation=str(LOCATION.get())
   numberOfSamples=int(NUMBEROFSAMPLES.get())
   setTemperature=float(PRECISIONTEMP.get())
   setHumidity=float(HUMIDITY.get())
   standardTemp=float(RHTEMP2000TEMP.get())
   standardRH=float(RHTEMP2000HUMIDITY.get())

   temp=xyzRobot.getTemperature()
   tempCorrection=standardTemp-temp
   rhCorrection=standardRH-xyzRobot.getHumidity()
   status="prefire"

   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")
   value=DataReadWriteNoBalance.updateRunPreFire(runID,setInitials,setName,today,setLocation,preOrPost,0,setTemperature,
      setHumidity,status,0,numberOfSamples,0,startPosition)
   if value is False:
      logger.error("There has been an error since updateRunPreFire returned FALSE")
      communication.sendEmail ("RHX Error","An error has occurred with updateRunPreFire!")
      alert.deiconify()
      Message(alert,text="There has been a problem. The arm has returned to Home.", bg='red', fg='ivory', relief=GROOVE)

   setupCrucibles.deiconify()
   setupCrucibles.wm_title("Crucible Entry")

   #Create Menus
   menubar = Menu(setupCrucibles)
   #File Bar
   filemenu = Menu(menubar, tearoff=0)
   filemenu.add_command(label="New", command=restart_program)
   filemenu.add_separator()
   filemenu.add_command(label="Exit", command=KillProgram)
   menubar.add_cascade(label="File", menu=filemenu)
   #Help Menu
   helpmenu = Menu(menubar, tearoff=0)
   menubar.add_cascade(label="Help", menu=helpmenu)
   #Display the Menus
   setupCrucibles.config(menu=menubar)
   crucibleWeight,crucibleStdDev,weightCount = DataReadWriteNoBalance.getEmptyCrucible(count,runID)
   CRUCIBLEWEIGHT.set(crucibleWeight)
   CRUCIBLEWEIGHTSTDDEV.set(crucibleStdDev)

   sherdWeight,sherdStdDev = DataReadWriteNoBalance.getInitialSherd(count,runID)
   INITIALWEIGHT.set(sherdWeight)
   INITIALWEIGHTSTDDEV.set(sherdWeight)

   sherd105Weight,sherd105StdDev,weightCount = DataReadWriteNoBalance.get105Crucible(count,runID)
   SAMPLEWEIGHT.set(sherd105Weight)
   SAMPLEWEIGHTSTDDEV.set(sherd105StdDev)

   sherd550Weight,sherd550StdDev,weightCount = DataReadWriteNoBalance.get550Crucible(count,runID)
   POSTFIREWEIGHT.set(sherd550Weight)
   POSTFIREWEIGHTSTDDEV.set(sherd550StdDev)
   Label(setupCrucibles, text="CHECK THESE VALUES").grid(row=1,column=0,sticky=W)
   Label(setupCrucibles, text="Mean").grid(row=1, column=1, sticky=W)
   Label(setupCrucibles, text="StdDEv").grid(row=1, column=2, sticky=W)
   Label(setupCrucibles, text="Current Sample Number").grid(row=1, column=0, sticky=W)
   Entry(setupCrucibles, textvariable=CURRENTSAMPLE).grid(row=1, column=1, sticky=W)
   ctext="Crucible #"+ str(count)+ " Empty Weight (g)"
   Label(setupCrucibles, text=ctext).grid(row=2, column=0, sticky=W)
   Entry(setupCrucibles, textvariable=CRUCIBLEWEIGHT).grid(row=2, column=1, sticky=W)
   Entry(setupCrucibles, textvariable=CRUCIBLEWEIGHTSTDDEV).grid(row=2, column=2, sticky=W)

   smtext="Sample #"+ str(count)+ " Initial Weight (g) (with Crucible)"
   Label(setupCrucibles, text=smtext).grid(row=3, column=0, sticky=W)
   Entry(setupCrucibles, textvariable=INITIALWEIGHT).grid(row=3, column=1, sticky=W)
   Entry(setupCrucibles, textvariable=INITIALWEIGHTSTDDEV).grid(row=3, column=2, sticky=W)

   smtext="Sample #"+ str(count)+ " 105 Degree Weight (g) (with Crucible)"
   Label(setupCrucibles, text=smtext).grid(row=4, column=0, sticky=W)
   Entry(setupCrucibles, textvariable=SAMPLEWEIGHT).grid(row=4, column=1, sticky=W)
   Entry(setupCrucibles, textvariable=SAMPLEWEIGHTSTDDEV).grid(row=4, column=2, sticky=W)

   sftext="Sample #"+ str(count)+ " Post-Fire Weight (g) (with Crucible)"
   Label(setupCrucibles, text=sftext).grid(row=5, column=0, sticky=W)
   Entry(setupCrucibles, textvariable=POSTFIREWEIGHT).grid(row=5, column=1, sticky=W)
   Entry(setupCrucibles, textvariable=POSTFIREWEIGHTSTDDEV).grid(row=5, column=2, sticky=W)

   Button(setupCrucibles, text="Submit Data for Sample/Crucible", command=updateCrucibleAndSample).grid(row=6, column=0, sticky=W, padx=2, pady=2)
   Button(setupCrucibles, text="End (No more samples)", command=quit_setup).grid(row=6, column=1,sticky=W, padx=2, pady=2)
   update_windows()

def updateCrucibleAndSample():
   setupCrucibles.withdraw()
   runID = RUNID.get()
   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")
   position=CURRENTSAMPLE.get()
   preOrPost=1
   setInitials=str(INITIALS.get())
   startPosition=int(START_POSITION.get())
   setName=str(NAME.get())
   setLocation=str(LOCATION.get())
   numberOfSamples=int(NUMBEROFSAMPLES.get())
   setTemperature=float(PRECISIONTEMP.get())
   setHumidity=float(HUMIDITY.get())
   standardTemp=float(RHTEMP2000TEMP.get())
   standardRH=float(RHTEMP2000HUMIDITY.get())
   initialSherdWeight=float(INITIALWEIGHT.get())
   initialSherdWeightStdDev=float(INITIALWEIGHTSTDDEV.get())

   status="prefire"


   value=DataReadWriteNoBalance.updateCrucible(position,CRUCIBLEWEIGHT.get(),
      CRUCIBLEWEIGHTSTDDEV.get(),RHTEMP2000TEMP.get(),0.0,RHTEMP2000HUMIDITY.get(),
      0.0,today,runID,position)
   if (value==False):
      alertWindow("updateCrucible returned an error.")
      exit(1)
   netSampleWeight=SAMPLEWEIGHT.get()-CRUCIBLEWEIGHT.get()
   netSampleWeightStdDev=SAMPLEWEIGHTSTDDEV.get()
   (meanWeight, stdevWeight) = DataReadWriteNoBalance.getCrucibleWeightStats(runID,position)

   value=DataReadWriteNoBalance.updateSamplePreFire(runID,position,position,netSampleWeight,netSampleWeightStdDev,initialSherdWeight,initialSherdWeightStdDev,RHTEMP2000TEMP.get(),0.0,\
      RHTEMP2000HUMIDITY.get(),0.0)

   if value is False:
      alertWindow("updateSamplePrefire returned an error")
      communication.sendEmail ("RHX Error","An error has occurred with insertNewSample!")
      exit(1)

   netPostFireWeight=POSTFIREWEIGHT.get()-CRUCIBLEWEIGHT.get()
   netPostFireWeightStdDev=POSTFIREWEIGHTSTDDEV.get()
   value=DataReadWriteNoBalance.updateSamplePostFireWeight(runID, position,netPostFireWeight,netPostFireWeightStdDev )
   CURRENTSAMPLE.set(position+1)
   root.update()
   go_setupPart2()


def quit_setup():
   setupCrucibles.withdraw
   logger.debug( "Setup is done ")
   root.update()
   root.deiconify()
   return True;


def backToMainWindowFromMoveArm():
   """
   backToMainWinodwFromMoveArm destroys the moveArm window and brings the root back to focus.
   """
   #moveArm.withdraw()
   root.deiconify()
   return True;



def backToMainWindow():
   """
   backToMainWindow() removes other windows and bring the root window to the focus
   """
   alert.withdraw()
   root.update()
   root.deiconify()
   return True;

def preFire():

   status="Pre-firing"
   root.withdraw()
   prefire.deiconify()
   prefire.wm_title("Pre-Fire")
   setMotorXToZero()
   setMotorYToZero()
   setAbsZeroXY()
   #Create Menus
   menubar = Menu(prefire)
   #File Bar 
   filemenu = Menu(menubar, tearoff=0)
   filemenu.add_command(label="New", command=restart_program)
   filemenu.add_separator()
   filemenu.add_command(label="Exit", command=KillProgram)
   menubar.add_cascade(label="File", menu=filemenu)

   #Help Menu
   helpmenu = Menu(menubar, tearoff=0)
   menubar.add_cascade(label="Help", menu=helpmenu)
   #Display the Menus

   prefire.config(menu=menubar)

   RHTEMP2000TEMP.set(xyzRobot.getTemperature())
   RHTEMP2000HUMIDITY.set(xyzRobot.getHumidity())
   PRECISIONTEMP.set(xyzRobot.getTemperature())

   if FILENAME.get() is not "":
      initials,name,location,numberOfSamples,startPosition,durationOfMeasurements,samplingInterval,repetitions,locationTemperature,locationHumidity=DataReadWrite.getPrefireAttributes(RUNID.get())
      INITIALS.set(initials)
      NAME.set(name)
      LOCATION.set(location)
      NUMBEROFSAMPLES.set(numberOfSamples)
      START_POSITION.set(startPosition)
      DURATION.set(duration)
      INTERVAL.set(interval)
      REPS.set(repetitions)
      TEMP.set(locationTemperature)
      HUMIDITY.set(locationHumidity)
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
   TEMPL= Label(prefire, text="Location Temperature (C)").grid(row=10, column=0, sticky=W, padx=2, pady=2)
   TEMPE = Entry(prefire, textvariable=TEMP).grid(row=10, column=1, sticky=W, padx=2, pady=2)
   HUMIDITYL= Label(prefire, text="Location Relative Humidity").grid(row=11, column=0, sticky=W, padx=2, pady=2)
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
   QUITBUTTON = Button(prefire, text="Quit", command=quit_prefire).grid(row=18, column=0, padx=2, pady=2)
   update_windows()

def quit_prefire():
   root.deiconify()
   prefire.withdraw()

def go_preFire():
   dbName=DATABASENAME.get()
   dbDir=DBDIRECTORY.get()

   value=DataReadWriteNoBalance.openDatabase(dbDir,dbName)
   if value is False:
      logger.error("There has been an error since openDatabase returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. Cannot create database", bg='red', fg='ivory', relief=GROOVE)

   runID=int(RUNID.get())
   if (runID<1):
      alert.deiconify()
      alert.title("Alert: No RunID Number!")
      Message(alert,text="You must have a RunID to continue.", bg='red', fg='ivory', relief=GROOVE)
      logger.debug("You must have a RunID entered in order to continue.")
      return False;
   preOrPost=1
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
   tempCorrection=standardTemp-temp
   rhCorrection=standardRH-xyzRobot.getHumidity()
   status="prefire"

   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")
   value=DataReadWriteNoBalance.updateRunPreFire(runID,setInitials,setName,today,setLocation,preOrPost,intervalsec,setTemperature,setHumidity,status,duration,numberOfSamples,repetitions,startPosition)
   if value is False:
      logger.error("There has been an error since updateRunPreFire returned FALSE")
      communication.sendEmail ("RHX Error","An error has occurred with updateRunPreFire!")
      alert.deiconify()
      Message(alert,text="There has been a problem. The arm has returned to Home.", bg='red', fg='ivory', relief=GROOVE)
   count=1
   repeat=0
   crucibleWeightArray=[]

   timeToCompletion = ((duration*numberOfSamples)+numberOfSamples)*repetitions
   end = timedelta(minutes=timeToCompletion)
   now = datetime.today()
   endOfRunTime = now + end
   endOfRun = endOfRunTime.strftime("%m-%d-%y %H:%M:%S")
   print "This run will end ca. ", endOfRun

   while (count < (numberOfSamples+1)):
      root.update()
      (meanWeight, stdevWeight) = DataReadWriteNoBalance.getCrucibleWeightStats(runID,count)
      # Now do an insert for tblSample for each sample include--- from here on we can then just update the record. 
      sampleID = DataReadWriteNoBalance.insertNewSample(runID,count,setName,now,setLocation,preOrPost,intervalsec,setTemperature,setHumidity,status,duration,repetitions,meanWeight,stdevWeight)
      if sampleID is False:
         alertWindow("insertNewSample returned an error")
         communication.sendEmail ("RHX Error","An error has occurred with insertNewSample!")
         exit(1)
      count += 1

   ## repeat as many times as asked (all of the crucibles)
   while repeat < repetitions:
      CYCLE.set(repeat)
      xyzRobot.weighAllSamplesPreFire(runID,duration,intervalsec,
         numberOfSamples,startPosition,tempCorrection,
         rhCorrection,repeat,
         robotStatus,POSITION,MCOUNT,CURRENTSTEP,
         STATUS,DURATION,LOGGERINTERVAL,RUNID,
         NUMBEROFSAMPLES,TIMEREMAINING,CYCLE,MEAN,STDEV,VARIANCE, alert)
      repeat += 1
      update_windows()

   root.deiconify()
   prefire.withdraw()
   value=DataReadWriteNoBalance.closeDatabase()
   root.update()
   communication.sendEmail ("RHX Status Change","Prefire is complete!")

   return True

def postFire():
   logger.debug("Now running postFire function")
   preOrPost=2
   status ="Post-fired"
   root.withdraw()
   postfire.deiconify()
   postfire.wm_title("Post-Fire")
   setMotorXToZero()
   setMotorYToZero()
   setAbsZeroXY()
   #Create Menus
   menubar = Menu(postfire)

   #File Bar 
   filemenu = Menu(menubar, tearoff=0)
   filemenu.add_command(label="New", command=restart_program)
   filemenu.add_separator()
   filemenu.add_command(label="Exit", command=KillProgram)
   menubar.add_cascade(label="File", menu=filemenu)

   #Help Menu
   helpmenu = Menu(menubar, tearoff=0)
   menubar.add_cascade(label="Help", menu=helpmenu)
   #Display the Menus
   init.config(menu=menubar)

   RHTEMP2000TEMP.set(xyzRobot.getTemperature())
   RHTEMP2000HUMIDITY.set(xyzRobot.getHumidity())
   PRECISIONTEMP.set(xyzRobot.getTemperature())

   if FILENAME.get() is not "":
      numberOfSamples,startPosition,dateOfFiring,timeOfFiring,rateOfHeating,tempOfFiring,durationOfFiring,duration,interval,repetitions,locationTemperature,locationHumidity=DataReadWrite.getPostfireAttributes(RUNID.get())
      INITIALS.set(initials)
      RUNID.set(RUNID.get())
      NUMBEROFSAMPLES.set(numberOfSamples)
      START_POSITION.set(startPosition)
      TEMPOFFIRING.set(tempOfFiring)
      DATEOFFIRING.set(dateOfFiring)
      TIMEOFFIRING.set(timeOfFiring)
      DURATIONOFFIRING.set(durationOfFiring)
      DURATION.set(duration)
      INTERVAL.set(interval)
      REPS.set(repetitions)
      TEMP.set(locationTemperature)
      HUMIDITY.set(locationHumidity)

   INITIALSL = Label(postfire, text="Initials").grid(row=1, column=0, sticky=W)
   INITIALSE = Entry(postfire, textvariable=INITIALS).grid(row=1, column=1, sticky=W)

   RUNIDL = Label(postfire, text="Run ID").grid(row=2, column=0, sticky=W, padx=2, pady=2)
   RUNIDE = Entry(postfire, textvariable=RUNID).grid(row=2, column=1, sticky=W,padx=2, pady=2)
   NUMSAML = Label(postfire, text="Number of Samples").grid(row=3, column=0, sticky=W, padx=2, pady=2)
   NUMSAME = Entry(postfire, textvariable=NUMBEROFSAMPLES).grid(row=3, column=1, sticky=W, padx=2, pady=2)
   STARTPOS= Label(postfire, text="Start Position").grid(row=4, column=0, sticky=W)
   STARTPOS= Entry(postfire, textvariable=START_POSITION).grid(row=4, column=1, sticky=W)

   DATEFIREL = Label(postfire, text="Date of Firing (mm-dd-yyyy):").grid(row=5, column=0, sticky=W, padx=2, pady=2)
   DATEFIREE = Entry(postfire, textvariable=DATEOFFIRING).grid(row=5, column=1, sticky=W,padx=2, pady=2)
   TIMEFIREL = Label(postfire, text="24 Hour start time of Firing (hh:mm:ss) [24 Hours]:").grid(row=6, column=0, sticky=W, padx=2, pady=2)
   TIMEFIREE = Entry(postfire, textvariable=TIMEOFFIRING).grid(row=6, column=1, sticky=W,padx=2, pady=2)
   TEMPFIREL = Label(postfire, text="Temperature of Firing (C)").grid(row=7, column=0, sticky=W, padx=2, pady=2)
   TEMPFIREE = Entry(postfire, textvariable=TEMPOFFIRING).grid(row=7, column=1, sticky=W, padx=2, pady=2)
   RATEOFHL = Label(postfire,text="Rate of Heating (C per minute, e.g., 27):").grid(row=8,column=0, stick=W, padx=2, pady=2)
   RATEOFHE = Entry(postfire, textvariable=RATEOFHEATING).grid(row=8, column=1, sticky=W, padx=2, pady=2)
   DURFIREL= Label(postfire, text="Duration of Firing (min) (e.g., 360").grid(row=9, column=0, sticky=W, padx=2, pady=2)
   DURFIREE = Entry(postfire, textvariable= DURATIONOFFIRING).grid(row=9, column=1, sticky=W, padx=2, pady=2)
   DURATIONL= Label(postfire, text="Duration of Measurements (min)").grid(row=10, column=0, sticky=W, padx=2, pady=2)
   DURATIONE = Entry(postfire, textvariable=DURATION).grid(row=10, column=1, sticky=W, padx=2, pady=2)
   INTERVALL= Label(postfire, text="Sampling interval (seconds):").grid(row=11, column=0, sticky=W, padx=2, pady=2)
   INTERVALE = Entry(postfire, textvariable=INTERVAL).grid(row=11, column=1, sticky=W, padx=2, pady=2)
   REPSL= Label(postfire, text="Repetitions:").grid(row=12, column=0, sticky=W, padx=2, pady=2)
   REPSE = Entry(postfire, textvariable=REPS).grid(row=12, column=1, sticky=W, padx=2, pady=2)
   TEMPL= Label(postfire, text="Temperature (C) (at location):").grid(row=13, column=0, sticky=W, padx=2, pady=2)
   TEMPE = Entry(postfire, textvariable=TEMP).grid(row=13, column=1, sticky=W, padx=2, pady=2)
   HUMIDITYL= Label(postfire, text="Relative Humidity (set rh):").grid(row=14, column=0, sticky=W, padx=2, pady=2)
   HUMIDITYE = Entry(postfire, textvariable=HUMIDITY).grid(row=14, column=1, sticky=W, padx=2, pady=2)
   TEMPL=Label(postfire,text="Madge Tech Temperature (current value):").grid(row=15,column=0,sticky=W,padx=2,pady=2)
   TEMPE=Entry(postfire,textvariable=RHTEMP2000TEMP).grid(row=15,column=1,sticky=W,padx=2,pady=2)
   RHL=Label(postfire,text="Madge Tech RH (current value):").grid(row=16,column=0,sticky=W,padx=2,pady=2)
   RHE=Entry(postfire,text=RHTEMP2000HUMIDITY).grid(row=16,column=1,sticky=W,padx=2,pady=2)

   PTEMP1=Label(init,text="Precision Temp").grid(row=17,column=0,sticky=W)
   PTEMP2=Label(init,textvariable=PRECISIONTEMP).grid(row=17,column=1,sticky=W)
   HUMIDITY1=Label(init,text="Humidity").grid(row=18,column=0,sticky=W)
   HUMIDITY2=Label(init,textvariable=HUMIDITY).grid(row=18,column=1,sticky=W)

   DIRL=Label(postfire,text="Directory: ").grid(row=19,column=0,sticky=W,padx=2,pady=2)
   DIRE=Entry(postfire,textvariable=DBDIRECTORY).grid(row=19,column=1,sticky=W,padx=2,pady=2)

   DATAF=Label(postfire,text="Database filename to use:").grid(row=20,column=0,sticky=W)
   DATAL=Entry(postfire,textvariable=DATABASENAME).grid(row=20,column=1, sticky=W)

   INITBUTTON = Button(postfire, text="Start Post Fire", command=go_postFire).grid(row=21, column=2, padx=2, pady=2)
   QUITBUTTON = Button(postfire, text="Quit", command=quit_prefire).grid(row=21, column=0, padx=0, pady=2)
   update_windows()

def quit_postfire():
   root.deiconfiy()
   postfire.withdraw()

def go_postFire():
   dbName=DATABASENAME.get()
   dbDir=DBDIRECTORY.get()

   value=DataReadWriteNoBalance.openDatabase(dbDir,dbName)
   if (value == False):
      logger.error("There has been an error since openDatabase returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. Cannot create database", bg='red', fg='ivory', relief=GROOVE)

   runID=int(RUNID.get())
   if (runID<1):
      alert.deiconify()
      alert.title("Alert: No RunID Number!")
      Message(alert,text="You must have a RunID to continue.", bg='red', fg='ivory', relief=GROOVE)
      logger.debug("You must have a RunID entered in order to continue.")
      return False;

   runID=int(RUNID.get())
   if (runID<1):
      alert.deiconify()
      alert.title("Alert: No RunID Number!")
      Message(alert,text="You must have a RunID to continue.", bg='red', fg='ivory', relief=GROOVE)
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
   tempCorrection=standardTemp-temp
   rhCorrection=standardRH-xyzRobot.getHumidity()
   temperatureOfFiring=int(TEMPOFFIRING.get())
   durationOfFiring=int(DURATIONOFFIRING.get())
   preOrPost=2
   status="postfire"
   numberOfSamples=NUMBEROFSAMPLES.get()
   description=""


   startPosition=START_POSITION.get()
   startdate=DATEOFFIRING.get()
   starttime=TIMEOFFIRING.get()
   sdate=startdate.split("-",3)
   stime=starttime.split(":",3)
   startOfFiring = datetime(int(sdate[2]), int(sdate[0]), int(sdate[1]), int(stime[0]), int(stime[1]), int(stime[2]))
   rateOfHeating=int(RATEOFHEATING.get())
   timeToHeat=temperatureOfFiring/rateOfHeating
   durationOfFiring += timeToHeat
   end = timedelta(minutes=durationOfFiring)
   endOfFiring = startOfFiring + end
   now = datetime.today()

   # minutes since firing ended
   diffTime = now - endOfFiring

   d_endOfFiring = endOfFiring.strftime("%m-%d-%y %H:%M:%S")
   intervalsec=int(INTERVAL.get())
   postMeasurementTimeInterval=int(DURATION.get())
   repetitions=int(REPS.get())
   logger.debug("updateRunPostFire( %d,%s,%s,%d,%d,%d,%d,%d,%s,%d,%d )" %
                (runID,setInitials,status,
                 durationOfFiring,temperatureOfFiring,postMeasurementTimeInterval,
                 duration,repetitions,d_endOfFiring,startPosition,intervalsec))

   value=DataReadWriteNoBalance.updateRunPostFire(runID,setInitials,status,startOfFiring,
      durationOfFiring,temperatureOfFiring,postMeasurementTimeInterval,
      duration,repetitions,endOfFiring,startPosition,intervalsec)

   if value is False:
      logger.error("There has been an error since updateRunPostFire returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. The arm has returned to Home.", bg='red', fg='ivory', relief=GROOVE)
      communication.sendEmail ("RHX Error","An error has occurred with updateRunPostFire!")
   timeToCompletion = ((duration*numberOfSamples)+numberOfSamples)*repetitions
   end = timedelta(minutes=timeToCompletion)
   now = datetime.today()
   endOfRunTime = now + end
   endOfRun = endOfRunTime.strftime("%m-%d-%y %H:%M:%S")
   print "This run will end ca. ", endOfRun

   count=0
   repeat=1
   CYCLE.set(repeat)
   while repeat < (repetitions+1):
      root.update()
      CYCLE.set(repeat)
      xyzRobot.weighAllSamplesPostFire(runID,duration,
         intervalsec,numberOfSamples,startPosition,
         endOfFiring,tempCorrection,rhCorrection,repeat,
         robotStatus,POSITION,MCOUNT,
         CURRENTSTEP,STATUS,DURATION,
         LOGGERINTERVAL,RUNID,NUMBEROFSAMPLES,
         TIMEREMAINING,TIMEELAPSEDMIN,REPS,CYCLE,alert)
      repeat += 1
      update_windows()
   root.update()
   root.deiconify()
   postfire.withdraw()
   value=DataReadWriteNoBalance.closeDatabase()
   communication.sendEmail ("RHX Status Change","Postfire is complete!")
   update_windows()
   return True;

def moveMotorX():
   logger.debug("moveMotorX to %i", int(M0EE1.get()))
   MV.set(0)
   MB1V1.set("0")
   xyzRobot.M0Mover(int(M0EE1.get()))
   update_windows()
   return True;

def moveMotorY():
   logger.debug("moveMotorY to %i",int(M2EE1.get()))
   MV.set(2)
   MB1V1.set("2")
   xyzRobot.M2Mover(int(M2EE1.get()))
   update_windows()
   return True;

def moveMotor(motorNumber):
   logger.debug("moveMotor: %i",int(motorNumber))
   if motorNumber==0:
      MV.set(0)
      MB1V1.set("0")
      logger.debug("moveMotor: %i to %i", int(motorNumber), int(M0EE1.get()))
      xyzRobot.M0Mover(int(M0EE1.get()))
   elif motorNumber==1:
      MV.set(1)
      MB1V1.set("1")
      logger.debug("moveMotor: %i to %i", int(motorNumber), int(M1EE1.get()))
      xyzRobot.M1Mover(int(M1EE1.get()))
   elif motorNumber==2:
      MV.set(2)
      MB1V1.set("2")
      logger.debug("moveMotor: %i to %i",int(motorNumber), int(M2EE1.get()))
      xyzRobot.M2Mover(int(M2EE1.get()))
   else:
      logger.critical("Error - no such motor number: %d",int(motorNumber))
   update_windows()
   return True;

def setMotorXToZero():
   logger.debug("setMotorXToZero")
   MB2V1.set("0")
   xyzRobot.M0SetP()
   M0EE1.set("0")
   update_windows()
   return True;

def setMotorYToZero():
   logger.debug("setMotorYToZero")
   MB2V1.set("2")
   xyzRobot.M2SetP()
   M2EE1.set("0")
   update_windows()
   return True;

def setMotorsToZero(motorNumber):
   logger.debug("setMotorsToZero: %d",motorNumber)
   if motorNumber==0:
      MB2V1.set("0")
      xyzRobot.M0SetP()
      M0EE1.set("0")
   elif motorNumber==1:
      MB2V1.set("1")
      xyzRobot.M1SetP()
      M1EE1.set("0")
   elif motorNumber==2:
      MB2V1.set("2")
      xyzRobot.M2SetP()
      M2EE1.set("0")
   else:
      logger.critical( "Error - no such motor number: %d ",motorNumber )
   update_windows()
   return True;

def MotorPosition(motorNumber):
   logger.debug("MotorPosition:  %d",int(MB2V1.get()))
   xyzRobot.MotorPosition(int(MB2V1.get()))
   update_windows()
   return True;

def moveArmToPosition():
   logger.debug("moveArmToPosition: %d",int(AV.get()))
   xyzRobot.moveArmToPosition(int(AV.get()))
   update_windows()
   return True;

def bumpXMotorUp():
   logger.debug("bumpXMotorUp: %d",int(MOTORSTEP.get()))
   xyzRobot.bumpXMotorUp(int(MOTORSTEP.get()))
   update_windows()

def bumpYMotorRight():
   logger.debug("bumpYMotorRight: %d",int(MOTORSTEP.get()))
   xyzRobot.bumpYMotorRight(int(MOTORSTEP.get()))
   update_windows()

def bumpYMotorLeft():
   logger.debug("bumpYMotorLeft: %d",int(MOTORSTEP.get()))
   xyzRobot.bumpYMotorLeft(int(MOTORSTEP.get()))
   update_windows()

def bumpXMotorDown():
   logger.debug("bumpXMotorDown: %d",int(MOTORSTEP.get()))
   xyzRobot.bumpXMotorDown(int(MOTORSTEP.get()))
   update_windows()

def bumpMotorNE():
   logger.debug("bumpMotorNE")
   logger.debug("bumpXMotorUp: %d",int(MOTORSTEP.get()))
   xyzRobot.bumpXMotorUp(int(MOTORSTEP.get()))
   logger.debug("bumpYMotorLeft: %d",int(MOTORSTEP.get()))
   xyzRobot.bumpYMotorLeft(int(MOTORSTEP.get()))
   update_windows()

def bumpMotorNW():
   logger.debug("bumpMotorNW")
   logger.debug("bumpXMotorUp: %d",int(MOTORSTEP.get()))
   xyzRobot.bumpXMotorUp(int(MOTORSTEP.get()))
   #update_windows()
   logger.debug("bumpYMotorRight: %d",int(MOTORSTEP.get()))
   xyzRobot.bumpYMotorRight(int(MOTORSTEP.get()))
   update_windows()

def bumpMotorSE():
   logger.debug("bumpMotorSE")
   logger.debug("bumpXMotorDown: %d",int(MOTORSTEP.get()))
   xyzRobot.bumpXMotorDown(int(MOTORSTEP.get()))
   #update_windows()
   logger.debug("bumpYMotorRight: %s",int(MOTORSTEP.get()))
   xyzRobot.bumpYMotorRight(int(MOTORSTEP.get()))
   update_windows()

def bumpMotorSW():
   logger.debug("bumpMotorSW")
   logger.debug("bumpXMotorMotor: %s",int(MOTORSTEP.get()))
   xyzRobot.bumpXMotorDown(int(MOTORSTEP.get()))
   #update_windows()
   logger.debug("bumpYMotorLeft: %s",int(MOTORSTEP.get()))
   xyzRobot.bumpYMotorLeft(int(MOTORSTEP.get()))
   update_windows()

def goHome():
   logger.debug("goHome: Go to Home Position")
   xyzRobot.goHome()
   update_windows()

def openGripper():
   logger.debug("openGripper: Open gripper")
   xyzRobot.openGripper()
   update_windows()

def closeGripper():
   logger.debug("closeGripper: Close gripper")
   xyzRobot.closeGripper()
   update_windows()

def BZero():
   logger.debug("BZero: Zero the balance")
   DataReadWriteNoBalance.BZero()
   update_windows()

def openBalanceDoor():
   logger.debug("openBalanceDoor: Open the balance door")
   DataReadWriteNoBalance.openBalanceDoor()
   update_windows()

def closeBalanceDoor():
   logger.debug("closeBalanceDoor:  Close the balance door")
   xpos = xyzRobot.getXMotorPosition()
   if xpos > -2800:
      DataReadWriteNoBalance.closeBalanceDoor()
   else:
      logger.warn("Cannot close door. Arm is inside balance.")
      #update_windows()
   update_windows()

def goToPosition():
   pos=POSITION.get()
   logger.debug("goToPosition:  Go to position: %i",int(pos))
   xyzRobot.goToSamplePosition(int(pos),startWindow=1)
   update_windows()

def refine():
   pos=POSITION.get()
   if pos<26:
      logger.debug("refine sample position: %i",int(pos))
      xyzRobot.refineSamplePosition(pos)
   elif pos==27:
      logger.debug("refine inside balance position: %i",int(pos))
      xyzRobot.refineInsideBalancePosition()
   else:
      pass
   update_windows()

def goToBalance():
   POSITION.set(26)
   logger.debug("goToBalance:  Go to point outside of balance")
   xyzRobot.goToOutsideBalanceFromOutside()
   #make sure balance door is open
   openBalanceDoor()
   #update_windows()
   logger.debug("Go to inside of balance")
   POSITION.set(27)
   xyzRobot.goToInsideBalanceFromOutside()
   update_windows()

def getSampleFromBalance():
   logger.debug("getSampleFromBalance: %d",SAMPLENUM.get())
   sampleNum=SAMPLENUM.get()
   if (sampleNum<1):
      alert.title("Alert: No Sample #!")
      Message(alert,text="You must enter a sample number to continue.", bg='red', fg='ivory', relief=GROOVE)
      logger.warning("You must have a sample number in order to continue.")
      return False;
   else:
      xyzRobot.goToOutsideBalanceFromOutside()
      openBalanceDoor()
      val=xyzRobot.goToInsideBalanceFromOutside()
      val=xyzRobot.pickUpSampleFromBalance()
      val=xyzRobot.goToOutsideBalanceFromInside()
      closeBalanceDoor()
      val=xyzRobot.goToSamplePosition(sampleNum, startWindow=1)
      val=xyzRobot.samplePutDown()
      val=xyzRobot.goHome()
      update_windows()
      return True;

def alertWindow(message):
   title = "RHX ERROR!"
   communication.sendEmail(title,message)
   while 1:
      easygui.msgbox(message, title, ok_button="Exit")     # show a Continue/Cancel dialog
   return

def fileDialog():
   dirname=tkFileDialog.askdirectory(parent=root,initialdir="/Users/Archy/Dropbox/Rehydroxylation/",title="Pick a directory ...")
   update_windows()
   return True;

def findHome():
   logger.debug("first find zero on the X axis")
   xyzRobot.moveXUntilZero()
   logger.debug("first find zero on the Y axis")
   xyzRobot.moveYUntilZero()
   logger.debug("Now reset motors to Zero")
   xyzRobot.setAbsZeroXY()
   xyzRobot.resetXYValuesToZero()
   update_windows()
   return True;

def setAbsZeroXY():
   value=xyzRobot.setAbsZeroXY()
   update_windows()
   return True;

def setXYForSampleLocation():
   sampleLocation=POSITION.get()
   x=int(xyzRobot.getXPosition())
   y=int(xyzRobot.getYPosition())

   value = DataReadWriteNoBalance.updateXYForSampleLocation(sampleLocation,x,y)

   xD,yD=xyzRobot.getCurrentXYCoordinates()
   value=DataReadWriteNoBalance.updateXYCoordinatesForPosition(sampleLocation,xD,yD)
   update_windows()
   return value

def setZForSampleLocation():
   sampleZPosition=AV.get()
   sampleLocation=POSITION.get()
   value = DataReadWriteNoBalance.updateZForSampleLocation(sampleLocation,sampleZPosition)
   update_windows()
   return value

def setZForBalanceLocation():
   balanceZPosition=AV.get()
   value = DataReadWriteNoBalance.updateZForBalanceLocation(balanceZPosition)
   update_windows()
   return value

def setXYForAllLocations():
   sampleLocation=POSITION.get()
   originalX=0
   originalY=0
   (originalX, originalY) = DataReadWriteNoBalance.getXYForSampleLocation(sampleLocation)
   x=int(xyzRobot.getXPosition())
   y=int(xyzRobot.getYPosition())
   diffX=originalX - x
   diffY=originalY - y
   pos=sampleLocation
   value = DataReadWriteNoBalance.updateXYForSampleLocation(sampleLocation,x,y)
   while pos < 26:
      (originalX, originalY) = DataReadWriteNoBalance.getXYForSampleLocation(pos)
      newX=originalX - diffX
      newY=originalY - diffY
      value = DataReadWriteNoBalance.updateXYForSampleLocation(pos,newX,newY)
      pos +=1
   update_windows()
   return value

def setXYForBalance(point):
   originalX=0
   originalY=0
   (originalX, originalY) = DataReadWriteNoBalance.getXYForBalance(point)
   x=int(xyzRobot.getXPosition())
   y=int(xyzRobot.getYPosition())
   print("motor locations for %s are X: %d and Y: %d", point,x,y)
   logger.debug("motor locations for %s are X: %d and Y: %d", point,x,y)
   value = DataReadWriteNoBalance.updateXYForBalance(point,x,y)
   xC, yC = xyzRobot.getCurrentXYCoordinates()
   logger.debug("Coordinates for %s are X: %d and Y: %d ",point, xC, yC)
   print("Coordinates for %s are X: %d and Y: %d ",point, xC, yC)
   DataReadWriteNoBalance.updateXYCoordinatesForBalance(point,xC,yC)
   logger.debug("Coordinates Updated!")
   update_windows()
   return value

def moveToNextSampleLocation():
   sampleLocation=int(POSITION.get())
   ##print("Now at position %d" % (sampleLocation))

   sampleLocation += 1

   POSITION.set(sampleLocation)
   value=0
   if sampleLocation>25:
      sampleLocation=1
   ##print("Moving to position %d" % (sampleLocation))
   POSITION.set(sampleLocation)
   goToPosition()
   update_windows()
   return True;

def goToOutsideBalance():
   xyzRobot.goToOutsideBalanceFromOutside()
   update_windows()
   return True

def goToInsideBalance():
   xyzRobot.goToOutsideBalanceFromOutside()
   POSITION.set(26)
   update_windows()
   xyzRobot.goToInsideBalanceFromOutside()
   update_windows()
   POSITION.set(27)
   return True

def setOutsideBalance():
   setXYForBalance("outside")
   update_windows()
   return True

def setInsideBalance():
   setXYForBalance("inside")
   update_windows()
   return True

def checkEachSamplePosition():
   print "Ill only check the first 5 sample locations"
   sampleLocation=1
   print "First, go home."
   value=xyzRobot.goHome()
   print "make sure gripper is open..."
   value=xyzRobot.openGripper()
   while sampleLocation < 6:
      print "Going to location: ", sampleLocation
      value=xyzRobot.goToSamplePosition(sampleLocation,startWindow=1)
      print "Lower arm to sample"
      value=xyzRobot.lowerArmToSample()
      print "Close gripper"
      value=xyzRobot.closeGripper()
      print "Open gripper"
      value=xyzRobot.openGripper()
      print "Raise arm to top"
      value=xyzRobot.raiseArmToTop()
      print "Next..."
      sampleLocation += 1
   print "Now go home"
   value=xyzRobot.goHome()
   print "Done."
   update_windows()

def visitEachSampleLocation():
   """
   visitEachSampleLocation() function will move the robot arm to each location one at a time. It'll pause at each location and ask whether
   the location is good.  Then it will allow one to "bump" the location one direction or another. One can then "save" the
   new location. This will require switching the locations of the crucibles to the XY database.
   """
   sampleLocation=0
   if sampleLocation>0:
      value=xyzRobot.goToSamplePosition(sampleLocation,   startWindow=1      )
      if value is False:
         alert.title("Alert: problem going to position 1")
         Message(alert,text="There was a problem going to position 1.", bg='red', fg='ivory', relief=GROOVE)
   moveArm.deiconify()
   POSITION.set(sampleLocation)
   BumpUp = Button(moveArm, text="+X Axis", command=bumpXMotorUp)
   BumpLeft = Button(moveArm,text="-Y Axis", command=bumpYMotorLeft)
   BumpRight = Button(moveArm,text="+Y Axis", command=bumpYMotorRight)
   BumpDown = Button(moveArm,text="-X Axis", command=bumpXMotorDown)
   BumpNE = Button(moveArm, text="NE", command=bumpMotorNE).grid(row=1, column=0,sticky=E)
   BumpNW = Button(moveArm, text="NW", command=bumpMotorNW).grid(row=1, column=2,sticky=W)

   CurrentPosition = Label(moveArm,textvariable=POSITION).grid(row=2,column=1)
   BumpSE = Button(moveArm, text="SE", command=bumpMotorSE).grid(row=3, column=2,sticky=W)
   BumpSW = Button(moveArm, text="SW", command=bumpMotorSW).grid(row=3, column=0,sticky=E)
   BumpUp.grid(row=1, column=1)
   BumpLeft.grid(row=2, column=0, sticky=E)
   BumpRight.grid(row=2, column=2, sticky=W)
   BumpDown.grid (row=3, column=1)

   BumpSizeL=Label(moveArm,text="Step Size").grid(row=4,column=0,sticky=W)
   BumpSizeE=Entry(moveArm,textvariable=MOTORSTEP).grid(row=4,column=1,sticky=W)
   SETXYB=Button(moveArm,text="Set XY for this position",command=setXYForSampleLocation).grid(row=5,column=0)
   SETXYB=Button(moveArm,text="Update all XYs based on this position",command=setXYForAllLocations).grid(row=5,column=1)
   NEXTSAMPLEB=Button(moveArm,text="Next position", command=moveToNextSampleLocation).grid(row=5,column=2)
   BALANCE_OUT_GO=Button(moveArm,text="Go to Outside Balance Point", command=goToOutsideBalance).grid(row=6,column=0)
   BALANCE_OUT_SET=Button(moveArm,text="Set Outside Balance Point",command=setOutsideBalance).grid(row=6,column=1)
   BALANCE_IN_GO=Button(moveArm,text="Go to Inside Balance Point", command=goToInsideBalance).grid(row=7,column=0)
   BALANCE_IN_SET=Button(moveArm,text="Set Inside Balance Point",command=setInsideBalance).grid(row=7,column=1)

   QUITB=Button(moveArm,text="Cancel",command=backToMainWindowFromMoveArm).grid(row=8,column=2)
   update_windows()
   moveArm.update()

def lasersOn():
   output = xyzRobot.turnLasersOn()
   update_windows()
   return output

def lasersOff():
   output = xyzRobot.turnLasersOff()
   update_windows()
   return output

def reloadFile():
   file = tkFileDialog.askopenfilename(filetypes=[('sqlite files', '.sqlite')],
      initialdir='\\Users\\Clipo\\Dropbox\\Rehydroxylation\\', parent=root,
      title='Choose a Sqlite database file')
   value=DataReadWriteNoBalance.reopenDatabase(file)
   runID=DataReadWriteNoBalance.getLastRunID()
   RUNID.set(runID)
   update_windows()
   return value

def refinePosition():
   position=POSITION.get()
   xyzRobot.refinePosition(position)
   update_windows()
   return

def loadRun():
   RUNID.set(SETRUNID.get())
   update_windows()
   return True

def setXMaxVelocity():
   maxvelocity=MAXXMOTORVELOCITY.get()
   xyzRobot.setXMotorVelocityLimit(maxvelocity)
   #MAXXMOTORVELOCITY.set(xyzRobot.getXMotorVelocityLimit())
   update_windows()
   return

def setYMaxVelocity():
   maxvelocity=MAXYMOTORVELOCITY.get()
   xyzRobot.setYMotorVelocityLimit(maxvelocity)
   #MAXYMOTORVELOCITY.get(xyzRobot.getYMotorVelocityLimit())
   update_windows()
   return

def moveUntilXZero():
   xyzRobot.moveXUntilZero()
   update_windows()
   return

def moveUntilYZero():
   xyzRobot.moveYUntilZero()
   update_windows()
   return

###############################################################
###GUI Program#################################################


update_windows()
#Create Menus
menubar = Menu(root)
#File Bar 
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=restart_program)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=KillProgram)
menubar.add_cascade(label="File", menu=filemenu)

#Help Menu
helpmenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=helpmenu)
#Display the Menus
root.config(menu=menubar)

## always use Run #1 unless otherwise stated..
if RUNID.get() is None:
   RUNID.set(1)

##Motor 0 Controls  
M0L1 = Label(root, text="X-Axis")
M0L1.grid(row=0, column=0, sticky=W)
M0E1 = Entry(root, textvariable=M0EE1)
M0E1.grid(row=1, column=0, sticky=W)
M0B1 = Button(root, text="Move X", command=moveMotorX)
M0B1.grid(row=1, column=1, padx=2, pady=2)
M0B2 = Button(root, text="Set Current Position of X to 0", command=setMotorXToZero)
M0B2.grid(row=1, column=2, padx=2, pady=2)

##Motor 2 Controls
M1L1 = Label(root, text="Y-Axis")
M1L1.grid(row=2, column=0, sticky=W)
M1E1 = Entry(root, textvariable=M2EE1)
M1E1.grid(row=3, column=0, sticky=W)
M1B1 = Button(root, text="Move Y", command=moveMotorY)
M1B1.grid(row=3, column=1, padx=2, pady=2)
M1B2 = Button(root, text="Set Current Position  of Y to 0", command=setMotorYToZero).grid(row=3, column=2, padx=2, pady=2)

BumpUp = Button(root, text="+X Axis", command=bumpXMotorUp)
BumpLeft = Button(root,text="-Y Axis", command=bumpYMotorLeft)
BumpRight = Button(root,text="+Y Axis", command=bumpYMotorRight)
BumpDown = Button(root,text="-X Axis", command=bumpXMotorDown)
BumpNE = Button(root, text="NE", command=bumpMotorNE).grid(row=4, column=0,sticky=E)
BumpNW = Button(root, text="NW", command=bumpMotorNW).grid(row=4, column=2,sticky=W)
BumpSE = Button(root, text="SE", command=bumpMotorSE).grid(row=6, column=2,sticky=W)
BumpSW = Button(root, text="SW", command=bumpMotorSW).grid(row=6, column=0,sticky=E)

BumpUp.grid(row=4, column=1)
BumpLeft.grid(row=5, column=0, sticky=E)
BumpRight.grid(row=5, column=2, sticky=W)
BumpDown.grid (row=6, column=1)

##Arm Controller
ACL1 = Label(root, text="Arm Controller (Z Axis)")
ACL1.grid(row=7, column=0, sticky=W)

STEP=Label(root,text="Motor Step").grid(row=7,column=1,sticky=W)
STEP1=Entry(root,textvariable=MOTORSTEP).grid(row=7,column=2,sticky=W)
ACB1 = Button(root, text="Lower to Sample", command=xyzRobot.lowerArmToSample)
ACB1.grid(row=8, column=0, sticky=W, padx=2, pady=2)
ACB2 = Button(root, text="Raise to Top Position", command=xyzRobot.raiseArmToTop)
ACB2.grid(row=8, column=1, sticky=W, padx=2, pady=2)

ACB3 = Button(root, text="Lower to Balance", command=xyzRobot.lowerArmToBalance)
ACB3.grid(row=8, column=2, sticky=W, padx=2, pady=2)

##Arm Controls  
AML1 = Label(root, text="Arm Controller (Z-Axis)")
AML1.grid(row=9, column=0, sticky=W)
AME1 = Entry(root, textvariable=AV)
AME1.grid(row=9, column=1, sticky=W)
AMB1=Button(root, text="Move", command=moveArmToPosition)
AMB1.grid(row=9, column=2, sticky=W)

TEMPL=Label(root, text="Temp (C)").grid(row=15,column=0,sticky=W)
TEMP2=Label(root, textvariable=TEMPERATURE).grid(row=15,column=1,sticky=W)
HUMIDL=Label(root, text="Humidity (%rh)").grid(row=15,column=2,sticky=W)
HUMID2=Label(root, textvariable=HUMIDITY).grid(row=15,column=3,sticky=W)

PRETEMPL=Label(root, text="Precision Temp C").grid(row=16,column=0,sticky=W)
PRETEMPE=Label(root,textvariable=PRECISIONTEMP).grid(row=16,column=1,sticky=W)

STARTPOS= Label(root, text="Start Position").grid(row=17, column=0, sticky=W)
STARTPOS= Entry(root, textvariable=START_POSITION).grid(row=17, column=1, sticky=W)

GOPOS= Label(root, text="Go To Sample Position").grid(row=18, column=0, sticky=W)
GOPOS1= Entry(root, textvariable=POSITION).grid(row=18, column=1, sticky=W)
GOPOS2=Button(root, text="GO", command=goToPosition).grid(row=18, column=2, sticky=W)
Button(root,text="Refine Position",command=refine).grid(row=18,column=3,sticky=W)

GETSAMP1=Label(root,text="Retrieve Sample from Balance").grid(row=19,column=0,sticky=W)
GETSAMP2=Entry(root,textvariable=SAMPLENUM).grid(row=19,column=1,sticky=W)
GETSAMP3=Button(root,text="GO",command=getSampleFromBalance).grid(row=19,column=2,sticky=W)

SETABSZEROXY=Button(root,text="Set Home Here (Abs X and Y to 0,0)",command=setAbsZeroXY).grid(row=20,column=1)

ABSOLX1=Label(root, text="X Position (encoder)").grid(row=21,column=0,sticky=W)
ABSOLX2=Label(root, textvariable=ABSOLUTEXPOSITION).grid(row=21,column=1,sticky=W)
ABSOLY1=Label(root, text="Y Position (encoder)").grid(row=21,column=2,sticky=W)
ABSOLY2=Label(root, textvariable=ABSOLUTEYPOSITION).grid(row=21,column=3,sticky=W)

Label(root, text="X Zero?").grid(row=22,column=0,sticky=W)
Label(root, textvariable=XZERO).grid(row=22,column=1,sticky=W)
Label(root, text="Y Zero ?").grid(row=22,column=2,sticky=W)
Label(root, textvariable=YZERO).grid(row=22,column=3,sticky=W)

BZL4=Label(root, text="X Motor").grid(row=23,column=0,sticky=W)
BZL5=Label(root, textvariable=XMOTORPOSITION).grid(row=23,column=1,sticky=W)

BZL6=Label(root, text="Y Motor").grid(row=23,column=2,sticky=W)
BZL7=Label(root, textvariable=YMOTORPOSITION).grid(row=23,column=3,sticky=W)

M1B3 = Button(root, text="Release Gripper", command=openGripper).grid(row=24, column=0, padx=2, pady=2)
M1B4 = Button(root, text="Engage Gripper", command=closeGripper).grid(row=24, column=1, padx=2, pady=2)

Button(root, text="Lasers On", command=lasersOn).grid(row=25, column=0, padx=2, pady=2)
Button(root, text="Lasers Off", command=lasersOff).grid(row=25, column=1, padx=2, pady=2)

Label(root, text="X Motor Velocity Max").grid(row=26, column=0, padx=2,pady=2)
Entry(root, textvariable=MAXXMOTORVELOCITY).grid(row=26,column=1,padx=2,pady=2)
Button(root,text="Set X Motor Max Velocity",command=setXMaxVelocity).grid(row=26,column=2,padx=2,pady=2)

Label(root, text="Y Motor Velocity Max").grid(row=27, column=0, padx=2,pady=2)
Entry(root, textvariable=MAXYMOTORVELOCITY).grid(row=27,column=1,padx=2,pady=2)
Button(root,text="Set Y Motor Max Velocity",command=setYMaxVelocity).grid(row=27,column=2,padx=2,pady=2)

BALANCE1=Button(root,text="Go Directly to Balance", command=goToBalance).grid(row=28,column=0,padx=2,pady=2)
M1B5 = Button(root, text="Update Values", command=update_windows).grid(row=28,column=2,padx=2,pady=2)
M1B6 = Button(root,text="Go Home", command=goHome).grid(row=28,column=1,padx=2,pady=2)

M1B7 = Button(root,text="Find Home Position", command=findHome).grid(row=29,column=0,padx=2,pady=2)
M1B8 = Button(root, text="Move to each sample location (1-25)", command=visitEachSampleLocation).grid(row=29,column=1,padx=2,pady=2)
Button(root,text="Check Each Sample Position (5)",command=checkEachSamplePosition).grid(row=29,column=2,padx=2,pady=2)
Button(root,text="Move X until zero",command=moveUntilXZero).grid(row=30,column=0,padx=2,pady=2)
Button(root,text="Move Y until zero",command=moveUntilYZero).grid(row=30,column=1,padx=2,pady=2)

Button(root,text="Set XY for this position",command=setXYForSampleLocation).grid(row=30,column=2)

Button(root,text="Go to Outside Balance Point", command=goToOutsideBalance).grid(row=31,column=0)
Button(root,text="Set Outside Balance Point",command=setOutsideBalance).grid(row=31,column=1)
Button(root,text="Set Z for Sample Position",command=setZForSampleLocation).grid(row=31,column=2)

Button(root,text="Go to Inside Balance Point", command=goToInsideBalance).grid(row=32,column=0)
Button(root,text="Set Inside Balance Point",command=setInsideBalance).grid(row=32,column=1)
Button(root,text="Set Z for Balance Position",command=setZForBalanceLocation).grid(row=32,column=2)


Label(root,text="Run Number", textvariable=SETRUNID).grid(row=33,column=0)
Button(root,text="Load Run", command=loadRun).grid(row=33,column=1)
Button(root,text="Load Sqlite File", command=reloadFile).grid(row=33,column=2)
Button(root,text="Refine Position", command=refinePosition).grid(row=33,column=3)

##start the other scripts

QUIT=Button(root,text="Quit", command=quit).grid(row=35,column=2,padx=2,pady=2)

## open gripper
openGripper()

value = setAbsZeroXY()
#root.after(1000,update_windows)
update_windows()



root.mainloop()
#Run Main Loop

#root.destroy()
