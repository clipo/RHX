__author__ = 'clipo'

#Basic imports

import sqlite3 as sqlite
import sys
import logging

import easygui


sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
from ctypes import *
import os
import io
import re
import serial
from time import sleep
import sched, time
from datetime import datetime
from datetime import timedelta
import msvcrt
import os, sys
from Tkinter import *
from numpy import *
import math
import ComPorts
import tkFileDialog
from tkMessageBox import *
from tkColorChooser import askcolor
from tkFileDialog import askopenfilename


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


logger = logging.getLogger("weighApp")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
today_date = datetime.today()
datestring = today_date.strftime("%Y-%m-%d-%H-%M")
debugfilename = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Logs/weighApp-" + datestring + "_debug.log"
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

root = Tk()
root.wm_title("Weight Measurement")
init = Toplevel()
init.withdraw()
emptyCrucibles = Toplevel()
emptyCrucibles.withdraw()
emptyCrucibles.wm_title("Empty Crucible Weight Measurement")
noteText = Text(emptyCrucibles)
prefireCrucibles = Toplevel()
prefireCrucibles.wm_title("Prefire (105) Crucible Weight Measurement")
prefireCrucibles.withdraw()
statusWindow = Toplevel()
statusWindow.withdraw()

prefireStatusWindow = Toplevel()
prefireStatusWindow.withdraw()

postfireStatusWindow = Toplevel()
postfireStatusWindow.withdraw()

initialSherds = Toplevel()
initialSherds.withdraw()
initialSherds.wm_title("Initial Sherd Weight")
alertWindow = Toplevel()
alertWindow.withdraw()
postfireCrucibles = Toplevel()
postfireCrucibles.wm_title("Postfire (550) Crucible Weight Measurement")
postfireCrucibles.withdraw()

standard_balance = serial.Serial(port=ComPorts.SampleBalance, baudrate=9600, bytesize=8, parity='N', stopbits=1,
                                 timeout=1, xonxoff=0)

SQLFILENAME = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/SQL/RHX-New.sql"
XYDBFILENAME = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Data/RHX.sqlite"
#  open the sqlite database and create a connection
# create a cursor to the database

xyconn = sqlite.connect(XYDBFILENAME, detect_types=sqlite.PARSE_DECLTYPES)
path = 'c:\Users\Archy\Dropbox\Rehydroxylation\Logger\RequiredFiles\libsqlitefunctions.so'
# open the sqlite database and create a connection
# create a cursor to the database
xyconn.enable_load_extension(True)
xyconn.load_extension(path)
xyconn.row_factory = dict_factory

INITIALS = StringVar()
NUMBEROFCRUCIBLES = IntVar()
RUNID = IntVar()
FILENAME = StringVar()
CURRENTCRUCIBLE = IntVar()
MCOUNT = IntVar()
TIMEREMAINING = IntVar()
DIRECTORY = StringVar()
#DIRECTORY.set("c:\\users\\archy\\dropbox\\Rehydroxylation\\Logger\\Data\\")
STATUS = StringVar()
AVERAGEWEIGHT = DoubleVar()
STDDEVWEIGHT = DoubleVar()
ACOUNT = IntVar()
STOPPED = IntVar()
NEXTSTEP = IntVar()
LOCATION = StringVar()
ASSEMBLAGE = StringVar()
TEMPERATURE = DoubleVar()
FIRINGTEMPERATURE = IntVar()
FIRINGDURATION = IntVar()
SHERDID = StringVar()
LOCATIONTEMPERATURE = DoubleVar()
DATEOFFIRING = StringVar()
TIMEOFFIRING = StringVar()
RUNINFOSTATUS = StringVar()
RESUBMIT = StringVar()
NOTES = StringVar()
CURRENTDATETIME = StringVar()


def ask_for_delete_file(filename):
    msg = "File already exits.  Do you want to delete the file: %s ?" % filename
    title = "Delete File?"
    if easygui.ccbox(msg, title):     # show a Continue/Cancel dialog
        pass  # user chose Continue
    else:
        sys.exit(0)


def no_fileordirname():
    msg = "You must enter a filename and directory."
    title = "ERROR: NO FILENAME OR DIRNAME"
    while 1:
        easygui.msgbox(msg, title, ok_button="Exit")     # show a Continue/Cancel dialog
    return


def initializeDatabase(dirname, filename):
    global conn

    dbfilename = easygui.filesavebox(msg='Create a new file for this set of samples.', title='New Database',
                                     default="C:/Users/Archy/Dropbox/Rehydroxylation/Logger/Data/*.sqlite",
                                     filetypes='*.sqlite')
    if dbfilename is None:
        return
    if os.path.exists(dbfilename) is True:
        value = ask_for_delete_file(dbfilename)
        os.remove(dbfilename)

    # open the sqlite database and create a connection
    conn = sqlite.connect(dbfilename, detect_types=sqlite.PARSE_DECLTYPES)
    # create a cursor to the database

    path = '../RequiredFiles/libsqlitefunctions.so'
    # open the sqlite database and create a connection
    # create a cursor to the database
    conn.enable_load_extension(True)
    conn.load_extension(path)
    conn.row_factory = dict_factory
    try:
        c = conn.cursor()
        ##dbfilename="c:/Users/Archy/Dropbox/Rehydroxylation/RHX.sql"
        for line in open(SQLFILENAME):
            c.execute(line)
            conn.commit()
        return True;
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred trying to open teh SQLFILENAME: %s", msg)
        return False;


def openDatabase():
    global conn

    dbfilename = easygui.fileopenbox(msg='Open an existing sqlite file for this set of samples.', title='Open Database',
                                     default="C:/Users/Archy/Dropbox/Rehydroxylation/Logger/Data/*.sqlite",
                                     filetypes='*.sqlite')
    if dbfilename is None:
        return
    try:
        conn = sqlite.connect(dbfilename, detect_types=sqlite.PARSE_DECLTYPES, isolation_level=None)
        path = '../RequiredFiles/libsqlitefunctions.so'
        # open the sqlite database and create a connection
        # create a cursor to the database
        conn.enable_load_extension(True)
        conn.load_extension(path)
        conn.row_factory = dict_factory
        return True;
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False;

## if the sqlite file is already in existence and you have the file handle -- just need to do this...
def reopenDatabase():
    dbfilename = easygui.fileopenbox(msg='Open an existing sqlite file for this set of samples.', title='Open Database',
                                     default="C:/Users/Archy/Dropbox/Rehydroxylation/Logger/Data/*.sqlite",
                                     filetypes='*.sqlite')
    #print "filename:", filename
    if dbfilename is None:
        return
    global conn
    try:
        conn = sqlite.connect(dbfilename, detect_types=sqlite.PARSE_DECLTYPES, isolation_level=None)
        path = '../RequiredFiles/libsqlitefunctions.so'
        # open the sqlite database and create a connection
        # create a cursor to the database
        conn.enable_load_extension(True)
        conn.load_extension(path)
        conn.row_factory = dict_factory
        return True;
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False;


def closeDatabase():
# Ensure variable is defined
    try:
        conn
    except NameError:
        conn = None
    if conn is not None:
        try:
            conn.commit()
            conn.close()
            return True;
        except sqlite.OperationalError, msg:
            logger.error("A SQL error occurred: %s", msg)
            return False;
    return True


def readStandardBalance():
    try:
        standard_balance.write('P\n\r')
    except:
        pass

    try:
        out = standard_balance.readline()
    except:
        out = None

    if out is not None:
        if out.count(' g') == 1:
            out = out.replace('g', '')
            out = out.replace(' ', '')
            out = out.rstrip()
            return float(out)
    else:
        return False


def insertRun(setInitials, today, numberOfSamples, v_locationCode, t_assemblageName, f_locationTemperature, t_notes):
    logger.debug("insert run")
    now = datetime.today()
    try:
        t = (setInitials, now, numberOfSamples, v_locationCode, t_assemblageName, f_locationTemperature, t_notes)
        # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        c.execute(
            'insert into tblRun (v_operatorName,d_datetime,i_numberOfSamples, v_locationCode, t_assemblageName,f_locationTemperature,t_notes) VALUES (?,?,?,?,?,?,?)',
            t)
        logger.debug(
            'insert into tblRun (v_operatorName,d_datetime,i_numberOfSamples,v_locationCode, t_assemblageName,f_locationTemperature,t_notes) VALUES (%s,%s,%d,%s,%s,%f,%s)' % (
                t))
        # Save (commit) the changes
        conn.commit()
        # Now get the id for the run so we can update with other info as we ask...
        runID = c.lastrowid
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False
    MCOUNT.set(0)
    return runID


def insertEmptyCrucible(runID, positionNumber):
    logger.debug("insert empty crucible measurement into tblCrucible")
    # preOrPost 0=empty 1=pre with sample, 2=105 Degree (with sample) 3=550 Degree (with sample)
    crucibleID = 0
    now = datetime.today()
    if STOPPED.get() > 0:
        # print "ooops!!!"
        return
    try:
        c = conn.cursor()
        t = (1, positionNumber, now)
        ## note that weight of the crucible is in tblCrucible twice -- as f_averageWeight and f_emptyWeightAverage. Need to collapse those...
        c.execute('insert into tblCrucible (i_runID,i_positionNumber,d_emptyWeightDateTime) VALUES (?,?,?)', t)
        conn.commit()
        crucibleID = c.lastrowid
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False;
    MCOUNT.set(0)
    return crucibleID


