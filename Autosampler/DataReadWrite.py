#!/usr/bin/python
# Filename: DataReadWrite.py

import logging
import sqlite3 as sqlite
import time
from ctypes import *
import math
import os
import io
import sys
import serial
import serial
import easygui

## comment for Mac OS X
#sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
from time import sleep
import sched, time
import signal
import sys
import random
import csv
import re
import numpy as np
from numpy import *
from datetime import datetime
from datetime import timedelta
import os.path
import os
import ComPorts
import easygui
from decimal import Decimal

logger = logging.getLogger("AutoSampler-DataReadWrite")
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
today_date = datetime.today()
datestring = today_date.strftime("%Y-%m-%d-%H-%M")

# check the os to determine the debug file location
debugfilename = ""
if sys.platform == "win32":
    debugfilename = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Logs/rhx-DataReadWrite-" + datestring + "_debug.log"
elif sys.platform == "darwin":
    debugfilename = "/Users/Clipo/Dropbox/Rehydroxylation/Logger/Logs/rhx-startRHX" + datestring + "_debug.log"
else:
    print "Platform is ", sys.platform, " which is not recognized.  Exiting."
    sys.exit()

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

############################################CONSTANTS##############################
## set this to FALSE until there is a standard balance in use
STANDARDBALANCE = True

INSIDE_BALANCE_POSITION = 20000  ##rough guess for y-axis for error checking
OUTSIDE_BALANCE_POSITION = 10000  ## rough guess for y-axis error checking
###############################################################################
def alertWindow(message):
    title = "RHX ERROR!"
    while 1:
        easygui.msgbox(message, title, ok_button="Exit")     # show a Continue/Cancel dialog
    return

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

non_decimal = re.compile(r'[^\d.]+')
float_pat = re.compile('[0-9]+(\.[0-9]+)?')

balance = serial
standard_balance = serial

if sys.platform == "win32":
    try:
        balance = serial.Serial(port=ComPorts.UltraBalance, baudrate=9600, bytesize=8, parity='N', stopbits=1,
                                timeout=10,
                                xonxoff=1, rtscts=0)
    except:
        message = "Cannot open serial port Com %s for the ultra balance. Check CompPorts.py. Quitting." % ComPorts\
        .UltraBalance
        alertWindow(message)
        sys.exit()

    if STANDARDBALANCE is True:
        try:
            standard_balance = serial.Serial(port=ComPorts.StandardBalance, baudrate=9600, bytesize=8, parity='N',
                                             stopbits=1, timeout=1, xonxoff=0)
        except:
            message = "Cannot open serial port Com %s for the standard balance. Check CompPorts.py.  Quitting." % ComPorts\
            .StandardBalance
            alertWindow(message)
            sys.exit()

elif sys.platform == "darwin":
    print "No balances since we are on a MAC "
else:
    print "Platform is ", sys.platform, " which is not recognized.  Exiting."
    sys.exit()

SQLFILENAME = ""
if sys.platform == "darwin":
    SQLFILENAME = "/Users/Clipo/Dropbox/Rehydroxylation/Logger/SQL/RHX-New.sql"
else:
    SQLFILENAME = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/SQL/RHX-New.sql"

XYDBFILENAME = ""
if sys.platform == "darwin":
    XYDBFILENAME = "/Users/Clipo/Dropbox/Rehydroxylation/Logger/Data/RHX.sqlite"
else:
    XYDBFILENAME = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Data/RHX.sqlite"

#  open the sqlite database and create a connection
# create a cursor to the database

xyconn = sqlite.connect(XYDBFILENAME, detect_types=sqlite.PARSE_DECLTYPES)
path = '/Users/Clipo/Dropbox/Rehydroxylation/Logger/RequiredFiles/libsqlitefunctions.so'

path = ""
if sys.platform == "win32":
    path = 'c:/Users/Archy/Dropbox/Rehydroxylation/Logger/RequiredFiles/libsqlitefunctions.so'
elif sys.platform == "darwin":
    # Im not sure this will work on Mac OS (i.e., loading the static library)
    path = '/Users/Archy/Dropbox/Rehydroxylation/Logger/RequiredFiles/libsqlitefunctions.so'

# open the sqlite database and create a connection
# create a cursor to the database
xyconn.enable_load_extension(True)
xyconn.load_extension(path)
xyconn.row_factory = dict_factory
xyconn.isolation_level = 'EXCLUSIVE'
xyconn.execute('BEGIN EXCLUSIVE')

#######################################################################################
####### NO LONGER USED HERE --- DB FILE IS CREATED BY WEIGHAPP.PY ####################
def initializeDatabase(dirname, filename):
    global conn
    file_list = []
    extension = ".sqlite"
    file_list.append(dirname)
    file_list.append(filename)
    file_list.append(extension)
    dbfilename = ''.join(file_list)

    #if os.path.exists(dbfilename) is True:
    #   print "Database ", dbfilename, " already exists."
    #   #value=raw_input('Do you want to write over this file and delete its contents? (y/n)')
    #   value = ask_for_delete_file(dbfilename)
    #   os.remove(dbfilename)

    # open the sqlite database and create a connection
    conn = sqlite.connect(dbfilename, detect_types=sqlite.PARSE_DECLTYPES, isolation_level=None)
    # create a cursor to the database

    path = ""
    if sys.platform == "win32":
        path = 'c:/Users/Archy/Dropbox/Rehydroxylation/Logger/RequiredFiles/libsqlitefunctions.so'
    elif sys.platform == "darwin":
        # Im not sure this will work on Mac OS (i.e., loading the static library)
        path = '/Users/Archy/Dropbox/Rehydroxylation/Logger/RequiredFiles/libsqlitefunctions.so'
    path = 'c:/Users/Archy/Dropbox/Rehydroxylation/Logger/RequiredFiles/libsqlitefunctions.so'
    # open the sqlite database and create a connection
    # create a cursor to the database
    conn.enable_load_extension(True)
    conn.load_extension(path)
    conn.row_factory = dict_factory
    try:
        dbfilename = ""
        c = conn.cursor()
        if sys.platform == "win32":
            dbfilename = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/SQL/RHX.sql"
        elif sys.platform == "darwin":
            dbfilename = "/Users/Archy/Dropbox/Rehydroxylation/Logger/SQL/RHX.sql"
        else:
            print "Not a recognized platform. Exiting."
            sys.exit()

        for line in open(SQLFILENAME):
            c.execute(line)
            conn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred initializeDatabase: %s", msg)
        return False

#######################################################################################

#### NOT USED ######
def ask_for_crucible(crucible):
    msg = "Please place crucible %d on balance and hit Continue when stabilized" % crucible
    title = "Add Crucible"
    if easygui.ccbox(msg, title):     # show a Continue/Cancel dialog
        return "continue"  # user chose Continue
    else:
        return "exit"

#####################

def quit():
    closeXYDatabase()
    closeDatabase()
    sys.exit()


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
            return True
        except sqlite.OperationalError, msg:
            logger.error("A SQL error occurred in closeDatabase: %s", msg)
            return False
    return True


def closeXYDatabase():
# Ensure variable is defined
    try:
        xyconn
    except NameError:
        xyconn = None
    if xyconn is not None:
        try:
            xyconn.commit()
            xyconn.close()
            return True
        except sqlite.OperationalError, msg:
            logger.error("A SQL error occurred in closeXYDatabase: %s", msg)
            return False
    return True


