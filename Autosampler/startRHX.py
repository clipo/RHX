###Simple program that moves the motors and the arms - used for finding positions.


##Imports
import sys
import easygui
# comment while on Mac OS X
#sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
import easygui
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
import DataReadWrite
import xyzRobot
import math
import communication

LOGINT=5
logger = logging.getLogger("AutoSampler-startRHX")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
today_date = datetime.today()
datestring = today_date.strftime("%Y-%m-%d-%H-%M")

if sys.platform=="darwin":
   ## Mac OS X
   debugfilename = "/Users/Clipo/Dropbox/Rehydroxylation/Logger/Logs/rhx-startRHX" + datestring + "_debug.log"
else:
   debugfilename = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Logs/rhx-startRHX" + datestring + "_debug.log"
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

## CONSTANTS
INSIDE_BALANCE_POSITION=10000
OUTSIDE_BALANCE_POSITION=20000

#### These are all variables for the displays. Ive made them global so that I can access them anywhere here. Kludgy
LOCATION_TEMPERATURE=DoubleVar()
ASSEMBLAGE=StringVar()
MAXPOSITIONS=IntVar()
MAXPOSITIONS.set(25)  ## this is a constant for the max # of sample position (now 25)
POSITION_NAME=StringVar()  ## this is the name of the position -- HOME, SAMPLE, OUTSIDE_BALANCE, INSIDE_BALANCE are possibilities
ARM_STATUS=StringVar()  ## status for arm TOP, SAMPLE or BALANCE
LIGHTSTATUS=StringVar()    ### ON OR OFF
LIGHTSTATUS.set("OFF")
XZERO=StringVar()
YZERO=StringVar()
ZZERO=StringVar()

RESUBMIT=StringVar()
RUNINFOSTATUS=StringVar()
RUNID=IntVar()
INITIALS=StringVar()
DURATION=IntVar()
NUMBEROFSAMPLES=IntVar()
START_POSITION=IntVar()
START_POSITION.set(1)
XMOTORPOSITION=StringVar()
YMOTORPOSITION= StringVar()
ZMOTORPOSITION=StringVar()
GRIPPERPOSITION=StringVar()
BALANCEWEIGHT=DoubleVar()
BALANCESTATUS=StringVar()
ABSOLUTEXPOSITION=StringVar()
ABSOLUTEYPOSITION=StringVar()
ABSOLUTEZPOSITION=StringVar()
CRUCIBLEYESNO=StringVar()
MOTORSTEP=StringVar()
MOTORSTEP.set("5000")
ZMOTORSTEP=StringVar()
ZMOTORSTEP.set("5000")
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
SAMPLE_POSITION=IntVar()
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
#DBDIRECTORY.set("c:/Users/Archy/Dropbox/Rehydroxylation/")
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
MAXZMOTORVELOCITY=DoubleVar()
USINGSTANDARDBALANCE=BooleanVar()
ZTOPPOSITION=BooleanVar()

def quit():
   value=DataReadWrite.closeDatabase()
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

def are_you_sure(message):
   msg = "Do you really want to do this: %s " % message
   title = "Continue?"
   if easygui.ccbox(msg, title):     # show a Continue/Cancel dialog
      pass  # user chose Continue
   else:
      return False
   return True

def callback():
   askopenfilename()

def printValues():
   print "XMotor: ",xyzRobot.getXMotorPosition(), " YMotor: ",xyzRobot.getYMotorPosition()
   print "Absolute X Position: ", xyzRobot.getAbsoluteXPosition()
   (weight,status)=DataReadWrite.readWeightFromBalance()
   print "Balance: ", weight, "Status: ",status
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
      #DataReadWrite.tempHumidity.close()
   DataReadWrite.balance.close()
   #if (DataReadWrite.conn is not None):
   #   DataReadWrite.closeDatabase()

   DataReadWrite.standard_balance.close()
   alert.quit()
   root.quit()
   init.quit()
   prefire.quit()
   postfire.quit()
   return True;

def update_windows():
   USINGSTANDARDBALANCE.set(DataReadWrite.STANDARDBALANCE)

   XMOTORPOSITION.set(xyzRobot.getXMotorPosition())
   YMOTORPOSITION.set(xyzRobot.getYMotorPosition())
   ZMOTORPOSITION.set(xyzRobot.getZMotorPosition())
   XZERO.set(xyzRobot.atXZero())
   YZERO.set(xyzRobot.atYZero())
   ZZERO.set(xyzRobot.atZZero())

   PRECISIONTEMP.set(xyzRobot.getTemperature())
   results=[]
   (weight,status)=DataReadWrite.readInstantWeightFromBalance()
   #TODO:  renable the standard balance
   standardBalance=0.0
   if DataReadWrite.STANDARDBALANCE is True:
      standardBalance=float(DataReadWrite.readStandardBalance())
   STANDARD_BALANCE.set(standardBalance)
   BALANCEWEIGHT.set(weight)
   BALANCESTATUS.set(status)

   if xyzRobot.atXZero()=="TRUE" and xyzRobot.atYZero()=="TRUE":
      value = xyzRobot.setAbsZeroXY()
      POSITION_NAME.set("HOME")

   ABSOLUTEXPOSITION.set(xyzRobot.getAbsoluteXPosition())
   ABSOLUTEYPOSITION.set(xyzRobot.getAbsoluteYPosition())
   ABSOLUTEZPOSITION.set(xyzRobot.getAbsoluteZPosition())
   ##GRIPPERPOSITION.set(xyzRobot.getGripperPosition())

   #BALANCEDOOR.set(DataReadWrite.isBalanceDoorOpen())
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
   zlimit=xyzRobot.getZMotorVelocityLimit()
   MAXXMOTORVELOCITY.set(xlimit)
   MAXYMOTORVELOCITY.set(ylimit)
   MAXZMOTORVELOCITY.set(zlimit)

   ## To prevent negative values. If the limit detectors are TRUE then we must be at the zero point.
   ## so set the motor to 0 and the abs coordinate value to 0
   ## for each dimension separately.

   if xyzRobot.atXZero()=="TRUE":
      XZERO.set("TRUE")
      XMOTORPOSITION.set(0)
      value = xyzRobot.setXMotorPosition(0)
      value = xyzRobot.setXCoordinate(0)

   if xyzRobot.atYZero()=="TRUE":
      YZERO.set("TRUE")
      YMOTORPOSITION.set(0)
      value = xyzRobot.setYMotorPosition(0)
      value = xyzRobot.setYCoordinate(0)

   if xyzRobot.atZZero()=="TRUE":
      ZZERO.set("TRUE")
      ARM_STATUS.set("TOP")
      ZMOTORPOSITION.set(0)
      value = xyzRobot.setZMotorPosition(0)
      value= xyzRobot.setZCoordinate(0)


def initialize():
   root.withdraw()
   init.deiconify()
   init.wm_title("Initialize and Weigh Crucibles")
   ## first go home!
   xyzRobot.goHome()

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

   #################################
   ## GUI BUILD ####################
   init.config(menu=menubar)
   Label(init, text="Initials").grid(row=1, column=0, sticky=W)
   Entry(init, textvariable=INITIALS).grid(row=1, column=1, sticky=W)

   Label(init, text="Number of Crucibles").grid(row=3, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=NUMBEROFSAMPLES).grid(row=3, column=1, sticky=W, padx=2, pady=2)

   Label(init, text="Start Position").grid(row=4, column=0, sticky=W)
   Entry(init, textvariable=START_POSITION).grid(row=4, column=1, sticky=W)

   Label(init, text="Duration of Measurements").grid(row=5, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=DURATION).grid(row=5, column=1, sticky=W, padx=2, pady=2)

   Label(init,text="Madge Tech Temperature:").grid(row=6,column=0,sticky=W,padx=2,pady=2)
   Entry(init,textvariable=RHTEMP2000TEMP).grid(row=6,column=1,sticky=W,padx=2,pady=2)
   Label(init,text="Madge Tech RH:").grid(row=7,column=0,sticky=W,padx=2,pady=2)
   Entry(init,text=RHTEMP2000HUMIDITY).grid(row=7,column=1,sticky=W,padx=2,pady=2)

   Label(init,text="Precision Temp").grid(row=8,column=0,sticky=W)
   Label(init,textvariable=PRECISIONTEMP).grid(row=8,column=1,sticky=W)

   Label(init,text="Humidity").grid(row=9,column=0,sticky=W)
   Label(init,textvariable=HUMIDITY).grid(row=9,column=1,sticky=W)

   Button(init, text="Start Initialize", command=go_initialize).grid(row=12, column=2, sticky=W, padx=2, pady=2)
   Button(init, text="Quit", command=quit_init).grid(row=12, column=0, sticky=W, padx=2, pady=2)
   #################################
   ## GUI BUILD ####################

   update_windows()