def insertEmptySample(runID, positionNumber):
    logger.debug("insert empty sample measurement into tblSample with just the crucible info")
    # preOrPost 0=empty 1=pre with sample, 2=105 Degree (with sample) 3=550 Degree (with sample)
    crucibleID = 0
    now = datetime.today()
    if STOPPED.get() > 0:
        # print "ooops!!!"
        return
    try:
        c = conn.cursor()
        t = (1, positionNumber, positionNumber, now)
        c.execute('insert into tblSample (i_runID,i_positionNumber,i_crucibleID,d_datetime) VALUES (?,?,?,?)', t)
        conn.commit()
        crucibleID = c.lastrowid
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False;
    MCOUNT.set(0)
    return crucibleID


def insertInitialSherd(i_runID, i_crucibleID, sherdID, assemblage, locationTemperature):
    logger.debug("insert initial sample into tblSample")
    ## note that I am actually updating the sample record since I created it when I did the crucible record - method
    # updateEmptyCrucible
    if STOPPED.get() > 0:
        # print "ooops!!!"
        return
    try:
        # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        t = (sherdID, assemblage, locationTemperature, 1, i_crucibleID )
        c.execute(
            'update tblSample set t_sampleName=?, t_assemblageName=?, f_locationTemperature=? where i_runID=? and '
            'i_positionNumber=?', t)
        conn.commit()
        sampleID = c.lastrowid
        return sampleID
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False