def openDatabase(dbfilename):
    global conn
    try:
        conn = sqlite.connect(dbfilename, detect_types=sqlite.PARSE_DECLTYPES, isolation_level=None)
        ## Mac OS X
        path = ""
        if sys.platform == "darwin":
            path = '/Users/Clipo/Dropbox/Rehydroxylation/Logger/RequiredFiles/libsqlitefunctions.so'
        else:
            path = 'c:/Users/Archy/Dropbox/Rehydroxylation/Logger/RequiredFiles/libsqlitefunctions.so'

        # open the sqlite database and create a connection
        # create a cursor to the database
        conn.enable_load_extension(True)
        conn.load_extension(path)
        conn.row_factory = dict_factory
        conn.isolation_level = 'EXCLUSIVE'
        conn.execute('BEGIN EXCLUSIVE')
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in openDatabase: %s", msg)
        return False

## if the sqlite file is already in existence and you have the file handle -- just need to do this...
def reopenDatabase(filename):
    #print "filename:", filename
    global conn
    try:
        conn = sqlite.connect(filename, detect_types=sqlite.PARSE_DECLTYPES, isolation_level=None)
        path = ""
        if sys.platform == "darwin":
            ## Mac os X
            path = '/Users/Archy/Dropbox/Rehydroxylation/Logger/RequiredFiles/libsqlitefunctions.so'
        else:
            path = 'c:/Users/Archy/Dropbox/Rehydroxylation/Logger/RequiredFiles/libsqlitefunctions.so'

        # open the sqlite database and create a connection
        # create a cursor to the database
        conn.enable_load_extension(True)
        conn.load_extension(path)
        conn.row_factory = dict_factory
        conn.isolation_level = 'EXCLUSIVE'
        conn.execute('BEGIN EXCLUSIVE')
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in reopenDatabase: %s", msg)
        return False


def getLastRunID():
    maxrun = 0
    try:
        c = conn.cursor()
        logger.debug("select max(i_runID) as max from tblRun")
        c.execute("select max(i_runID) as max from tblRun")
        maxrun = c.fetchone()["max"]
        if (maxrun is None):
            return 0
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in getLastRunID: %s", msg)
        return False
    return maxrun


def updatePosition(xpos, ypos, zpos):
    c = xyconn.cursor()
    t = (xpos, ypos, zpos)
    try:
        logger.debug('update tblXY SET i_xposition=%d, i_yposition=%d, i_zposition=%d where rowid=1' % (t))
        c.execute('update tblXY SET i_xposition=?, i_yposition=?, i_zposition=? where rowid=1', t)
        # Save (commit) the changes
        xyconn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in updatePosition: %s", msg)
        return False


def zeroBalance():
    balance.write(str.encode("ZI\r\n"))
    bline = balance.readline()
    if (bline.startswith("ZI I")   ):
        logger.debug("Balance says: %s", bline)
        return False
    else:
        return True


def setPosition(x, y, z):
    c = xyconn.cursor()
    t = (x, y, z)
    try:
        logger.debug('update tblXY SET i_xposition=%d, i_yposition=%d, i_zposition=%d where rowid=1' % (t))
        c.execute('update tblXY SET i_xposition=?, i_yposition=?, i_zposition=? where rowid=1', t)
        # Save (commit) the changes
        xyconn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in setPosition: %s", msg)
        return False


def getLastPosition():
    c = xyconn.cursor()
    logger.debug('Select i_xposition, i_yposition, i_zposition FROM tblXY where rowid=1')
    c.execute('Select i_xposition, i_yposition, i_zposition FROM tblXY where rowid=1')
    for row in c.fetchall():
        x = row["i_xposition"]
        y = row["i_yposition"]
        z = row["i_zposition"]
    return (x, y, z)


def openBalanceDoor():
    logger.debug("openBalanceDoor")
    logger.debug("Sending WS 1\r\n to balance")
    balance.write(str.encode("WS 1\r\n"))
    logger.debug("Balance replies: %s", balance.readline())
    sleep(1)
    return True


def closeBalanceDoor():
    logging.debug("closeBalanceDoor")
    logging.debug("Sending WS 0\r\n to balance")
    balance.write(str.encode("WS 0\r\n"))
    logging.debug("Balance replies: %s", balance.readline())
    sleep(1)
    return True


def isBalanceDoorOpen():
    logger.debug("isBalanceDoorOpen")
    vals = []
    balance.write(str.encode("M37\r\n"))
    bline = balance.readline()
    bline.rstrip("\r\n") + " "
    logger.debug("Balance says:  %s", bline)
    if (bline.rfind("S") > 0):
        logger.debug("sleeping and trying again...")
        sleep(3)
        bline = balance.readline()
        bline.rstrip("\r\n") + " "
        logger.debug("Balance now says:  %s", bline)
    try:
        vals = bline.split(" ", 3)
    except:
        return "UNKNOWN"
    val = int(vals[2])
    logger.debug("balance value: %s", val)
    #status=val.rstrip()
    # 0 is the CLOSED status
    # 2 or 1 is the OPEN status
    if val < 80:
        return "CLOSED"
    else:
        return "OPEN"


def getMaxPreFireCount(runID, position):
    max = 0
    try:
        c = conn.cursor()
        t = (runID, position)
        logger.debug(
            "select max(i_count) as max from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=1" % (
                t))
        c.execute(
            "select max(i_count) as max from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=1",
            t)
        max = c.fetchone()["max"]
        if (max is None):
            max = 0
        return max
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in getMaxPreFireCount: %s", msg)
        return 0


def getMaxPostFireCount(runID, position):
    max = 0
    try:
        c = conn.cursor()
        t = (runID, position)
        logger.debug(
            "select max(i_count) as max from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=2" % (
                t))
        c.execute(
            "select max(i_count) as max from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=2",
            t)
        max = c.fetchone()["max"]
        if max is None:
            max = 0
        return max
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in getMaxPostFireCount: %s", msg)
        return 0


def getPrefireAttributes(runID):
    initials = ""
    name = ""
    location = ""
    numberOfSamples = 0
    startPosition = 1
    durationOfMeasurements = 0
    samplingInterval = 5
    repetitions = 1
    locationTemperature = 0.0
    locationHumidity = 0.0

    try:
        c = conn.cursor()

        c.execute("select i_repetitions,v_locationCode,i_numberOfSamples,v_operatorName,i_equilibrationDuration, \
         t_assemblageName,f_temperature,f_humidity,f_locationTemperature,f_locationHumidity, \
         v_status,i_loggingInterval,i_durationOfPreMeasurements from tblRun where i_runID = %d"
            , runID)

        row = c.fetchone()
        location = row["v_locationCode"]
        initials = row["v_operatorName"]
        name = row["t_assemblageName"]
        numberOfSamples = row["i_numberOfSamples"]
        durationOfMeasurements = row["i_durationOfPreMeasurements"]
        samplingInterval = row["i_loggingInterval"]
        repetitions = row["i_repetitions"]
        locationTemperature = row["f_locationTemperature"]
        locationHumidity = row["f_locationHumidity"]

        return initials, name, location, numberOfSamples, startPosition, durationOfMeasurements, samplingInterval, repetitions, locationTemperature, locationHumidity

    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in getPrefireAttributes: %s", msg)
        return 0