def quit_init():
   root.deiconify()
   init.withdraw()

def go_initialize():
   status="Initialize"
   logger.debug('go_initialize: initialize function running. pre-weigh crucibles')

   logger.debug("XMotor: %i  YMotor: %i" % (xyzRobot.getXMotorPosition(), xyzRobot.getYMotorPosition()))
   #dbName=DATABASENAME.get()
   #dbDir=DBDIRECTORY.get()

   #value=DataReadWrite.initializeDatabase(dbDir,dbName)
   #if value is False:
   #   logger.error("There has been an error since initializeDatabase returned FALSE")
   #   alert.deiconify()
   #   Message(alert,text="There has been a problem. Cannot create database", bg='red', fg='ivory', relief=GROOVE)

   #(xpos,ypos) = DataReadWrite.getLastPosition()
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
   returnValue = xyzRobot.weighAllCrucibles(setInitials,numberOfSamples,LOGINT,duration,startPosition,tempCorrection,
      rhCorrection,
      robotStatus,POSITION,MCOUNT,CURRENTSTEP,STATUS,DURATION,LOGGERINTERVAL,RUNID,NUMBEROFSAMPLES,TIMEREMAINING,alert)

   if returnValue is False:
      logger.error("There has been an error since weighAllCrucibles returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem with weiging the crucibles. ",
         bg='red',
         fg='ivory', relief=GROOVE)
      communication.sendEmail ("RHX Error","An error has occurred with weighAllCrucibles!")

   ##DataReadWrite.updateTempRHCorrection(tempCorrection,rhCorrection,runID)

   logger.debug( "Initialize Crucibles: Done!   ")

   init.withdraw()
   root.update()
   root.deiconify()

   ## first go home!
   xyzRobot.goHome()

   value=DataReadWrite.closeDatabase()
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
   dbfilename=easygui.fileopenbox(msg='Open file for this set of samples.', title='Open Database',
      default="C:/Users/Archy/Dropbox/Rehydroxylation/Logger/Data/*.sqlite", filetypes='*.sqlite')

   DATABASENAME.set(dbfilename)

   value=DataReadWrite.openDatabase(dbfilename)
   if value is False:
      logger.error("There has been an error since openDatabase returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. Cannot read database", bg='red', fg='ivory', relief=GROOVE)
      alert.update()

   dt = datetime

   (v_locationCode, i_numberOfSamples, v_description, f_locationTemperature, f_locationHumidity,
      d_dateTimeFiring ,i_durationOfFiring,i_temperatureOfFiring, v_operatorName) =DataReadWrite.getRunInfo(1)
   NUMBEROFSAMPLES.set(i_numberOfSamples)
   INITIALS.set(v_operatorName)
   LOCATION.set(v_locationCode)
   ASSEMBLAGE.set(v_description)
   LOCATION_TEMPERATURE.set(f_locationTemperature)
   DURATIONOFFIRING.set(i_durationOfFiring)
   TEMPOFFIRING.set(i_temperatureOfFiring)
   #print "d_dateTimeFiring: ",d_dateTimeFiring
   if d_dateTimeFiring is not None:
      dt=datetime.strptime(d_dateTimeFiring, "%m-%d-%y %H:%S")
      DATEOFFIRING.set( dt.strftime("%m-%d-%y"))
      TIMEOFFIRING.set( dt.strftime("%H:%M:%S"))
   RUNINFOSTATUS.set("Please enter the required information to set up the run.")
   setupGUI()

def setupGUI():
   #################################
   ## GUI BUILD ####################
   init.config(menu=menubar)

   Label(init, text="Initials (e.g., CPL):").grid(row=1, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=INITIALS).grid(row=1, column=1, sticky=W, padx=2, pady=2)

   Label(init, text="Name of Assemblage (e.g., Belle Meade):").grid(row=2, column=0, sticky=W, padx=2,pady=2)
   Entry(init, textvariable=ASSEMBLAGE).grid(row=2, column=1, sticky=W,padx=2, pady=2)

   Label(init, text="Source Location (e.g., LMV):").grid(row=3, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=LOCATION).grid(row=3, column=1, sticky=W,padx=2, pady=2)

   Label(init, text="Lifetime Effective Temperature (C):").grid(row=4, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=LOCATION_TEMPERATURE).grid(row=4, column=1, sticky=W,padx=2, pady=2)

   Label(init, text="Number of Samples (n):").grid(row=5, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=NUMBEROFSAMPLES).grid(row=5, column=1, sticky=W, padx=2, pady=2)

   Label(init, text="Start Position (1-N):").grid(row=6, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=START_POSITION).grid(row=6, column=1, sticky=W, padx=2, pady=2)

   Label(init, text="Firing Temperature (C):").grid(row=7, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=TEMPOFFIRING).grid(row=7, column=1, sticky=W, padx=2, pady=2)

   Label(init, text="Start Date of Firing (mm-dd-yy):").grid(row=8, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=DATEOFFIRING).grid(row=8, column=1, sticky=W, padx=2, pady=2)

   Label(init, text="Start Time of Firing (HH:MM:SS):").grid(row=9, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=TIMEOFFIRING).grid(row=9, column=1, sticky=W, padx=2, pady=2)

   Label(init, text="Firing Duration (m):").grid(row=10, column=0, sticky=W, padx=2, pady=2)
   Entry(init, textvariable=DURATIONOFFIRING).grid(row=10, column=1, sticky=W, padx=2, pady=2)

   Label(init,text="Madge Tech Temperature (C):").grid(row=11,column=0,sticky=W,padx=2,pady=2)
   Entry(init,textvariable=RHTEMP2000TEMP).grid(row=11,column=1,sticky=W,padx=2,pady=2)

   Label(init,text="Madge Tech Humidity (%RH):").grid(row=12,column=0,sticky=W,padx=2,pady=2)
   Entry(init,text=RHTEMP2000HUMIDITY).grid(row=12,column=1,sticky=W,padx=2,pady=2)

   Label(init,text="Current Precision Temp (C):").grid(row=13,column=0,sticky=W, padx=2, pady=2)
   Label(init,textvariable=PRECISIONTEMP).grid(row=13,column=1,sticky=W, padx=2, pady=2)

   Label(init,text="Current Humidity (%RH):").grid(row=14,column=0,sticky=W, padx=2, pady=2)
   Label(init,textvariable=HUMIDITY).grid(row=14,column=1,sticky=W, padx=2, pady=2)

   Label(init,text="Database filename to use:").grid(row=15,column=0,sticky=W, padx=2, pady=2)
   Entry(init,textvariable=DATABASENAME).grid(row=15,column=1, sticky=W, padx=2, pady=2)

   Button(init, text="Setup Run", command=go_setup).grid(row=16, column=2, sticky=W, padx=2,pady=2)
   Button(init, text="Quit", command=quit_init).grid(row=16, column=0, sticky=W, padx=2, pady=2)

   Label(init,textvariable=RUNINFOSTATUS).grid(row=17,column=0,sticky=W, padx=2, pady=2)
   #################################
   update_windows()


