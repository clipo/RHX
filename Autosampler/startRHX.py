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


LOGINT = 5
logger = logging.getLogger("AutoSampler-startRHX")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
today_date = datetime.today()
datestring = today_date.strftime("%Y-%m-%d-%H-%M")

if sys.platform == "darwin":
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
prefire = Toplevel()
prefire.withdraw()
postfire = Toplevel()
postfire.withdraw()
robotStatus = Toplevel()
robotStatus.wm_title("Robot Status")
robotStatus.withdraw()
moveArm = Toplevel()
moveArm.wm_title("Move Arm")
moveArm.withdraw()
setupCrucibles = Toplevel()
setupCrucibles.withdraw()

## CONSTANTS
HOME = 0
INSIDE_BALANCE_POSITION = 10000
OUTSIDE_BALANCE_POSITION = 20000

#### These are all variables for the displays. Ive made them global so that I can access them anywhere here. Kludgy
LOCATION_TEMPERATURE = DoubleVar()
ASSEMBLAGE = StringVar()
MAXPOSITIONS = IntVar()
MAXPOSITIONS.set(25)  ## this is a constant for the max # of sample position (now 25)
POSITION_NAME = StringVar()  ## this is the name of the position -- HOME, SAMPLE, OUTSIDE_BALANCE, INSIDE_BALANCE are possibilities
ARM_STATUS = StringVar()  ## status for arm TOP, SAMPLE or BALANCE
LIGHTSTATUS = StringVar()    ### ON OR OFF
LIGHTSTATUS.set("OFF")
XZERO = StringVar()
YZERO = StringVar()
ZZERO = StringVar()

RESUBMIT = StringVar()
RUNINFOSTATUS = StringVar()
RUNID = IntVar()
INITIALS = StringVar()
DURATION = IntVar()
NUMBEROFSAMPLES = IntVar()
START_POSITION = IntVar()
START_POSITION.set(1)
XMOTORPOSITION = StringVar()
YMOTORPOSITION = StringVar()
ZMOTORPOSITION = StringVar()
GRIPPERPOSITION = StringVar()
BALANCEWEIGHT = DoubleVar()
BALANCESTATUS = StringVar()
ABSOLUTEXPOSITION = StringVar()
ABSOLUTEYPOSITION = StringVar()
ABSOLUTEZPOSITION = StringVar()
CRUCIBLEYESNO = StringVar()
MOTORSTEP = StringVar()
MOTORSTEP.set("5000")
ZMOTORSTEP = StringVar()
ZMOTORSTEP.set("5000")
BALANCEDOOR = StringVar()
SAMPLEPOSITION = StringVar()
POSITION = IntVar()
TEMP = DoubleVar()
HUMIDITY = DoubleVar()
REPS = IntVar()
INTERVAL = IntVar()
INTERVAL.set(5)
RUNID = IntVar()
RUNID.set(1)
DATEOFFIRING = StringVar()
TIMEOFFIRING = StringVar()
DURATIONOFFIRING = IntVar()
RATEOFHEATING = IntVar()
TEMPOFFIRING = IntVar()
CURRENTPOSITION = IntVar()
CURRENTREP = IntVar()
NAME = StringVar()
LOCATION = StringVar()
POSITION = IntVar()
SAMPLE_POSITION = IntVar()
MCOUNT = IntVar()
CURRENTSTEP = StringVar()
STATUS = StringVar()
DURATION = IntVar()
LOGGERINTERVAL = IntVar()
RUNID = IntVar()
NUMBEROFSAMPLES = IntVar()
STANDARD_BALANCE = DoubleVar()
TIMEREMAINING = IntVar()
TIMEELAPSEDMIN = DoubleVar()
TEMPERATURE = DoubleVar()
HUMIDITY = DoubleVar()
SAMPLENUM = IntVar()
FILENAME = StringVar()
RHTEMP2000TEMP = DoubleVar()
RHTEMP2000HUMIDITY = DoubleVar()
CYCLE = IntVar()
PRECISIONTEMP = DoubleVar()
DATABASENAME = StringVar()
DBDIRECTORY = StringVar()
#DBDIRECTORY.set("c:/Users/Archy/Dropbox/Rehydroxylation/")
tempCorrection = 0.0
rhCorrection = 0.0
fileName = "RHX.sqlite"
dirname = "/Users/Archy/Dropbox/Rehydroxylation/"
CRUCIBLEWEIGHT = DoubleVar()
CRUCIBLEWEIGHTSTDDEV = DoubleVar()
SAMPLEWEIGHT = DoubleVar()
CURRENTSAMPLE = IntVar()
ABSOLUTEXZERO = IntVar()
ABSOLUTEYZERO = IntVar()
ABSOLUTEXZERO.set(3)
ABSOLUTEYZERO.set(230)
COUNTSFORSTATS = IntVar()
COUNTSFORSTATS.set(3)
MEAN = DoubleVar()
STDEV = DoubleVar()
VARIANCE = DoubleVar()
SETRUNID = IntVar()
POSTFIREWEIGHT = DoubleVar()
POSTFIREWEIGHTSTDDEV = DoubleVar()
CURRENTSAMPLE = IntVar()
INITIALWEIGHT = DoubleVar()
INITIALWEIGHTSTDDEV = DoubleVar()
NOTES = StringVar()
INITIALSHERDWEIGHTSTDDEV = DoubleVar()
INITIALWEIGHTSTDDEV = DoubleVar()
SAMPLEWEIGHTSTDDEV = DoubleVar()
SAMPLEZPOSITION = IntVar()
BALANCEZPOSITION = IntVar()
MAXXMOTORVELOCITY = DoubleVar()
MAXYMOTORVELOCITY = DoubleVar()
MAXZMOTORVELOCITY = DoubleVar()
USINGSTANDARDBALANCE = BooleanVar()
ZTOPPOSITION = BooleanVar()


def quit():
    value = DataReadWrite.closeDatabase()
    if value is False:
        logger.error("There has been an error since closeDatabase returned FALSE")
        errorMessage("There has been a problem. Cannot close the current sample database file")
    value = DataReadWrite.closeXYDatabase()
    if value is False:
        logger.error("There has been an error since closeXYDatabase returned FALSE")
        errorMessage("There has been a problem. Cannot close XY database (RHX.sqlite)")
        return False
    prefire.quit()
    postfire.quit()
    init.quit()
    root.quit()
    xyzRobot.KillMotors()
    sys.exit(1)


def errorMessage(message):
    title = "Error! Continue?"
    if easygui.ccbox(message, title):     # show a Continue/Cancel dialog
        pass  # user chose Continue
    else:
        return False
    return True


def are_you_sure(message):
    msg = "Do you really want to do this: %s " % message
    title = "Continue?"
    if easygui.ccbox(msg, title):     # show a Continue/Cancel dialog
        pass  # user chose Continue
    else:
        return False
    return True

#Program Controls

def restart_program():
    try:
        xyzRobot.KillMotors()
    except:
        pass
    python = sys.executable
    os.execl(python, python, *sys.argv)
    return True


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
    DataReadWrite.closeDatabase()
    DataReadWrite.closeXYDatabase()
    DataReadWrite.standard_balance.close()
    root.quit()
    init.quit()
    prefire.quit()
    postfire.quit()
    return True