def getPostfireAttributes():
    try:
        c = conn.cursor()
        c.execute(
            "select i_numberOfSamples,i_durationOfPostMeasurements,i_loggingInterval, i_repetitions from tblRun where i_runID = 1")
        row = c.fetchone()
        numberOfSamples = row["i_numberOfSamples"]
        duration = row["i_durationOfPostMeasurements"]
        interval = row["i_loggingInterval"]
        repetitions = row["i_repetitions"]

        return (numberOfSamples, duration, interval, repetitions)

    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in getPostfireAttributes: %s", msg)
        return 0


def insertPreFireMeasurement(runID, sampleID, position, weightMeasurement, status,
                             temperature, humidity, crucibleWeight, standard_weight, today, total_count, repetition,
                             repetition_count, count):
    logger.debug("insert prefire measurement.")
    # Find elapsed time
    now = datetime.today()
    today = now.strftime("%m-%d-%y %H:%M:%S")
    preOrPost = 1
    status = 1
    #sampleMeasurement = weightMeasurement - crucibleWeight
    try:
        c = conn.cursor()
        t = (
            runID, sampleID, position, weightMeasurement, status, now, temperature, humidity, standard_weight,
            total_count,
            repetition, repetition_count, count, preOrPost)
        logger.debug(
            'insert into tblMeasurement (i_runID,i_sampleID,i_positionNumber,f_weight,v_status,d_datetime,f_temperature,f_humidity,f_standardWeight, i_count,i_repetition,i_repetitionCount,i_count,i_preOrPost)  VALUES (%d,%d,%d,%f,%s,%s,%f,%f,%f,%d,%d,%d,%d,%d)' % (
                t))
        c.execute(
            'insert into tblMeasurement (i_runID,i_sampleID,i_positionNumber,f_weight,v_status,d_datetime,f_temperature,f_humidity,f_standardWeight, i_count,i_repetition,i_repetitionCount,i_count,i_preOrPost)  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
            , t)
        # Save (commit) the changes
        conn.commit()
        # Now get the id for the run so we can update with other info as we ask...
        measurementID = c.lastrowid
        return measurementID
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in insertPreFireMeasurement: %s", msg)
        return False


def insertPostFireMeasurement(runID, sampleID, positionNumber, weightMeasurement, status,
                              temperature, humidity, endOfFiring,
                              crucibleWeight, standard_weight, today, total_count, repetition, repetition_count, count):
    logger.debug("Insert post fire measurement.")
    # Find elapsed time
    now = datetime.today()
    today = now.strftime("%m-%d-%y %H:%M:%S")

    elapsedTime = now - endOfFiring

    elapsedTimeSec = elapsedTime.total_seconds()
    logger.debug("Time elapsed (seconds): %d", elapsedTimeSec)
    elapsedTimeMin = float(elapsedTimeSec / 60)
    logger.debug("Time elapsed (minutes): %f", elapsedTimeMin)
    elapsedTimeQuarterPower = float(pow(abs(elapsedTimeMin), 0.25))
    logger.debug("Time elapsed (min) ^ 0.25: %f", elapsedTimeQuarterPower)
    #sampleMeasurement = weightMeasurement - crucibleWeight
    preOrPost = 4
    status = 4
    try:
        c = conn.cursor()
        ### %d,%d,%d,%f,%s,%s,%d,%f,%f,%f,%f,%f,%f,%d,%d,%d,%d
        t = (runID, sampleID, positionNumber, weightMeasurement, status,
             now, elapsedTimeMin, elapsedTimeQuarterPower, temperature,
             humidity, standard_weight, total_count, repetition, repetition_count, count, preOrPost)

        ### logger.debug('insert into tblMeasurement (i_runID,i_sampleID,i_positionNumber,f_weight,v_status,d_datetime,f_elapsedTimeMin,f_elapsedTimeQuarterPower,f_temperature,f_humidity,f_standardWeight,i_count,i_repetition,i_repetitionCount,i_count,i_preOrPost)  VALUES ( %d,%d,%d,%f,%s,%s,%d,%f,%f,%f,%f,%f,%f,%d,%d,%d,%d,%d)' %(t))
        c.execute('insert into tblMeasurement (i_runID,i_sampleID,i_positionNumber,f_weight,v_status, \
                d_datetime,f_elapsedTimeMin,f_elapsedTimeQuarterPower,f_temperature, \
                f_humidity,f_standardWeight,i_count,i_repetition, \
                i_repetitionCount,i_count,i_preOrPost) \
                VALUES (?,?,?,?,?, \
                ?,?,?,?, \
                ?,?,?,?, \
                ?,?,?)', t)

        # Save (commit) the changes
        conn.commit()
        # Now get the id for the run so we can update with other info as we ask...
        measurementID = c.lastrowid
        return measurementID
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in insertPostFireMeasurement: %s", msg)
        return False


def updateRunInformation(i_numberOfSamples, v_operatorName, v_locationCode, t_assemblageName, f_locationTemperature,
                         t_notes, runID):
    #print "ASSEMBLAGE NAME IS BEING UPDATED: ", t_assemblageName
    try:
        c = conn.cursor()
        t = (i_numberOfSamples, v_operatorName, v_locationCode, t_assemblageName, f_locationTemperature, t_notes, runID)
        logger.debug(
            "update tblRun set i_numberOfSamples=%d, v_operatorName=%s, v_locationCode=%s,t_assemblageName=%s,f_locationTemperature=%s, t_notes=%s where i_RunID=%d" % (
                t))
        c.execute(
            'update tblRun set i_numberOfSamples=?,  v_operatorName=?,  v_locationCode=?, t_assemblageName=?, f_locationTemperature=?, t_notes=?  where i_RunID=?',
            t)
        conn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in updateRunInformation: %s", msg)
        return False


def updateRunInfoWithFiringInformation(d_dateTimeFiring, i_temperatureOfFiring, i_durationOfFiring, runID):
    end = timedelta(minutes=i_durationOfFiring)
    endOfFiring = datetime
    endOfFiring = d_dateTimeFiring + end
    d_endOfFiring = endOfFiring.strftime("%m-%d-%y %H:%M:%S")

    try:
        c = conn.cursor()
        t = (d_dateTimeFiring, i_durationOfFiring, d_endOfFiring, i_temperatureOfFiring, i_durationOfFiring, runID)
        logger.debug(
            "update tblRun set d_dateTimeFiring=%s,i_durationOfFiring=%d, d_endOfFiring=%s, i_temperatureOfFiring=%d, i_durationOfFiring=%d where i_RunID=%d" % (
                t))
        c.execute(
            'update tblRun set  d_dateTimeFiring=?,i_durationOfFiring=?, d_endOfFiring=?, i_temperatureOfFiring=?, i_durationOfFiring=? where i_RunID=?',
            t)
        conn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in updateRunInfoWithFiringInformation: %s", msg)
        return False