def go_setup():
   status="Setup"
   logger.debug('go_setup: initialize function running. pre-weigh crucibles')

   if  DATEOFFIRING.get() is None or TIMEOFFIRING.get() is None or DURATIONOFFIRING.get() is None:
      RUNINFOSTATUS.set("Date of firing, Time of firing and Duration of Firing are all required. Please enter these data.")
      RESUBMIT.set("resubmission")
      setupGUI()

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

   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")

   #first create a new run so we have an ID.
   #logger.debug("DataReadWrite.insertRun( %s,%s,%d )" %(setInitials,today,numberOfSamples))
   #runID=DataReadWrite.insertRun(setInitials,today,numberOfSamples)
   runID=DataReadWrite.getLastRunID()
   if runID is False:
      logger.error("There has been an error since insertRun returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. Cannot find a run. Must set up measures ahead of time.", bg='red', fg='ivory',
         relief=GROOVE)
      exit(1)

   statustext = "Run ID is %d" % int(runID)

   dt=datetime
   datetimeOfFiring=DATEOFFIRING.get() + " "+ TIMEOFFIRING.get()
   try:
      dt = datetime.strptime(datetimeOfFiring, "%m-%d-%y %H:%M:%S")
   except:
      RUNINFOSTATUS.set("Date and time formats are incorrect. Reenter.")
      setupGUI()

   DataReadWrite.updateTempRHCorrection(tempCorrection,rhCorrection,runID)

   DataReadWrite.updateRunInformation(int(NUMBEROFSAMPLES.get()), INITIALS.get(), LOCATION.get(),ASSEMBLAGE.get(),float(LOCATION_TEMPERATURE.get()),runID)
   DataReadWrite.updateRunInfoWithFiringInformation(dt, float(TEMPOFFIRING.get()),int(DURATIONOFFIRING.get()),runID)
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
   if runID<1:
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
   value=DataReadWrite.updateRunPreFire(runID,setInitials,setName,today,setLocation,preOrPost,0,setTemperature,
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
   crucibleWeight,crucibleStdDev,weightCount = DataReadWrite.getEmptyCrucible(count,runID)
   CRUCIBLEWEIGHT.set(crucibleWeight)
   CRUCIBLEWEIGHTSTDDEV.set(crucibleStdDev)

   sherdWeight,sherdStdDev = DataReadWrite.getInitialSherd(count,runID)
   INITIALWEIGHT.set(sherdWeight)
   INITIALWEIGHTSTDDEV.set(sherdWeight)

   sherd105Weight,sherd105StdDev,weightCount = DataReadWrite.get105Crucible(count,runID)
   SAMPLEWEIGHT.set(sherd105Weight)
   SAMPLEWEIGHTSTDDEV.set(sherd105StdDev)

   sherd550Weight,sherd550StdDev,weightCount = DataReadWrite.get550Crucible(count,runID)
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


   value=DataReadWrite.updateCrucible(position,CRUCIBLEWEIGHT.get(),
      CRUCIBLEWEIGHTSTDDEV.get(),RHTEMP2000TEMP.get(),0.0,RHTEMP2000HUMIDITY.get(),
      0.0,today,runID,position)
   if (value==False):
      alertWindow("updateCrucible returned an error.")
      exit(1)
   netSampleWeight=SAMPLEWEIGHT.get()-CRUCIBLEWEIGHT.get()
   netSampleWeightStdDev=SAMPLEWEIGHTSTDDEV.get()
   (meanWeight, stdevWeight) = DataReadWrite.getCrucibleWeightStats(runID,position)

   value=DataReadWrite.updateSamplePreFire(runID,position,position,netSampleWeight,netSampleWeightStdDev,initialSherdWeight,initialSherdWeightStdDev,RHTEMP2000TEMP.get(),0.0,\
      RHTEMP2000HUMIDITY.get(),0.0)

   if value is False:
      alertWindow("updateSamplePrefire returned an error")
      communication.sendEmail ("RHX Error","An error has occurred with insertNewSample!")
      exit(1)

   netPostFireWeight=POSTFIREWEIGHT.get()-CRUCIBLEWEIGHT.get()
   netPostFireWeightStdDev=POSTFIREWEIGHTSTDDEV.get()
   value=DataReadWrite.updateSamplePostFireWeight(runID, position,netPostFireWeight,netPostFireWeightStdDev )
   CURRENTSAMPLE.set(position+1)
   root.update()
   go_setupPart2()


def quit_setup():
   setupCrucibles.withdraw()
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

   ## first go home!
   xyzRobot.goHome()

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
      initials,name,location,numberOfSamples,startPosition,durationOfMeasurements,samplingInterval,\
      repetitions,locationTemperature,locationHumidity=DataReadWrite.getPrefireAttributes(RUNID.get())
      INITIALS.set(initials)
      NAME.set(name)
      LOCATION.set(location)
      NUMBEROFSAMPLES.set(numberOfSamples)
      START_POSITION.set(startPosition)
      DURATION.set(durationOfMeasurements)
      INTERVAL.set(samplingInterval)
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

   DATAF=Label(prefire,text="Database filename to use:").grid(row=17,column=0,sticky=W)
   DATAL=Entry(prefire,textvariable=DATABASENAME).grid(row=17,column=1, sticky=W)

   INITBUTTON = Button(prefire, text="Start Pre Fire", command=go_preFire).grid(row=18, column=2, padx=2, pady=2)
   QUITBUTTON = Button(prefire, text="Quit", command=quit_prefire).grid(row=18, column=0, padx=2, pady=2)
   update_windows()

def quit_prefire():
   root.deiconify()
   prefire.withdraw()

def go_preFire():
   dbfilename=DATABASENAME.get()
   value=DataReadWrite.openDatabase(dbfilename)
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
   value=DataReadWrite.updateRunPreFire(runID,setInitials,setName,today,setLocation,preOrPost,intervalsec,
                                        setTemperature,setHumidity,status,duration,numberOfSamples,repetitions,startPosition)
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
      (meanWeight, stdevWeight) = DataReadWrite.getCrucibleWeightStats(runID,count)
      # Now do an insert for tblSample for each sample include--- from here on we can then just update the record. 
      sampleID = DataReadWrite.insertNewSample(runID,count,setName,now,setLocation,preOrPost,intervalsec,
                                               setTemperature,setHumidity,status,duration,repetitions,meanWeight,stdevWeight)
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
   value=DataReadWrite.closeDatabase()
   root.update()
   ## now go home!
   xyzRobot.goHome()
   communication.sendEmail ("RHX Status Change","Prefire is complete!")
   update_windows()

   return True

def postFire():
   logger.debug("Now running postFire function")
   preOrPost=2
   status ="Post-fired"
   root.withdraw()
   postfire.deiconify()
   postfire.wm_title("Post-Fire")

   ## first go home!
   xyzRobot.goHome()

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

   dbfilename=easygui.fileopenbox(msg='Open file for this set of samples.', title='Open Database',
                                  default="C:/Users/Archy/Dropbox/Rehydroxylation/Logger/Data/*.sqlite", filetypes='*.sqlite')

   DATABASENAME.set(dbfilename)

   value=DataReadWrite.openDatabase(dbfilename)
   if value == False:
      logger.error("There has been an error since openDatabase returned FALSE")
      alert.deiconify()
      Message(alert,text="There has been a problem. Cannot open database", bg='red', fg='ivory', relief=GROOVE)

   RHTEMP2000TEMP.set(xyzRobot.getTemperature())
   RHTEMP2000HUMIDITY.set(xyzRobot.getHumidity())
   PRECISIONTEMP.set(xyzRobot.getTemperature())

   if FILENAME.get() is not "":
      numberOfSamples,startPosition,dateOfFiring,timeOfFiring,rateOfHeating,tempOfFiring,durationOfFiring,\
      duration,interval,repetitions,locationTemperature,locationHumidity=DataReadWrite.getPostfireAttributes(RUNID.get())

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

   #################################
   #################################
   Label(postfire, text="Initials").grid(row=1, column=0, sticky=W)
   Entry(postfire, textvariable=INITIALS).grid(row=1, column=1, sticky=W)

   Label(postfire, text="Run ID").grid(row=2, column=0, sticky=W, padx=2, pady=2)
   Entry(postfire, textvariable=RUNID).grid(row=2, column=1, sticky=W,padx=2, pady=2)

   Label(postfire, text="Number of Samples").grid(row=3, column=0, sticky=W, padx=2, pady=2)
   Entry(postfire, textvariable=NUMBEROFSAMPLES).grid(row=3, column=1, sticky=W, padx=2, pady=2)

   Label(postfire, text="Start Position").grid(row=4, column=0, sticky=W)
   Entry(postfire, textvariable=START_POSITION).grid(row=4, column=1, sticky=W)

   Label(postfire, text="Date of Firing (mm-dd-yyyy):").grid(row=5, column=0, sticky=W, padx=2, pady=2)
   Entry(postfire, textvariable=DATEOFFIRING).grid(row=5, column=1, sticky=W,padx=2, pady=2)

   Label(postfire, text="24 Hour start time of Firing (hh:mm:ss) [24 Hours]:").grid(row=6, column=0, sticky=W, padx=2, pady=2)
   Entry(postfire, textvariable=TIMEOFFIRING).grid(row=6, column=1, sticky=W,padx=2, pady=2)

   Label(postfire, text="Temperature of Firing (C)").grid(row=7, column=0, sticky=W, padx=2, pady=2)
   Entry(postfire, textvariable=TEMPOFFIRING).grid(row=7, column=1, sticky=W, padx=2, pady=2)

   Label(postfire,text="Rate of Heating (C per minute, e.g., 27):").grid(row=8,column=0, stick=W, padx=2, pady=2)
   Entry(postfire, textvariable=RATEOFHEATING).grid(row=8, column=1, sticky=W, padx=2, pady=2)

   Label(postfire, text="Duration of Firing (min) (e.g., 360").grid(row=9, column=0, sticky=W, padx=2, pady=2)
   Entry(postfire, textvariable= DURATIONOFFIRING).grid(row=9, column=1, sticky=W, padx=2, pady=2)

   Label(postfire, text="Duration of Measurements (min)").grid(row=10, column=0, sticky=W, padx=2, pady=2)
   Entry(postfire, textvariable=DURATION).grid(row=10, column=1, sticky=W, padx=2, pady=2)

   Label(postfire, text="Sampling interval (seconds):").grid(row=11, column=0, sticky=W, padx=2, pady=2)
   Entry(postfire, textvariable=INTERVAL).grid(row=11, column=1, sticky=W, padx=2, pady=2)

   Label(postfire, text="Repetitions:").grid(row=12, column=0, sticky=W, padx=2, pady=2)
   Entry(postfire, textvariable=REPS).grid(row=12, column=1, sticky=W, padx=2, pady=2)

   Label(postfire, text="Temperature (C) (at location):").grid(row=13, column=0, sticky=W, padx=2, pady=2)
   Entry(postfire, textvariable=TEMP).grid(row=13, column=1, sticky=W, padx=2, pady=2)

   Label(postfire, text="Relative Humidity (set rh):").grid(row=14, column=0, sticky=W, padx=2, pady=2)
   Entry(postfire, textvariable=HUMIDITY).grid(row=14, column=1, sticky=W, padx=2, pady=2)

   Label(postfire,text="Madge Tech Temperature (current value):").grid(row=15,column=0,sticky=W,padx=2,pady=2)
   Entry(postfire,textvariable=RHTEMP2000TEMP).grid(row=15,column=1,sticky=W,padx=2,pady=2)

   Label(postfire,text="Madge Tech RH (current value):").grid(row=16,column=0,sticky=W,padx=2,pady=2)
   Entry(postfire,text=RHTEMP2000HUMIDITY).grid(row=16,column=1,sticky=W,padx=2,pady=2)

   Label(init,text="Precision Temp").grid(row=17,column=0,sticky=W)
   Label(init,textvariable=PRECISIONTEMP).grid(row=17,column=1,sticky=W)

   Label(init,text="Humidity").grid(row=18,column=0,sticky=W)
   Label(init,textvariable=HUMIDITY).grid(row=18,column=1,sticky=W)

   Label(postfire,text="Directory: ").grid(row=19,column=0,sticky=W,padx=2,pady=2)
   Entry(postfire,textvariable=DBDIRECTORY).grid(row=19,column=1,sticky=W,padx=2,pady=2)

   Label(postfire,text="Database filename to use:").grid(row=20,column=0,sticky=W)
   Entry(postfire,textvariable=DATABASENAME).grid(row=20,column=1, sticky=W)

   Button(postfire, text="Start Post Fire", command=go_postFire).grid(row=21, column=2, padx=2, pady=2)
   Button(postfire, text="Quit", command=quit_prefire).grid(row=21, column=0, padx=0, pady=2)

   #########################
   update_windows()

def quit_postfire():
   root.deiconfiy()
   postfire.withdraw()

def go_postFire():
   dbName=DATABASENAME.get()
   dbDir=DBDIRECTORY.get()


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

   value=DataReadWrite.updateRunPostFire(runID,setInitials,status,startOfFiring,
      durationOfFiring,temperatureOfFiring,postMeasurementTimeInterval,
      duration,repetitions,endOfFiring,startPosition,intervalsec,setHumidity,setTemperature)

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
   value=DataReadWrite.closeDatabase()
   communication.sendEmail ("RHX Status Change","Postfire is complete!")
   ## now go home!
   xyzRobot.goHome()
   update_windows()
   return True;

def moveMotorX():
   logger.debug("moveMotorX to %i",int(XMOTORPOSITION.get()))
   xyzRobot.moveMotorXToPosition(int(XMOTORPOSITION.get()))
   POSITION_NAME.set("UNKNOWN")
   sleep(2)
   logger.debug("now located at x: %d y: %d z: %d" % (xyzRobot.getXPosition(),xyzRobot.getYPosition(),xyzRobot.getZPosition()))
   DataReadWrite.updatePosition(xyzRobot.getXPosition(),xyzRobot.getYPosition(),xyzRobot.getZPosition())
   update_windows()
   return True;

def moveMotorY():
   logger.debug("moveMotorY to %i",int(YMOTORPOSITION.get()))
   xyzRobot.moveMotorYToPosition(int(YMOTORPOSITION.get()))
   POSITION_NAME.set("UNKNOWN")
   sleep(2)
   logger.debug("now located at x: %d y: %d z: %d" % (xyzRobot.getXPosition(),xyzRobot.getYPosition(),xyzRobot.getZPosition()))
   DataReadWrite.updatePosition(xyzRobot.getXPosition(),xyzRobot.getYPosition(),xyzRobot.getZPosition())
   update_windows()
   return True;

def setMotorXToZero():
   logger.debug("setMotorXToZero")
   xyzRobot.setXMotorPosition(0)
   XMOTORPOSITION.set("0")
   update_windows()
   return True;

def setMotorYToZero():
   logger.debug("setMotorYToZero")
   xyzRobot.setYMotorPosition(0)
   YMOTORPOSITION.set("0")
   update_windows()
   return True;

def setMotorsToZero(motorNumber):
   logger.debug("setMotorsToZero: %d",motorNumber)
   if motorNumber==0:
      xyzRobot.setXMotorPosition(0)
      XMOTORPOSITION.set("0")
   elif motorNumber==2:
      xyzRobot.setYMotorPosition(0)
      YMOTORPOSITION.set("0")
   else:
      logger.critical( "Error - no such motor number: %d ",motorNumber )
   POSITION_NAME.set("HOME")
   update_windows()
   return True;


def moveArmToPosition():
   logger.debug("moveArmToPosition: %d",int(ZMOTORPOSITION.get()))
   xyzRobot.moveArmToPosition(int(ZMOTORPOSITION.get()))
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
   logger.debug("bumpXMotorDown: %d",int(MOTORSTEP.get()))
   xyzRobot.bumpXMotorDown(int(MOTORSTEP.get()))
   #update_windows()
   logger.debug("bumpYMotorLeft: %d",int(MOTORSTEP.get()))
   xyzRobot.bumpYMotorLeft(int(MOTORSTEP.get()))
   update_windows()

def bumpZMotorUp():
   logger.debug("bumpZMotorUp")
   logger.debug("bumpZMotorUp: %d",int(ZMOTORSTEP.get()))
   if int(ZMOTORSTEP.get())>100000:
      print "Too dangerous to move that far up in one move. Ignoring..."
   else:
      xyzRobot.bumpZMotorUp(int(ZMOTORSTEP.get()))

   update_windows()

def bumpZMotorDown():
   logger.debug("bumpZMotorDown")
   logger.debug("bumpZMotorDown: %d",int(ZMOTORSTEP.get()))
   if int(ZMOTORSTEP.get())>100000:
      print "Too dangerous to move that far down in one move. Ignoring..."
   else:
      # print ("bumpZMotorDown")
      #print ("bumpZMotorDown: %d",int(ZMOTORSTEP.get()))
      xyzRobot.bumpZMotorDown(int(ZMOTORSTEP.get()))
   update_windows()

def lowerArmToSample():
   xyzRobot.lowerArmToSample()
   ARM_STATUS.set("SAMPLE")
   update_windows()

def raiseArmToTop():
   xyzRobot.raiseArmToTop()
   ARM_STATUS.set("TOP")
   update_windows()

def lowerArmToBalance():
   (xpos,ypos)=xyzRobot.getCurrentXYCoordinates()
   (bal_xpos, bal_ypos)=DataReadWrite.getXYCoordinatesForInsideBalance()

   if ypos<(bal_ypos-300):
      ## we are not on the balance so we cannot descend.
      print "Error:  we are not in a position to descend. Please move to the balance."
   else:
      xyzRobot.lowerArmToBalance()
      ARM_STATUS.set("BALANCE")
   update_windows()

def goHome():
   logger.debug("goHome: Go to Home Position")
   value= xyzRobot.goHome()
   if value==False:
      print "There has been an error going home -- we have not zero'd on one of the axes. Quitting."
      quit()

   SAMPLE_POSITION.set(0)
   XMOTORPOSITION.set(xyzRobot.getXMotorPosition())
   YMOTORPOSITION.set(xyzRobot.getYMotorPosition())
   ZMOTORPOSITION.set(xyzRobot.getZMotorPosition())
   XZERO.set(xyzRobot.atXZero())
   YZERO.set(xyzRobot.atYZero())
   ZZERO.set(xyzRobot.atZZero())
   sleep(1)
   if xyzRobot.atXZero()=="TRUE":
      XZERO.set("TRUE")
      XMOTORPOSITION.set(0)
      ARM_STATUS.set("TOP")
      value = xyzRobot.setXMotorPosition(0)
      value = xyzRobot.setXCoordinate(0)

   if xyzRobot.atYZero()=="TRUE":
      YZERO.set("TRUE")
      YMOTORPOSITION.set(0)
      value = xyzRobot.setYMotorPosition(0)
      value = xyzRobot.setYCoordinate(0)

   if xyzRobot.atZZero()=="TRUE":
      ZZERO.set("TRUE")
      ZMOTORPOSITION.set(0)
      value = xyzRobot.setZMotorPosition(0)
      value= xyzRobot.setZCoordinate(0)
   POSITION_NAME.set("HOME")
   update_windows()

def turnLightOn():
   logger.debug("turnLightOn")
   xyzRobot.turnLightOn()
   LIGHTSTATUS.set("ON")
   update_windows()

def turnLightOff():
   logger.debug("turnLightOff")
   xyzRobot.turnLightOff()
   LIGHTSTATUS.set("OFF")
   update_windows()

def openGripper():
   logger.debug("openGripper: Open gripper")
   xyzRobot.openGripper()
   GRIPPERPOSITION.set("OPEN - DISENGAGED")
   update_windows()

def closeGripper():
   logger.debug("closeGripper: Close gripper")
   xyzRobot.closeGripper()
   GRIPPERPOSITION.set("CLOSED - ENGAGED")
   update_windows()

def BZero():
   logger.debug("BZero: Zero the balance")
   DataReadWrite.BZero()
   update_windows()

def openBalanceDoor():
   logger.debug("openBalanceDoor: Open the balance door")
   DataReadWrite.openBalanceDoor()
   BALANCEDOOR("OPEN")
   update_windows()

def closeBalanceDoor():
   logger.debug("closeBalanceDoor:  Close the balance door")
   (xpos,ypos)=xyzRobot.getCurrentXYCoordinates()
   (bal_xpos, bal_ypos)=DataReadWrite.getXYCoordinatesForOutsideBalance()
   if ypos <= bal_ypos:
      DataReadWrite.closeBalanceDoor()
      BALANCEDOOR("CLOSED")
   else:
      logger.warn("Cannot close door. Arm is inside balance.")
      #update_windows()
   update_windows()

def goToPosition():
   pos=SAMPLE_POSITION.get()
   if pos>MAXPOSITIONS.get():
         update_windows()
         return
   else:
      POSITION_NAME.set("SAMPLE")
      logger.debug("goToPosition:  Go to position: %i",int(pos))
      xyzRobot.goToSamplePosition(int(pos),startWindow=1)
      update_windows()

def refine():
   pos=SAMPLE_POSITION.get()
   if pos<MAXPOSITIONS.get()+1:
      logger.debug("refine sample position: %i",int(pos))
      xyzRobot.refineSamplePosition(pos)
   elif pos==INSIDE_BALANCE_POSITION:
      logger.debug("refine inside balance position: %i",int(pos))
      xyzRobot.refineInsideBalancePosition()
   else:
      pass
   update_windows()

def goToBalance():
   SAMPLE_POSITION.set(INSIDE_BALANCE_POSITION)
   logger.debug("goToBalance:  Go to point outside of balance")
   xyzRobot.goToOutsideBalanceFromOutside()
   POSITION_NAME.set("OUTSIDE_BALANCE")
   #make sure balance door is open
   openBalanceDoor()
   BALANCEDOOR().set("OPEN")
   #update_windows()
   logger.debug("Go to inside of balance")
   POSITION.set(OUTSIDE_BALANCE_POSITION)
   xyzRobot.goToInsideBalanceFromOutside()
   POSITION_NAME.set("OUTSIDE_BALANCE")
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
      POSITION_NAME.set("OUTSIDE_BALANCE")
      openBalanceDoor()
      BALANCEDOOR.set("CLOSED")
      val=xyzRobot.goToInsideBalanceFromOutside()
      POSITION_NAME.set("INSIDE_BALANCE")
      val=xyzRobot.pickUpSampleFromBalance()
      val=xyzRobot.goToOutsideBalanceFromInside()
      POSITION_NAME.set("OUTSIDE_BALANCE")
      closeBalanceDoor()
      BALANCEDOOR.set("CLOSED")
      val=xyzRobot.goHome()
      POSITION_NAME.set("HOME")
      val=xyzRobot.goToSamplePosition(sampleNum,startWindow=1)
      POSITION_NAME.set("SAMPLE")
      SAMPLE_POSITION.set(sampleNum)
      val=xyzRobot.samplePutDown()
      val=xyzRobot.goHome()
      POSITION_NAME.set("HOME")
      update_windows()
      return True;

setup

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
   xyzRobot.resetXYValuesToZero()
   POSITION_NAME.set("HOME")
   update_windows()
   return True;

def setAbsZeroXY():
   sampleLocation=SAMPLE_POSITION.get()
   value=xyzRobot.setAbsZeroXY()
   update_windows()
   return True


def setXYForSampleLocation():
   sampleLocation=SAMPLE_POSITION.get()
   message="Set the XY for sample position: %d " % sampleLocation
   value=are_you_sure(message)
   if value is True:
      x=int(xyzRobot.getXPosition())
      y=int(xyzRobot.getYPosition())
      value = DataReadWrite.updateXYForSampleLocation(sampleLocation,x,y)

      xD,yD=xyzRobot.getCurrentXYCoordinates()
      value=DataReadWrite.updateXYCoordinatesForSampleLocation(sampleLocation,xD,yD)
      update_windows()
      return value
   return False

def setZForSampleLocation():
   message="Set Z position for samples here?"
   value=are_you_sure(message)
   if value is True:
      sampleZPosition=ZMOTORPOSITION.get()
      sampleLocation=SAMPLE_POSITION.get()
      value = DataReadWrite.updateZForSampleLocation(sampleLocation,sampleZPosition)
      update_windows()
      return value
   return False

def setZForBalanceLocation():
   message="Set the Z position for the balance here?"
   value=are_you_sure(message)
   if value is True:
      balanceZPosition=ZMOTORPOSITION.get()
      value = DataReadWrite.updateZForBalanceLocation(balanceZPosition)
      update_windows()
      return value
   return False

def setXYForAllLocations():
   message="Set the XY values for all locations?"
   value=are_you_sure(message)
   if value is True:
      sampleLocation=SAMPLE_POSITION.get()
      originalX=0
      originalY=0
      (originalX, originalY) = DataReadWrite.getXYForSampleLocation(sampleLocation)
      x=int(xyzRobot.getXPosition())
      y=int(xyzRobot.getYPosition())
      diffX=originalX - x
      diffY=originalY - y
      pos=sampleLocation
      value = DataReadWrite.updateXYForSampleLocation(sampleLocation,x,y)
      while pos < MAXPOSITIONS.get()+1:
         (originalX, originalY) = DataReadWrite.getXYForSampleLocation(pos)
         newX=originalX - diffX
         newY=originalY - diffY
         value = DataReadWrite.updateXYForSampleLocation(pos,newX,newY)
         pos +=1
      update_windows()
      return value
   return False

def setXYForInsideBalance():
   message="Set the Inside Balance point here?"
   value=are_you_sure(message)
   if value is True:
      x=int(xyzRobot.getXPosition())
      y=int(xyzRobot.getYPosition())
      value = DataReadWrite.updateXYForInsideBalance(x,y)
      xC, yC = xyzRobot.getCurrentXYCoordinates()
      DataReadWrite.updateXYCoordinatesForInsideBalance(xC,yC)
      update_windows()
      return value
   return False

def setXYForOutsideBalance():
   message="Set the Outside Balance point here?"
   value=are_you_sure(message)
   if value is True:
      x=int(xyzRobot.getXPosition())
      y=int(xyzRobot.getYPosition())
      value = DataReadWrite.updateXYForOutsideBalance(x,y)
      xC, yC = xyzRobot.getCurrentXYCoordinates()
      DataReadWrite.updateXYCoordinatesForOutsideBalance(xC,yC)
      update_windows()
      return value
   return False

def moveToNextSampleLocation():

   sampleLocation=int(SAMPLE_POSITION.get())
   ## first go home to set the position to ZERO then move to the point...
   xyzRobot.goHome()
   POSITION_NAME.set("HOME")
   ##print("Now at position %d" % (sampleLocation))

   sampleLocation += 1

   SAMPLE_POSITION.set(sampleLocation)
   POSITION_NAME.set("SAMPLE")
   value=0
   if sampleLocation>MAXPOSITIONS.get():
      sampleLocation=1

   ##print("Moving to position %d" % (sampleLocation))

   SAMPLE_POSITION.set(sampleLocation)

   goToPosition()
   POSITION_NAME.set("SAMPLE")
   update_windows()
   return True;

def resetZMotorToZeroPosition():
   xyzRobot.resetZMotorToZeroPosition()
   update_windows()
   return True

def resetZToZero():
   xyzRobot.resetZToZero()
   update_windows()
   return True

def goToOutsideBalance():
   xyzRobot.goToOutsideBalanceFromOutside()
   POSITION_NAME.set("OUTSIDE_BALANCE")
   SAMPLE_POSITION.set(OUTSIDE_BALANCE_POSITION)
   update_windows()
   return True

def goToInsideBalance():
   xyzRobot.goToOutsideBalanceFromOutside()
   POSITION_NAME.set("OUTSIDE_BALANCE")
   SAMPLE_POSITION.set(OUTSIDE_BALANCE_POSITION)
   update_windows()
   xyzRobot.goToInsideBalanceFromOutside()
   POSITION_NAME.set("INSIDE_BALANCE")
   update_windows()
   SAMPLE_POSITION.set(INSIDE_BALANCE_POSITION)
   return True

def setOutsideBalance():
   setXYForOutsideBalance()
   POSITION_NAME.set("OUTSIDE_BALANCE")
   update_windows()
   return True

def setInsideBalance():
   setXYForInsideBalance()
   POSITION_NAME.set("INSIDE_BALANCE")
   update_windows()
   return True

def checkEachSamplePosition():
   print "Ill only check the first 5 sample locations"
   sampleLocation=1
   print "First, go home."
   value=xyzRobot.goHome()
   POSITION_NAME.set("HOME")
   print "make sure gripper is open..."
   value=xyzRobot.openGripper()
   GRIPPERPOSITION.set("OPEN - DISENGAGED")
   while sampleLocation < MAXPOSITIONS.get()+1:
      print "Going to location: ", sampleLocation
      value=xyzRobot.goToSamplePosition(sampleLocation,startWindow=1)
      POSITION_NAME.set("SAMPLE")
      print "Lower arm to sample"
      value=xyzRobot.lowerArmToSample()
      ARM_STATUS.set("SAMPLE")
      print "Close gripper"
      value=xyzRobot.closeGripper()
      GRIPPERPOSITION.set("CLOSED - ENGAGED")
      print "Open gripper"
      value=xyzRobot.openGripper()
      GRIPPERPOSITION.set("OPEN - DISENGAGED")
      print "Raise arm to top"
      value=xyzRobot.raiseArmToTop()
      ARM_STATUS.set("TOP")
      print "Next..."
      sampleLocation += 1
   print "Now go home"
   value=xyzRobot.goHome()
   POSITION_NAME.set("HOME")
   print "Done."
   update_windows()

def visitEachSampleLocation():
   """
   visitEachSampleLocation() function will move the robot arm to each location one at a time. It'll pause at each location and ask whether
   the location is good.  Then it will allow one to "bump" the location one direction or another. One can then "save" the
   new location. This will require switching the locations of the crucibles to the XY database.
   """
   xyzRobot.goHome()
   sampleLocation=1
   if sampleLocation>0:
      value=xyzRobot.goToSamplePosition(sampleLocation,1)
      POSITION_NAME.set("SAMPLE")
      if value is False:
         alert.title("Alert: problem going to position 1")
         Message(alert,text="There was a problem going to position 1.", bg='red', fg='ivory', relief=GROOVE)
   moveArm.deiconify()
   SAMPLE_POSITION.set(sampleLocation)

   Button(moveArm, text="+X Axis", command=bumpXMotorUp).grid(row=1, column=1)
   Button(moveArm,text="-Y Axis", command=bumpYMotorLeft).grid(row=2, column=0, sticky=E)
   Button(moveArm,text="+Y Axis", command=bumpYMotorRight).grid(row=2, column=2, sticky=W)
   Button(moveArm,text="-X Axis", command=bumpXMotorDown).grid (row=3, column=1)
   Button(moveArm, text="NE", command=bumpMotorNE).grid(row=1, column=0,sticky=E)
   Button(moveArm, text="NW", command=bumpMotorNW).grid(row=1, column=2,sticky=W)

   Label(moveArm,textvariable=POSITION).grid(row=2,column=1)
   Button(moveArm, text="SE", command=bumpMotorSE).grid(row=3, column=2,sticky=W)
   Button(moveArm, text="SW", command=bumpMotorSW).grid(row=3, column=0,sticky=E)

   Label(moveArm,text="Step Size").grid(row=4,column=0,sticky=W)
   Entry(moveArm,textvariable=MOTORSTEP).grid(row=4,column=1,sticky=W)
   Button(moveArm,text="Set XY for this crucible position",command=setXYForSampleLocation).grid(row=5,column=0)
   Button(moveArm,text="Update all XYs based on this position",command=setXYForAllLocations).grid(row=5,column=1)
   Button(moveArm,text="Next position", command=moveToNextSampleLocation).grid(row=5,column=2)
   Button(moveArm,text="Go to Outside Balance Point", command=goToOutsideBalance).grid(row=6,column=0)
   Button(moveArm,text="Set Outside Balance Point",command=setOutsideBalance).grid(row=6,column=1)
   Button(moveArm,text="Go to Home Position(0,0)",command=goHome).grid(row=6,column=2)
   Button(moveArm,text="Go to Inside Balance Point", command=goToInsideBalance).grid(row=7,column=0)
   Button(moveArm,text="Set Inside Balance Point",command=setInsideBalance).grid(row=7,column=1)
   Button(moveArm,text="Cancel",command=backToMainWindowFromMoveArm).grid(row=8,column=2)

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
      initialdir='C:\\Users\\Archy\\Dropbox\\Rehydroxylation\\', parent=root,
      title='Choose a Sqlite database file')
   value=DataReadWrite.reopenDatabase(file)
   runID=DataReadWrite.getLastRunID()
   RUNID.set(runID)
   update_windows()
   return value