def updateEmptyCrucible(runID, crucible, weightAverage, weightStdDev, weightCount):
    if STOPPED.get() > 0:
    # print "ooops!!!"
        return
    logger.debug("update empty crucible weight, etc.")

    now = datetime.today()
    today = now.strftime("%m-%d-%y %H:%M:%S")
    try:
        c = conn.cursor()
        t = (weightAverage, weightStdDev, weightCount, weightAverage, weightStdDev, weightCount, today, crucible, runID)
        logger.debug(
            'update tblCrucible SET f_averageWeight=%f,f_stdevWeight=%f,i_count=%d, f_emptyWeightAverage=%f, f_emptyWeightStdDev=%f,i_emptyWeightCount=%d, d_dateTime=%s WHERE i_positionNumber=%d AND i_runID=%d' % t)
        c.execute(
            'update tblCrucible SET f_averageWeight=?,f_stdevWeight=?,i_count=?, f_emptyWeightAverage=?, f_emptyWeightStdDev=?,i_emptyWeightCount=?, d_dateTime=? WHERE i_positionNumber=? AND i_runID=?',
            t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False
        ## note I am going to update the record so it must exist prior to this.
    try:
        c = conn.cursor()
        t = (weightAverage, weightStdDev, today, crucible, runID)
        logger.debug('update tblSample SET f_crucibleWeightAverage=%f, f_crucibleWeightStdDev=%f,'
                     'd_datetime=%s WHERE i_positionNumber=%d and i_runID=%d' % t)
        c.execute('update tblSample SET f_crucibleWeightAverage=?, f_crucibleWeightStdDev=?,'
                  'd_datetime=? WHERE i_positionNumber=? and i_runID=?', t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False
    return True


def updateInitialSherd(runID, crucible, weightAverage, weightStdDev):
    logger.debug("update initial sherd weight, etc.")
    now = datetime.today()
    if STOPPED.get() > 0:
        # print "ooops!!!"
        return
    try:
        c = conn.cursor()
        t = (weightAverage, weightStdDev, crucible, runID)
        c.execute(
            'update tblSample SET f_sherdWeightInitialAverage=?, f_sherdWeightInitialStdDev=? WHERE i_positionNumber=? AND i_runID=?'
            , t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False
    return True


def update105Crucible(runID, crucible, weightAverage, weightStdDev, weightCount):
    logger.debug("update crucible record with prefire ( 105) weight, etc.")
    now = datetime.today()
    if STOPPED.get() > 0:
        # print "ooops!!!"
        return
    try:
        c = conn.cursor()
        t = (weightAverage, weightStdDev, weightCount, now, crucible, runID)
        c.execute(
            'update tblCrucible SET f_105WeightAverage=?, f_105WeightStdDev=?, i_105WeightCount=?, d_105WeightDateTime=? WHERE i_positionNumber=? AND i_runID=?'
            , t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False
    MCOUNT.set(0)
    return True


def update105Sample(runID, crucible, weightAverage, weightStdDev):
    logger.debug("update sample record with prefire ( 105) weight, etc.")
    ## the weight of the crucible has ALREADY been removed.
    if STOPPED.get() > 0:
        #print "ooops!!!"
        return
    try:
        c = conn.cursor()
        t = (weightAverage, weightStdDev, crucible, runID)
        c.execute(
            'update tblSample SET f_preWeightAverage=?, f_preWeightStdDev=? WHERE i_positionNumber=? AND i_runID=?'
            , t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False;
    MCOUNT.set(0)
    return True;


def update550Crucible(runID, crucible, weightAverage, weightStdDev, weightCount):
    logger.debug("update crucible record with postfire (550) weight, etc.")
    now = datetime.today()
    if STOPPED.get() > 0:
        # print "ooops!!! this means we went too far -- shouldnt be updating anything after we've stopped"
        return
    try:
        c = conn.cursor()
        t = (float(weightAverage), float(weightStdDev), weightCount, now, crucible, runID)
        c.execute(
            'update tblCrucible SET f_550WeightAverage=?, f_550WeightStdDev=?, i_550WeightCount=?, d_550WeightDateTime=? WHERE i_positionNumber=? AND i_runID=?'
            , t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False;
    return True;


def update550Sample(runID, crucible, weightAverage, weightStdDev):
    # print "550 Weight: ",weightAverage, " Std Dev:", weightStdDev
    logger.debug("update sample record with postfire ( 550) weight, etc.")

    if STOPPED.get() > 0:
        # print "ooops!!! this means we went too far -- shouldnt be updating anything after we've stopped"
        return
    try:
        c = conn.cursor()
        t = (weightAverage, weightStdDev, crucible, runID)
        c.execute(
            'update tblSample SET f_postFireWeightAverage=?, f_postFireWeightStdDev=? WHERE i_positionNumber=? AND i_runID=?'
            , t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False;
    MCOUNT.set(0)
    return True;


def update_windows():
    value = 0


def quitProgram():
    print "Quitting!"
    exit()


def alertWindows(message):
    alertWindow.deiconify()
    Message(alertWindow, text=message, bg='red', fg='ivory', relief=GROOVE)
    return


def emptyCrucibleRun():
    NEXTSTEP.set(0)
    filename = FILENAME.get()
    directory = DIRECTORY.get()
    emptyCrucibles.deiconify()
    initializeDatabase(directory, filename)
    menubar = Menu(emptyCrucibles)
    #File Bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=quitProgram)
    menubar.add_cascade(label="File", menu=filemenu)
    #Help Menu
    helpmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=helpmenu)
    #Display the Menus

    emptyCrucibles.config(menu=menubar)
    Label(emptyCrucibles, text="Initials (e.g., CPL):").grid(row=1, column=0, sticky=W, padx=2, pady=2)
    Entry(emptyCrucibles, textvariable=INITIALS, width=4).grid(row=1, column=1, sticky=W, padx=2, pady=2)
    Label(emptyCrucibles, text="Site Location (e.g., LMV):").grid(row=2, column=0, sticky=W, padx=2, pady=2)
    Entry(emptyCrucibles, textvariable=LOCATION, width=25).grid(row=2, column=1, sticky=W, padx=2, pady=2)
    Label(emptyCrucibles, text="Assemblage (e.g., Belle Meade):").grid(row=3, column=0, sticky=W, padx=2, pady=2)
    Entry(emptyCrucibles, textvariable=ASSEMBLAGE, width=25).grid(row=3, column=1, sticky=W, padx=2, pady=2)
    Label(emptyCrucibles, text="Notes:").grid(row=4, column=0, sticky=W, padx=2, pady=2)
    Entry(emptyCrucibles, textvariable=NOTES, width=60).grid(row=4, column=1, sticky=W, padx=2, pady=2)
    Label(emptyCrucibles, text="Temperature at Location (C):").grid(row=5, column=0, sticky=W, padx=2, pady=2)
    Entry(emptyCrucibles, textvariable=TEMPERATURE, width=5).grid(row=5, column=1, sticky=W, padx=2, pady=2)
    Label(emptyCrucibles, text="Number of Crucibles (N):").grid(row=6, column=0, sticky=W, padx=2, pady=2)
    Spinbox(emptyCrucibles, textvariable=NUMBEROFCRUCIBLES, from_=1, to=30).grid(row=6, column=1, sticky=W, padx=2,
                                                                                 pady=2)
    Button(emptyCrucibles, text="Start", command=startEmptyCrucibleWeigh).grid(row=7, column=0, sticky=W, padx=2,
                                                                               pady=2)
    Button(emptyCrucibles, text="Quit", command=quitProgram).grid(row=7, column=1, sticky=W, padx=2, pady=2)


def startEmptyCrucibleWeigh():
    if NEXTSTEP.get() > 0:
        ## no more looping return
        return
    emptyCrucibles.withdraw()
    statusWindow.deiconify()
    #first create a new run so we have an ID.
    #logger.debug("DataReadWrite.insertRun( %s,%s,%d )" %(initials,today,numberOfSamples))
    now = datetime.today()
    today = now.strftime("%m-%d-%y %H:%M:%S")
    setInitials = INITIALS.get()

    numberOfCrucibles = NUMBEROFCRUCIBLES.get()
    if CURRENTCRUCIBLE.get() > numberOfCrucibles:
        NEXTSTEP.set(1)
        return
    runID = insertRun(setInitials, today, numberOfCrucibles, LOCATION.get(), ASSEMBLAGE.get(), float(TEMPERATURE.get()),
                      NOTES.get())
    if runID is False:
        logger.error("There has been an error since insertRun returned FALSE")
        alertWindow.deiconify()
        Message(alertWindow, text="There has been a problem. Cannot insert initial Run", bg='red', fg='ivory',
                relief=GROOVE)
        exit(1)
    statustext = "Run ID is %d" % int(runID)
    STATUS.set(statustext)
    RUNID.set(int(runID))
    CURRENTCRUCIBLE.set(0)
    ACOUNT.set(0)
    MCOUNT.set(0)
    statusWindow.update()
    nextEmptyCrucible()


def nextEmptyCrucible():
    if NEXTSTEP.get() > 0:
        STOPPED.set(0)
        return
    CURRENTCRUCIBLE.set(0)
    AVERAGEWEIGHT.set(0.0)
    STDDEVWEIGHT.set(0.0)
    ACOUNT.set(0)
    MCOUNT.set(0)

    Label(statusWindow, text="Run ID:").grid(row=0, column=0, sticky=W)
    Label(statusWindow, textvariable=RUNID).grid(row=0, column=1, sticky=W)
    Label(statusWindow, text="Current crucible number:").grid(row=1, column=0, sticky=W)
    Label(statusWindow, textvariable=CURRENTCRUCIBLE).grid(row=1, column=1, sticky=W)
    Label(statusWindow, text="Total Number of Crucibles:").grid(row=2, column=0, sticky=W)
    Label(statusWindow, textvariable=NUMBEROFCRUCIBLES).grid(row=2, column=1, sticky=W)
    Label(statusWindow, text="Current measurement attempts:").grid(row=3, column=0, sticky=W)
    Label(statusWindow, textvariable=ACOUNT).grid(row=3, column=1, sticky=W)
    Label(statusWindow, text="Current measurement count:").grid(row=4, column=0, sticky=W)
    Label(statusWindow, textvariable=MCOUNT).grid(row=4, column=1, sticky=W)

    Label(statusWindow, text="Step").grid(row=6, column=0, sticky=W)
    Label(statusWindow, text="Empty Crucible Weighing").grid(row=6, column=1, sticky=W)
    Label(statusWindow, text="Status").grid(row=7, column=0, sticky=W)
    Label(statusWindow, textvariable=STATUS).grid(row=7, column=1, sticky=W)
    Button(statusWindow, text="Pause", command=ask_for_pause).grid(row=8, column=0, padx=2, pady=2)
    Button(statusWindow, text="Weigh Next Sample", command=loopEmptyCrucible).grid(row=8, column=1, padx=2, pady=2)
    Button(statusWindow, text="Quit", command=quitProgram).grid(row=8, column=2, padx=2, pady=2)
    loopEmptyCrucible()


def ask_for_crucible(crucible):
    msg = "Please place crucible %d on balance and hit Continue when stabilized" % crucible
    title = "Add Crucible"
    if easygui.ccbox(msg, title):     # show a Continue/Cancel dialog
        return "continue"  # user chose Continue
    else:
        return "exit"


def ask_for_pause():
    msg = "Pausing weighing. Press Continue to carry on with measurement."
    mtitle = "Pause"
    if easygui.ccbox(msg, title=mtitle):     # show a Continue/Cancel dialog
        return "continue"  # user chose Continue
    else:
        return "exit"


def no_runID():
    msg = "Run ID returned as 0 or FALSE. There has been a problem."
    title = "ERROR: NO RUNID"
    while 1:
        easygui.msgbox(msg, title, ok_button="Exit")     # show a Continue/Cancel dialog
    sys.exit(0)


def loopEmptyCrucible():
    if NEXTSTEP.get() > 1:
        return
    STOPPED.set(0)
    crucible = CURRENTCRUCIBLE.get() + 1
    if crucible > NUMBEROFCRUCIBLES.get():
        NEXTSTEP.set(1)
        MCOUNT.set(0)
        ACOUNT.set(0)
        CURRENTCRUCIBLE.set(0)
        AVERAGEWEIGHT.set(0.0)
        STDDEVWEIGHT.set(0.0)
        done()
        statusWindow.withdraw()
        closeDatabase()
        return
    else:
        CURRENTCRUCIBLE.set(crucible)
        insertEmptyCrucible(RUNID.get(), crucible)
        insertEmptySample(RUNID.get(), crucible)
        statustext = "Now on crucible: %d" % int(CURRENTCRUCIBLE.get())
        logger.debug(statustext)
        statustext = "Please place crucible %d on balance and hit WEIGH" % crucible
        STATUS.set(statustext)
        statusWindow.update()
        value = ask_for_crucible(crucible)
        if value == "exit":
            closeDatabase()
            return
        else:
            now = datetime.today()
            runID = RUNID.get()
            weighCheck = 0
            weighSample(runID, crucible, 0)
            weightCount = MCOUNT.get()
            weightAverage = AVERAGEWEIGHT.get()
            weightStdDev = STDDEVWEIGHT.get()
            updateEmptyCrucible(runID, crucible, weightAverage, weightStdDev, weightCount)
            statustext = "Updated Weight for Crucible # %d" % int(crucible)
            STATUS.set(statustext)
            statusWindow.update()
            return


def getStatsForWeight(runID, position, step ):
    t = (runID, position, step)
    try:
        c = conn.cursor()
        logger.debug(
            'select avg(f_weight) as avg, stdev(f_weight) as stdev from tblMeasurement '\
            ' where i_runID=%d AND i_positionNumber=%d AND i_preOrPost= %d' % (
                t))
        #c.execute(' select (sum(f_weight)-min(f_weight)-max(f_weight)) / cast(f_weight* 2 as float) as avg, '
        #          'stdev(f_weight) as stdev from tblMeasurement where i_runID=? and i_positionNumber= ? and i_preOrPost=?' , t)
        c.execute(
            'select avg(f_weight) as avg, stdev(f_weight) as std from tblMeasurement '\
            ' where i_runID=? AND i_positionNumber=? AND i_preOrPost=?'
            , t)
        data = c.fetchone()
        if (data is None):
            # print "no data!"
            return (0.0, 0.0)
        else:
            avg = data['avg']
            stdev = data['std']
            # print "count: ",position, " average: ",avg, " stdev: ",stdev
            return avg, stdev
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False;


def updateRecord(runID, crucible, weightAverage, weightStdDev, count, step):
    if STOPPED.get() > 0:
        return

    crucibleWeightAverage = float(0.0)
    crucibleWeightStdDev = float(0.0)

    #print "sample Weight = ", sampleWeight
    if step == 0:
        updateEmptyCrucible(runID, crucible, weightAverage, weightStdDev, count)
    elif step == 1:
        (crucibleWeightAverage, crucibleWeightStdDev) = getCrucibleWeight(runID, crucible)
        sampleWeight = weightAverage - crucibleWeightAverage
        updateInitialSherd(runID, crucible, sampleWeight, weightStdDev)
    elif step == 2:
        (crucibleWeightAverage, crucibleWeightStdDev) = getCrucibleWeight(runID, crucible)
        sampleWeight = weightAverage - crucibleWeightAverage
        update105Crucible(runID, crucible, crucibleWeightAverage, weightStdDev, count)
        update105Sample(runID, crucible, sampleWeight, weightStdDev)
    else:
        (crucibleWeightAverage, crucibleWeightStdDev) = getCrucibleWeight(runID, crucible)
        sampleWeight = weightAverage - crucibleWeightAverage
        update550Crucible(runID, crucible, crucibleWeightAverage, weightStdDev, count)
        update550Sample(runID, crucible, sampleWeight, weightStdDev)

    return True


def weighSample(runID, crucible, step):
    listOfValues = []
    weight = float(0.0)
    count = 0
    kcount = 0
    averageWeight = 0.0
    stdevWeight = 0.0
    statustext = "Weighing crucible # %d" % crucible
    STATUS.set(statustext)
    statusWindow.update()
    a = array([])
    ACOUNT.set(0)
    MCOUNT.set(0)
    AVERAGEWEIGHT.set(0.0)
    STDDEVWEIGHT.set(0.0)
    STATUS.set("")
    statusWindow.update()
    stopCheck = STOPPED.get()
    while STOPPED.get() < 1:
        statusWindow.update()
        result = []
        weight = readStandardBalance()
        ACOUNT.set(ACOUNT.get() + 1)
        statusWindow.update()
        if weight is False:
            pass
        elif weight > 0.0:
            count += 1
            if STOPPED.get() < 1:
                if count > 2:
                    insertMeasurement(runID, crucible, weight, count, step)
                    averageWeight = 0.0
                    stdevWeight = 0.0
                if count > 5:
                    averageWeight, stdevWeight = getStatsForWeight(runID, crucible, step)
                    # print "runID: ",runID, " crucible:",crucible, " averageWeight: ",averageWeight, "stdevWeight:",stdevWeight,"count: ",count, "step:",step
                    value = updateRecord(runID, crucible, averageWeight, stdevWeight, count, step)
                MCOUNT.set(count)
                if count < 6:
                    statustext = " Count: %d the average weight of crucible # %i is <need at least 5 measurements>" % (
                        count, crucible)
                else:
                    statustext = "Count: %d the average weight of crucible # %i is: %f with stdev of: %f" % (
                        count, crucible, averageWeight, stdevWeight)
                STATUS.set(statustext)
                AVERAGEWEIGHT.set(averageWeight)
                STDDEVWEIGHT.set(stdevWeight)
                statusWindow.update()
                stopCheck = STOPPED.get()
        else:
            is_there_a_sample()

        sleep(.5)
    NEXTSTEP.set(1)
    return


def getRunID():
    maxrun = 0
    try:
        c = conn.cursor()
        logger.debug("select max(i_runID) as max from tblRun")
        c.execute("select max(i_runID) as max from tblRun")
        data = c.fetchone()
        maxrun = data["max"]
        if maxrun is None:
            return 0
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False
    return maxrun


def getRunInfo():
    try:
        c = conn.cursor()
        logger.debug(
            "select i_numberOfSamples, v_operatorName, v_locationCode,t_assemblageName,f_locationTemperature, i_temperatureOfFiring, d_dateTimeFiring, i_durationOfFiring from tblRun")
        c.execute(
            "select i_numberOfSamples, v_operatorName, v_locationCode,t_assemblageName,f_locationTemperature, i_temperatureOfFiring,d_dateTimeFiring, i_durationOfFiring from tblRun")
        data = c.fetchone()
        i_numberOfSamples = data["i_numberOfSamples"]
        v_operatorName = data["v_operatorName"]
        v_locationCode = data["v_locationCode"]
        t_assemblageName = data["t_assemblageName"]
        f_locationTemperature = data["f_locationTemperature"]
        i_temperatureOfFiring = data["i_temperatureOfFiring"]
        i_durationOfFiring = data["i_durationOfFiring"]
        d_dateTimeFiring = data["d_dateTimeFiring"]
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False
    return i_numberOfSamples, v_operatorName, v_locationCode, t_assemblageName, f_locationTemperature, i_temperatureOfFiring, i_durationOfFiring, d_dateTimeFiring


def updateRunInfo(i_numberOfSamples, v_operatorName, v_locationCode, t_assemblageName, f_locationTemperature):
    try:
        c = conn.cursor()
        t = (i_numberOfSamples, v_operatorName, v_locationCode, t_assemblageName, f_locationTemperature)
        logger.debug(
            "update tblRun set i_numberOfSamples=%d, v_operatorName=%s, v_locationCode=%s,t_assemblageName=%s,f_locationTemperature=%s where i_RunID=1" % (
                t))
        c.execute(
            'update tblRun set  i_numberOfSamples=?, v_operatorName=?, v_locationCode=?,t_assemblageName=?,f_locationTemperature=? where i_RunID=1',
            t)
        conn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False


def updateRunInfoWithFiringInformation(d_dateTimeFiring, i_temperatureOfFiring, i_durationOfFiring):
    end = timedelta(minutes=i_durationOfFiring)
    endOfFiring = d_dateTimeFiring + end
    d_endOfFiring = endOfFiring.strftime("%m-%d-%y %H:%M")
    startOfFiring = d_dateTimeFiring.strftime("%m-%d-%y %H:%M")
    try:
        c = conn.cursor()
        t = (startOfFiring, d_endOfFiring, i_temperatureOfFiring, i_durationOfFiring)
        logger.debug(
            "update tblRun set d_dateTimeFiring=%s,d_endOfFiring=%s, i_temperatureOfFiring=%d, i_durationOfFiring=%d where i_RunID=1" % (
                t))
        c.execute(
            'update tblRun set  d_dateTimeFiring=?,d_endOfFiring=?, i_temperatureOfFiring=?, i_durationOfFiring=? where i_RunID=1',
            t)
        conn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False


def getNumberOfCrucibles(runID):
    numberOfSamples = 0
    try:
        c = conn.cursor()
        logger.debug("select i_numberOfSamples from tblRun")
        c.execute("select i_numberOfSamples from tblRun")
        data = c.fetchone()
        numberOfSamples = data["i_numberOfSamples"]
        if (numberOfSamples is None):
            return 0
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False
    return numberOfSamples


def initialSherdRun():
    NEXTSTEP.set(0)
    #filename = FILENAME.get()
    #directory = DIRECTORY.get()

    #if filename == "" :
    #   alertWindows("Need filename")
    #   return

    value = reopenDatabase()
    if value == FALSE:
        alertWindows("Database open failed!")
        return

    initialSherds.deiconify()
    menubar = Menu(initialSherds)
    #File Bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Exit", command=quitProgram)
    menubar.add_cascade(label="File", menu=filemenu)

    ## first get the RunID and number of crucibles
    runID = getRunID()
    if runID == FALSE or runID == 0:
        no_runID()

    RUNID.set(runID)
    numberOfCrucibles = getNumberOfCrucibles(runID)
    NUMBEROFCRUCIBLES.set(numberOfCrucibles)
    #Help Menu
    CURRENTCRUCIBLE.set(0)
    helpmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=helpmenu)
    #Display the Menus
    i_numberOfSamples, v_operatorName, v_locationCode, v_assemblageName, f_locationTemperature, i_temperatureOfFiring, i_durationOfFiring, d_dateTimeFiring = getRunInfo()
    INITIALS.set(v_operatorName)
    LOCATION.set(v_locationCode)
    ASSEMBLAGE.set(v_assemblageName)
    TEMPERATURE.set(f_locationTemperature)
    FIRINGDURATION.set(i_durationOfFiring)
    FIRINGTEMPERATURE.set(i_temperatureOfFiring)
    dateOfFiring = datetime
    timeOfFiring = datetime
    if d_dateTimeFiring is not None:
        dt = datetime.strptime(d_dateTimeFiring, "%Y-%m-%d %H:%M:%S")
        DATEOFFIRING.set(dt.strftime("%m-%d-%y"))
        TIMEOFFIRING.set(dt.strftime("%H:%M"))

    initialSherds.config(menu=menubar)
    ####################################
    Label(initialSherds, text="Initials").grid(row=1, column=0, sticky=W, padx=2, pady=2)
    Entry(initialSherds, textvariable=INITIALS, width=4).grid(row=1, column=1, sticky=W, padx=2, pady=2)

    Label(initialSherds, text="Site Location:").grid(row=2, column=0, sticky=W, padx=2, pady=2)
    Entry(initialSherds, textvariable=LOCATION, width=25).grid(row=2, column=1, sticky=W, padx=2, pady=2)

    Label(initialSherds, text="Assemblage:").grid(row=3, column=0, sticky=W, padx=2, pady=2)
    Entry(initialSherds, textvariable=ASSEMBLAGE, width=25).grid(row=3, column=1, sticky=W, padx=2, pady=2)

    Label(initialSherds, text="Temperature at Location:").grid(row=4, column=0, sticky=W, padx=2, pady=2)
    Entry(initialSherds, textvariable=TEMPERATURE, width=5).grid(row=4, column=1, sticky=W, padx=2, pady=2)

    Label(initialSherds, text="Number of Sherds (in crucibles)").grid(row=5, column=0, sticky=W, padx=2, pady=2)
    Spinbox(initialSherds, textvariable=NUMBEROFCRUCIBLES, from_=1, to=30).grid(row=5, column=1, sticky=W, padx=2,
                                                                                pady=2)

    Button(initialSherds, text="Start", command=startInitialSherdWeigh).grid(row=6, column=0, sticky=W, padx=2,
                                                                             pady=2)
    Button(initialSherds, text="Quit", command=quitProgram).grid(row=6, column=1, sticky=W, padx=2, pady=2)


def startInitialSherdWeigh():
    if NEXTSTEP.get() > 0:
        ## no more looping return
        return

    updateRunInfo(int(NUMBEROFCRUCIBLES.get()), INITIALS.get(), LOCATION.get(), ASSEMBLAGE.get(),
                  float(TEMPERATURE.get()))

    initialSherds.withdraw()
    statusWindow.deiconify()
    MCOUNT.set(0)
    CURRENTCRUCIBLE.set(0)
    AVERAGEWEIGHT.set(0.0)
    STDDEVWEIGHT.set(0.0)
    ACOUNT.set(0)
    STATUS.set("")

    Label(statusWindow, text="Run ID:").grid(row=0, column=0, sticky=W)
    Label(statusWindow, textvariable=RUNID).grid(row=0, column=1, sticky=W)

    Label(statusWindow, text="Current crucible number:").grid(row=1, column=0, sticky=W)
    Label(statusWindow, textvariable=CURRENTCRUCIBLE).grid(row=1, column=1, sticky=W)

    Label(statusWindow, text="Sherd Identification:").grid(row=2, column=0, sticky=W)
    Label(statusWindow, textvariable=SHERDID).grid(row=2, column=1, sticky=W)

    Label(statusWindow, text="Total Number of Crucibles:").grid(row=3, column=0, sticky=W)
    Label(statusWindow, textvariable=NUMBEROFCRUCIBLES).grid(row=3, column=1, sticky=W)

    Label(statusWindow, text="Current measurement attempts:").grid(row=4, column=0, sticky=W)
    Label(statusWindow, textvariable=ACOUNT).grid(row=4, column=1, sticky=W)

    Label(statusWindow, text="Current measurement count:").grid(row=5, column=0, sticky=W)
    Label(statusWindow, textvariable=MCOUNT).grid(row=5, column=1, sticky=W)

    Label(statusWindow, text="Step").grid(row=6, column=0, sticky=W)
    Label(statusWindow, text="Initial Sherd Weighing...").grid(row=6, column=1, sticky=W)

    Label(statusWindow, text="Status").grid(row=7, column=0, sticky=W)
    Label(statusWindow, textvariable=STATUS).grid(row=7, column=1, sticky=W)

    Button(statusWindow, text="Pause", command=ask_for_pause).grid(row=8, column=0, padx=2, pady=2)
    Button(statusWindow, text="Weigh Next Sample", command=loopInitialSherd).grid(row=8, column=1, padx=2, pady=2)
    Button(statusWindow, text="Quit", command=quitProgram).grid(row=8, column=2, padx=2, pady=2)
    statusWindow.update()
    nextInitialSherd()


def nextInitialSherd():
    if NEXTSTEP.get() > 0:
        return

    Label(statusWindow, text="Run ID:").grid(row=0, column=0, sticky=W)
    Label(statusWindow, textvariable=RUNID).grid(row=0, column=1, sticky=W)

    Label(statusWindow, text="Current crucible number:").grid(row=1, column=0, sticky=W)
    Label(statusWindow, textvariable=CURRENTCRUCIBLE).grid(row=1, column=1, sticky=W)

    Label(statusWindow, text="Sherd Identification:").grid(row=2, column=0, sticky=W)
    Label(statusWindow, textvariable=SHERDID).grid(row=2, column=1, sticky=W)

    Label(statusWindow, text="Total Number of Crucibles:").grid(row=3, column=0, sticky=W)
    Label(statusWindow, textvariable=NUMBEROFCRUCIBLES).grid(row=3, column=1, sticky=W)

    Label(statusWindow, text="Current measurement attempts:").grid(row=4, column=0, sticky=W)
    Label(statusWindow, textvariable=ACOUNT).grid(row=4, column=1, sticky=W)

    Label(statusWindow, text="Current measurement count:").grid(row=5, column=0, sticky=W)
    Label(statusWindow, textvariable=MCOUNT).grid(row=5, column=1, sticky=W)

    Label(statusWindow, text="Step").grid(row=6, column=0, sticky=W)
    Label(statusWindow, text="Initial Sherd Weighing...").grid(row=6, column=1, sticky=W)

    Label(statusWindow, text="Status").grid(row=7, column=0, sticky=W)
    Label(statusWindow, textvariable=STATUS).grid(row=7, column=1, sticky=W)

    Button(statusWindow, text="Pause", command=ask_for_pause).grid(row=8, column=0, padx=2, pady=2)
    Button(statusWindow, text="Weigh Next Crucible", command=loopInitialSherd).grid(row=8, column=1, padx=2, pady=2)
    Button(statusWindow, text="Quit", command=quitProgram).grid(row=8, column=2, padx=2, pady=2)
    loopInitialSherd()


def loopInitialSherd():
    if NEXTSTEP.get() > 1:
        return
    STOPPED.set(0)
    crucible = CURRENTCRUCIBLE.get() + 1
    ## first get the RunID and number of crucibles
    runID = getRunID()
    if runID == FALSE or runID == 0:
        no_runID()

    RUNID.set(runID)
    if crucible > NUMBEROFCRUCIBLES.get():
        NEXTSTEP.set(1)
        MCOUNT.set(0)
        ACOUNT.set(0)
        CURRENTCRUCIBLE.set(0)
        AVERAGEWEIGHT.set(0.0)
        STDDEVWEIGHT.set(0.0)
        done()
        statusWindow.withdraw()
        closeDatabase()
        return
    else:
        CURRENTCRUCIBLE.set(crucible)
        i_numberOfSamples, v_operatorName, v_locationCode, t_assemblageName, f_locationTemperature, i_temperatureOfFiring, i_durationOfFiring, d_dateTimeFiring = getRunInfo()
        INITIALS.set(v_operatorName)
        LOCATION.set(v_locationCode)
        ASSEMBLAGE.set(t_assemblageName)
        TEMPERATURE.set(f_locationTemperature)
        FIRINGDURATION.set(i_durationOfFiring)
        FIRINGTEMPERATURE.set(i_temperatureOfFiring)

        statustext = "Now on crucible: %d" % int(CURRENTCRUCIBLE.get())
        sherdID = easygui.enterbox(msg='Enter sherd number or identifier', title='Sherd ID', default='', strip=True,
                                   image=None, root=None)
        SHERDID.set(sherdID)
        logger.debug(statustext)
        statustext = "Please place crucible %d on balance and hit WEIGH" % crucible

        STATUS.set(statustext)
        statusWindow.update()
        value = ask_for_crucible(crucible)

    if value == "exit":
        return
    else:
        #print "Creating record for sherd # %d" % int(crucible)
        crucibleWeightAverage, crucibleWeightStdDev = getCrucibleWeight(runID, crucible)
        sherdID = SHERDID.get()
        assemblage = ASSEMBLAGE.get()
        location = LOCATION.get()
        locationTemperature = TEMPERATURE.get()
        insertInitialSherd(runID, crucible, sherdID, assemblage, locationTemperature)

        weighSample(runID, crucible, 1)
        weightCount = MCOUNT.get()
        weightAverage = AVERAGEWEIGHT.get() - crucibleWeightAverage
        weightStdDev = STDDEVWEIGHT.get()
        updateInitialSherd(runID, crucible, weightAverage, weightStdDev)
        ## first get the weight of the crucible
        now = datetime.today()
        ## insert these data into the tblSample
        statustext = "Created record for sherd # %d" % int(crucible)
        STATUS.set(statustext)
        statusWindow.update()


def is_there_a_sample():
    msg = "The balance reported a weight of 0.0000 g. Is there a sample on the balance?"
    title = "Missing sample?"
    if easygui.ccbox(msg, title):     # show a Continue/Cancel dialog
        return "continue"
    else:
        return "cancel"


## Get the average weight and std dev of weight for this crucible.
def getCrucibleWeight(runID, positionNumber):
    try:
        c = conn.cursor()
        t = (runID, positionNumber)
        #print "RUNID:  ",runID, "PositionNumber:",positionNumber
        averageWeight = float(0.0)
        c.execute(
            'select f_averageWeight, f_stdevWeight from tblCrucible where i_runID=? and i_positionNumber=?', t)
        logger.debug(
            'select f_averageWeight, f_stdevWeight from tblCrucible where i_runID=%d and i_positionNumber=%d' % (t))
        data = c.fetchone()
        if data is None:
            return False
        else:
            #print "Crucible Weight: ", data["f_averageWeight"],"+/-", data["f_stdevWeight"]
            return float(data["f_averageWeight"]), float(data["f_stdevWeight"])
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False


def prefireCrucibleRun():
    NEXTSTEP.set(0)
    #filename = FILENAME.get()
    #directory = DIRECTORY.get()
    #if filename == "" or directory == "":
    #   alertWindows("Need filename and directory")
    #   return
    value = reopenDatabase()
    if value == FALSE:
        alertWindows("Database open failed!")
        return
    prefireCrucibles.deiconify()
    menubar = Menu(prefireCrucibles)
    #File Bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Exit", command=quitProgram)
    menubar.add_cascade(label="File", menu=filemenu)

    ## first get the RunID and number of crucibles
    runID = getRunID()
    if runID == FALSE or runID == 0:
        no_runID()

    RUNID.set(runID)
    numberOfCrucibles = getNumberOfCrucibles(runID)
    NUMBEROFCRUCIBLES.set(numberOfCrucibles)
    #Help Menu
    i_numberOfSamples, v_operatorName, v_locationCode, v_assemblageName, f_locationTemperature, i_temperatureOfFiring, i_durationOfFiring, d_dateTimeFiring = getRunInfo()
    INITIALS.set(v_operatorName)
    LOCATION.set(v_locationCode)
    ASSEMBLAGE.set(v_assemblageName)
    TEMPERATURE.set(f_locationTemperature)

    helpmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=helpmenu)
    #Display the Menus

    prefireCrucibles.config(menu=menubar)
    Label(prefireCrucibles, text="Initials (e.g., CPL):").grid(row=1, column=0, sticky=W, padx=2, pady=2)
    Entry(prefireCrucibles, textvariable=INITIALS, width=4).grid(row=1, column=1, sticky=W, padx=2, pady=2)

    Label(prefireCrucibles, text="Site Location (e.g., NE Arkansas):").grid(row=2, column=0, sticky=W, padx=2, pady=2)
    Entry(prefireCrucibles, textvariable=LOCATION, width=25).grid(row=2, column=1, sticky=W, padx=2, pady=2)

    Label(prefireCrucibles, text="Assemblage (e.g., Belle Meade):").grid(row=3, column=0, sticky=W, padx=2, pady=2)
    Entry(prefireCrucibles, textvariable=ASSEMBLAGE, width=25).grid(row=3, column=1, sticky=W, padx=2, pady=2)

    Label(prefireCrucibles, text="Temperature at Location (C):").grid(row=4, column=0, sticky=W, padx=2, pady=2)
    Entry(prefireCrucibles, textvariable=TEMPERATURE, width=8).grid(row=4, column=1, sticky=W, padx=2, pady=2)

    Label(prefireCrucibles, text="Number of Crucibles/Samples:").grid(row=5, column=0, sticky=W, padx=2, pady=2)
    Spinbox(prefireCrucibles, textvariable=NUMBEROFCRUCIBLES, from_=1, to=30).grid(row=5, column=1, sticky=W, padx=2,
                                                                                   pady=2)

    Button(prefireCrucibles, text="Start", command=startPrefireCrucibleWeigh).grid(row=6, column=0, sticky=W, padx=2,
                                                                                   pady=2)
    Button(prefireCrucibles, text="Quit", command=quitProgram).grid(row=6, column=1, sticky=W, padx=2, pady=2)


def startPrefireCrucibleWeigh():
    if NEXTSTEP.get() > 0:
        ## no more looping return
        return
    updateRunInfo(int(NUMBEROFCRUCIBLES.get()), INITIALS.get(), LOCATION.get(), ASSEMBLAGE.get(),
                  float(TEMPERATURE.get()))

    prefireCrucibles.withdraw()
    prefireStatusWindow.deiconify()
    MCOUNT.set(0)
    CURRENTCRUCIBLE.set(0)
    AVERAGEWEIGHT.set(0.0)
    STDDEVWEIGHT.set(0.0)
    ACOUNT.set(0)
    STATUS.set("")

    Label(prefireStatusWindow, text="Run ID:").grid(row=0, column=0, sticky=W)
    Label(prefireStatusWindow, textvariable=RUNID).grid(row=0, column=1, sticky=W)

    Label(prefireStatusWindow, text="Current crucible number:").grid(row=1, column=0, sticky=W)
    Label(prefireStatusWindow, textvariable=CURRENTCRUCIBLE).grid(row=1, column=1, sticky=W)

    Label(prefireStatusWindow, text="Total Number of Crucibles:").grid(row=2, column=0, sticky=W)
    Label(prefireStatusWindow, textvariable=NUMBEROFCRUCIBLES).grid(row=2, column=1, sticky=W)

    Label(prefireStatusWindow, text="Current measurement attempts:").grid(row=3, column=0, sticky=W)
    Label(prefireStatusWindow, textvariable=ACOUNT).grid(row=3, column=1, sticky=W)

    Label(prefireStatusWindow, text="Current measurement count:").grid(row=4, column=0, sticky=W)
    Label(statusWindow, textvariable=MCOUNT).grid(row=4, column=1, sticky=W)

    Label(prefireStatusWindow, text="Step").grid(row=5, column=0, sticky=W)
    Label(prefireStatusWindow, text="Prefire (105 Degrees C) Weighing").grid(row=5, column=1, sticky=W)

    Label(prefireStatusWindow, text="Status").grid(row=6, column=0, sticky=W)
    Label(prefireStatusWindow, textvariable=STATUS).grid(row=6, column=1, sticky=W)

    Button(prefireStatusWindow, text="Pause", command=ask_for_pause).grid(row=7, column=0, padx=2, pady=2)
    Button(prefireStatusWindow, text="Weigh Next Crucible", command=loopEmptyCrucible).grid(row=7, column=1, padx=2,
                                                                                            pady=2)
    Button(prefireStatusWindow, text="Quit", command=quitProgram).grid(row=7, column=2, padx=2, pady=2)
    prefireStatusWindow.update()
    nextPrefireCrucible()


def nextPrefireCrucible():
    if NEXTSTEP.get() > 0:
        return

    Label(prefireStatusWindow, text="Run ID:").grid(row=0, column=0, sticky=W)
    Label(prefireStatusWindow, textvariable=RUNID).grid(row=0, column=1, sticky=W)

    Label(prefireStatusWindow, text="Current crucible number:").grid(row=1, column=0, sticky=W)
    Label(prefireStatusWindow, textvariable=CURRENTCRUCIBLE).grid(row=1, column=1, sticky=W)

    Label(prefireStatusWindow, text="Total Number of Crucibles:").grid(row=2, column=0, sticky=W)
    Label(prefireStatusWindow, textvariable=NUMBEROFCRUCIBLES).grid(row=2, column=1, sticky=W)

    Label(prefireStatusWindow, text="Current measurement attempts:").grid(row=3, column=0, sticky=W)
    Label(prefireStatusWindow, textvariable=ACOUNT).grid(row=3, column=1, sticky=W)

    Label(prefireStatusWindow, text="Current measurement count:").grid(row=4, column=0, sticky=W)
    Label(prefireStatusWindow, textvariable=MCOUNT).grid(row=4, column=1, sticky=W)

    Label(prefireStatusWindow, text="Step").grid(row=5, column=0, sticky=W)
    Label(prefireStatusWindow, text="Prefire (105 Degrees C) Weighing").grid(row=5, column=1, sticky=W)

    Label(prefireStatusWindow, text="Status").grid(row=6, column=0, sticky=W)
    Label(prefireStatusWindow, textvariable=STATUS).grid(row=6, column=1, sticky=W)

    Button(prefireStatusWindow, text="Pause", command=ask_for_pause).grid(row=7, column=0, padx=2, pady=2)
    Button(prefireStatusWindow, text="Weigh Next Crucible", command=loopPrefireCrucible).grid(row=7, column=1, padx=2,
                                                                                              pady=2)
    Button(prefireStatusWindow, text="Quit", command=quitProgram).grid(row=7, column=2, padx=2, pady=2)
    loopPrefireCrucible()


def loopPrefireCrucible():
    if NEXTSTEP.get() > 0:
        return
    STOPPED.set(0)

    crucible = CURRENTCRUCIBLE.get() + 1
    CURRENTCRUCIBLE.set(crucible)
    runID = RUNID.get()
    if crucible > NUMBEROFCRUCIBLES.get():
        NEXTSTEP.set(1)
        prefireStatusWindow.withdraw()
        closeDatabase()
        MCOUNT.set(0)
        ACOUNT.set(0)
        CURRENTCRUCIBLE.set(0)
        AVERAGEWEIGHT.set(0.0)
        STDDEVWEIGHT.set(0.0)
        STATUS.set("")
        done()
        return
    else:
        CURRENTCRUCIBLE.set(crucible)
        statustext = "Now on crucible: %d" % int(CURRENTCRUCIBLE.get())
        logger.debug(statustext)
        statustext = "Please place crucible %d on balance and hit WEIGH" % crucible
        STATUS.set(statustext)
        prefireStatusWindow.update()
        value = ask_for_crucible(crucible)

        if value == "exit":
            return
        else:
            crucibleWeightAverage, crucibleWeightStdDev = getCrucibleWeight(runID, crucible)
            weighSample(runID, crucible, 2)
            #weightCount = MCOUNT.get()
            #weightAverage = AVERAGEWEIGHT.get()-crucibleWeightAverage
            #weightStdDev = STDDEVWEIGHT.get()

            #update105Crucible(runID, crucible, weightAverage, weightStdDev, weightCount)
            #update105Sample(runID, crucible, weightAverage, weightStdDev)

            statustext = "Updated 105 Weight for Crucible and Sample # %d " % int(crucible)
            STATUS.set(statustext)
            prefireStatusWindow.update()
    return


def postfireCrucibleRun():
    NEXTSTEP.set(0)

    value = reopenDatabase()
    if value is FALSE:
        alertWindows("Database open failed!")
        return

    postfireCrucibles.deiconify()

    i_numberOfSamples, v_operatorName, v_locationCode, t_assemblageName, f_locationTemperature, i_temperatureOfFiring, i_durationOfFiring, d_dateTimeFiring = getRunInfo()
    INITIALS.set(v_operatorName)
    LOCATION.set(v_locationCode)
    ASSEMBLAGE.set(t_assemblageName)
    TEMPERATURE.set(f_locationTemperature)
    FIRINGDURATION.set(i_durationOfFiring)
    FIRINGTEMPERATURE.set(i_temperatureOfFiring)

    ## first get the RunID and number of crucibles
    runID = getRunID()
    RUNID.set(runID)
    if runID == FALSE or runID == 0:
        no_runID()

    numberOfCrucibles = getNumberOfCrucibles(runID)
    NUMBEROFCRUCIBLES.set(numberOfCrucibles)

    menubar = Menu(prefireCrucibles)
    #File Bar
    filemenu = Menu(menubar, tearoff=0)

    filemenu.add_command(label="Exit", command=quitProgram)
    menubar.add_cascade(label="File", menu=filemenu)

    ## first get the RunID and number of crucibles
    runID = getRunID()
    RUNID.set(runID)

    #Help Menu
    CURRENTCRUCIBLE.set(1)
    helpmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=helpmenu)
    #Display the Menus
    postfireCrucibles.config(menu=menubar)
    today = datetime.now()
    CURRENTDATETIME.set(today.strftime("%m-%d-%y %H:%M"))
    DATEOFFIRING.set(today.strftime("%m-%d-%y"))
    TIMEOFFIRING.set(today.strftime("%H:%M"))
    RUNINFOSTATUS.set("Please enter the required information to set up the run.")
    FIRINGTEMPERATURE.set(500)
    postfireGUI()


def postfireGUI():
    Label(postfireCrucibles, text="Initials (e.g., CPL):").grid(row=1, column=0, sticky=W)
    Entry(postfireCrucibles, textvariable=INITIALS, width=4).grid(row=1, column=1, sticky=W)

    Label(postfireCrucibles, text="Number of Crucibles:").grid(row=2, column=0, sticky=W, padx=2, pady=2)
    Spinbox(postfireCrucibles, textvariable=NUMBEROFCRUCIBLES, from_=1, to=30).grid(row=2, column=1, sticky=W, padx=2,
                                                                                    pady=2)

    Label(postfireCrucibles, text="Site Location (e.g., NE Arkansas):").grid(row=2, column=0, sticky=W, padx=2, pady=2)
    Entry(postfireCrucibles, textvariable=LOCATION, width=25).grid(row=2, column=1, sticky=W, padx=2, pady=2)

    Label(postfireCrucibles, text="Assemblage (e.g., Belle Meade):").grid(row=3, column=0, sticky=W, padx=2, pady=2)
    Entry(postfireCrucibles, textvariable=ASSEMBLAGE, width=25).grid(row=3, column=1, sticky=W, padx=2, pady=2)

    Label(postfireCrucibles, text="Temperature at Location (C):").grid(row=4, column=0, sticky=W, padx=2, pady=2)
    Entry(postfireCrucibles, textvariable=TEMPERATURE, width=8).grid(row=4, column=1, sticky=W, padx=2, pady=2)

    Label(postfireCrucibles, text="Firing Temperature (C):").grid(row=5, column=0, sticky=W, padx=2, pady=2)
    Entry(postfireCrucibles, textvariable=FIRINGTEMPERATURE, width=8).grid(row=5, column=1, sticky=W, padx=2, pady=2)

    Label(postfireCrucibles, text="Date of Firing (mm-dd-yy):").grid(row=7, column=0, sticky=W, padx=2, pady=2)
    Entry(postfireCrucibles, textvariable=DATEOFFIRING, width=12).grid(row=7, column=1, sticky=W, padx=2, pady=2)

    Label(postfireCrucibles, text="Time of Firing (HH:MM):").grid(row=8, column=0, sticky=W, padx=2, pady=2)
    Entry(postfireCrucibles, textvariable=TIMEOFFIRING, width=12).grid(row=8, column=1, sticky=W, padx=2, pady=2)

    Label(postfireCrucibles, text="Current Date and Time:").grid(row=6, column=0, sticky=W, padx=2, pady=2)
    Entry(postfireCrucibles, textvariable=CURRENTDATETIME, width=15).grid(row=6, column=1, sticky=W, padx=2, pady=2)

    Button(postfireCrucibles, text="Start", command=startPostfireCrucibleWeigh).grid(row=10, column=0, sticky=W, padx=2,
                                                                                     pady=2)
    Button(postfireCrucibles, text="Quit", command=quitProgram).grid(row=10, column=1, sticky=W, padx=2, pady=2)

    Label(postfireCrucibles, textvariable=RUNINFOSTATUS).grid(row=11, column=0, sticky=W, padx=2, pady=2)


def startPostfireCrucibleWeigh():
    if DATEOFFIRING.get() == "" or TIMEOFFIRING.get() == "" or FIRINGTEMPERATURE.get == None:
        RUNINFOSTATUS.set(
            "Date of firing, time of firing and duration of firing are all required. Please enter these data.")
        RESUBMIT.set("resubmission")
        postfireGUI()

    if NEXTSTEP.get() > 0:
        ## no more looping return
        return
    postfireStatusWindow.deiconify()

    dt = datetime
    dateTimeFiring = DATEOFFIRING.get() + " " + TIMEOFFIRING.get()
    try:
        dt = datetime.strptime(dateTimeFiring, "%m-%d-%y %H:%M")
    except:
        RUNINFOSTATUS.set("Date and/or time formats are incorrect. Reenter.")
        postfireGUI()

    currentDateTime = CURRENTDATETIME.get()
    cdt = datetime
    try:
        cdt = datetime.strptime(currentDateTime, "%m-%d-%y %H:%M")
    except:
        RUNINFOSTATUS.set("Current date and/or time formats are incorrect. Reenter.")
        postfireGUI()

    duration = cdt - dt
    firingDuration = int(duration.total_seconds()) / 60
    firingDuration = int(firingDuration)
    postfireGUI()
    updateRunInfo(int(NUMBEROFCRUCIBLES.get()), INITIALS.get(), LOCATION.get(), ASSEMBLAGE.get(),
                  float(TEMPERATURE.get()))
    updateRunInfoWithFiringInformation(dt, float(FIRINGTEMPERATURE.get()), firingDuration)
    postfireCrucibles.withdraw()

    MCOUNT.set(0)
    ACOUNT.set(0)
    CURRENTCRUCIBLE.set(0)
    AVERAGEWEIGHT.set(0.0)
    STDDEVWEIGHT.set(0.0)

    Label(postfireStatusWindow, text="Run ID:").grid(row=0, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=RUNID).grid(row=0, column=1, sticky=W)

    Label(postfireStatusWindow, text="Current crucible number:").grid(row=1, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=CURRENTCRUCIBLE).grid(row=1, column=1, sticky=W)

    Label(postfireStatusWindow, text="Total Number of Crucibles:").grid(row=2, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=NUMBEROFCRUCIBLES).grid(row=2, column=1, sticky=W)

    Label(postfireStatusWindow, text="Current measurement attempts:").grid(row=3, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=ACOUNT).grid(row=3, column=1, sticky=W)

    Label(postfireStatusWindow, text="Current measurement count:").grid(row=4, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=MCOUNT).grid(row=4, column=1, sticky=W)

    Label(postfireStatusWindow, text="Step").grid(row=5, column=0, sticky=W)
    Label(postfireStatusWindow, text="Postfire (550 Degrees C) Weighing").grid(row=5, column=1, sticky=W)

    Label(postfireStatusWindow, text="Status").grid(row=6, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=STATUS).grid(row=6, column=1, sticky=W)

    Button(postfireStatusWindow, text="Pause", command=ask_for_pause).grid(row=7, column=0, padx=2, pady=2)
    Button(postfireStatusWindow, text="Weigh Next Crucible", command=loopPostfireCrucible).grid(row=7, column=1, padx=2,
                                                                                                pady=2)
    Button(postfireStatusWindow, text="Quit", command=quitProgram).grid(row=7, column=2, padx=2, pady=2)

    postfireStatusWindow.update()
    nextPostfireCrucible()


def nextPostfireCrucible():
    ##print "got here"
    if NEXTSTEP.get() > 0:
        ## no more looping return
        return
        ##print "got here"
    ACOUNT.set(0)
    MCOUNT.set(0)
    Label(postfireStatusWindow, text="Run ID:").grid(row=0, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=RUNID).grid(row=0, column=1, sticky=W)

    Label(postfireStatusWindow, text="Current crucible number:").grid(row=1, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=CURRENTCRUCIBLE).grid(row=1, column=1, sticky=W)

    Label(postfireStatusWindow, text="Total Number of Crucibles:").grid(row=2, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=NUMBEROFCRUCIBLES).grid(row=2, column=1, sticky=W)

    Label(postfireStatusWindow, text="Current measurement attempts:").grid(row=3, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=ACOUNT).grid(row=3, column=1, sticky=W)

    Label(postfireStatusWindow, text="Current measurement count:").grid(row=4, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=MCOUNT).grid(row=4, column=1, sticky=W)

    Label(postfireStatusWindow, text="Step").grid(row=5, column=0, sticky=W)
    Label(postfireStatusWindow, text="Postfire (550 Degrees C) Weighing").grid(row=5, column=1, sticky=W)

    Label(postfireStatusWindow, text="Status").grid(row=6, column=0, sticky=W)
    Label(postfireStatusWindow, textvariable=STATUS).grid(row=6, column=1, sticky=W)

    Button(postfireStatusWindow, text="Pause", command=ask_for_pause).grid(row=7, column=0, padx=2, pady=2)
    Button(postfireStatusWindow, text="Weigh Next Crucible", command=loopPostfireCrucible).grid(row=7, column=1, padx=2,
                                                                                                pady=2)
    Button(postfireStatusWindow, text="Quit", command=quitProgram).grid(row=7, column=2, padx=2, pady=2)
    loopPostfireCrucible()


def loopPostfireCrucible():
    if NEXTSTEP.get() > 0:
        return
    STOPPED.set(0)

    crucible = CURRENTCRUCIBLE.get() + 1
    CURRENTCRUCIBLE.set(crucible)
    runID = RUNID.get()
    ##print "now on crucible ",crucible
    if crucible > NUMBEROFCRUCIBLES.get():
        postfireStatusWindow.withdraw()
        closeDatabase()
        NEXTSTEP.set(1)
        MCOUNT.set(0)
        ACOUNT.set(0)
        CURRENTCRUCIBLE.set(0)
        AVERAGEWEIGHT.set(0.0)
        STDDEVWEIGHT.set(0.0)
        done()
        return
    else:
        statustext = "Now on crucible: %d" % int(CURRENTCRUCIBLE.get())
        logger.debug(statustext)
        statustext = "Please place crucible %d on balance and hit WEIGH" % crucible
        STATUS.set(statustext)
        ##print statustext
        postfireStatusWindow.update()
        value = ask_for_crucible(crucible)
        if value == "exit":
            return
        else:
            crucibleWeightAverage, crucibleWeightStdDev = getCrucibleWeight(runID, crucible)
            weighSample(runID, crucible, 3)
            statustext = "Updated 550 Weight for Crucible and Sample # %d " % int(crucible)
            STATUS.set(statustext)
            postfireStatusWindow.update()
    return


def done():
    STOPPED.set(1)
    NEXTSTEP.set(1)
    msg = "Done with this step. Continue or exit?"
    mtitle = "Continue or Exit"
    if easygui.ccbox(msg, title=mtitle):     # show a Continue/Cancel dialog
        return "continue"  # user chose Continue
    else:
        sys.exit(0)


def getCurrentStateOfRun():
    c = conn.cursor()
    try:
        c.execute('select max(i_preOrPost) as max from tblMeasurement')
        row = c.fetchone()
        if row['max'] is None:
            return -1
        return int(row['max'])
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return -1


def insertMeasurement(runID, positionNumber, weight, count, step):
    logger.debug("insert  measurement into tblMeasurement")

    ## 0 = crucible 1 = sherd/crucible 2=105  3=550 4= RHX
    measurementID = 0
    now = datetime.today()
    try:
        c = conn.cursor()
        t = (1, positionNumber, weight, now, count, step)
        #print runID,positionNumber,weight,status,now,temperature,humidity,count,preOrPost
        logger.debug('insert into tblMeasurement (i_runID,i_positionNumber,f_weight,d_datetime,'\
                     'i_count,i_preOrPost) VALUES (%s,%s,%s,%s,%s,%s)' % (t))
        c.execute('insert into tblMeasurement (i_runID,i_positionNumber,f_weight,d_datetime,'\
                  'i_count,i_preOrPost) VALUES (?,?,?,?,?,?)', t)
        conn.commit()
        measurementID = c.lastrowid
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False
    return measurementID


def updateAndFixAverageValues():
    value = reopenDatabase()
    if value is False:
        alertWindows("Database open failed!")
        return
        # first get the number of samples
    i_numberOfSamples, v_operatorName, v_locationCode, t_assemblageName, f_locationTemperature, i_temperatureOfFiring, i_durationOfFiring, d_dateTimeFiring = getRunInfo()
    currentMaxState = getCurrentStateOfRun()
    currentMaxState += 1
    stateCounter = 0
    while stateCounter < currentMaxState:
        sampleCounter = 1
        runID = 1
        while sampleCounter <= i_numberOfSamples:
            #print "State:  ", stateCounter, "  Sample # ", sampleCounter

            (crucibleWeightAverage, crucibleWeightStdDev) = getCrucibleWeight(runID, sampleCounter)
            try:
                c = conn.cursor()
                t = ( sampleCounter, stateCounter )
                logger.debug(
                    'select avg(f_weight) as AVE, stdev(f_weight) as SD from tblMeasurement where i_positionNumber= %d and i_preOrPost= %d and i_runID=1' % t)
                c.execute(
                    'select avg(f_weight) as AVE, stdev(f_weight) as SD from tblMeasurement where i_positionNumber=? and i_preOrPost=? and i_runID=1',
                    t)
                data = c.fetchone()
                averageWeight = float(data['AVE'])
                stddevWeight = float(data['SD'])
                #print "Average Measurement Weight: ", averageWeight, " +/- ", stddevWeight
            except sqlite.OperationalError, msg:
                logger.error("A SQL error occurred: %s", msg)
                return False

            sampleWeight = float(averageWeight - crucibleWeightAverage)
            #print "Average Sherd Weight: ", sampleWeight, " +/-", stddevWeight

            if stateCounter == 0:
                try:
                    t = ( averageWeight, stddevWeight, averageWeight, stddevWeight, sampleCounter )
                    print(
                        'update tblCrucible set f_averageWeight=%f, f_stdevWeight=%f, f_emptyWeightAverage=%f, f_emptyWeightStdDev=%f where i_runID=1 and i_positionNumber=%d  ' % t)
                    c.execute(
                        'update tblCrucible set f_averageWeight=?, f_stdevWeight=?, f_emptyWeightAverage=?, f_emptyWeightStdDev=? where i_runID=1 and i_positionNumber=?  ',
                        t)
                    conn.commit
                    t = ( averageWeight, stddevWeight, sampleCounter )
                    print(
                        'update tblSample set f_crucibleWeightAverage=%f, f_crucibleWeightStdDev=%f where i_runID=1 and i_positionNumber=%d  ' % t)
                    c.execute(
                        'update tblSample set f_crucibleWeightAverage=?, f_crucibleWeightStdDev=? where i_runID=1 and i_positionNumber=?  ',
                        t)
                    conn.commit

                    c.execute(
                        'select  f_averageWeight, f_stdevWeight from tblCrucible where  i_runID=1 and i_positionNumber=%d  ' % sampleCounter)
                    data = c.fetchone()
                    #print "Values -- averageWeight: %s  stdDev: %s ", (data['f_averageWeight'],data['f_stdevWeight'])
                except sqlite.OperationalError, msg:
                    logger.error("A SQL error occurred: %s", msg)
                    return False

            elif stateCounter == 1:
                try:
                    t = ( sampleWeight, stddevWeight, sampleCounter )
                    print(
                        'update tblSample set f_sherdWeightInitialAverage=%f, f_sherdWeightInitialStdDev=%f where i_runID=1 and i_positionNumber=%d  ' % t)
                    c.execute(
                        'update tblSample set f_sherdWeightInitialAverage=?, f_sherdWeightInitialStdDev=? where i_runID=1 and i_positionNumber=? ',
                        t)
                    conn.commit

                    c.execute(
                        'select  f_sherdWeightInitialAverage, f_sherdWeightInitialStdDev from tblSample where  i_runID=1 and i_positionNumber=%d  ' % sampleCounter)
                    data = c.fetchone()
                    #print "Values -- averageWeight: %s  stdDev: %s ", (data['f_sherdWeightInitialAverage'],data['f_sherdWeightInitialStdDev'])

                except sqlite.OperationalError, msg:
                    logger.error("A SQL error occurred: %s", msg)
                    return False

            elif stateCounter == 2:
                try:
                    t = ( averageWeight, stddevWeight, sampleCounter )
                    print(
                        'update tblCrucible set f_105WeightAverage=%f, f_105WeightStdDev=%f  where i_runID=1 and i_positionNumber=%d  ' % t)
                    c.execute(
                        'update tblCrucible set f_105WeightAverage=?, f_105WeightStdDev=? where i_runID=1 and i_positionNumber=?  ',
                        t)
                    conn.commit

                    c.execute(
                        'select  f_105WeightAverage, f_105WeightStdDev from tblCrucible where  i_runID=1 and i_positionNumber=%d  ' % sampleCounter)
                    data = c.fetchone()
                    #print "Values -- averageWeight: %s  stdDev: %s ", (data['f_105WeightAverage'],data['f_105WeightStdDev'])
                except sqlite.OperationalError, msg:
                    logger.error("A SQL error occurred: %s", msg)
                    return False

                try:
                    t = ( sampleWeight, stddevWeight, sampleCounter )
                    print(
                        'update tblSample set f_preWeightAverage=%f, f_preWeightStdDev=%f where i_runID=1 and i_positionNumber=%d  ' % t)
                    c.execute(
                        'update tblSample set f_preWeightAverage=?, f_preWeightStdDev=? where i_runID=1 and i_positionNumber=?  ',
                        t)
                    conn.commit
                except sqlite.OperationalError, msg:
                    logger.error("A SQL error occurred: %s", msg)
                    return False


            elif stateCounter == 3:
                try:
                    t = ( averageWeight, stddevWeight, sampleCounter )
                    print(
                        'update tblCrucible set f_550WeightAverage=%f, f_550WeightStdDev=%f where i_runID=1 and i_positionNumber=%d  ' % t)
                    c.execute(
                        'update tblCrucible set f_550WeightAverage=?, f_550WeightStdDev=? where i_runID=1 and i_positionNumber=?  ',
                        t)
                    conn.commit
                    c.execute(
                        'select  f_550WeightAverage, f_550WeightStdDev from tblCrucible where  i_runID=1 and i_positionNumber=%d  ' % sampleCounter)
                    data = c.fetchone()
                    #print "Values -- averageWeight: %s  stdDev: %s ", (data['f_550WeightAverage'],data['f_550WeightStdDev'])
                except sqlite.OperationalError, msg:
                    logger.error("A SQL error occurred: %s", msg)
                    return False

                try:
                    t = ( sampleWeight, stddevWeight, sampleCounter )
                    print(
                        'update tblSample set f_postFireWeightAverage=%f, f_postFireWeightStdDev=%f where i_runID=1 and i_positionNumber=%d  ' % t)
                    c.execute(
                        'update tblSample set f_postFireWeightAverage=?, f_postFireWeightStdDev=? where i_runID=1 and i_positionNumber=?  ',
                        t)
                    conn.commit
                    c.execute(
                        'select  f_postFireWeightAverage, f_postFireWeightStdDev from tblSample where  i_runID=1 and i_positionNumber=%d  ' % sampleCounter)
                    data = c.fetchone()
                    #print "Values -- averageWeight: %s  stdDev: %s ", (data['f_postFireWeightAverage'],data['f_postFireWeightStdDev'])
                except sqlite.OperationalError, msg:
                    logger.error("A SQL error occurred: %s", msg)
                    return False
            sampleCounter += 1
        stateCounter += 1
    closeDatabase()
    msg = "Data update is complete."
    title = "Done"
    if easygui.ccbox(msg, title):     # show a Continue/Cancel dialog
        return "continue"
    else:
        return "cancel"


#############################################################

#Label(root, text="File Name:").grid(row=0, column=0)
#Entry(root, textvariable=FILENAME).grid(row=0, column=1)
#Label(root, text="Directory:").grid(row=1, column=0)
#Entry(root, textvariable=DIRECTORY).grid(row=1, column=1)
Button(root, text="Weigh Empty Crucibles", command=emptyCrucibleRun).grid(row=2, column=0)
Button(root, text="Weigh Initial Sherds and Crucibles", command=initialSherdRun).grid(row=2, column=1)
Button(root, text="Weigh Prefire (105) Sherds and Crucibles", command=prefireCrucibleRun).grid(row=2, column=2)
Button(root, text="Weigh Postfire (550) Sherds and Crucibles", command=postfireCrucibleRun).grid(row=2, column=3)
Button(root, text="Repair Datafile", command=updateAndFixAverageValues).grid(row=2, column=4)
Button(root, text="Quit", command=quit).grid(row=3, column=1, padx=2, pady=2)

root.mainloop()