def getRunInfo(runID):
    locationCode = ""
    numberOfSamples = 0
    description = ""
    temperature = 0.0
    humidity = 0.0
    status = True
    row = []
    try:
        c = conn.cursor()
        logger.debug(
            "select v_locationCode, i_numberOfSamples, t_assemblageName, f_locationTemperature, f_locationHumidity, d_dateTimeFiring, i_durationOfFiring,i_temperatureOfFiring, v_operatorName, t_notes from tblRun where i_runID = %d" % (
                runID))
        c.execute(
            'select v_locationCode, i_numberOfSamples, t_assemblageName, f_locationTemperature, f_locationHumidity, d_dateTimeFiring ,i_durationOfFiring,i_temperatureOfFiring, v_operatorName, t_notes from tblRun where i_runID=%s' % runID)
        data = c.fetchone()
        i_numberOfSamples = data["i_numberOfSamples"]
        v_operatorName = data["v_operatorName"]
        v_locationCode = data["v_locationCode"]
        t_assemblageName = data["t_assemblageName"]
        f_locationTemperature = data["f_locationTemperature"]
        i_temperatureOfFiring = data["i_temperatureOfFiring"]
        i_durationOfFiring = data["i_durationOfFiring"]
        f_locationHumidity = data["f_locationHumidity"]
        d_dateTimeFiring = data["d_dateTimeFiring"]
        t_notes = data["t_notes"]
        return (
            v_locationCode, i_numberOfSamples, t_assemblageName, f_locationTemperature, f_locationHumidity,
            d_dateTimeFiring,
            i_durationOfFiring, i_temperatureOfFiring, v_operatorName, t_notes)
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in getRunInfo: %s" % msg)
        return False


def readStandardBalance():
    ## balance read
    non_decimal = re.compile(r'[^\d.]+')

    ## first ask for a value
    try:
        standard_balance.write("SI\n\r")
    except:
        print "There has been an error reading the standard balance. You may need to disconnect and try again.\n"

    ## now read value from balance
    try:
        bline = standard_balance.readline()
    except:
        bline = None

    weight = float(0.0)  # set weight to 0.0

    if bline is not None:
        if len(bline) == 18:
            ## bbline is bline stripped of the beginning and ending stuff
            bbline = bline.lstrip(" S S   ")
            bbline = bline.lstrip(" S D   ")
            weights = bbline.replace(" g", "")
            weights = weights.rstrip()
            weight = float(non_decimal.sub('', weights))

    return weight


def readWeightFromBalance():
    logger.debug("Reading weight from balance")
    ## balance read
    status = ""
    balance.write("S\n\r")
    bline = balance.readline()
    code = []
    if (len(bline) > 4):
        code.append(bline[0])
        code.append(bline[1])
        code.append(bline[2])
        string = ''.join(code)
        logger.debug("String value: %s" % string)
        if string == "S S":
            status = "Stable"
        elif string == "S D":
            status = "Unstable"
        elif string == "S I":
            status = "Busy"
    else:
        status = "Error"

    logger.debug("Balance Ouput:%s--%s" % ( bline, status))
    weight = float(0.0)
    result = []
    if len(bline) == 18:
        bbline = bline.lstrip("S S   ")
        weights = bbline.replace(" g", "")
        weights = weights.rstrip(" ")
        weights = weights[:-1]
        weights = weights.rstrip("\n")
        weights = weights.rstrip("\r")
        weight = non_decimal.sub('', weights)
        #weight=re.search(float_pat,weights)
        if weight == "":
            weight = 0.0
            #if weight.count('.')>1:
        #   weight=0.0
        result.append(weight)
        result.append(status)
        logger.debug("WEIGHT: %s " % (weight))
        return result
    else:
        #try getting an instant reading
        (weight, status) = readInstantWeightFromBalance()
        if (result == "error"):
            return 0.0, "error"
        else:
            return weight, "Unstable"


def readInstantWeightFromBalance():
    ## balance read
    logger.debug("Reading instant weight from balance")
    non_decimal = re.compile(r'[^\d.]+')
    balance.write("SI\n\r")
    bline = balance.readline()
    logger.debug("instant read: %s" % (bline))
    code = []
    code.append(bline[0])
    code.append(bline[1])
    code.append(bline[2])
    string = ''.join(code)
    logger.debug("String value: %s" % (string))
    if string == "S S":
        status = "Stable"
    elif string == "S D":
        status = "Unstable"
    elif string == "S I":
        status = "Busy"
    else:
        status = "Error"
    logger.debug("Balance Ouput:%s--%s" % (bline, status))

    weight = float(0.0)
    result = []
    if len(bline) == 18:
        bbline = bline.lstrip("S S   ")
        bbline = bline.lstrip("S D   ")
        weights = bbline.replace(" g", "")
        weights = weights.rstrip()
        weight = non_decimal.sub('', weights)

        if weight == "":
            weight = 0.0
        logger.debug("Weight: %s", weight)
        result.append(weight)
        result.append(status)
        return result
    else:
        return (0.0, "error")


def insertInitialCrucible(runID, position, today):
    logger.debug("insert initial crucible into tblCrucible")
    try:
        c = conn.cursor()
        t = (runID, today, position)
        logger.debug('insert INTO tblCrucible (i_runID, d_datetime, i_positionNumber) VALUES (%d,%s,%i)' % (t))
        c.execute('insert INTO tblCrucible (i_runID, d_datetime, i_positionNumber) VALUES (?,?,?)', t)
        conn.commit()
        crucibleID = c.lastrowid
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in insertInitialCrucible: %s", msg)
        return False
    return crucibleID


def insertCrucibleMeasurement(runID, positionNumber, weight, status, temperature, humidity, count, now):
    logger.debug("insert crucible measurement into tblMeasurement")
    preOrPost = 0
    measurementID = 0
    now = datetime.today()
    try:
        c = conn.cursor()
        t = (runID, positionNumber, weight, status, now, temperature, humidity, count, preOrPost)
        #print runID,positionNumber,weight,status,now,temperature,humidity,count,preOrPost
        logger.debug('insert into tblMeasurement (i_runID,i_positionNumber,f_weight,v_status,d_datetime,'\
                     'f_temperature,f_humidity,i_count,i_preOrPost)  '\
                     'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)' % (t))
        c.execute('insert into tblMeasurement (i_runID,i_positionNumber,f_weight,v_status,d_datetime,'\
                  'f_temperature,f_humidity,i_count,i_preOrPost)  '\
                  'VALUES (?,?,?,?,?,?,?,?,?)', t)
        conn.commit()
        measurementID = c.lastrowid
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in insertCrucibleMeasurement: %s", msg)
        return False
    return measurementID