def refinePosition():
   position=SAMPLE_POSITION.get()
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

def setZMaxVelocity():
   maxvelocity=MAXZMOTORVELOCITY.get()
   xyzRobot.setZMotorVelocityLimit(maxvelocity)
   #MAXYMOTORVELOCITY.get(xyzRobot.getYMotorVelocityLimit())
   update_windows()
   return

def moveUntilXZero():
   xyzRobot.moveXUntilZero()
   sleep(1)
   update_windows()
   return

def moveUntilYZero():
   xyzRobot.moveYUntilZero()
   sleep(1)
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
Label(root, text="X-Axis").grid(row=1, column=0, sticky=E)
Entry(root, textvariable=XMOTORPOSITION).grid(row=1, column=1, sticky=W)
Button(root, text="Move X", command=moveMotorX).grid(row=1, column=2, padx=2, pady=2, sticky=W)
Button(root, text="Set Current Position of X to 0", command=setMotorXToZero).grid(row=1, column=3, padx=2, pady=2,sticky=W)

##Motor 2 Controls
Label(root, text="Y-Axis").grid(row=3, column=0, sticky=E)
Entry(root, textvariable=YMOTORPOSITION).grid(row=3, column=1, sticky=W)
Button(root, text="Move Y", command=moveMotorY).grid(row=3, column=2, padx=2, pady=2,sticky=W)
Button(root, text="Set Current Position  of Y to 0", command=setMotorYToZero).grid(row=3, column=3, padx=2, pady=2,sticky=W)