def update_windows():
    ## To prevent negative values.
    ## so set the motor to 0 and the abs coordinate value to 0
    ## for each dimension separately.
    if xyzRobot.getAbsoluteXPosition() < 0:
        xyzRobot.setXCoordinate(HOME)
        ABSOLUTEXPOSITION.set(HOME)

    if xyzRobot.getAbsoluteYPosition() < 0:
        xyzRobot.setYCoordinate(HOME)
        ABSOLUTEYPOSITION.set(HOME)

    if xyzRobot.getXCoordinate() < 0:
        xyzRobot.setXMotorPosition(HOME)
        XMOTORPOSITION.set(HOME)

    if xyzRobot.getYCoordinate() < 0:
        xyzRobot.setYMotorPosition(HOME)
        YMOTORPOSITION.set(HOME)

    USINGSTANDARDBALANCE.set(DataReadWrite.STANDARDBALANCE)
    XMOTORPOSITION.set(xyzRobot.getXMotorPosition())
    YMOTORPOSITION.set(xyzRobot.getYMotorPosition())
    ZMOTORPOSITION.set(xyzRobot.getZMotorPosition())
    XZERO.set(xyzRobot.atXZero())
    YZERO.set(xyzRobot.atYZero())
    ZZERO.set(xyzRobot.atZZero())
    PRECISIONTEMP.set(xyzRobot.getTemperature())

    weight, status = DataReadWrite.readInstantWeightFromBalance()
    #TODO:  renable the standard balance
    standardBalance = 0.0
    if DataReadWrite.STANDARDBALANCE is True:
        standardBalance = float(DataReadWrite.readStandardBalance())
    STANDARD_BALANCE.set(standardBalance)
    BALANCEWEIGHT.set(weight)
    BALANCESTATUS.set(status)

    ## only check the setting if we are supposedly at HOME
    ## this is because sample positions really close to home might still trigger the sensors
    if SAMPLE_POSITION.get() == HOME:
        if xyzRobot.atXZero() == "TRUE" and xyzRobot.atYZero() == "TRUE":
            value = xyzRobot.setAbsZeroXY()
            POSITION_NAME.set("HOME")
            SAMPLE_POSITION.set(HOME)
            XMOTORPOSITION.set(HOME)
            YMOTORPOSITION.set(HOME)
        if XZERO.get() == "TRUE":
            ## reset the Absolute Zero points
            value = xyzRobot.setXMotorPosition(HOME)

        if YZERO.get() == "TRUE":
            value = xyzRobot.setYMotorPosition(HOME)

        if xyzRobot.atXZero() == "TRUE":
            XZERO.set("TRUE")
            XMOTORPOSITION.set(HOME)
            value = xyzRobot.setXMotorPosition(HOME)
            value = xyzRobot.setXCoordinate(HOME)

        if xyzRobot.atYZero() == "TRUE":
            YZERO.set("TRUE")
            YMOTORPOSITION.set(HOME)
            value = xyzRobot.setYMotorPosition(HOME)
            value = xyzRobot.setYCoordinate(HOME)

    ## check Z separately
    if xyzRobot.atZZero() == "TRUE":
        ZZERO.set("TRUE")
        ARM_STATUS.set("TOP")
        ZMOTORPOSITION.set(0)
        value = xyzRobot.setZMotorPosition(0)
        value = xyzRobot.setZCoordinate(0)

    ABSOLUTEXPOSITION.set(xyzRobot.getAbsoluteXPosition())
    ABSOLUTEYPOSITION.set(xyzRobot.getAbsoluteYPosition())
    ABSOLUTEZPOSITION.set(xyzRobot.getAbsoluteZPosition())

    #logger.debug("Going to read the temp and humidity")
    TEMPERATURE.set(xyzRobot.getTemperature())
    HUMIDITY.set(xyzRobot.getHumidity())
    value = xyzRobot.isGripperHoldingSomething()
    if value is True:
        CRUCIBLEYESNO.set("Yes")
    else:
        CRUCIBLEYESNO.set("No")
    xlimit = xyzRobot.getXMotorVelocityLimit()
    ylimit = xyzRobot.getYMotorVelocityLimit()
    zlimit = xyzRobot.getZMotorVelocityLimit()
    MAXXMOTORVELOCITY.set(xlimit)
    MAXYMOTORVELOCITY.set(ylimit)
    MAXZMOTORVELOCITY.set(zlimit)


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
    Label(init, text="Initials:").grid(row=1, column=0, sticky=W)
    Entry(init, textvariable=INITIALS, width=4).grid(row=1, column=1, sticky=W)

    Label(init, text="Number of Crucibles:").grid(row=3, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=NUMBEROFSAMPLES, width=3).grid(row=3, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Start Position:").grid(row=4, column=0, sticky=W)
    Entry(init, textvariable=START_POSITION, width=3).grid(row=4, column=1, sticky=W)

    Label(init, text="Duration of Measurements:").grid(row=5, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=DURATION, width=4).grid(row=5, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Madge Tech Temperature:").grid(row=6, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=RHTEMP2000TEMP, width=8).grid(row=6, column=1, sticky=W, padx=2, pady=2)
    Label(init, text="Madge Tech RH:").grid(row=7, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=RHTEMP2000HUMIDITY, width=8).grid(row=7, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Precision Temp:").grid(row=8, column=0, sticky=W)
    Label(init, text=PRECISIONTEMP.get()).grid(row=8, column=1, sticky=W)

    Label(init, text="Humidity:").grid(row=9, column=0, sticky=W)
    Label(init, text=HUMIDITY.get()).grid(row=9, column=1, sticky=W)

    Button(init, text="Start Initialize", command=go_initialize).grid(row=12, column=2, sticky=W, padx=2, pady=2)
    Button(init, text="Quit", command=quit_init).grid(row=12, column=0, sticky=W, padx=2, pady=2)
    #################################
    ## GUI BUILD ####################

    update_windows()


def quit_init():
    root.deiconify()
    DataReadWrite.closeDatabase()
    init.withdraw()


def go_initialize():
    status = "Initialize"
    logger.debug('go_initialize: initialize function running. pre-weigh crucibles')

    logger.debug("XMotor: %i  YMotor: %i" % (xyzRobot.getXMotorPosition(), xyzRobot.getYMotorPosition()))

    logger.debug("Set the current position of motors to zero ... ")
    standardTemp = float(RHTEMP2000TEMP.get())
    standardRH = float(RHTEMP2000HUMIDITY.get())

    ## initially use the 0,0 as the correction to see what we need to adjust to match the MadgeTech 2000
    ## Note these are GLOBAL so that we can read the corrections when running the other stuff
    temp = xyzRobot.getTemperature()
    tempCorrection = standardTemp - temp
    rhCorrection = standardRH - xyzRobot.getHumidity()

    numberOfSamples = int(NUMBEROFSAMPLES.get())
    duration = int(DURATION.get())
    startPosition = int(START_POSITION.get())
    xyzRobot.resetXYValuesToZero()
    setInitials = INITIALS.get()

    timeToCompletion = (duration * numberOfSamples) + numberOfSamples
    end = timedelta(minutes=timeToCompletion)

    now = datetime.today()
    endOfRunTime = now + end
    endOfRun = endOfRunTime.strftime("%m-%d-%y %H:%M:%S")

    print "This run will end ca. ", endOfRun

    logger.debug("Now going to move and measure each of the crucibles... ")
    logger.debug(
        "xyzRobot.weighAllCrucibles(%s,%d,%d,%d,%d)" % (setInitials, numberOfSamples, LOGINT, duration, startPosition))
    returnValue = xyzRobot.weighAllCrucibles(setInitials, numberOfSamples, LOGINT, duration, startPosition,
                                             tempCorrection,
                                             rhCorrection,
                                             robotStatus, SAMPLE_POSITION, MCOUNT, CURRENTSTEP, STATUS, DURATION,
                                             LOGGERINTERVAL, RUNID, NUMBEROFSAMPLES, TIMEREMAINING)

    if returnValue is False:
        logger.error("There has been an error since weighAllCrucibles returned FALSE")
        errorMessage("There has been a problem weighing the crucibles (weighAllCrucibles). ")
        return False

    ##DataReadWrite.updateTempRHCorrection(tempCorrection,rhCorrection,runID)

    logger.debug("Initialize Crucibles: Done!   ")

    init.withdraw()
    root.update()
    root.deiconify()

    ## first go home!
    xyzRobot.goHome()

    value = DataReadWrite.closeDatabase()
    communication.sendEmail("RHX Status Change", "Initialization is complete!")
    return True


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
    dbfilename = easygui.fileopenbox(msg='Open file for this set of samples.', title='Open Database',
                                     default="C:/Users/Archy/Dropbox/Rehydroxylation/Logger/Data/*.sqlite",
                                     filetypes='*.sqlite')

    if dbfilename is None:
        return

    DATABASENAME.set(dbfilename)

    value = DataReadWrite.openDatabase(dbfilename)
    if value is False:
        logger.error("There has been an error since openDatabase returned FALSE")
        errorMessage("There has been a problem. Cannot read database (openDatabase).")
        return False

    dt = datetime
    t_assemblageName = str
    v_locationCode = str
    i_numberOfSamples = int
    f_locationTemperature = float
    f_locationHumidity = float
    d_dateTimefiring = datetime
    i_durationOfFiring = int
    i_temperatureOfFiring = int
    v_operatorName = str
    try:
        (v_locationCode, i_numberOfSamples, t_assemblageName, f_locationTemperature, f_locationHumidity,
         d_dateTimeFiring, i_durationOfFiring, i_temperatureOfFiring, v_operatorName,
         t_notes) = DataReadWrite.getRunInfo(
            1)
    except:
        logger.error("There has been an error since DataReadWrite.getRunInfo(1) returned FALSE")
        errorMessage("There has been a problem with getRunInfo. Cannot read database")
        return False

    NOTES.set(t_notes)
    NUMBEROFSAMPLES.set(i_numberOfSamples)
    INITIALS.set(v_operatorName)
    LOCATION.set(v_locationCode)
    ASSEMBLAGE.set(t_assemblageName)
    LOCATION_TEMPERATURE.set(f_locationTemperature)
    DURATIONOFFIRING.set(i_durationOfFiring)
    TEMPOFFIRING.set(i_temperatureOfFiring)
    #print "d_dateTimeFiring: ",d_dateTimeFiring
    if d_dateTimeFiring is not None:
        try:
            dt = datetime.strptime(d_dateTimeFiring, "%Y-%m-%d %H:%M:%S")
        except:
            dt = datetime.strptime(d_dateTimeFiring, "%m-%d-%y %H:%M")

        DATEOFFIRING.set(dt.strftime("%m-%d-%y"))
        TIMEOFFIRING.set(dt.strftime("%H:%M:%S"))
    RUNINFOSTATUS.set("Please enter the required information to set up the run.")
    setupGUI()


def setupGUI():
    #################################
    ## GUI BUILD ####################
    init.config(menu=menubar)

    Label(init, text="Initials (e.g., CPL):").grid(row=1, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=INITIALS, width=3).grid(row=1, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Source Location (e.g., LMV):").grid(row=2, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=LOCATION, width=40).grid(row=2, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Name of Assemblage (e.g., Belle Meade):").grid(row=3, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=ASSEMBLAGE, width=40).grid(row=3, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Lifetime Effective Temperature (C):").grid(row=4, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=LOCATION_TEMPERATURE, width=6).grid(row=4, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Number of Samples (n):").grid(row=5, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=NUMBEROFSAMPLES, width=3).grid(row=5, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Notes:").grid(row=6, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=NOTES, width=60).grid(row=6, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Start Position (1-N):").grid(row=7, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=START_POSITION, width=3).grid(row=7, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Firing Temperature (C):").grid(row=8, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=TEMPOFFIRING, width=6).grid(row=8, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Start Date of Firing (mm-dd-yy):").grid(row=9, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=DATEOFFIRING, width=12).grid(row=9, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Start Time of Firing (HH:MM):").grid(row=10, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=TIMEOFFIRING, width=12).grid(row=10, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Firing Duration (m):").grid(row=11, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=DURATIONOFFIRING, width=6).grid(row=11, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Madge Tech Temperature (C):").grid(row=12, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=RHTEMP2000TEMP, width=8).grid(row=12, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Madge Tech Humidity (%RH):").grid(row=13, column=0, sticky=W, padx=2, pady=2)
    Entry(init, text=RHTEMP2000HUMIDITY, width=8).grid(row=13, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Current Precision Temp (C):").grid(row=14, column=0, sticky=W, padx=2, pady=2)
    Label(init, text=PRECISIONTEMP.get()).grid(row=14, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Current Humidity (%RH):").grid(row=15, column=0, sticky=W, padx=2, pady=2)
    Label(init, text=HUMIDITY.get()).grid(row=15, column=1, sticky=W, padx=2, pady=2)

    Label(init, text="Database filename to use:").grid(row=16, column=0, sticky=W, padx=2, pady=2)
    Entry(init, textvariable=DATABASENAME, width=60).grid(row=16, column=1, sticky=W, padx=2, pady=2)

    Button(init, text="Setup Run", command=go_setup).grid(row=17, column=2, sticky=W, padx=2, pady=2)
    Button(init, text="Quit", command=quit_init).grid(row=17, column=0, sticky=W, padx=2, pady=2)

    Label(init, textvariable=RUNINFOSTATUS).grid(row=18, column=0, sticky=W, padx=2, pady=2)
    #################################
    update_windows()


def go_setup():
    status = "Setup"
    logger.debug('go_setup: initialize function running. pre-weigh crucibles')

    if DATEOFFIRING.get() is None or TIMEOFFIRING.get() is None or DURATIONOFFIRING.get() is None:
        RUNINFOSTATUS.set(
            "Date of firing, Time of firing and Duration of Firing are all required. Please enter these data.")
        RESUBMIT.set("resubmission")
        setupGUI()

    standardTemp = float(RHTEMP2000TEMP.get())
    standardRH = float(RHTEMP2000HUMIDITY.get())

    ## initially use the 0,0 as the correction to see what we need to adjust to match the MadgeTech 2000
    ## Note these are GLOBAL so that we can read the corrections when running the other stuff
    temp = xyzRobot.getTemperature()
    tempCorrection = standardTemp - temp
    rhCorrection = standardRH - xyzRobot.getHumidity()

    numberOfSamples = int(NUMBEROFSAMPLES.get())
    startPosition = int(START_POSITION.get())
    setInitials = INITIALS.get()

    now = datetime.today()
    today = now.strftime("%m-%d-%y %H:%M:%S")

    #first create a new run so we have an ID.
    runID = DataReadWrite.getLastRunID()
    if runID is False:
        logger.error("There has been an error since insertRun returned FALSE")
        errorMessage("There has been a problem. Cannot find a run. Must set up measures ahead of time.")
        return False

    statustext = "Run ID is %d" % int(runID)

    dt = datetime
    datetimeOfFiring = DATEOFFIRING.get() + " " + TIMEOFFIRING.get()
    try:
        dt = datetime.strptime(datetimeOfFiring, "%m-%d-%y %H:%M")
    except:
        RUNINFOSTATUS.set("Date and time formats are incorrect. Reenter.")
        return False

    DataReadWrite.updateTempRHCorrection(tempCorrection, rhCorrection, runID)
    DataReadWrite.updateRunInformation(int(NUMBEROFSAMPLES.get()), INITIALS.get(), LOCATION.get(), ASSEMBLAGE.get(),
                                       float(LOCATION_TEMPERATURE.get()), NOTES.get(), runID)
    DataReadWrite.updateRunInfoWithFiringInformation(dt, float(TEMPOFFIRING.get()), int(DURATIONOFFIRING.get()), runID)
    logger.debug(statustext)
    RUNID.set(int(runID))
    CURRENTSAMPLE.set(1)
    init.update()

    go_setupPart2()


def go_setupPart2():
    count = CURRENTSAMPLE.get()
    if count > NUMBEROFSAMPLES.get():
        quit_setup()
        return True

    runID = int(RUNID.get())
    if runID < 1:
        errorMessage("You must have a RunID to continue.")
        logger.debug("You must have a RunID entered in order to continue.")
        return False

    setInitials = str(INITIALS.get())
    setLocation = str(LOCATION.get())
    numberOfSamples = int(NUMBEROFSAMPLES.get())
    setHumidity = float(HUMIDITY.get())
    locationTemperature = LOCATION_TEMPERATURE.get()

    status = "prefire"
    assemblage = ASSEMBLAGE.get()

    value = DataReadWrite.updateRunPreFire(runID, setInitials, assemblage, setLocation, locationTemperature,
                                           setHumidity,
                                           status, numberOfSamples)
    if value is False:
        logger.error("There has been an error since updateRunPreFire returned FALSE")
        errorMessage("There has been a problem.updateRunPreFire has returned FALSE.")
        return False

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

    crucibleWeight, crucibleStdDev, weightCount = DataReadWrite.getEmptyCrucible(count, runID)
    CRUCIBLEWEIGHT.set(crucibleWeight)
    CRUCIBLEWEIGHTSTDDEV.set(crucibleStdDev)

    sherdWeight, sherdStdDev = DataReadWrite.getInitialSherd(count, runID)
    INITIALWEIGHT.set(sherdWeight)
    INITIALWEIGHTSTDDEV.set(sherdStdDev)

    sherd105Weight, sherd105StdDev = DataReadWrite.getPreFireSherd(count, runID)
    SAMPLEWEIGHT.set(sherd105Weight)
    SAMPLEWEIGHTSTDDEV.set(sherd105StdDev)

    sherd550Weight, sherd550StdDev = DataReadWrite.getPostFireSherd(count, runID)
    POSTFIREWEIGHT.set(sherd550Weight)
    POSTFIREWEIGHTSTDDEV.set(sherd550StdDev)

    Label(setupCrucibles, text="CHECK AND VERIFY THESE VALUES").grid(row=0, column=0, sticky=W)
    Label(setupCrucibles, text="Mean").grid(row=2, column=1, sticky=W)
    Label(setupCrucibles, text="StdDev").grid(row=2, column=2, sticky=W)
    Label(setupCrucibles, text="Current Sample Number").grid(row=1, column=0, sticky=W)
    Entry(setupCrucibles, textvariable=CURRENTSAMPLE).grid(row=1, column=1, sticky=W)
    ctext = "Crucible #" + str(count) + " Empty Weight (g)"
    Label(setupCrucibles, text=ctext).grid(row=3, column=0, sticky=W)
    Entry(setupCrucibles, textvariable=CRUCIBLEWEIGHT).grid(row=3, column=1, sticky=W)
    Entry(setupCrucibles, textvariable=CRUCIBLEWEIGHTSTDDEV).grid(row=3, column=2, sticky=W)

    smtext = "Sample #" + str(count) + " Initial weight of sherd (g):"
    Label(setupCrucibles, text=smtext).grid(row=4, column=0, sticky=W)
    Entry(setupCrucibles, textvariable=INITIALWEIGHT).grid(row=4, column=1, sticky=W)
    Entry(setupCrucibles, textvariable=INITIALWEIGHTSTDDEV).grid(row=4, column=2, sticky=W)

    smtext = "Sample #" + str(count) + " 105 degree weight of sherd (g): "
    Label(setupCrucibles, text=smtext).grid(row=5, column=0, sticky=W)
    Entry(setupCrucibles, textvariable=SAMPLEWEIGHT).grid(row=5, column=1, sticky=W)
    Entry(setupCrucibles, textvariable=SAMPLEWEIGHTSTDDEV).grid(row=5, column=2, sticky=W)

    sftext = "Sample #" + str(count) + " Post-Fire Weight of sherd (g):"
    Label(setupCrucibles, text=sftext).grid(row=6, column=0, sticky=W)
    Entry(setupCrucibles, textvariable=POSTFIREWEIGHT).grid(row=6, column=1, sticky=W)
    Entry(setupCrucibles, textvariable=POSTFIREWEIGHTSTDDEV).grid(row=6, column=2, sticky=W)

    Button(setupCrucibles, text="Submit Weight Data for Sample/Crucible", command=updateCrucibleAndSample).grid(row=7,
                                                                                                                column=0,
                                                                                                                sticky=W,
                                                                                                                padx=2,
                                                                                                                pady=2)
    Button(setupCrucibles, text="End (No more samples)", command=quit_setup).grid(row=7, column=1, sticky=W, padx=2,
                                                                                  pady=2)
    update_windows()


def updateCrucibleAndSample():
    setupCrucibles.withdraw()
    runID = RUNID.get()
    now = datetime.today()
    today = now.strftime("%m-%d-%y %H:%M:%S")
    position = CURRENTSAMPLE.get()
    preOrPost = 1
    setInitials = str(INITIALS.get())
    startPosition = int(START_POSITION.get())
    setName = str(NAME.get())
    setLocation = str(LOCATION.get())
    numberOfSamples = int(NUMBEROFSAMPLES.get())
    setTemperature = float(PRECISIONTEMP.get())
    setHumidity = float(HUMIDITY.get())
    standardTemp = float(RHTEMP2000TEMP.get())
    standardRH = float(RHTEMP2000HUMIDITY.get())
    initialSherdWeight = float(INITIALWEIGHT.get())
    initialSherdWeightStdDev = float(INITIALWEIGHTSTDDEV.get())

    status = "prefire"

    value = DataReadWrite.updateCrucible(position, CRUCIBLEWEIGHT.get(),
                                         CRUCIBLEWEIGHTSTDDEV.get(), RHTEMP2000TEMP.get(), 0.0,
                                         RHTEMP2000HUMIDITY.get(),
                                         0.0, today, runID, position)

    if value is False:
        errorMessage("updateCrucible returned an error")
        return False

    prefireSampleWeight = SAMPLEWEIGHT.get()
    prefireSampleWeightStdDev = SAMPLEWEIGHTSTDDEV.get()

    value = DataReadWrite.updateSamplePreFire(runID, position, initialSherdWeight, initialSherdWeightStdDev,
                                              prefireSampleWeight, prefireSampleWeightStdDev, RHTEMP2000TEMP.get(), 0.0,
                                              RHTEMP2000HUMIDITY.get(), 0.0)

    if value is False:
        errorMessage("You must have a RunID to continue: updateSamplePrefire returned an error")
        return False

    postfireSampleWeight = POSTFIREWEIGHT.get()
    postfireSampleWeightStdDev = POSTFIREWEIGHTSTDDEV.get()
    value = DataReadWrite.updateSamplePostFireWeight(runID, position, postfireSampleWeight, postfireSampleWeightStdDev)
    CURRENTSAMPLE.set(position + 1)
    root.update()
    go_setupPart2()


def quit_setup():
    init.withdraw()
    setupCrucibles.withdraw()
    logger.debug("Setup is done ")
    DataReadWrite.closeDatabase()
    root.update()
    root.deiconify()
    return True


def backToMainWindowFromMoveArm():
    """
    backToMainWinodwFromMoveArm destroys the moveArm window and brings the root back to focus.
    """
    #moveArm.withdraw()
    root.deiconify()
    return True


def backToMainWindow():
    """
    backToMainWindow() removes other windows and bring the root window to the focus
    """
    root.update()
    root.deiconify()
    return True


def postFire():
    logger.debug("Now running postFire function")
    preOrPost = 2
    status = "Post-fired"
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

    dbfilename = easygui.fileopenbox(msg='Open file for this set of samples.', title='Open Database',
                                     default="C:/Users/Archy/Dropbox/Rehydroxylation/Logger/Data/*.sqlite",
                                     filetypes='*.sqlite')
    if dbfilename is None:
        return
    DATABASENAME.set(dbfilename)

    value = DataReadWrite.openDatabase(dbfilename)
    if value is False:
        logger.error("There has been an error since openDatabase returned FALSE")
        errorMessage("There has been a problem. Cannot open database")
        return False

    RHTEMP2000TEMP.set(xyzRobot.getTemperature())
    RHTEMP2000HUMIDITY.set(xyzRobot.getHumidity())
    PRECISIONTEMP.set(xyzRobot.getTemperature())
    HUMIDITY.set(xyzRobot.getHumidity())
    RUNID.set(1)
    t_assemblageName = str
    v_locationCode = str
    i_numberOfSamples = int
    f_locationTemperature = float
    f_locationHumidity = float
    d_dateTimefiring = datetime
    i_durationOfFiring = int
    i_temperatureOfFiring = int
    v_operatorName = str

    try:
        (v_locationCode, i_numberOfSamples, t_assemblageName, f_locationTemperature, f_locationHumidity,
         d_dateTimeFiring, i_durationOfFiring, i_temperatureOfFiring, v_operatorName,
         t_notes) = DataReadWrite.getRunInfo(
            1)
    except:
        logger.error("There has been an error since DataReadWrite.getRunInfo(1) returned FALSE")
        errorMessage("There has been a problem with getRunInfo. Cannot read database")
        return False

    NUMBEROFSAMPLES.set(i_numberOfSamples)
    TEMP.set(f_locationTemperature)
    LOCATION_TEMPERATURE.set(f_locationTemperature)
    LOCATION.set(v_locationCode)
    ASSEMBLAGE.set(t_assemblageName)
    INITIALS.set(v_operatorName)
    NOTES.set(t_notes)

    (numberOfSamples, duration, interval, repetitions) = DataReadWrite.getPostfireAttributes()
    if duration is None:
        duration = int(60 / numberOfSamples)

    if interval is None or interval == 0:
        interval = 5

    if repetitions is None:
        repetitions = 4 * 24

    START_POSITION.set(1)
    DURATION.set(duration)
    INTERVAL.set(interval)
    REPS.set(repetitions)


    #################################
    #################################

    Label(postfire, text="Location:").grid(row=0, column=0, sticky=W, padx=2, pady=2)
    Label(postfire, text=LOCATION.get()).grid(row=0, column=1, sticky=W, padx=2, pady=2)

    Label(postfire, text="Assemblage:").grid(row=1, column=0, sticky=W, padx=2, pady=2)
    Label(postfire, text=ASSEMBLAGE.get()).grid(row=1, column=1, sticky=W, padx=2, pady=2)

    Label(postfire, text="Effective Lifetime Temperature (C):").grid(row=2, column=0, sticky=W, padx=2, pady=2)
    Label(postfire, text=LOCATION_TEMPERATURE.get()).grid(row=2, column=1, sticky=W, padx=2, pady=2)

    Label(postfire, text="Number of samples (e.g., 3):").grid(row=3, column=0, sticky=W, padx=2, pady=2)
    Label(postfire, text=NUMBEROFSAMPLES.get()).grid(row=3, column=1, sticky=W, padx=2, pady=2)

    Label(postfire, text="Starting position (e.g., 1):").grid(row=4, column=0, sticky=W)
    Entry(postfire, textvariable=START_POSITION, width=3).grid(row=4, column=1, sticky=W)

    Label(postfire, text="Duration of measurements per cycle (min):").grid(row=10, column=0, sticky=W, padx=2, pady=2)
    Entry(postfire, textvariable=DURATION, width=4).grid(row=10, column=1, sticky=W, padx=2, pady=2)

    Label(postfire, text="Sampling interval for weight measurements in seconds (e.g., 5):").grid(row=11, column=0,
                                                                                                 sticky=W, padx=2,
                                                                                                 pady=2)
    Entry(postfire, textvariable=INTERVAL, width=3).grid(row=11, column=1, sticky=W, padx=2, pady=2)

    Label(postfire, text="Cycles (e.g., 10):").grid(row=12, column=0, sticky=W, padx=2, pady=2)
    Entry(postfire, textvariable=REPS, width=3).grid(row=12, column=1, sticky=W, padx=2, pady=2)

    Label(postfire, text="Set temperature of RHX chamber (C):").grid(row=13, column=0, sticky=W, padx=2, pady=2)
    Entry(postfire, textvariable=TEMP, width=15).grid(row=13, column=1, sticky=W, padx=2, pady=2)

    Label(postfire, text="Set RH% of RHX chamber (%RH):").grid(row=14, column=0, sticky=W, padx=2, pady=2)
    Entry(postfire, textvariable=HUMIDITY, width=15).grid(row=14, column=1, sticky=W, padx=2, pady=2)

    Label(postfire, text="Enter Madge Tech Temperature (C)):").grid(row=15, column=0, sticky=W, padx=2, pady=2)
    Entry(postfire, textvariable=RHTEMP2000TEMP, width=15).grid(row=15, column=1, sticky=W, padx=2, pady=2)

    Label(postfire, text="Enter Madge Tech Humidity (%RH):").grid(row=16, column=0, sticky=W, padx=2, pady=2)
    Entry(postfire, text=RHTEMP2000HUMIDITY, width=15).grid(row=16, column=1, sticky=W, padx=2, pady=2)

    Label(postfire, text="Current Temperature of Chamber (C):").grid(row=17, column=0, sticky=W)
    Label(postfire, text=PRECISIONTEMP.get()).grid(row=17, column=1, sticky=W)

    Label(postfire, text="Current Humidity of Chamber (%RH):").grid(row=18, column=0, sticky=W)
    Label(postfire, text=HUMIDITY.get()).grid(row=18, column=1, sticky=W)

    Label(postfire, text="Operator Initials (e.g., CPL):").grid(row=21, column=0, sticky=W, padx=2, pady=2)
    Entry(postfire, textvariable=INITIALS.get(), width=4).grid(row=21, column=1, sticky=W, padx=2, pady=2)

    Button(postfire, text="Start Post Fire", command=go_postFire).grid(row=22, column=1, padx=2, pady=2)
    Button(postfire, text="Quit", command=quit_postfire).grid(row=22, column=0, padx=0, pady=2)

    #########################
    update_windows()


def quit_postfire():
    root.deiconfiy()
    DataReadWrite.closeDatabase()
    postfire.withdraw()


def go_postFire():
    runID = int(RUNID.get())
    if runID < 1:
        errorMessage("You must have a RunID to continue.")
        logger.debug("You must have a RunID entered in order to continue.")
        return False

    message = "You are going to run %d samples. Have you set up and weighed %d empty crucibles yet? If not, hit cancel. Otherwise, continue. " % (
        NUMBEROFSAMPLES.get(), NUMBEROFSAMPLES.get())
    if easygui.ccbox(msg=message, title='Check for empty crucibles'):
        pass
    else:
        return

    setInitials = str(INITIALS.get())
    duration = int(DURATION.get())
    setTemperature = float(LOCATION_TEMPERATURE.get())
    setHumidity = float(HUMIDITY.get())
    standardTemp = float(RHTEMP2000TEMP.get())
    standardRH = float(RHTEMP2000HUMIDITY.get())
    temp = xyzRobot.getTemperature()
    tempCorrection = standardTemp - temp
    rhCorrection = standardRH - xyzRobot.getHumidity()
    preOrPost = 2
    status = "postfire"
    numberOfSamples = NUMBEROFSAMPLES.get()
    startPosition = START_POSITION.get()
    intervalsec = int(INTERVAL.get())
    postMeasurementTimeInterval = int(DURATION.get())
    repetitions = int(REPS.get())

    value = DataReadWrite.updateRunPostFire(runID, status, postMeasurementTimeInterval, duration, repetitions,
                                            intervalsec, setHumidity)

    if value is False:
        logger.error("There has been an error since updateRunPostFire returned FALSE")
        errorMessage("There has been a problem with updateRunPostFire")
        return False

    d_dateTimeFiring = datetime
    try:
        (v_locationCode, i_numberOfSamples, t_assemblageName, f_locationTemperature, f_locationHumidity,
         d_dateTimeFiring, i_durationOfFiring, i_temperatureOfFiring, v_operatorName,
         t_notes) = DataReadWrite.getRunInfo(
            1)
    except:
        logger.error("There has been an error since DataReadWrite.getRunInfo(1) returned FALSE")
        errorMessage("There has been a problem with getRunInfo. Cannot read database")
        return False
    print "Date of Firing: ", d_dateTimeFiring
    dt = datetime
    try:
        dt = datetime.strptime(d_dateTimeFiring, "%Y-%m-%d %H:%M:%S")
    except:
        errorMessage("There has been a problem. The time/date for firing is not correct.")
        RUNINFOSTATUS.set("Date and/or time formats are incorrect. Reenter.")
        print "There is a problem with the date format..."
        return False
    end = timedelta(minutes=int(DURATIONOFFIRING.get()))
    endOfFiring = dt + end

    timeToCompletion = ((duration * numberOfSamples) + numberOfSamples) * repetitions
    end = timedelta(minutes=timeToCompletion)
    now = datetime.today()
    endOfRunTime = now + end
    endOfRun = endOfRunTime.strftime("%m-%d-%y %H:%M:%S")
    print "This run will end ca. ", endOfRun

    count = 0
    repeat = 1
    CYCLE.set(repeat)
    while repeat < (repetitions + 1):
        root.update()
        CYCLE.set(repeat)
        xyzRobot.weighAllSamplesPostFire(runID, duration,
                                         intervalsec, numberOfSamples, startPosition,
                                         endOfFiring, tempCorrection, rhCorrection, repeat,
                                         robotStatus, SAMPLE_POSITION, MCOUNT,
                                         CURRENTSTEP, STATUS, DURATION,
                                         LOGGERINTERVAL, RUNID, NUMBEROFSAMPLES,
                                         TIMEREMAINING, TIMEELAPSEDMIN, REPS, CYCLE)
        repeat += 1
        update_windows()
    root.update()
    root.deiconify()
    postfire.withdraw()
    value = DataReadWrite.closeDatabase()
    communication.sendEmail("RHX Status Change", "Postfire is complete!")
    ## now go home!
    xyzRobot.goHome()
    update_windows()
    return True


def moveMotorX():
    logger.debug("moveMotorX to %i", int(XMOTORPOSITION.get()))
    xyzRobot.moveMotorXToPosition(int(XMOTORPOSITION.get()))
    POSITION_NAME.set("UNKNOWN")
    sleep(2)
    logger.debug(
        "now located at x: %d y: %d z: %d" % (
        xyzRobot.getXPosition(), xyzRobot.getYPosition(), xyzRobot.getZPosition()))
    DataReadWrite.updatePosition(xyzRobot.getXPosition(), xyzRobot.getYPosition(), xyzRobot.getZPosition())
    update_windows()
    return True


def moveMotorY():
    logger.debug("moveMotorY to %i", int(YMOTORPOSITION.get()))
    xyzRobot.moveMotorYToPosition(int(YMOTORPOSITION.get()))
    POSITION_NAME.set("UNKNOWN")
    sleep(2)
    logger.debug(
        "now located at x: %d y: %d z: %d" % (
        xyzRobot.getXPosition(), xyzRobot.getYPosition(), xyzRobot.getZPosition()))
    DataReadWrite.updatePosition(xyzRobot.getXPosition(), xyzRobot.getYPosition(), xyzRobot.getZPosition())
    update_windows()
    return True


def setMotorXToZero():
    logger.debug("setMotorXToZero")
    xyzRobot.setXMotorPosition(0)
    XMOTORPOSITION.set("0")
    update_windows()
    return True


def setMotorYToZero():
    logger.debug("setMotorYToZero")
    xyzRobot.setYMotorPosition(0)
    YMOTORPOSITION.set("0")
    update_windows()
    return True


def setMotorsToZero(motorNumber):
    logger.debug("setMotorsToZero: %d", motorNumber)
    if motorNumber == 0:
        xyzRobot.setXMotorPosition(0)
        XMOTORPOSITION.set("0")
    elif motorNumber == 2:
        xyzRobot.setYMotorPosition(0)
        YMOTORPOSITION.set("0")
    else:
        logger.critical("Error - no such motor number: %d ", motorNumber)
    POSITION_NAME.set("HOME")
    update_windows()
    return True


def moveArmToPosition():
    logger.debug("moveArmToPosition: %d", int(ZMOTORPOSITION.get()))
    xyzRobot.moveArmToPosition(int(ZMOTORPOSITION.get()))
    update_windows()
    return True


def bumpXMotorUp():
    logger.debug("bumpXMotorUp: %d", int(MOTORSTEP.get()))
    xyzRobot.bumpXMotorUp(int(MOTORSTEP.get()))
    update_windows()


def bumpYMotorRight():
    logger.debug("bumpYMotorRight: %d", int(MOTORSTEP.get()))
    xyzRobot.bumpYMotorRight(int(MOTORSTEP.get()))
    update_windows()


def bumpYMotorLeft():
    logger.debug("bumpYMotorLeft: %d", int(MOTORSTEP.get()))
    xyzRobot.bumpYMotorLeft(int(MOTORSTEP.get()))
    update_windows()


def bumpXMotorDown():
    logger.debug("bumpXMotorDown: %d", int(MOTORSTEP.get()))
    xyzRobot.bumpXMotorDown(int(MOTORSTEP.get()))
    update_windows()


def bumpMotorNE():
    logger.debug("bumpMotorNE")
    logger.debug("bumpXMotorUp: %d", int(MOTORSTEP.get()))
    xyzRobot.bumpXMotorUp(int(MOTORSTEP.get()))
    logger.debug("bumpYMotorLeft: %d", int(MOTORSTEP.get()))
    xyzRobot.bumpYMotorLeft(int(MOTORSTEP.get()))
    update_windows()


def bumpMotorNW():
    logger.debug("bumpMotorNW")
    logger.debug("bumpXMotorUp: %d", int(MOTORSTEP.get()))
    xyzRobot.bumpXMotorUp(int(MOTORSTEP.get()))
    #update_windows()
    logger.debug("bumpYMotorRight: %d", int(MOTORSTEP.get()))
    xyzRobot.bumpYMotorRight(int(MOTORSTEP.get()))
    update_windows()


def bumpMotorSE():
    logger.debug("bumpMotorSE")
    logger.debug("bumpXMotorDown: %d", int(MOTORSTEP.get()))
    xyzRobot.bumpXMotorDown(int(MOTORSTEP.get()))
    #update_windows()
    logger.debug("bumpYMotorRight: %s", int(MOTORSTEP.get()))
    xyzRobot.bumpYMotorRight(int(MOTORSTEP.get()))
    update_windows()


def bumpMotorSW():
    logger.debug("bumpMotorSW")
    logger.debug("bumpXMotorDown: %d", int(MOTORSTEP.get()))
    xyzRobot.bumpXMotorDown(int(MOTORSTEP.get()))
    #update_windows()
    logger.debug("bumpYMotorLeft: %d", int(MOTORSTEP.get()))
    xyzRobot.bumpYMotorLeft(int(MOTORSTEP.get()))
    update_windows()


def bumpZMotorUp():
    logger.debug("bumpZMotorUp")
    logger.debug("bumpZMotorUp: %d", int(ZMOTORSTEP.get()))
    if int(ZMOTORSTEP.get()) > 100000:
        print "Too dangerous to move that far up in one move. Ignoring..."
    else:
        xyzRobot.bumpZMotorUp(int(ZMOTORSTEP.get()))

    update_windows()


def bumpZMotorDown():
    logger.debug("bumpZMotorDown")
    logger.debug("bumpZMotorDown: %d", int(ZMOTORSTEP.get()))
    if int(ZMOTORSTEP.get()) > 100000:
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
    (xpos, ypos) = xyzRobot.getCurrentXYCoordinates()
    (bal_xpos, bal_ypos) = DataReadWrite.getXYCoordinatesForInsideBalance()

    if ypos < (bal_ypos - 300):
        ## we are not on the balance so we cannot descend.
        print "Error:  we are not in a position to descend. Please move to the balance."
    else:
        xyzRobot.lowerArmToBalance()
        ARM_STATUS.set("BALANCE")
    update_windows()


def goHome():
    logger.debug("goHome: Go to Home Position")
    value = xyzRobot.goHome()
    if value == False:
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
    if xyzRobot.atXZero() == "TRUE":
        XZERO.set("TRUE")
        XMOTORPOSITION.set(0)
        ARM_STATUS.set("TOP")
        value = xyzRobot.setXMotorPosition(0)
        value = xyzRobot.setXCoordinate(0)

    if xyzRobot.atYZero() == "TRUE":
        YZERO.set("TRUE")
        YMOTORPOSITION.set(0)
        value = xyzRobot.setYMotorPosition(0)
        value = xyzRobot.setYCoordinate(0)

    if xyzRobot.atZZero() == "TRUE":
        ZZERO.set("TRUE")
        ZMOTORPOSITION.set(0)
        value = xyzRobot.setZMotorPosition(0)
        value = xyzRobot.setZCoordinate(0)
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
    BALANCEDOOR.set("OPEN")
    update_windows()


def closeBalanceDoor():
    logger.debug("closeBalanceDoor:  Close the balance door")
    (xpos, ypos) = xyzRobot.getCurrentXYCoordinates()
    (bal_xpos, bal_ypos) = DataReadWrite.getXYCoordinatesForOutsideBalance()
    if ypos <= bal_ypos:
        DataReadWrite.closeBalanceDoor()
        BALANCEDOOR.set("CLOSED")
    else:
        logger.warn("Cannot close door. Arm is inside balance.")
        #update_windows()
    update_windows()


def goToPosition():
    pos = SAMPLE_POSITION.get()
    if pos > MAXPOSITIONS.get():
        update_windows()
        return
    else:
        POSITION_NAME.set("SAMPLE")
        logger.debug("goToPosition:  Go to position: %i", int(pos))
        xyzRobot.goToSamplePosition(int(pos), startWindow=1)
        update_windows()


def refine():
    pos = SAMPLE_POSITION.get()
    if pos < MAXPOSITIONS.get() + 1:
        logger.debug("refine sample position: %i", int(pos))
        xyzRobot.refineSamplePosition(pos)
    elif pos == INSIDE_BALANCE_POSITION:
        logger.debug("refine inside balance position: %i", int(pos))
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
    BALANCEDOOR.set("OPEN")
    #update_windows()
    logger.debug("Go to inside of balance")
    SAMPLE_POSITION.set(OUTSIDE_BALANCE_POSITION)
    POSITION.set(OUTSIDE_BALANCE_POSITION)
    xyzRobot.goToInsideBalanceFromOutside()
    POSITION_NAME.set("INSIDE_BALANCE")
    POSITION.set(INSIDE_BALANCE_POSITION)
    update_windows()


def getSampleFromBalance():
    logger.debug("getSampleFromBalance: %d", SAMPLENUM.get())
    sampleNum = SAMPLENUM.get()
    if sampleNum < 1:
        errorMessage("You must enter a sample number to continue.")
        logger.warning("You must have a sample number in order to continue.")
        return False
    else:
        xyzRobot.goToOutsideBalanceFromOutside()
        SAMPLE_POSITION.set(OUTSIDE_BALANCE_POSITION)
        POSITION.set(OUTSIDE_BALANCE_POSITION)
        POSITION_NAME.set("OUTSIDE_BALANCE")
        openBalanceDoor()
        BALANCEDOOR.set("CLOSED")
        val = xyzRobot.goToInsideBalanceFromOutside()
        POSITION_NAME.set("INSIDE_BALANCE")
        SAMPLE_POSITION.set(INSIDE_BALANCE_POSITION)
        POSITION.set(INSIDE_BALANCE_POSITION)
        val = xyzRobot.pickUpSampleFromBalance()
        val = xyzRobot.goToOutsideBalanceFromInside()
        POSITION_NAME.set("OUTSIDE_BALANCE")
        SAMPLE_POSITION.set(OUTSIDE_BALANCE_POSITION)
        POSITION.set(OUTSIDE_BALANCE_POSITION)
        closeBalanceDoor()
        BALANCEDOOR.set("CLOSED")
        val = xyzRobot.goHome()
        POSITION_NAME.set("HOME")
        SAMPLE_POSITION.set(0)
        POSITION.set(0)
        val = xyzRobot.goToSamplePosition(sampleNum, startWindow=1)
        POSITION_NAME.set("SAMPLE")
        SAMPLE_POSITION.set(sampleNum)
        POSITION.set(sampleNum)
        val = xyzRobot.samplePutDown()
        val = xyzRobot.goHome()
        POSITION_NAME.set("HOME")
        POSITION.set(0)
        SAMPLE_POSITION.set(0)
        update_windows()
        return True


def fileDialog():
    dirname = tkFileDialog.askdirectory(parent=root, initialdir="/Users/Archy/Dropbox/Rehydroxylation/",
                                        title="Pick a directory ...")
    update_windows()
    return True


def findHome():
    logger.debug("first find zero on the X axis")
    xyzRobot.moveXUntilZero()
    logger.debug("first find zero on the Y axis")
    xyzRobot.moveYUntilZero()
    logger.debug("Now reset motors to Zero")
    xyzRobot.resetXYValuesToZero()
    POSITION_NAME.set("HOME")
    SAMPLE_POSITION.set(0)
    POSITION.set(0)
    update_windows()
    return True


def setAbsZeroXY():
    sampleLocation = SAMPLE_POSITION.get()
    position = POSITION.get()
    t = (sampleLocation, position)
    message = "Check that the arm is in the HOME Position. If okay, I will set HOME position to this spot."
    message += "I am currently at %s and position number %d." % t

    if xyzRobot.atXZero() == "TRUE" and xyzRobot.atYZero() == "TRUE":
        message += " Note that the X and Y sensors are NOT both TRUE. Are you absolutely certain? "

    value = are_you_sure(message)
    if value is True:
        SAMPLE_POSITION.set(HOME)
        POSITION_NAME.set("HOME")
        POSITION.set(HOME)
        XMOTORPOSITION.set(HOME)
        YMOTORPOSITION.set(HOME)
        returnValue = xyzRobot.setAbsZeroXY()
        update_windows()
        return True
    else:
        return False


def setXYForSampleLocation():
    sampleLocation = SAMPLE_POSITION.get()
    message = "Set the XY for sample position: %d " % sampleLocation
    value = are_you_sure(message)
    if value is True:
        x = int(xyzRobot.getXPosition())
        y = int(xyzRobot.getYPosition())
        value = DataReadWrite.updateXYForSampleLocation(sampleLocation, x, y)

        xD, yD = xyzRobot.getCurrentXYCoordinates()
        value = DataReadWrite.updateXYCoordinatesForSampleLocation(sampleLocation, xD, yD)
        update_windows()
        return value
    return False


def setZForSampleLocation():
    sampleZPosition = ZMOTORPOSITION.get()
    message = "Set Z position for samples to %s?" % sampleZPosition
    value = are_you_sure(message)
    if value is True:
        sampleLocation = SAMPLE_POSITION.get()
        value = DataReadWrite.updateZForSampleLocation(sampleLocation, sampleZPosition)
        update_windows()
        return value
    return False


def setZForBalanceLocation():
    balanceZPosition = ZMOTORPOSITION.get()
    message = "Set the Z position for the balance %s?" % balanceZPosition
    value = are_you_sure(message)
    if value is True:
        value = DataReadWrite.updateZForBalanceLocation(balanceZPosition)
        update_windows()
        return value
    return False


def setXYForAllLocations():
    message = "Set the X: %d  Y: %d values for all locations?"
    value = are_you_sure(message)
    if value is True:
        sampleLocation = SAMPLE_POSITION.get()
        originalX = 0
        originalY = 0
        (originalX, originalY) = DataReadWrite.getXYForSampleLocation(sampleLocation)
        x = int(xyzRobot.getXPosition())
        y = int(xyzRobot.getYPosition())
        diffX = originalX - x
        diffY = originalY - y
        pos = sampleLocation
        value = DataReadWrite.updateXYForSampleLocation(sampleLocation, x, y)
        while pos < MAXPOSITIONS.get() + 1:
            (originalX, originalY) = DataReadWrite.getXYForSampleLocation(pos)
            newX = originalX - diffX
            newY = originalY - diffY
            value = DataReadWrite.updateXYForSampleLocation(pos, newX, newY)
            pos += 1
        update_windows()
        return value
    return False


def setXYForInsideBalance():
    message = "Set the Inside Balance point here?"
    value = are_you_sure(message)
    if value is True:
        x = int(xyzRobot.getXPosition())
        y = int(xyzRobot.getYPosition())
        value = DataReadWrite.updateXYForInsideBalance(x, y)
        xC, yC = xyzRobot.getCurrentXYCoordinates()
        DataReadWrite.updateXYCoordinatesForInsideBalance(xC, yC)
        update_windows()
        return value
    return False


def setXYForOutsideBalance():
    message = "Set the Outside Balance point here?"
    value = are_you_sure(message)
    if value is True:
        x = int(xyzRobot.getXPosition())
        y = int(xyzRobot.getYPosition())
        value = DataReadWrite.updateXYForOutsideBalance(x, y)
        xC, yC = xyzRobot.getCurrentXYCoordinates()
        DataReadWrite.updateXYCoordinatesForOutsideBalance(xC, yC)
        update_windows()
        return value
    return False


def moveToNextSampleLocation():
    sampleLocation = int(SAMPLE_POSITION.get())
    ## first go home to set the position to ZERO then move to the point...
    xyzRobot.goHome()
    POSITION_NAME.set("HOME")
    ##print("Now at position %d" % (sampleLocation))

    sampleLocation += 1

    SAMPLE_POSITION.set(sampleLocation)
    POSITION_NAME.set("SAMPLE")
    POSITION.set(sampleLocation)
    value = 0
    if sampleLocation > MAXPOSITIONS.get():
        sampleLocation = 1

    ##print("Moving to position %d" % (sampleLocation))

    SAMPLE_POSITION.set(sampleLocation)

    goToPosition()
    POSITION_NAME.set("SAMPLE")
    update_windows()
    return True


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
    POSITION.set(OUTSIDE_BALANCE_POSITION)
    update_windows()
    return True


def goToInsideBalance():
    xyzRobot.goToOutsideBalanceFromOutside()
    POSITION_NAME.set("OUTSIDE_BALANCE")
    SAMPLE_POSITION.set(OUTSIDE_BALANCE_POSITION)
    POSITION.set(OUTSIDE_BALANCE_POSITION)
    update_windows()
    xyzRobot.goToInsideBalanceFromOutside()
    POSITION_NAME.set("INSIDE_BALANCE")
    POSITION.set(INSIDE_BALANCE_POSITION)
    update_windows()
    SAMPLE_POSITION.set(INSIDE_BALANCE_POSITION)
    return True


def setOutsideBalance():
    setXYForOutsideBalance()
    POSITION_NAME.set("OUTSIDE_BALANCE")
    SAMPLE_POSITION.set(OUTSIDE_BALANCE_POSITION)
    POSITION.set(OUTSIDE_BALANCE_POSITION)
    update_windows()
    return True


def setInsideBalance():
    setXYForInsideBalance()
    POSITION_NAME.set("INSIDE_BALANCE")
    SAMPLE_POSITION.set(INSIDE_BALANCE_POSITION)
    POSITION.set(INSIDE_BALANCE_POSITION)
    update_windows()
    return True


def checkEachSamplePosition():
    print "Ill only check the first 5 sample locations"
    sampleLocation = 1
    print "First, go home."
    value = xyzRobot.goHome()
    POSITION_NAME.set("HOME")
    POSITION.set(HOME)
    SAMPLE_POSITION(HOME)
    print "make sure gripper is open..."
    value = xyzRobot.openGripper()
    GRIPPERPOSITION.set("OPEN - DISENGAGED")
    while sampleLocation < MAXPOSITIONS.get() + 1:
        print "Going to location: ", sampleLocation
        value = xyzRobot.goToSamplePosition(sampleLocation, startWindow=1)
        POSITION_NAME.set("SAMPLE")
        POSITION.set(sampleLocation)
        SAMPLE_POSITION.set(sampleLocation)
        print "Lower arm to sample"
        value = xyzRobot.lowerArmToSample()
        ARM_STATUS.set("SAMPLE")
        print "Close gripper"
        value = xyzRobot.closeGripper()
        GRIPPERPOSITION.set("CLOSED - ENGAGED")
        print "Open gripper"
        value = xyzRobot.openGripper()
        GRIPPERPOSITION.set("OPEN - DISENGAGED")
        print "Raise arm to top"
        value = xyzRobot.raiseArmToTop()
        ARM_STATUS.set("TOP")
        print "Next..."
        sampleLocation += 1
    print "Now go home"
    value = xyzRobot.goHome()
    POSITION_NAME.set("HOME")
    POSITION.set(HOME)
    SAMPLE_POSITION.set(HOME)
    print "Done."
    update_windows()


def visitEachSampleLocation():
    """
    visitEachSampleLocation() function will move the robot arm to each location one at a time. It'll pause at each location and ask whether
    the location is good.  Then it will allow one to "bump" the location one direction or another. One can then "save" the
    new location. This will require switching the locations of the crucibles to the XY database.
    """
    xyzRobot.goHome()
    SAMPLE_POSITION.set(HOME)
    POSITION.set(HOME)
    POSITION_NAME.set("HOME")
    sampleLocation = 1
    if sampleLocation > 0:
        value = xyzRobot.goToSamplePosition(sampleLocation, 1)
        POSITION_NAME.set("SAMPLE")
        POSITION.set(sampleLocation)
        SAMPLE_POSITION.set(sampleLocation)
        if value is False:
            errorMessage("There was a problem going to position 1.")
            return False
    moveArm.deiconify()
    SAMPLE_POSITION.set(sampleLocation)
    POSITION.set(sampleLocation)

    Button(moveArm, text="+X Axis", command=bumpXMotorUp).grid(row=1, column=1)
    Button(moveArm, text="-Y Axis", command=bumpYMotorLeft).grid(row=2, column=0, sticky=E)
    Button(moveArm, text="+Y Axis", command=bumpYMotorRight).grid(row=2, column=2, sticky=W)
    Button(moveArm, text="-X Axis", command=bumpXMotorDown).grid(row=3, column=1)
    Button(moveArm, text="NE", command=bumpMotorNE).grid(row=1, column=0, sticky=E)
    Button(moveArm, text="NW", command=bumpMotorNW).grid(row=1, column=2, sticky=W)

    Label(moveArm, textvariable=POSITION).grid(row=2, column=1)
    Button(moveArm, text="SE", command=bumpMotorSE).grid(row=3, column=2, sticky=W)
    Button(moveArm, text="SW", command=bumpMotorSW).grid(row=3, column=0, sticky=E)

    Label(moveArm, text="Step Size").grid(row=4, column=0, sticky=W)
    Entry(moveArm, textvariable=MOTORSTEP).grid(row=4, column=1, sticky=W)
    Button(moveArm, text="Set XY for this crucible position", command=setXYForSampleLocation).grid(row=5, column=0)
    Button(moveArm, text="Update all XYs based on this position", command=setXYForAllLocations).grid(row=5, column=1)
    Button(moveArm, text="Next position", command=moveToNextSampleLocation).grid(row=5, column=2)
    Button(moveArm, text="Go to Outside Balance Point", command=goToOutsideBalance).grid(row=6, column=0)
    Button(moveArm, text="Set Outside Balance Point", command=setOutsideBalance).grid(row=6, column=1)
    Button(moveArm, text="Go to Home Position(0,0)", command=goHome).grid(row=6, column=2)
    Button(moveArm, text="Go to Inside Balance Point", command=goToInsideBalance).grid(row=7, column=0)
    Button(moveArm, text="Set Inside Balance Point", command=setInsideBalance).grid(row=7, column=1)
    Button(moveArm, text="Cancel", command=backToMainWindowFromMoveArm).grid(row=8, column=2)

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

    if file is None:
        return
    value = DataReadWrite.reopenDatabase(file)
    runID = DataReadWrite.getLastRunID()
    RUNID.set(runID)
    update_windows()
    return value


def refinePosition():
    position = SAMPLE_POSITION.get()
    xyzRobot.refinePosition(position)
    update_windows()
    return


def loadRun():
    RUNID.set(SETRUNID.get())
    update_windows()
    return True


def setXMaxVelocity():
    maxvelocity = MAXXMOTORVELOCITY.get()
    xyzRobot.setXMotorVelocityLimit(maxvelocity)
    #MAXXMOTORVELOCITY.set(xyzRobot.getXMotorVelocityLimit())
    update_windows()
    return


def setYMaxVelocity():
    maxvelocity = MAXYMOTORVELOCITY.get()
    xyzRobot.setYMotorVelocityLimit(maxvelocity)
    #MAXYMOTORVELOCITY.get(xyzRobot.getYMotorVelocityLimit())
    update_windows()
    return


def setZMaxVelocity():
    maxvelocity = MAXZMOTORVELOCITY.get()
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
##############################################################

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


##Motor X Controls
Label(root, text="X-Axis").grid(row=1, column=0, sticky=E, padx=2, pady=2)
Entry(root, textvariable=XMOTORPOSITION, width=6).grid(row=1, column=1, sticky=W, padx=2, pady=2)
Button(root, text="Move X", command=moveMotorX).grid(row=1, column=2, padx=2, pady=2, sticky=W)
Button(root, text="Set Current Position of X to 0", command=setMotorXToZero).grid(row=1, column=3, padx=2, pady=2,
                                                                                  sticky=W)
Button(root, text="Move X until zero", command=moveUntilXZero).grid(row=1, column=4, padx=2, pady=1)

##Motor Y Controls
Label(root, text="Y-Axis").grid(row=3, column=0, sticky=E, padx=2, pady=2)
Entry(root, textvariable=YMOTORPOSITION, width=6).grid(row=3, column=1, sticky=W)
Button(root, text="Move Y", command=moveMotorY).grid(row=3, column=2, padx=2, pady=2, sticky=W)
Button(root, text="Set Current Position of Y to 0", command=setMotorYToZero).grid(row=3, column=3, padx=2, pady=2,
                                                                                  sticky=W)
Button(root, text="Move Y until zero", command=moveUntilYZero).grid(row=3, column=4, padx=2, pady=2)

##Motor Z Controls
Label(root, text="Z-Axis").grid(row=4, column=0, sticky=E, padx=2, pady=2)
Entry(root, textvariable=ZMOTORPOSITION, width=6).grid(row=4, column=1, sticky=W, padx=2, pady=2)
Button(root, text="Move Z", command=moveArmToPosition).grid(row=4, column=2, sticky=W, padx=2, pady=2)
Button(root, text="Set Current Position of Z to 0", command=resetZToZero).grid(row=4, column=3, padx=2, pady=2,
                                                                               sticky=W)
Button(root, text="Move Z until zero", command=resetZMotorToZeroPosition).grid(row=4, column=4, padx=2, pady=2)

Button(root, text="+Y Axis", command=bumpYMotorRight).grid(row=5, column=1, padx=2, pady=2)
Button(root, text="-X Axis", command=bumpXMotorDown).grid(row=6, column=0, sticky=E, padx=2, pady=2)
Spinbox(root, textvariable=MOTORSTEP, width=6).grid(row=6, column=1, padx=2, pady=2)
Button(root, text="+X Axis", command=bumpXMotorUp).grid(row=6, column=2, sticky=W)
Button(root, text="-Y Axis", command=bumpYMotorLeft).grid(row=7, column=1, padx=2, pady=2)

Button(root, text="Up Z", command=bumpZMotorUp).grid(row=5, column=3, padx=2, pady=2)
Button(root, text="Raise to Top", command=raiseArmToTop).grid(row=5, column=4, padx=2, pady=2)
Entry(root, textvariable=ZMOTORSTEP, width=6).grid(row=6, column=3, padx=2, pady=2)
Button(root, text="Lower to Sample", command=lowerArmToSample).grid(row=6, column=4, padx=2, pady=2)
Button(root, text="Down Z", command=bumpZMotorDown).grid(row=7, column=3, padx=2, pady=2)
Button(root, text="Lower to Balance", command=lowerArmToBalance).grid(row=7, column=4, padx=2, pady=2)

##Balance Door controller
Label(root, text="Balance Door").grid(row=11, column=0, sticky=E, padx=2, pady=2)
Button(root, text="Open", command=openBalanceDoor).grid(row=11, column=1, sticky=E, padx=2, pady=2)
Button(root, text="Close", command=closeBalanceDoor).grid(row=11, column=2, sticky=W, padx=2, pady=2)
Label(root, text="Balance Door").grid(row=11, column=3, sticky=E, padx=2, pady=2)
Label(root, textvariable=BALANCEDOOR).grid(row=11, column=4, sticky=W, padx=2, pady=2)

##Balance Zeroing
Label(root, text="Tare the Balance").grid(row=12, column=0, sticky=E, padx=2, pady=2)
Button(root, text="Tare", command=BZero).grid(row=12, column=1, sticky=W, padx=2, pady=2)

Label(root, text="Balance Reading (g) ").grid(row=13, column=0, sticky=E, padx=2, pady=2)
Label(root, textvariable=BALANCEWEIGHT).grid(row=13, column=1, sticky=W, padx=2, pady=2)
Label(root, textvariable=BALANCESTATUS).grid(row=13, column=2, sticky=W, padx=2, pady=2)

Label(root, text="Low Precision Temp (C)").grid(row=14, column=0, sticky=E, padx=2, pady=2)
Label(root, textvariable=TEMPERATURE).grid(row=14, column=1, sticky=W, padx=2, pady=2)
Label(root, text="Humidity (%RH)").grid(row=14, column=2, sticky=E, padx=2, pady=2)
Label(root, textvariable=HUMIDITY).grid(row=14, column=3, sticky=W, padx=2, pady=2)

Label(root, text="Precision Temp C").grid(row=15, column=0, sticky=E, padx=2, pady=2)
Label(root, textvariable=PRECISIONTEMP).grid(row=15, column=1, sticky=W, padx=2, pady=2)

Label(root, text="Standard Balance (g)").grid(row=15, column=2, sticky=E, padx=2, pady=2)
Label(root, textvariable=STANDARD_BALANCE).grid(row=15, column=3, sticky=W, padx=2, pady=2)
Label(root, text="Using Standard Balance").grid(row=16, column=0, sticky=E, padx=2, pady=2)
Label(root, textvariable=USINGSTANDARDBALANCE).grid(row=16, column=1, sticky=W, padx=2, pady=2)

Label(root, text="Starting Sample Position").grid(row=17, column=0, sticky=E, padx=2, pady=2)
Spinbox(root, textvariable=START_POSITION, from_=1, to=25).grid(row=17, column=1, sticky=W, padx=2, pady=2)

listOfLocations = (
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 10000, 20000)
Label(root, text="Go To Sample Position Number").grid(row=18, column=0, sticky=E, padx=2, pady=2)
Spinbox(root, textvariable=SAMPLE_POSITION, values=listOfLocations, borderwidth=2).grid(row=18, column=1, sticky=W,
                                                                                        padx=2, pady=2)
Button(root, text="GO", command=goToPosition).grid(row=18, column=2, sticky=W, padx=2, pady=2)
Button(root, text="Refine Position", command=refine).grid(row=18, column=3, sticky=W, padx=2, pady=2)

Label(root, text="Retrieve Sample from Balance").grid(row=19, column=0, sticky=E, padx=2, pady=2)
Spinbox(root, textvariable=SAMPLENUM, from_=1, to=25).grid(row=19, column=1, sticky=W, padx=2, pady=2)
Button(root, text="GO", command=getSampleFromBalance).grid(row=19, column=2, sticky=W, padx=2, pady=2)

Label(root, text="Current Position:").grid(row=20, column=1, sticky=E, padx=2, pady=2)
Label(root, textvariable=POSITION_NAME).grid(row=20, column=2, sticky=W, padx=2, pady=2)
Label(root, text="Arm Location (Z)").grid(row=20, column=3, sticky=E, padx=2, pady=2)
Label(root, textvariable=ARM_STATUS).grid(row=20, column=4, sticky=W, padx=2, pady=2)

Label(root, text="X Coordinate (roller)").grid(row=21, column=0, sticky=E, padx=2, pady=2)
Label(root, textvariable=ABSOLUTEXPOSITION).grid(row=21, column=1, sticky=W, padx=2, pady=2)
Label(root, text="Y Coordinate (roller)").grid(row=21, column=2, sticky=E, padx=2, pady=2)
Label(root, textvariable=ABSOLUTEYPOSITION).grid(row=21, column=3, sticky=W, padx=2, pady=2)
Label(root, text="Z Coordinate (roller)").grid(row=21, column=4, sticky=E, padx=2, pady=2)
Label(root, textvariable=ABSOLUTEZPOSITION).grid(row=21, column=5, sticky=W, padx=2, pady=2)

Label(root, text="X Zero?").grid(row=22, column=0, sticky=E, padx=2, pady=2)
Label(root, textvariable=XZERO).grid(row=22, column=1, sticky=W, padx=2, pady=2)
Label(root, text="Y Zero?").grid(row=22, column=2, sticky=E, padx=2, pady=2)
Label(root, textvariable=YZERO).grid(row=22, column=3, sticky=W, padx=2, pady=2)
Label(root, text="Z Zero?").grid(row=22, column=4, sticky=E, padx=2, pady=2)
Label(root, textvariable=ZZERO).grid(row=22, column=5, sticky=W, padx=2, pady=2)

Label(root, text="X Motor Position").grid(row=23, column=0, sticky=E, padx=2, pady=2)
Label(root, textvariable=XMOTORPOSITION).grid(row=23, column=1, sticky=W, padx=2, pady=2)

Label(root, text="Y Motor Position").grid(row=23, column=2, sticky=E, padx=2, pady=2)
Label(root, textvariable=YMOTORPOSITION).grid(row=23, column=3, sticky=W, padx=2, pady=2)

Label(root, text="Z Motor Position").grid(row=23, column=4, sticky=W, padx=2, pady=2)
Label(root, textvariable=ZMOTORPOSITION).grid(row=23, column=5, sticky=W, padx=2, pady=2)

Button(root, text="Release Crucible/Close Gripper", command=openGripper).grid(row=24, sticky=E, column=0, padx=2,
                                                                              pady=2)
Button(root, text="Engage Crucible/Open Gripper", command=closeGripper).grid(row=24, sticky=W, column=1, padx=2, pady=2)
Label(root, text="Gripper Position").grid(row=24, column=2, sticky=E, padx=2, pady=2)
Label(root, textvariable=GRIPPERPOSITION).grid(row=24, column=3, sticky=W, padx=2, pady=2)

#Button(root, text="Lasers On", command=lasersOn).grid(row=25, column=0, padx=2, pady=2)
#Button(root, text="Lasers Off", command=lasersOff).grid(row=25, column=1, padx=2, pady=2)

Button(root, text="Chamber Lights On", command=turnLightOn).grid(row=25, column=0, sticky=E, padx=2, pady=2)
Button(root, text="Chamber Lights Off", command=turnLightOff).grid(row=25, column=1, sticky=W, padx=2, pady=2)
Label(root, text="Lights").grid(row=25, column=2, sticky=E, padx=2, pady=2)
Label(root, textvariable=LIGHTSTATUS).grid(row=25, column=3, sticky=W, padx=2, pady=2)

Label(root, text="X Motor Max").grid(row=26, column=0, padx=2, pady=2)
Entry(root, textvariable=MAXXMOTORVELOCITY, width=8).grid(row=26, column=1, padx=2, pady=2)
Button(root, text="Set X Motor Max", command=setXMaxVelocity).grid(row=26, column=2, padx=2, pady=2)
Button(root, text="Disengage Steppers", command=xyzRobot.disengageMotors).grid(row=26, column=3, padx=2, pady=2)

Label(root, text="Y Motor Max").grid(row=27, column=0, padx=2, pady=2)
Entry(root, textvariable=MAXYMOTORVELOCITY, width=8).grid(row=27, column=1, padx=2, pady=2)
Button(root, text="Set Y Motor Max Velocity", command=setYMaxVelocity).grid(row=27, column=2, padx=2, pady=2)

Label(root, text="Z Motor Max").grid(row=28, column=0, padx=2, pady=2)
Entry(root, textvariable=MAXZMOTORVELOCITY, width=8).grid(row=28, column=1, padx=2, pady=2)
Button(root, text="Set Z Motor Max", command=setZMaxVelocity).grid(row=28, column=2, padx=2, pady=2)

Button(root, text="Go Directly to Balance", command=goToBalance).grid(row=29, column=0, padx=2, pady=2)
Button(root, text="Update this Window", command=update_windows).grid(row=29, column=2, padx=2, pady=2)

Button(root, text="Find XY Home Position", command=findHome).grid(row=30, column=0, padx=2, pady=2)
Button(root, text="Set Positions", command=visitEachSampleLocation).grid(row=30, column=1, padx=2,
                                                                         pady=2)
Button(root, text="Check Positions", command=checkEachSamplePosition).grid(row=30, column=2, padx=2,
                                                                           pady=2)
Button(root, text="Set Home to this XY Location", command=setAbsZeroXY).grid(row=30, column=3, padx=2, pady=2)

Button(root, text="Go Home", command=goHome).grid(row=31, column=0, padx=2, pady=2)

Button(root, text="Set XY for this sample position", command=setXYForSampleLocation).grid(row=31, column=3, padx=2,
                                                                                          pady=2)

Button(root, text="Go to Outside Balance Point", command=goToOutsideBalance).grid(row=32, column=0, padx=2, pady=2)

Button(root, text="Set Z for Sample Position", command=setZForSampleLocation).grid(row=32, column=2, padx=2, pady=2)
Button(root, text="Set XY for Outside Balance Point", command=setOutsideBalance).grid(row=32, column=3, padx=2, pady=2)

Button(root, text="Go to Inside Balance Point", command=goToInsideBalance).grid(row=33, column=0, padx=2, pady=2)
Button(root, text="Set XY for Inside Balance Point", command=setInsideBalance).grid(row=33, column=3, padx=2, pady=2)
Button(root, text="Set Z for Balance Position", command=setZForBalanceLocation).grid(row=33, column=2, padx=2, pady=2)

Label(root, text="Run ID:").grid(row=34, column=0, sticky=E, padx=2, pady=2)
Label(root, textvariable=SETRUNID).grid(row=34, column=1, sticky=W, padx=2, pady=2)
Button(root, text="Refine Position", command=refinePosition).grid(row=34, column=3, padx=2, pady=2)

##start the other scripts
Button(root, text="1. Empty Crucibles", command=initialize).grid(row=35, column=0, padx=2, pady=2)
Button(root, text="2. Setup Samples", command=setup).grid(row=35, column=1, padx=2, pady=2)
Button(root, text="3. Post-Fire RHX", command=postFire).grid(row=35, column=2, padx=2, pady=2)

Button(root, text="<Quit>", command=quit).grid(row=35, column=3, padx=2, pady=2)

root.mainloop()