def updateCrucible(position, averageWeight, stdevWeight, averageTemp, stdevTemp, averageHumidity, stdevHumidity, today,
                   runID, count):
    logger.debug("update crucible record with weight, etc.")
    now = datetime.today()
    try:
        c = conn.cursor()
        t = (float(averageWeight), float(stdevWeight), float(averageTemp), float(stdevTemp), float(averageHumidity),
             float(stdevHumidity), now, count, position, runID)
        logger.debug(
            'update tblCrucible SET f_averageWeight=%f, f_stdevWeight=%f, f_averageTemp=%f, f_stdevTemp=%f,f_averageHumidity=%f, f_stdevHumidity=%f, d_datetime=%s, i_count=%d WHERE i_positionNumber=%d AND i_runID=%d' % t)
        c.execute(
            'update tblCrucible SET f_averageWeight=?, f_stdevWeight=?, f_averageTemp=?, f_stdevTemp=?, f_averageHumidity=?, f_stdevHumidity=?, d_datetime=?, i_count=? WHERE i_positionNumber=? AND i_runID=?'
            , t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in updateCrucible: %s", msg)
        return False
    return True


def updateChamberCrucible(position, averageWeight, stdevWeight, today, count):
    logger.debug("update crucible record in tblCrucibleXY in RHX.sqlite with weight, etc.")
    now = datetime.today()
    try:
        c = xyconn.cursor()
        t = (float(averageWeight), float(stdevWeight), now, count, position)
        logger.debug(
            'update tblCrucibleXY SET f_weightAverage=%f, f_weightStdDev=%f, d_weightDateTime=%s, '
            'i_weightCount=%d WHERE i_samplePosition=%d' % t)
        c.execute(
            'update tblCrucibleXY SET f_weightAverage=?, f_weightStdDev=?, d_weightDateTime=?, '
            'i_weightCount=? WHERE i_samplePosition=?'
            , t)
        xyconn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in updateChamberCrucible: %s", msg)
        return False
    return True


def getInitialSherd(position, runID):
    logger.debug("get sherd weight before prefire ")
    now = datetime.today()
    try:
        c = conn.cursor()
        t = (position, runID)
        logger.debug(
            'select f_sherdWeightInitialAverage, f_sherdWeightInitialStdDev from tblSample WHERE i_positionNumber=%d AND i_runID=%d' % t)
        c.execute(
            'select f_sherdWeightInitialAverage, f_sherdWeightInitialStdDev from tblSample WHERE i_positionNumber=? AND i_runID=?'
            , t)
        data = c.fetchone()
        if data is None:
            return False
        return float(data["f_sherdWeightInitialAverage"]), float(data["f_sherdWeightInitialStdDev"])
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in getInitialSherd: %s", msg)
        return False
    return True


def getEmptyCrucible(position, runID):
    logger.debug("get crucible weight before prefire ")
    now = datetime.today()
    try:
        c = conn.cursor()
        t = (position, runID)
        logger.debug(
            'select f_emptyWeightAverage, f_emptyWeightStdDev, i_emptyWeightCount from tblCrucible WHERE i_positionNumber=%d AND i_runID=%d' % t)
        c.execute(
            'select f_emptyWeightAverage, f_emptyWeightStdDev, i_emptyWeightCount from tblCrucible WHERE i_positionNumber=? AND i_runID=?'
            , t)
        data = c.fetchone()
        if (data is None):
            return False
        return float(data["f_emptyWeightAverage"]), float(data["f_emptyWeightStdDev"]), int(data["i_emptyWeightCount"])
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in getEmptyCrucible: %s", msg)
        return False
    return True


def getPreFireSherd(position, runID):
    logger.debug("get crucible weight for 105 prefire... ")
    now = datetime.today()
    try:
        c = conn.cursor()
        t = (position, runID)
        logger.debug(
            'select f_preWeightAverage, f_preWeightStdDev from tblSample WHERE i_positionNumber=%d AND '
            'i_runID=%d' % t)
        c.execute(
            'select f_preWeightAverage, f_preWeightStdDev from tblSample WHERE i_positionNumber=? AND i_runID=?'
            , t)
        data = c.fetchone()
        if data is None:
            return False
        return float(data["f_preWeightAverage"]), float(data["f_preWeightStdDev"])
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in get105Crucible: %s", msg)
        return False
    return True


def getPostFireSherd(position, runID):
    logger.debug("get crucible weight for 105 prefire... ")
    now = datetime.today()
    try:
        c = conn.cursor()
        t = (position, runID)
        logger.debug(
            'select f_postFireWeightAverage, f_postFireWeightStdDev from tblSample WHERE i_positionNumber=%d AND '
            'i_runID=%d' % t)
        c.execute(
            'select f_postFireWeightAverage, f_postFireWeightStdDev from tblSample WHERE i_positionNumber=? AND i_runID=?',
            t)
        data = c.fetchone()
        if data is None:
            return False
        return float(data["f_postFireWeightAverage"]), float(data["f_postFireWeightStdDev"])
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurredin get550Crucible: %s", msg)
        return False
    return True


def insertRun(setInitials, today, numberOfSamples):
    logger.debug("insert run")
    now = datetime.today()
    try:
        t = (setInitials, now, numberOfSamples)
        # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        c.execute('insert into tblRun (v_operatorName,d_datetime,i_numberOfSamples) VALUES (?,?,?)', t)
        logger.debug('insert into tblRun (v_operatorName,d_datetime,i_numberOfSamples) VALUES (%s,%s,%d)' % (t))
        # Save (commit) the changes
        conn.commit()
        # Now get the id for the run so we can update with other info as we ask...
        runID = c.lastrowid
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in insertRun: %s", msg)
        return False
    return runID


def updateTempRHCorrection(tempCorrection, rhCorrection, runID):
    logger.debug("update correction for temp and humidity")
    try:
        t = (tempCorrection, rhCorrection, runID)
        c = conn.cursor()
        c.execute('update tblRun set f_tempCorrection=?, f_rhCorrection=? where i_runID=?', t)
        conn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in updateTempRHCorrection: %s", msg)
        return False


def updateRunPreFire( runID, setInitials, assemblage, setLocation, setTemperature, setHumidity, status,
                      numberOfSamples):
    now = datetime.today()
    logger.debug("update run pre fire")
    try:
        t = (setInitials, now, assemblage, setLocation, setTemperature, setHumidity, status, numberOfSamples, runID)
        # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        logger.debug(
            'update tblRun SET v_operatorName=%s, d_datetime=%s, t_assemblageName=%s, v_locationCode=%s, f_locationTemperature=%f, f_LocationHumidity=%f, v_status=%s, i_numberOfSamples=%d WHERE i_runID=%d' % (
                t))
        c.execute(
            'update tblRun SET v_operatorName=?, d_datetime=?, t_assemblageName=?, v_locationCode=?, f_locationTemperature=?, f_locationHumidity=?, v_status=?, i_numberOfSamples=? WHERE i_runID=?',
            t)
        # Save (commit) the changes
        conn.commit()
        return runID
    except sqlite.OperationalError, msg:
        logger.debug("A SQL error occurred in updateRunPreFire: %s", msg)
        return False


def insertInitialSherd(i_runID, i_crucibleID, f_sampleWeightInitialAverage, f_sampleWeightInitialStdDev,
                       f_crucibleWeightAverage,
                       f_crucibleWeightStdDev):
    logger.debug("insert initial sample into tblSample")

    try:
        # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        t = (i_runID, i_crucibleID, f_sampleWeightInitialAverage, f_sampleWeightInitialStdDev, f_crucibleWeightAverage,
             f_crucibleWeightStdDev)
        logger.debug(
            'insert into tblSample (i_runID,i_positionNumber,f_sampleWeightInitialAverage,f_sampleWeightInitialStdDev,f_crucibleWeightAverage,f_crucibleWeightStdDev) VALUES (%d,%d,%f,%f,%f,%f)' % (
                t))    #

        c.execute(
            'insert into tblSample (i_runID,i_positionNumber,f_sampleWeightInitialAverage,f_sampleWeightInitialStdDev,f_crucibleWeightAverage,f_crucibleWeightStdDev) VALUES (?,?,?,?,?,?)',
            t)    #
        conn.commit()
        sampleID = c.lastrowid
        return (sampleID)
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in insertInitialSherd: %s", msg)
        return False