Button(root, text="+X Axis", command=bumpXMotorUp).grid(row=4, column=1)
Button(root,text="-Y Axis", command=bumpYMotorLeft).grid(row=5, column=0, sticky=E)
Button(root,text="+Y Axis", command=bumpYMotorRight).grid(row=5, column=2, sticky=W)
Button(root,text="-X Axis", command=bumpXMotorDown).grid (row=6, column=1)
Button(root, text="NE", command=bumpMotorNE).grid(row=4, column=0,sticky=E)
Button(root, text="NW", command=bumpMotorNW).grid(row=4, column=2,sticky=W)
Button(root, text="SE", command=bumpMotorSE).grid(row=6, column=2,sticky=W)
Button(root, text="SW", command=bumpMotorSW).grid(row=6, column=0,sticky=E)

##Arm Controller
Label(root, text="Arm Controller (Z Axis)").grid(row=7, column=0, sticky=W)
Label(root,text="XY Motor Step").grid(row=7,column=1,sticky=W)
Entry(root,textvariable=MOTORSTEP).grid(row=7,column=2,sticky=W)

Label(root, text="Z at Top?").grid(row=7,column=3,sticky=W)
Label(root, textvariable=ZZERO).grid(row=7,column=4,sticky=W)
Button(root, text="Lower to Sample", command=lowerArmToSample).grid(row=8, column=0, sticky=W, padx=2, pady=2)
Button(root, text="Raise to Top Position", command=raiseArmToTop).grid(row=8, column=1, sticky=W, padx=2, pady=2)
Button(root, text="Lower to Balance", command=lowerArmToBalance).grid(row=8, column=2, sticky=W, padx=2, pady=2)
Button(root, text="Set Z to Zero", command=resetZToZero).grid(row=8,column=4)

Button(root, text="Up Z", command=bumpZMotorUp).grid(row=9,column=0,sticky=E)
Entry(root, textvariable=ZMOTORSTEP).grid(row=9,column=1)
Label(root, text="Z Motor Step").grid(row=9,column=2)
Button(root, text="Down Z", command=bumpZMotorDown).grid(row=9,column=3,sticky=W)

Button(root, text="Reset Z to Top",command=resetZMotorToZeroPosition).grid(row=9,column=4)

##Arm Controls  
Label(root, text="Arm Controller (Z-Axis)").grid(row=10, column=0, sticky=E)
Entry(root, textvariable=ZMOTORPOSITION).grid(row=10, column=1, sticky=E)
Button(root, text="Move", command=moveArmToPosition).grid(row=10, column=2, sticky=W)
Label(root, text="Z Position").grid(row=10, column=3, sticky=W)
Label(root,textvariable=ZMOTORPOSITION).grid(row=10,column=4,sticky=W)

##Balance Door controller
Label(root, text="Balance Door").grid(row=11, column=0, sticky=W)
Button(root, text="Open", command=openBalanceDoor).grid(row=11, column=1, sticky=W, padx=2, pady=2)
Button(root, text="Close", command=closeBalanceDoor).grid(row=11, column=2, sticky=W, padx=2, pady=2)
Label(root, text="BALANCE_DOOR (Open/Closed)").grid(row=11,column=3,sticky=W)
Label(root, textvariable=BALANCEDOOR).grid(row=11,column=4,sticky=W)