def getChamberCrucibleWeight(positionNumber):
    try:
        c = xyconn.cursor()
        averageWeight = float(0.0)
        c.execute('select f_weightAverage from tblCrucibleXY where i_samplePosition=%d' % positionNumber)
        logger.debug('select f_weightAverage from tblCrucibleXY where i_samplePosition=%d' % positionNumber)
        data = c.fetchone()
        if data is None:
            return 0.0
        else:
            returnValue = float(data["f_weightAverage"])
            return returnValue
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in getChamberCrucibleWeight: %s", msg)
    return 0.0


def getCrucibleWeightStats(positionNumber):
    try:
        runID = 1
        c = xyconn.cursor()
        t = (runID, positionNumber)
        c.execute('select f_weightAverage, f_weightStdDev from tblCrucibleXY where i_runID=? and i_positionNumber=?', t)
        logger.debug(
            'select f_weightAverage,f_weightStdDev from tblCrucibleXY where i_runID=%d and i_positionNumber=%d' % t)
        data = c.fetchone()
        if data is None:
            return False
        meanVal = float(data["f_weightAverage"])
        stdevVal = float(data["f_weightStdDev"])
        return meanVal, stdevVal
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getCrucibleWeightStats: %s", msg)
        return False


def getEndOfFiring(runID):
    try:
        c = conn.cursor()
        t = (runID,)
        endOfFiring = ""
        logger.debug('select d_endOfFiring from tblRun where i_runID=%d' % (runID))
        c.execute('select d_endOfFiring from tblRun where i_runID=%s ' % runID)    #

        data = c.fetchone()
        if data is None:
            return False
        returnValue = data["d_endOfFiring"]
        return returnValue
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getEndOfFiring: %s", msg)
        return False


def getSampleID(runID, position):
    try:
        c = conn.cursor()
        t = (runID, position)
        sampleID = 0
        logger.debug(
            'select i_sampleID, t_sampleName, t_assemblageName from tblSample where i_runID=%d and i_positionNumber=%d' % (
                t))
        c.execute(
            'select i_sampleID, t_sampleName, t_assemblageName  from tblSample where i_runID=%d and i_positionNumber=%d' % (
                t))
        sampleID = 0
        data = c.fetchone()
        if data is None:
            return False
        else:
            sampleID = data["i_sampleID"]
            sampleName = data["t_sampleName"]
            assemblageName = data["t_assemblageName"]
            return sampleID, sampleName, assemblageName
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getSampleID: %s", msg)
        return False


def updateRunPostFire(runID, status, postMeasurementTimeInterval, duration, repetitions, intervalsec, setHumidity):
    logger.debug("updateRunPostFire with values.")
    t = (setHumidity, status, postMeasurementTimeInterval, duration, repetitions, intervalsec, runID)
    try:
    # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        logger.debug(
            'update tblRun SET f_humidity=%f, v_status=%s,i_postMeasurementTimeInterval=%d,i_durationOfPostMeasurements=%d,i_repetitions=%d,i_loggingInterval=%d WHERE i_runID=%d' % (
                t))
        c.execute(
            'update tblRun SET f_humidity=?, v_status=?, i_postMeasurementTimeInterval=?,i_durationOfPostMeasurements=?,i_repetitions=?,i_loggingInterval=? WHERE i_runID=?'
            , t)
        # Save (commit) the changes
        conn.commit()
        # Now get the id for the run so we can update with other info as we ask...
        runID = c.lastrowid
        return runID
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateRunPostFire: %s", msg)
        return False

##Balance Door Controls
def BDOpen():
    logger.debug("opening the balance door")
    balance.write(str.encode("WS 1\r\n"))
    logger.debug("balance says: %s", balance.readline())
    return True


def BDClose():
    logger.debug("closing the balance door")
    balance.write(str.encode("WS 0\r\n"))
    logger.debug("balance says: %s", balance.readline())
    return True

##Balance Zeroing
def BZero():
    logger.debug("zeroing the balance")
    balance.write(str.encode("ZI\r\n"))
    sleep(2)
    logger.debug("balance says: %s", balance.readline())
    return True


def getStatsForPrefireWeightOfSample(runID, position, length):
    # first find out what the latest count is for this series of measurements
    max = int(getMaxPreFireCount(runID, position))
    limit = max - length
    t = (runID, position, limit)
    try:
        c = conn.cursor()
        logger.debug(
            'select avg(f_weight) as avg, stdev(f_weight) as stdev ,variance(f_weight) as variance, avg(f_temperature) as preTempAverage, stdev(f_temperature) as preTempStdDev, avg(f_humidity) as preHumidityAverage, stdev(f_humidity) as preHumidityStdDev from tblMeasurement where i_runID=%d AND i_positionNumber=%d AND i_count>%d AND i_preOrPost=1' % (
                t))
        c.execute(
            'select avg(f_weight) as avg, stdev(f_weight) as stdev, variance(f_weight) as variance, avg(f_temperature) as preTempAverage, stdev(f_temperature) as preTempStdDev, avg(f_humidity) as preHumidityAverage, stdev(f_humidity) as preHumidityStdDev from tblMeasurement where i_runID=? AND i_positionNumber=? AND i_count>? AND i_preOrPost=1'
            , t)
        data = c.fetchone()
        if (data is None):
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        else:
            avg = data['avg']
            stdev = data['stdev']
            variance = data['variance']
            tempMean = data['preTempAverage']
            tempStdev = data['preTempStdDev']
            humidityMean = data['preHumidityAverage']
            humidityStdev = data['preHumidityStdDev']
            return (avg, stdev, variance, tempMean, tempStdev, humidityMean, humidityStdev)
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getStatsForPrefireWeightOfSample: %s", msg)
        return False


def getStatsForPostFireWeightOfSample(runID, position, length):
    # first find out what the latest count is for this series of measurements
    max = int(getMaxPostFireCount(runID, position))
    limit = max - length
    t = (runID, position, limit)
    try:
        c = conn.cursor()
        logger.debug('select avg(f_weight) as avg ,stdev(f_weight) as stdev ,variance(f_weight) as variance, '\
                     'avg(f_temperature) as postTempAverage, stdev(f_temperature) as postTempStdDev, '\
                     'avg(f_humidity) as postHumidityAverage, stdev(f_humidity) as postHumidityStdDev   from '\
                     'tblMeasurement where i_runID=%d and i_positionNumber=%d and i_count>%d and i_preOrPost=2' % (t))
        c.execute(
            'select avg(f_weight) as avg, stdev(f_weight) as stdev, variance(f_weight) as variance, avg(f_temperature) as postTempAverage, stdev(f_temperature) as postTempStdDev, avg(f_humidity) as postHumidityAverage, stdev(f_humidity) as postHumidityStdDev   from tblMeasurement where i_runID=? and i_positionNumber=? and i_count>? and i_preOrPost=2'
            , t)
        data = c.fetchone()
        #print "DATA: ",data
        if ((data is None) or (data['avg'] == 0.0)):
            return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        else:
            avg = data['avg']
            stdev = data['stdev']
            variance = data['variance']
            tempMean = data['postTempAverage']
            tempStdev = data['postTempStdDev']
            humidityMean = data['postHumidityAverage']
            humidityStdev = data['postHumidityStdDev']
            return avg, stdev, variance, tempMean, tempStdev, humidityMean, humidityStdev
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getStatsForPostFireWeightOfSample: %s", msg)
        return False