##Balance Zeroing
Label(root, text="Tare the Balance" ).grid(row=12, column=0, sticky=W)
Button(root, text="Tare", command=BZero).grid(row=12, column=1, sticky=W, padx=2, pady=2)

Label(root, text="Balance Reading (g) ").grid(row=13,column=0,sticky=W)
Label(root, textvariable=BALANCEWEIGHT).grid(row=13,column=1,sticky=W)
Label(root,textvariable=BALANCESTATUS).grid(row=13,column=2,sticky=W)

Label(root, text="Low Precision Temp (C)").grid(row=14,column=0,sticky=W)
Label(root, textvariable=TEMPERATURE).grid(row=14,column=1,sticky=W)
Label(root, text="Humidity (%rh)").grid(row=14,column=2,sticky=W)
Label(root, textvariable=HUMIDITY).grid(row=14,column=3,sticky=W)

Label(root, text="Precision Temp C").grid(row=15,column=0,sticky=W)
Label(root,textvariable=PRECISIONTEMP).grid(row=15,column=1,sticky=W)

Label(root,text="Standard Balance (g)").grid(row=15,column=2,sticky=W)
Label(root,textvariable=STANDARD_BALANCE).grid(row=15,column=3,sticky=W)
Label(root,text="Using Standard Balance").grid(row=16,column=0,sticky=W)
Label(root,textvariable=USINGSTANDARDBALANCE).grid(row=16,column=1,sticky=W)

Label(root, text="Starting Sample Position").grid(row=17, column=0, sticky=W)
Entry(root, textvariable=START_POSITION).grid(row=17, column=1, sticky=W)

Label(root, text="Go To Sample Position Number").grid(row=18, column=0, sticky=W)
Entry(root, textvariable=SAMPLE_POSITION).grid(row=18, column=1, sticky=W)
Button(root, text="GO", command=goToPosition).grid(row=18, column=2, sticky=W)
Button(root,text="Refine Position",command=refine).grid(row=18,column=3,sticky=W)

Label(root,text="Retrieve Sample from Balance").grid(row=19,column=0,sticky=W)
Entry(root,textvariable=SAMPLENUM).grid(row=19,column=1,sticky=W)
Button(root,text="GO",command=getSampleFromBalance).grid(row=19,column=2,sticky=W)

Button(root,text="Set Home to this XY Location",command=setAbsZeroXY).grid(row=20,column=0)
Label(root,text="Current Location (XY)").grid(row=20,column=1)
Label(root,textvariable=POSITION_NAME).grid(row=20,column=2)
Label(root,text="Arm Location (Z)").grid(row=20,column=3)
Label(root,textvariable=ARM_STATUS).grid(row=20,column=4)

Label(root, text="X Coordinate (roller)").grid(row=21,column=0,sticky=W)
Label(root, textvariable=ABSOLUTEXPOSITION).grid(row=21,column=1,sticky=W)
Label(root, text="Y Coordinate (roller)").grid(row=21,column=2,sticky=W)
Label(root, textvariable=ABSOLUTEYPOSITION).grid(row=21,column=3,sticky=W)
Label(root, text="Z Coordinate (roller)").grid(row=21,column=4,sticky=W)
Label(root, textvariable=ABSOLUTEZPOSITION).grid(row=21,column=5, sticky=W)

Label(root, text="X Zero?").grid(row=22,column=0,sticky=W)
Label(root, textvariable=XZERO).grid(row=22,column=1,sticky=W)
Label(root, text="Y Zero?").grid(row=22,column=2,sticky=W)
Label(root, textvariable=YZERO).grid(row=22,column=3,sticky=W)
Label(root, text="Z Zero?").grid(row=22,column=4,sticky=W)
Label(root, textvariable=ZZERO).grid(row=22,column=5,sticky=W)

Label(root, text="X Motor Position").grid(row=23,column=0,sticky=W)
Label(root, textvariable=XMOTORPOSITION).grid(row=23,column=1,sticky=W)

Label(root, text="Y Motor Position").grid(row=23,column=2,sticky=W)
Label(root, textvariable=YMOTORPOSITION).grid(row=23,column=3,sticky=W)

Label(root, text="Z Motor Position").grid(row=23,column=4,sticky=W)
Label(root, textvariable=ZMOTORPOSITION).grid(row=23,column=5,sticky=W)

Button(root, text="Release Gripper (Open)", command=openGripper).grid(row=24, column=0, padx=2, pady=2)
Button(root, text="Engage Gripper (Close)", command=closeGripper).grid(row=24, column=1, padx=2, pady=2)
Label(root, text="Gripper Position").grid(row=24,column=2,sticky=W)
Label(root, textvariable=GRIPPERPOSITION).grid(row=24,column=3,sticky=W)

#Button(root, text="Lasers On", command=lasersOn).grid(row=25, column=0, padx=2, pady=2)
#Button(root, text="Lasers Off", command=lasersOff).grid(row=25, column=1, padx=2, pady=2)

Button(root, text="Chamber Lights On", command=turnLightOn).grid(row=25, column=0, padx=2, pady=2)
Button(root, text="Chamber Lights Off", command=turnLightOff).grid(row=25, column=1, padx=2, pady=2)
Label(root, textvariable=LIGHTSTATUS).grid(row=25, column=2, padx=2,pady=2)

Label(root, text="X Motor Velocity Max").grid(row=26, column=0, padx=2,pady=2)
Entry(root, textvariable=MAXXMOTORVELOCITY).grid(row=26,column=1,padx=2,pady=2)
Button(root,text="Set X Motor Max Velocity",command=setXMaxVelocity).grid(row=26,column=2,padx=2,pady=2)
Button(root, text="Disengage All Stepper Motors",command=xyzRobot.disengageMotors).grid(row=26,column=3,padx=2,pady=2)

Label(root, text="Y Motor Velocity Max").grid(row=27, column=0, padx=2,pady=2)
Entry(root, textvariable=MAXYMOTORVELOCITY).grid(row=27,column=1,padx=2,pady=2)
Button(root,text="Set Y Motor Max Velocity",command=setYMaxVelocity).grid(row=27,column=2,padx=2,pady=2)

Label(root, text="Z Motor Velocity Max").grid(row=28, column=0, padx=2,pady=2)
Entry(root, textvariable=MAXZMOTORVELOCITY).grid(row=28,column=1,padx=2,pady=2)
Button(root,text="Set Z Motor Max Velocity",command=setZMaxVelocity).grid(row=28,column=2,padx=2,pady=2)

Button(root,text="Go Directly to Balance", command=goToBalance).grid(row=29,column=0,padx=2,pady=2)
Button(root, text="Update this Window", command=update_windows).grid(row=29,column=2,padx=2,pady=2)
Button(root,text="Go Home", command=goHome).grid(row=29,column=1,padx=2,pady=2)

Button(root,text="Find XY Home Position", command=findHome).grid(row=30,column=0,padx=2,pady=2)
Button(root, text="Move and set each sample position", command=visitEachSampleLocation).grid(row=30,column=1,padx=2,
   pady=2)
Button(root,text="Check all sample positions",command=checkEachSamplePosition).grid(row=30,column=2,padx=2,
   pady=2)

Button(root,text="Move X until zero",command=moveUntilXZero).grid(row=31,column=0,padx=2,pady=2)
Button(root,text="Move Y until zero",command=moveUntilYZero).grid(row=31,column=1,padx=2,pady=2)
Button(root,text="Set XY for this sample position",command=setXYForSampleLocation).grid(row=31,column=2)

Button(root,text="Go to Outside Balance Point", command=goToOutsideBalance).grid(row=32,column=0)
Button(root,text="Set XY for Outside Balance Point",command=setOutsideBalance).grid(row=32,column=1)
Button(root,text="Set Z for Sample Position",command=setZForSampleLocation).grid(row=32,column=2)

Button(root,text="Go to Inside Balance Point", command=goToInsideBalance).grid(row=33,column=0)
Button(root,text="Set XY for Inside Balance Point",command=setInsideBalance).grid(row=33,column=1)
Button(root,text="Set Z for Balance Position",command=setZForBalanceLocation).grid(row=33,column=2)


Label(root,text="Run Number", textvariable=SETRUNID).grid(row=34,column=0)
#Button(root,text="Load Run", command=loadRun).grid(row=34,column=1)
#Button(root,text="Load Sqlite File", command=reloadFile).grid(row=34,column=2)
Button(root,text="Refine Position", command=refinePosition).grid(row=34,column=3)

##start the other scripts
Button(root, text="1. Initialize Empty Crucibles", command=initialize).grid(row=35, column=0, padx=2, pady=2)
Button(root,text="2. Setup RHX Rate Run (After 105/550 firing)", command=setup).grid(row=35,column=1,padx=2,pady=2)
Button(root, text="3.  Post-Fire (RHX rate measurement)", command=postFire).grid(row=35, column=2, padx=2, pady=2)

Button(root,text="<Quit>", command=quit).grid(row=35,column=3,padx=2,pady=2)

## open gripper
#openGripper()

#value = setAbsZeroXY()
#root.after(1000,update_windows)
#update_windows()

root.mainloop()
#Run Main Loop

#root.destroy()