def getXYForSampleLocation(sampleLocation):
    try:
        c = xyconn.cursor()
        logger.debug(
            'select i_xPosition, i_yPosition from tblCrucibleXY where i_samplePosition = %d' % (sampleLocation))
        c.execute('select i_xPosition, i_yPosition from tblCrucibleXY where i_samplePosition = %s' % sampleLocation)
        data = c.fetchone()
        if data is None:
            return 0, 0
        else:
            x = data['i_xPosition']
            y = data['i_yPosition']
            return x, y
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getXYForSampleLocation: %s", msg)
        return 0, 0


def getXYCoordinatesForSampleLocation(sampleLocation):
    try:
        c = xyconn.cursor()
        logger.debug(
            'select f_xDistance, f_yDistance from tblCrucibleXY where i_samplePosition = %d' % (sampleLocation))
        c.execute('select f_xDistance, f_yDistance from tblCrucibleXY where i_samplePosition = %s' % sampleLocation)
        data = c.fetchone()
        if (data is None):
            return 0, 0
        else:
            x = data['f_xDistance']
            y = data['f_yDistance']
            return x, y
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getXYCoordinatesForSampleLocation: %s", msg)
        return 0, 0


def getXYForInsideBalance():
    try:
        c = xyconn.cursor()
        t = ("BALANCE_INSIDE",)
        logger.debug('select i_xPosition, i_yPosition from tblCrucibleXY where v_type = %s' % t)
        c.execute('select i_xPosition, i_yPosition from tblCrucibleXY where v_type=?', t)
        data = c.fetchone()
        if data is None:
            return 0, 0
        else:
            x = data['i_xPosition']
            y = data['i_yPosition']
            return x, y
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getXYForInsideBalance: %s", msg)
        return 0, 0


def getXYForOutsideBalance():
    try:
        c = xyconn.cursor()
        t = ("BALANCE_OUTSIDE",)
        logger.debug('select i_xPosition, i_yPosition from tblCrucibleXY where v_type = %s' % t)
        c.execute('select i_xPosition, i_yPosition from tblCrucibleXY where v_type=?', t)
        data = c.fetchone()
        if data is None:
            return 0, 0
        else:
            x = data['i_xPosition']
            y = data['i_yPosition']
            return x, y
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getXYForOutsideBalance: %s", msg)
        return 0, 0


def getXYCoordinatesForOutsideBalance():
    try:
        c = xyconn.cursor()
        t = ("BALANCE_OUTSIDE",)
        logger.debug('select f_xDistance, f_yDistance from tblCrucibleXY where v_type = %s' % t)
        c.execute('select f_xDistance, f_yDistance from tblCrucibleXY where v_type=? ', t)
        data = c.fetchone()
        if data is None:
            return 0, 0
        else:
            x = data['f_xDistance']
            y = data['f_yDistance']
            return x, y
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getXYCoordinatesForOutsideBalance: %s", msg)
        return 0, 0


def getXYCoordinatesForInsideBalance():
    try:
        c = xyconn.cursor()
        t = ("BALANCE_INSIDE",)
        logger.debug('select f_xDistance, f_yDistance from tblCrucibleXY where v_type = %s' % t)
        c.execute('select f_xDistance, f_yDistance from tblCrucibleXY where v_type=? ', t)
        data = c.fetchone()
        if data is None:
            return 0, 0
        else:
            x = data['f_xDistance']
            y = data['f_yDistance']
            return x, y
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getXYCoordinatesForInsideBalance: %s", msg)
        return 0, 0


def updateXYCoordinatesForSampleLocation(position, x, y):
    try:
        c = xyconn.cursor()
        t = (x, y, position)
        logger.debug('update tblCrucibleXY SET f_xDistance=%d, f_yDistance=%d where i_samplePosition=%d' % t)
        c.execute('update tblCrucibleXY SET f_xDistance=?, f_yDistance=? where i_samplePosition=?', t)
        xyconn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateXYCoordinatesForSampleLocation: %s", msg)
        return False


def updateXYCoordinatesForOutsideBalance( x, y):
    try:
        c = xyconn.cursor()
        t = (x, y, "BALANCE_OUTSIDE")
        logger.debug('update tblCrucibleXY SET f_xDistance=%d, f_yDistance=%d where v_type=%s' % t)
        c.execute('update tblCrucibleXY SET f_xDistance=?, f_yDistance=? where v_type=?', t)
        xyconn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateXYCoordinatesForOutsideBalance: %s", msg)
        return False


def updateXYCoordinatesForInsideBalance(x, y):
    try:
        c = xyconn.cursor()
        t = (x, y, "BALANCE_INSIDE")
        logger.debug('update tblCrucibleXY SET f_xDistance=%d, f_yDistance=%d where v_type=%s' % t)
        c.execute('update tblCrucibleXY SET f_xDistance=?, f_yDistance=? where v_type=?', t)
        xyconn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateXYCoordinatesForInsideBalance: %s", msg)
        return False


def updateXYForSampleLocation(sampleLocation, x, y):
    try:
        c = xyconn.cursor()
        t = (x, y, sampleLocation)
        logger.debug('update tblCrucibleXY SET i_xPosition=%d, i_yPosition=%d where i_samplePosition=%d' % t)
        c.execute('update tblCrucibleXY SET i_xPosition=?, i_yPosition=? where i_samplePosition=?', t)
        xyconn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateXYForSampleLocation: %s", msg)
        return False


def updateXYForInsideBalance(x, y):
    try:
        c = xyconn.cursor()
        t = (x, y, "BALANCE_INSIDE")
        logger.debug('update tblCrucibleXY SET i_xPosition=%d, i_yPosition=%d where v_type=%s' % t)
        c.execute('update tblCrucibleXY SET i_xPosition=?, i_yPosition=? where v_type=?', t)
        xyconn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateXYForInsideBalance: %s", msg)
        return False


def updateXYForOutsideBalance(x, y):
    try:
        c = xyconn.cursor()
        t = (x, y, "BALANCE_OUTSIDE")
        logger.debug('update tblCrucibleXY SET i_xPosition=%d, i_yPosition=%d where v_type=%s' % t)
        c.execute('update tblCrucibleXY SET i_xPosition=?, i_yPosition=? where v_type=?', t)
        xyconn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateXYForOutsideBalance: %s", msg)
        return False


def updateZForSampleLocation(sampleLocation, sampleZPosition):
    try:
        c = xyconn.cursor()
        t = (int(sampleZPosition), "crucible")
        logger.debug('update tblCrucibleXY SET f_zPosition=%d where v_type=%s' % t)
        c.execute('update tblCrucibleXY SET f_zPosition=? where v_type=?', t)
        xyconn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateZForSampleLocation: %s", msg)
        return False


def updateZForBalanceLocation(balanceZPosition):
    try:
        c = xyconn.cursor()
        t = (int(balanceZPosition), "BALANCE_INSIDE")
        logger.debug('update tblCrucibleXY SET f_zPosition=%d where v_type=%s' % t)
        c.execute('update tblCrucibleXY SET f_zPosition=? where v_type=?', t)
        xyconn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateZForBalanceLocation: %s", msg)
        return False


def getZForSampleLocation(sampleLocation):
    try:
        c = xyconn.cursor()
        logger.debug('Select f_zPosition FROM tblCrucibleXY where i_samplePosition=%d' % (sampleLocation))
        c.execute('Select f_zPosition FROM tblCrucibleXY where i_samplePosition=%d' % sampleLocation)
        row = c.fetchone()
        return row['f_zPosition']
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getZForSampleLocation: %s", msg)
        return False


def getZForBalanceLocation():
    try:
        c = xyconn.cursor()
        logger.debug('Select f_zPosition FROM tblCrucibleXY where i_samplePosition=%d' % (INSIDE_BALANCE_POSITION))
        c.execute('Select f_zPosition FROM tblCrucibleXY where i_samplePosition=%d' % INSIDE_BALANCE_POSITION)
        row = c.fetchone()
        return row['f_zPosition']
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred getZForBalanceLocation: %s", msg)
        return False


def getCrucibleWeightOverTime(runID, sampleLocation):
    val = []
    count = 0
    try:
        c = conn.cursor()
        t = (runID, sampleLocation)
        logger.debug(
            'select f_weight from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=0' % t)
        c.execute('select f_weight from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=0', t)
        for row in c.fetchall():
            count += 1
            val.append(row['f_weight'])
        return val
    except sqlite.OperationalError, msg:
        logger.error("A SQL error has occurred getCrucibleWeightOverTime: %s", msg)
        return False


def getPreFireWeightOverTime(runID, sampleLocation):
    val = []
    count = 0
    try:
        c = conn.cursor()
        t = (runID, sampleLocation)
        logger.debug(
            'select f_weight from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=0' % t)
        c.execute('select f_weight from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=1', t)
        for row in c.fetchall():
            count += 1
            val.append(row['f_weight'])
        return val
    except sqlite.OperationalError, msg:
        logger.error("A SQL error has occurred getPreFireWeightOverTime: %s", msg)
        return False


def getPostFireWeightOverTime(runID, sampleLocation):
    val = []
    count = 0
    try:
        c = conn.cursor()
        t = (runID, sampleLocation)
        logger.debug(
            'select f_weight from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=0' % t)
        c.execute('select f_weight from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=2', t)
        for row in c.fetchall():
            count += 1
            val.append(row['f_weight'])
        return val
    except sqlite.OperationalError, msg:
        logger.error("A SQL error has occurred getPostFireWeightOverTime: %s", msg)
        return False


def getCrucibleWeightMeasurement(runID, sampleLocation, number):
    val = 0.0
    count = 0
    try:
        c = conn.cursor()
        t = (runID, sampleLocation, number)
        logger.debug(
            'select f_weight from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=0 and i_count=%d' % t)
        c.execute(
            'select f_weight from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=0 and i_count=?',
            t)
        row = c.fetchone()

        return float(row['f_weight'])
    except sqlite.OperationalError, msg:
        logger.error("A SQL error has occurred getCrucibleWeightMeasurement: %s", msg)
        return False


def updateSamplePreFire(i_runID, i_positionNumber,
                        f_preWeightAverage, f_preWeightStdDev,
                        f_sherdWeightInitialAverage, f_sherdWeightInitialStdDev,
                        f_preTemperatureAverage, f_preTemperatureStdDev,
                        f_preHumidityAverage, f_preHumidityStdDev):
    logger.debug("update tblSample with weights")
    try:
        # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        t = (f_preWeightAverage, f_preWeightStdDev,
             f_sherdWeightInitialAverage, f_sherdWeightInitialStdDev,
             f_preTemperatureAverage, f_preTemperatureStdDev,
             f_preHumidityAverage, f_preHumidityStdDev,
             i_runID, i_positionNumber)
        logger.debug('update tblSample SET f_preWeightAverage=%d, f_preWeightStdDev=%d,  \
        f_sherdWeightInitialAverage=%d, f_sherdWeightInitialStdDev=%d, f_preTempAverage=%d, f_preTempStdDev=%d, \
        f_preHumidityAverage=%d, f_preHumidityStDev=%d where i_runID=%d and i_positionNumber=%d' % t)

        c.execute('update tblSample SET f_preWeightAverage=?, f_preWeightStdDev=?,  \
        f_sherdWeightInitialAverage=?, f_sherdWeightInitialStdDev=?, f_preTempAverage=?, f_preTempStdDev=?, \
        f_preHumidityAverage=?, f_preHumidityStdDev=? where i_runID=? and i_positionNumber=?', t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred: %s", msg)
        return False

    crucibleWeight, crucibleStdDev, weightCount = getEmptyCrucible(i_positionNumber, i_runID)

    crucibleAndSherd105Weight = crucibleWeight + f_sherdWeightInitialAverage

    logger.debug("update tblCrucible with weights")
    try:
        # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        t = (crucibleAndSherd105Weight, f_preWeightStdDev, i_runID, i_positionNumber)
        logger.debug(
            'update tblCrucible SET f_105WeightAverage=%f, f_105WeightStdDev=%f where i_runID=%d and i_positionNumber=%d' % t)
        c.execute(
            'update tblCrucible SET f_105WeightAverage=?, f_105WeightStdDev=? where i_runID=? and i_positionNumber=?',
            t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateSamplePreFire: %s", msg)
        return False

    return True


def updateSamplePostFireWeight(i_runID, i_positionNumber, f_postFireWeightAverage, f_postFireWeightStdDev ):
    logger.debug("update tblSample with postFire environmental info")
    try:
        # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        t = (f_postFireWeightAverage, f_postFireWeightStdDev, i_runID, i_positionNumber)
        c.execute(
            'update tblSample SET f_postFireWeightAverage=?, f_postFireWeightStdDev=? where i_runID=? and i_positionNumber=?',
            t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateSamplePostFireWeight: %s", msg)
        return False

    crucibleWeight, crucibleStdDev, weightCount = getEmptyCrucible(i_positionNumber, i_runID)

    crucibleAndSherd550Weight = crucibleWeight + f_postFireWeightAverage

    logger.debug("update tblCrucible with postfire weights")
    try:
        # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        t = (crucibleAndSherd550Weight, f_postFireWeightStdDev, i_runID, i_positionNumber)
        logger.debug(
            'update tblCrucible SET f_550WeightAverage=%f, f_550WeightStdDev=%f where i_runID=%d and i_positionNumber=%d' % t)
        c.execute(
            'update tblCrucible SET f_550WeightAverage=?, f_550WeightStdDev=? where i_runID=? and i_positionNumber=?',
            t)
        conn.commit()
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred updateSamplePostFireWeight: %s", msg)
        return False
    return True


def updateSamplePostFire(i_runID, i_positionNumber,
                         f_postTemperatureAverage, f_postTemperatureStdDev,
                         f_postHumidityAverage, f_postHumidityStdDev,
                         count, repeat, elapsedTimeMin ):
    # runID,sampleID,position,tempMean,tempStdev,humidityMean,humidityStdev,count,repeat,timeElapsed
    logger.debug("update sample with postFire environmental info")
    try:
        # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        t = (f_postTemperatureAverage, f_postTemperatureStdDev, f_postHumidityAverage,
             f_postHumidityStdDev, count, elapsedTimeMin, repeat, i_runID, i_positionNumber)

        c.execute('update tblSample SET \
        f_postTempAverage=?, f_postTempStdDev=?, \
        f_postHumidityAverage=?, f_postHumidityStdDev=?, i_count=?, f_elapsedTimeMin=?, \
        i_repetitions=? where i_runID=? and i_positionNumber=?', t)
        conn.commit()
        return True
    except sqlite.OperationalError, msg:
        logger.error("A SQL error occurred in updateSamplePostFire: %s", msg)
        return False