#!/usr/bin/python
# Filename: DataReadWrite.py

import logging
import serial
import sqlite3 as sqlite
import time
from ctypes import *
import math
import os
import io
import serial
import sys
sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
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

# CONSTANTS
TEMPHUMIDITY="V3"

def dict_factory(cursor, row):
   d = {}
   for idx,col in enumerate(cursor.description):
      d[col[0]] = row[idx]
   return d

logger=logging.getLogger("startRHX.DataReadWrite")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
today_date=datetime.today()
datestring=today_date.strftime("%Y-%m-%d-%H-%M")
debugfilename = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Autosampler/logs/rhx-" + datestring + "_debug.log"
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


non_decimal = re.compile(r'[^\d.]+')
float_pat = re.compile('[0-9]+(\.[0-9]+)?')

## HACK -- Ive commented out the tempHumidity sensor for now as it is not reading ##
# open the serial port for the temperature and humidity controller
### tempHumidity = serial.Serial(port='COM14', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2, xonxoff=1, rtscts=0)
#time.sleep(1)

# open the serial port for the balance
balance = serial.Serial(port=ComPorts.UltraBalance, baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10, xonxoff=1, rtscts=0)

SQLFILENAME="c:/Users/Archy/Dropbox/Rehydroxylation/RHX-New.sql"


XYDBFILENAME = "c:/Users/Archy/Dropbox/Rehydroxylation/RHX.sqlite"
#  open the sqlite database and create a connection
# create a cursor to the database

xyconn = sqlite.connect(XYDBFILENAME,detect_types=sqlite.PARSE_DECLTYPES)
path='c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Autosampler/libsqlitefunctions.so'
# open the sqlite database and create a connection
# create a cursor to the database
xyconn.enable_load_extension(True)
xyconn.load_extension(path)
xyconn.row_factory = dict_factory

def initializeDatabase(dirname,filename):
   global conn
   file_list=[]
   extension=".sqlite"
   file_list.append(dirname)
   file_list.append(filename)
   file_list.append(extension)
   dbfilename=''.join(file_list)

   if os.path.exists(dbfilename) is True:
      print "Database ",dbfilename, " already exists."
      value=raw_input('Do you want to write over this file and delete its contents? (y/n)')
      if value is 'y':
         os.remove(dbfilename)
      else:
         exit()

   # open the sqlite database and create a connection
   conn = sqlite.connect(dbfilename,detect_types=sqlite.PARSE_DECLTYPES)
   # create a cursor to the database

   path='c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Autosampler/libsqlitefunctions.so'
   # open the sqlite database and create a connection
   # create a cursor to the database
   conn.enable_load_extension(True)
   conn.load_extension(path)
   conn.row_factory = dict_factory
   try:
      c=conn.cursor()
      ##dbfilename="c:/Users/Archy/Dropbox/Rehydroxylation/RHX.sql"
      for line in open(SQLFILENAME):
         c.execute(line)
         conn.commit()
      return True;
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False; 

def closeDatabase():
# Ensure variable is defined
   try:
      conn
   except NameError:
      conn = None
   if conn is not None:
      try:
         conn.close()
         return True;
      except sqlite.OperationalError, msg:
         logger.error( "A SQL error occurred: %s", msg)
         return False;
   return True


def openDatabase(dirname,filename):
   global conn
   file_list=[]
   extension=".sqlite"
   file_list.append(dirname)
   file_list.append(filename)
   file_list.append(extension)
   dbfilename=''.join(file_list)
   try:
      conn = sqlite.connect(dbfilename,detect_types=sqlite.PARSE_DECLTYPES)
      path='c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Autosampler/libsqlitefunctions.so'
      # open the sqlite database and create a connection
      # create a cursor to the database
      conn.enable_load_extension(True)
      conn.load_extension(path)
      conn.row_factory = dict_factory
      return True;
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;

## if the sqlite file is already in existence and you have the file handle -- just need to do this...
def reopenDatabase(filename):
   print "filename:", filename
   global conn
   try:
       conn = sqlite.connect(filename,detect_types=sqlite.PARSE_DECLTYPES)
       path='c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Autosampler/libsqlitefunctions.so'
       # open the sqlite database and create a connection
       # create a cursor to the database
       conn.enable_load_extension(True)
       conn.load_extension(path)
       conn.row_factory = dict_factory
       return True;
   except sqlite.OperationalError, msg:
       logger.error( "A SQL error occurred: %s", msg)
       return False;

# dirname="c:/Users/Archy/Dropbox/Rehydroxylation/"
# databaseSQL= "c:/Users/Archy/Dropbox/Rehydroxylation/RHX.sql"
# dbfilename = "c:/Users/Archy/Dropbox/Rehydroxylation/RHX.sqlite"
# path='./libsqlitefunctions.so'
# 
# # open the sqlite database and create a connection
# # create a cursor to the database
# conn = sqlite.connect(dbfilename,detect_types=sqlite.PARSE_DECLTYPES)
# conn.enable_load_extension(True)
# conn.load_extension(path)
# conn.row_factory = dict_factory
def getLastRunID():
   try:
      c=conn.cursor()
      logger.debug("select max(i_runID) as max from tblRun")
      c.execute("select max(i_runID) as max from tblRun")
      max = c.fetchone()["max"]
      if (max is None):
         max = 0
      return False
   except sqlite.OperationalError, msg:
      logger.error("A SQL error occurred: %s",msg)
   return False

def updatePosition(xpos,ypos):
   c=xyconn.cursor()
   t=(xpos,ypos)
   logger.debug('update tblXY SET i_xposition=%d, i_yposition=%d where rowid=1' % (t))
   c.execute('update tblXY SET i_xposition=?, i_yposition=? where rowid=1',t)
   # Save (commit) the changes
   xyconn.commit()
   return True;

def zeroBalance():
   balance.write(str.encode("ZI\r\n"))
   bline=balance.readline()
   if (bline.startswith("ZI I")	):
      logger.debug("Balance says: %s", bline)
      return False;
   else:
      return True;

def setPosition(x,y):
   c=xyconn.cursor()
   t=(x,y)
   logger.debug('update tblXY SET i_xposition=%d, i_yposition=%d where rowid=1' % (t))
   c.execute('update tblXY SET i_xposition=?, i_yposition=? where rowid=1',t)
   # Save (commit) the changes
   xyconn.commit()
   return True;

def getLastPosition():
   c=xyconn.cursor()
   logger.debug('Select i_xposition, i_yposition FROM tblXY where rowid=1')
   c.execute('Select i_xposition, i_yposition FROM tblXY where rowid=1')
   for row in c.fetchall():
      x=row["i_xposition"]
      y=row["i_yposition"]
   return (x,y)

def openBalanceDoor():
   logger.debug("openBalanceDoor")
   logger.debug("Sending WS 1\r\n to balance")
   balance.write(str.encode("WS 1\r\n"))
   logger.debug("Balance replies: %s",balance.readline() )
   sleep(1)
   return True;

def closeBalanceDoor():
   logging.debug("closeBalanceDoor")
   logging.debug("Sending WS 0\r\n to balance")
   balance.write(str.encode("WS 0\r\n"))
   logging.debug("Balance replies: %s", balance.readline())
   sleep(1)
   return True;

def isBalanceDoorOpen():
   logger.debug("isBalanceDoorOpen")
   vals=[]
   balance.write(str.encode("M37\r\n"))
   bline = balance.readline()
   bline.rstrip("\r\n")+" "
   logger.debug( "Balance says:  %s", bline)
   if (bline.rfind("S")>0):
      logger.debug( "sleeping and trying again...")
      sleep(3)
      bline = balance.readline()      
      bline.rstrip("\r\n")+" "
      logger.debug( "Balance now says:  %s", bline)
   try:
      vals=bline.split(" ",3)
   except:
      return "UNKNOWN" 
   val=int(vals[2])
   logger.debug( "balance value: %s", val)
   #status=val.rstrip()
   # 0 is the CLOSED status
   # 2 or 1 is the OPEN status
   if val<80:
      return "CLOSED"
   else:
      return "OPEN"

def getMaxPreFireCount(runID,position):
   max=0
   try:
      c=conn.cursor()
      t=(runID,position)
      logger.debug("select max(i_count) as max from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=1" %(t))
      c.execute("select max(i_count) as max from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=1",t)   
      max = c.fetchone()["max"]
      if (max is None):
         max = 0
      return max
   except sqlite.OperationalError, msg:
      logger.error("A SQL error occurred: %s",msg)
      return 0

def getMaxPostFireCount(runID,position):
   max=0
   try:
      c=conn.cursor()
      t=(runID,position)
      logger.debug("select max(i_count) as max from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=2" %(t))
      c.execute("select max(i_count) as max from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=2",t)
      max = c.fetchone()["max"]
      if (max is None):
         max = 0
      return max
   except sqlite.OperationalError, msg:
      logger.error("A SQL error occurred: %s",msg)
      return 0

def getPrefireAttributes(runID):
   initials=""
   name=""
   location=""
   numberOfSamples=0
   startPosition=1
   durationOfMeasurements=0
   samplingInterval=5
   repetitions=1
   locationTemperature=0.0
   locationHumidity=0.0

   try:
      c=conn.cursor()

      c.execute("select i_repetitions,v_locationCode,i_numberOfSamples,v_operatorName,i_equilibrationDuration,i_preMeasurementTimeInterval, \
         v_description,f_temperature,f_humidity,f_locationTemperature,f_locationHumidity, \
         v_status,i_loggingInterval,i_durationOfPreMeasurements,i_numberOfPreMeasurements from tblRun where i_runID = %d", runID)

      row = c.fetchone()
      location=row["v_locationCode"]
      initials=row["v_operatorName"]
      name=row["v_description"]
      numberOfSamples=row["i_numberOfSamples"]
      durationOfMeasurements=row["i_durationOfPreMeasurements"]
      samplingInterval=row["i_loggingInterval"]
      repetitions=row["i_repetitions"]
      locationTemperature=row["f_locationTemperature"]
      locationHumidity=row["f_locationHumidity"]

      return initials,name,location,numberOfSamples,startPosition,durationOfMeasurements,samplingInterval,repetitions,locationTemperature,locationHumidity

   except sqlite.OperationalError, msg:
      logger.error("A SQL error occurred: %s",msg)
      return 0


def getPostfireAttributes(runID):
   initials=""
   name=""
   location=""
   numberOfSamples=0
   startPosition=1
   durationOfMeasurements=0
   samplingInterval=5
   repetitions=1
   locationTemperature=0.0
   locationHumidity=0.0

   try:
      c=conn.cursor()

      c.execute("select i_numberOfSamples,i_durationOfPostMeasurements,i_numberOfPostMeasurements,i_loggingInterval,i_repetitions,f_locationTemperature, \
         f_locationHumidity, i_durationOfFiring,d_datetimeOfFiring, i_rateOfHeating, i_tempOfFiring from tblRun where i_runID = %d", runID)

      row = c.fetchone()
      numberOfSamples=row["i_numberOfSamples"]
      duration=row["i_durationOfPostMeasurements"]
      interval=row["i_loggingInterval"]
      repetitions=row["i_repetitions"]
      locationTemperature=row["f_locationTemperature"]
      locationHumidity=row["f_locationHumidity"]
      durationOfFiring=row["i_durationOfFiring"]
      dateOfFiring=row["d_datetimeOfFiring"]
      timeOfFiring=row["d_datetimeOfFiring"]
      rateOfHeating=row["i_rateOfHeating"]
      tempOfFiring=row["i_tempOfFiring"]

      return numberOfSamples,startPosition,dateOfFiring,timeOfFiring,rateOfHeating,durationOfFiring,tempOfFiring,duration,interval,repetitions,locationTemperature,locationHumidity

   except sqlite.OperationalError, msg:
      logger.error("A SQL error occurred: %s",msg)
      return 0



def insertPreFireMeasurement(runID,sampleID,position,weightMeasurement,status,
                             temperature,humidity,crucibleWeight,standard_weight,today,total_count,repetition,repetition_count,count):

   logger.debug("insert prefire measurement.")
   # Find elapsed time
   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")
   preOrPost=1
   status=1
   #sampleMeasurement = weightMeasurement - crucibleWeight
   try:
      c=conn.cursor()
      t=(runID,sampleID,position,weightMeasurement,status,now,temperature,humidity,standard_weight,total_count,repetition,repetition_count,count,preOrPost)
      logger.debug('insert into tblMeasurement (i_runID,i_sampleID,i_positionNumber,f_weight,v_status,d_datetime,f_temperature,f_humidity,f_standardWeight, i_count,i_repetition,i_repetitionCount,i_count,i_preOrPost)  VALUES (%d,%d,%d,%f,%s,%s,%f,%f,%f,%d,%d,%d,%d,%d)' %(t))
      c.execute(   'insert into tblMeasurement (i_runID,i_sampleID,i_positionNumber,f_weight,v_status,d_datetime,f_temperature,f_humidity,f_standardWeight, i_count,i_repetition,i_repetitionCount,i_count,i_preOrPost)  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',t)
      # Save (commit) the changes
      conn.commit()
      # Now get the id for the run so we can update with other info as we ask...
      measurementID = c.lastrowid
      return measurementID
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;


def insertPostFireMeasurement(runID,sampleID,positionNumber,weightMeasurement,status,
                              temperature,humidity,endOfFiring,
                              crucibleWeight,standard_weight,today,total_count,repetition,repetition_count,count):
   logger.debug("Insert post fire measurement.")
   # Find elapsed time
   now = datetime.today()
   today = now.strftime("%m-%d-%y %H:%M:%S")

   elapsedTime = now - endOfFiring

   elapsedTimeSec=elapsedTime.total_seconds()
   logger.debug("Time elapsed (seconds): %d", elapsedTimeSec)
   elapsedTimeMin=elapsedTimeSec/60
   logger.debug("Time elapsed (minutes): %f", elapsedTimeMin)
   elapsedTimeQuarterPower =float( pow(abs(elapsedTimeMin),0.25))
   logger.debug("Time elapsed (min) ^ 0.25: %f", elapsedTimeQuarterPower)
   #sampleMeasurement = weightMeasurement - crucibleWeight
   preOrPost=2
   status=2
   try:
      c=conn.cursor() 
      ### %d,%d,%d,%f,%s,%s,%d,%f,%f,%f,%f,%f,%f,%d,%d,%d,%d
      t=(runID,sampleID,positionNumber,weightMeasurement,status,
         now,elapsedTimeMin,elapsedTimeQuarterPower,temperature,
         humidity,standard_weight,total_count,repetition,repetition_count,count,preOrPost)

      ### logger.debug('insert into tblMeasurement (i_runID,i_sampleID,i_positionNumber,f_weight,v_status,d_datetime,f_elapsedTimeMin,f_elapsedTimeQuarterPower,f_temperature,f_humidity,f_standardWeight,i_count,i_repetition,i_repetitionCount,i_count,i_preOrPost)  VALUES ( %d,%d,%d,%f,%s,%s,%d,%f,%f,%f,%f,%f,%f,%d,%d,%d,%d,%d)' %(t))
      c.execute('insert into tblMeasurement (i_runID,i_sampleID,i_positionNumber,f_weight,v_status, \
                d_datetime,f_elapsedTimeMin,f_elapsedTimeQuarterPower,f_temperature, \
                f_humidity,f_standardWeight,i_count,i_repetition, \
                i_repetitionCount,i_count,i_preOrPost) \
                VALUES (?,?,?,?,?, \
                ?,?,?,?, \
                ?,?,?,?, \
                ?,?,?)',t)

      # Save (commit) the changes
      conn.commit()
      # Now get the id for the run so we can update with other info as we ask...
      measurementID = c.lastrowid
      return measurementID
   except sqlite.OperationalError, msg:
      logger.error(  "A SQL error occurred: %s", msg)
      return False;

def getRunInfo(runID):
   locationCode=""
   numberOfSamples=0
   description=""
   temperature=0.0
   humidity=0.0
   status=True
   row=[]
   try:   
      t=int(runID,)
      c = conn.cursor()
      logger.debug("select v_locationCode, i_numberOfSamples, v_description, f_locationTemperature, f_locationHumidity, d_endOfFiring,i_durationOfFiring from tblRun where i_runID = %d" % (runID))
      c.execute('select v_locationCode, i_numberOfSamples, v_description, f_locationTemperature, f_locationHumidity, d_endOfFiring,i_durationOfFiring from tblRun where i_runID=%s'% runID)
      row=c.fetchone()
      return (status,row)
   except sqlite.OperationalError, msg:
      logger.error(  "A SQL error occurred: %s" % msg)
      return (False,row);

def readStandardBalance():
   out=0
   state=0
   # open the serial port for the standard balance
   standard_balance = serial.Serial(port=ComPorts.StandardBalance, baudrate=9600, bytesize=8, parity='N', stopbits=1,
      timeout=1, xonxoff=0)
   count=0
   sleep(2)

   standard_balance.write('P\r\n')
   #standard_balance.write('\n')
   #standard_balance.write('\r')
   out = standard_balance.readline()
   standard_balance.close()
   if out.find('g') ==1:

      #print "out->", out
      '''' ## comment this out for now
      ##
      while (out.find('g')  < 1):
         count+=1
         standard_balance = serial.Serial(port=ComPorts.StandardBalance, baudrate=9600, bytesize=8, parity='N', stopbits=1,
            timeout=1, xonxoff=0)
         standard_balance.write('P\r\n')
         #standard_balance.write('\n')
         #standard_balance.write('\r')
         out = standard_balance.readline()
         standard_balance.close()
         time.sleep(1)
         if count>1000:
            out="0.0 g"
      '''''

      out=out.lstrip()
      out=out.replace('g','')
      out=out.rstrip()

   else: ## either get a value or return 0.0.
      out=0.0
   value=float(out)
   return value

def readWeightFromBalance():
   logger.debug("Reading weight from balance")
   ## balance read
   status=""
   balance.write("S\n\r")
   bline = balance.readline()
   code=[]
   if (len(bline)>4):
      code.append(bline[0])
      code.append(bline[1])
      code.append(bline[2])
      string=''.join(code)
      logger.debug("String value: %s" % string)
      if (string=="S S"):
         status="Stable"
      elif (string=="S D"):
         status="Unstable"
      elif(string=="S I"):
         status="Busy"
   else:
      status="Error"

   logger.debug( "Balance Ouput:%s--%s" %( bline,status))
   weight=float(0.0)
   result=[]
   if len(bline) == 18:	
      bbline = bline.lstrip("S S   ")
      weights = bbline.replace(" g", "")
      weights=weights.rstrip(" ")
      weights = weights[:-1]
      weights=weights.rstrip("\n")
      weights=weights.rstrip("\r")
      weight = non_decimal.sub('', weights)
      #weight=re.search(float_pat,weights)
      if weight=="":
         weight=0.0
      #if weight.count('.')>1:
      #   weight=0.0
      result.append(weight)
      result.append(status)
      logger.debug( "WEIGHT: %s " % (weight))
      return result
   else:
      #try getting an instant reading
      (weight,status)=readInstantWeightFromBalance()
      if (result=="error"):
         return (0.0,"error");
      else:
         return (weight,"Unstable");

def readInstantWeightFromBalance():
   ## balance read
   logger.debug("Reading instant weight from balance")
   non_decimal = re.compile(r'[^\d.]+')
   balance.write("SI\n\r")
   bline = balance.readline()
   logger.debug("instant read: %s" % (bline))
   code=[]
   code.append(bline[0])
   code.append(bline[1])
   code.append(bline[2])
   string=''.join(code)
   logger.debug("String value: %s" % (string))
   if (string=="S S"):
      status="Stable"
   elif (string=="S D"):
      status="Unstable"
   elif(string=="S I"):
      status="Busy"
   else:
      status="Error"   
   logger.debug( "Balance Ouput:%s--%s"%  (bline,status))

   weight=float(0.0)
   result=[]
   if len(bline) == 18:	
      bbline = bline.lstrip("S S   ")
      bbline = bline.lstrip("S D   ")
      weights = bbline.replace(" g", "")
      weights=weights.rstrip()
      #weights = weights[:-1]
      weight = non_decimal.sub('', weights)

      if weight=="":
         weight=0.0
      #if weight.count('.')>1:
      #   weight=0.0
      logger.debug("Weight: %s",weight)
      result.append(weight)
      result.append(status)
      return result
   else:
      return (0.0,"error");

def readTempHumidity(tempCorrection,rhCorrection):
   results=[]    
   if TEMPHUMIDITY is "V2":
      results=readV2TempHumidity(tempCorrection,rhCorrection)
   elif TEMPHUMIDITY is "V3":
      results=readV3TempHumidity(tempCorrection,rhCorrection)
   else:
      results=readV4TempHumidity(tempCorrection,rhCorrection)

   return results

def readV2TempHumidity(tempCorrection,rhCorrection):
   ## temp Humidity Read
   float_pat = re.compile('[0-9]+(\.[0-9]+)?')
   logger.debug("Reading temp and humidity")
   tline=" "
   readOne=""
   ## Example string:  #57.08,079.51,021.4,070.60,100729,1022,0,007143$
   line = tempHumidity.readline()
   #print "line!: ", line
   random.seed()
   non_decimal = re.compile(r'[^\d.]+')
   time.sleep(1)
   tempHumidity.write("\n")
   arrayOfValues=[]
   listOfValues=[]
   humidity=[]
   hum=[]
   tempF=float(0.0)
   tempC=float(0.0)
   humnum=float(0.0)
   light=float(0.0)
   pressure=float(0.0)
   line=tempHumidity.readline()
   #print "read: ",line
   while(len(line)<> 50):
      line=tempHumidity.readline()
      #print "read: ",line
   line.lstrip('#')
   #print "lstrip:", line
   line.rstrip()
   line.rstrip('$')
   #print "rstrip:", line
   listOfValues=line.split(",",8)
   hum=listOfValues[0]
   humidity=[]
   humidity.append(hum[1])
   humidity.append(hum[2])
   humidity.append(hum[3])
   humidity.append(hum[4])
   humidity.append(hum[5])
   humnum=float(''.join(humidity))
   #print "humidity: ",humnum

   humnum += float(rhCorrection)
   tempC=float(listOfValues[2])+float(tempCorrection)

   #board is set to metric units
   #tempC=(float(tempF)-32.0)*5.0/9.0
   dewpoint=float(listOfValues[3])
   pressure=float(listOfValues[4])
   light=float(listOfValues[5])
   #print ("Values : Temp %s, humidity %s, pressure %s, light %s" % (tempC,humidity,pressure,light))

   #logger.debug("Values : Temp %s, humidity %s, pressure %s, light %s" % (tempC,humidity,pressure,light))
   arrayOfValues.append(tempC)
   arrayOfValues.append(humnum)
   arrayOfValues.append(dewpoint)
   arrayOfValues.append(pressure)
   arrayOfValues.append(light)

   return arrayOfValues



def readV2ATempHumidity(tempCorrection,rhCorrection):
   ## temp Humidity Read
   float_pat = re.compile('[0-9]+(\.[0-9]+)?')
   logger.debug("Reading temp and humidity")
   tline=" "
   readOne=""
   ## Example string:  #57.08,079.51,021.4,070.60,100729,1022,0,007143$
   line = tempHumidity.readline()
   #print "line!: ", line
   random.seed()
   non_decimal = re.compile(r'[^\d.]+')
   time.sleep(1)
   tempHumidity.write("\n")
   arrayOfValues=[]
   listOfValues=[]
   humidity=[]
   hum=[]
   tempF=float(0.0)
   tempC=float(0.0)
   humnum=float(0.0)
   light=float(0.0)
   pressure=float(0.0)
   while(readOne <> "#"):
      readOne =tempHumidity.read(1)
      tline = "#"+tempHumidity.read(47)
      #print("Read this from temphumidity card: %s " % (tline))
      while( tline.find("#") <> 0 and tline.find("$") < 47 ):
         logger.debug( "Incorrect string. try again.")
         time.sleep(0.5*random.random())
         logger.debug( "TempHumidity Reading: %s", tline)
         tline="#".tempHumidity.read(48)
   logger.debug("TempHumidity reads:  %s",tline)
   listOfValues=tline.split(",",8)
   hum=listOfValues[0]
   humidity=[]
   humidity.append(hum[1])
   humidity.append(hum[2])
   humidity.append(hum[3])
   humidity.append(hum[4])
   humidity.append(hum[5])
   humnum=float(''.join(humidity))
   #print "humidity: ",humnum

   humnum += float(rhCorrection)
   tempC=float(listOfValues[2])+float(tempCorrection)

   #board is set to metric units
   #tempC=(float(tempF)-32.0)*5.0/9.0
   dewpoint=float(listOfValues[3])
   pressure=float(listOfValues[4])
   light=float(listOfValues[5])

   #logger.debug("Values : Temp %s, humidity %s, pressure %s, light %s" % (tempC,humidity,pressure,light))
   arrayOfValues.append(tempC)
   arrayOfValues.append(humnum)
   arrayOfValues.append(dewpoint)
   arrayOfValues.append(pressure)
   arrayOfValues.append(light)

   return arrayOfValues

def readV3TempHumidity(tempCorrection,rhCorrection):
   ## temp Humidity Read
   float_pat = re.compile('[0-9]+(\.[0-9]+)?')
   logger.debug("Reading temp and humidity")
   tline=" "
   readOne=""
   ## Example string:  $,57.8,79,51.4,1009.48,0.0,0.0,-1,0.00,0.00,*
   ##                  $,57.8,79,51.5,1009.28,0.0,0.0,-1,0.00,0.00,*
   line=tempHumidity.readline()
   random.seed()
   non_decimal = re.compile(r'[^\d.]+')
   time.sleep(1)
   tempHumidity.write("\n")
   arrayOfValues=[]
   listOfValues=[]
   tempF=float(0.0)
   tempC=float(0.0)
   humidity=float(0.0)
   light=float(0.0)
   pressure=float(0.0)
   while(readOne <> "$"):
      readOne =tempHumidity.read(1)
      tline = "$"+tempHumidity.read(46)
      while( tline.find("$") <> 0 and tline.find("*") < 44 ):
         logger.warning( "Incorrect string. try again.")
         time.sleep(0.5*random.random())
         logger.warning( "TempHumidity Reading: %s", tline)
         tline="$".tempHumidity.read(46)
   logger.debug("TempHumidity reads:  %s",tline)
   listOfValues=tline.split(",",11)
   humidity=float(listOfValues[2])+float(rhCorrection)
   tempC=float(listOfValues[1])+float(tempCorrection)

   #board is set to metric units
   #tempC=(float(tempF)-32.0)*5.0/9.0
   dewpoint=float(listOfValues[3])
   pressure=float(listOfValues[4])
   light=float(listOfValues[5])

   #logger.debug("Values : Temp %s, humidity %s, pressure %s, light %s" % (tempC,humidity,pressure,light))
   arrayOfValues.append(tempC)
   arrayOfValues.append(humidity)
   arrayOfValues.append(dewpoint)
   arrayOfValues.append(pressure)
   arrayOfValues.append(light)

   return arrayOfValues


## sequence of steps for weighing sample for a period of time. 
def weighAndRecordSamplePreFire(runID,sampleID,positionNumber,duration,loggingInterval,tempCorrection,rhCorrection):
   logger.debug("Weight and Record Sample Pre Fire.")
   stopCode=0
   lengthOfTimeCounter=int((duration*60)/loggingInterval)
   logger.debug( "counter length: %d ", lengthOfTimeCounter)
   crucibleWeight=getCrucibleWeight(runID,positionNumber)
   while stopCode<>lengthOfTimeCounter:
      weight=float(readWeightFromBalance())
      logger.debug( "weight: %s",weight)
      standard_weight=0.0
      if weight==0.0:
         pass
      else:
         standard_weight=double(readStandardBalance())
         temp=xyzRobot.getTemperature()
         logger.debug( "temp: %s humidity: %s " % (temp,humidity))
         measurementID=insertPreFireMeasurement(runID,sampleID,weight,
                                                temperature,humidity,crucibleWeight,standard_weight)
         logger.debug( "measurement id:  %d",measurementID)
         time.sleep(loggingInterval)
      stopCode += 1
   return True;

## sequence of steps for weighing sample for a period of time. 
def weighAndRecordSamplePostFire(runID,sampleID,positionNumber,duration,loggingInterval,tempCorrection,rhCorrection):
   logger.debug("Weight and record sample pre fire")
   stopCode=0
   lengthOfTimeCounter=int((duration*60)/loggingInterval)
   logger.debug( "counter length: %d", lengthOfTimeCounter)
   crucible_weight=getCrucibleWeight(runID,positionNumber)
   endOfFiring=getEndOfFiring(runID)
   vals=[]
   now = datetime.today()
   while stopCode<>lengthOfTimeCounter:
      weight=float(readWeightFromBalance())
      logger.debug( "weight: %f",weight)
      standard_weight=0.0
      if weight==0.0:
         standard_weight=float(readStandardBalance())
         temp=xyzRobot.getTemperature()
         logger.debug( "temp: %s humidity: %s " % (temp,humidity))
         measurementID=insertPostFireMeasurement(runID,sampleID,positionNumber,weight,
                                                 temperature,humidity,
                                                 endOfFiring,now,standard_weight)
         logger.debug( "measurement id:  %d",measurementID)
         time.sleep(loggingInterval)
      stopCode=stopCode+1
   return True

def insertInitialCrucible(runID,position,today):
   logger.debug("insert initial crucible into tblCrucible")
   try:
      c=conn.cursor()
      t=(runID,today,position)
      logger.debug('insert INTO tblCrucible (i_runID, d_datetime, i_positionNumber) VALUES (%d,%s,%i)'% (t))
      c.execute('insert INTO tblCrucible (i_runID, d_datetime, i_positionNumber) VALUES (?,?,?)',t)
      conn.commit()
      crucibleID=c.lastrowid
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;
   return crucibleID

def insertCrucibleMeasurement(runID,positionNumber,weight,status,temperature,humidity, count,now):
   logger.debug("insert crucible measurement into tblMeasurement")
   preOrPost=0
   measurementID=0
   now = datetime.today()
   try:
      c=conn.cursor()
      t=(runID,positionNumber,weight,status,now,temperature,humidity,count,preOrPost)
      print runID,positionNumber,weight,status,now,temperature,humidity,count,preOrPost
      logger.debug('insert into tblMeasurement (i_runID,i_positionNumber,f_weight,v_status,d_datetime,' \
                   'f_temperature,f_humidity,i_count,i_preOrPost)  ' \
                   'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)' %(t))
      c.execute(   'insert into tblMeasurement (i_runID,i_positionNumber,f_weight,v_status,d_datetime,' \
                   'f_temperature,f_humidity,i_count,i_preOrPost)  ' \
                   'VALUES (?,?,?,?,?,?,?,?,?)',t)
      conn.commit()
      measurementID=c.lastrowid
   except sqlite.OperationalError, msg:
      logger.error("A SQL error occurred: %s",msg)
      return False;
   return measurementID

def updateCrucible(position,averageWeight,stdevWeight,averageTemp,stdevTemp,averageHumidity,stdevHumidity,today,runID,count):
   logger.debug("update crucible record with weight, etc.")
   now = datetime.today()
   try:
      c=conn.cursor()
      t=(float(averageWeight),float(stdevWeight),float(averageTemp),float(stdevTemp),float(averageHumidity),float(stdevHumidity),now,count,position,runID)
      logger.debug ('update tblCrucible SET f_averageWeight=%f, f_stdevWeight=%f, f_averageTemp=%f, f_stdevTemp=%f,f_averageHumidity=%f, f_stdevHumidity=%f, d_datetime=%s, i_count=%d WHERE i_positionNumber=%d AND i_runID=%d' % t)
      c.execute('update tblCrucible SET f_averageWeight=?, f_stdevWeight=?, f_averageTemp=?, f_stdevTemp=?, f_averageHumidity=?, f_stdevHumidity=?, d_datetime=?, i_count=? WHERE i_positionNumber=? AND i_runID=?',t)
      conn.commit()
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;
   return True;

def insertRun(setInitials,today,numberOfSamples):
   logger.debug("insert run")
   now = datetime.today()
   try:
      t=(setInitials,now,numberOfSamples)
      # create a cursor to the database
      c = conn.cursor()
      # Insert initial data for the run
      c.execute('insert into tblRun (v_operatorName,d_datetime,i_numberOfSamples) VALUES (?,?,?)',t)    
      logger.debug('insert into tblRun (v_operatorName,d_datetime,i_numberOfSamples) VALUES (%s,%s,%d)' % (t))  
      # Save (commit) the changes
      conn.commit()
      # Now get the id for the run so we can update with other info as we ask...
      runID = c.lastrowid
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False
   return runID

def updateTempRHCorrection(tempCorrection,rhCorrection,runID):
   logger.debug("update correction for temp and humidity")
   try:
      t=(tempCorrection,rhCorrection,runID)
      c=conn.cursor()
      c.execute('update tblRun set f_tempCorrection=?, f_rhCorrection=? where i_runID=?', t)
      conn.commit()
      return True
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False

def updateRunPreFire( runID,setInitials,setName,today,
                      setLocation,preOrPost,intervalsec,setTemperature,
                      setHumidity,status,duration,numberOfSamples,
                      repetitions,startPosition):

   now = datetime.today()
   logger.debug("update run pre fire")
   try:
      t=(setInitials,setName,now,setLocation,
         intervalsec,setTemperature,setHumidity,status,
         duration,numberOfSamples,
         repetitions,duration,runID)
      # create a cursor to the database
      c = conn.cursor()
      # Insert initial data for the run
      logger.debug('update tblRun SET v_operatorName=%s,v_description=%s,d_datetime=%s,v_locationCode=%s,i_loggingInterval=%d,f_locationTemperature=%f,f_LocationHumidity=%f,v_status=%s,i_preMeasurementTimeInterval=%d,i_numberOfSamples=%d,i_numberOfPreMeasurements=%d,i_durationOfPreMeasurements=%d WHERE i_runID=%d'% (t) )

      c.execute('update tblRun SET v_operatorName=?,v_description=?,d_datetime=?,v_locationCode=?,i_loggingInterval=?,f_locationTemperature=?,f_locationHumidity=?,v_status=?,i_preMeasurementTimeInterval=?,i_numberOfSamples=?,i_numberOfPreMeasurements=?,i_durationOfPreMeasurements=? WHERE i_runID=?',t)
      # Save (commit) the changes
      conn.commit()
      return runID
   except sqlite.OperationalError, msg:
      logger.debug( "A SQL error occurred: %s", msg)
      return False;

def insertNewSample(i_runID,i_crucibleID,v_description,d_datetime,
                    v_locationCode,i_preOrPost,i_loggingInterval,f_locationTemperature,
                    f_locationHumidity,v_status,i_preMeasurementTimeInterval,i_repetitions,f_crucibleWeightAverage,f_crucibleWeightStdDev):
   logger.debug("insert new sample")
   try:
      # create a cursor to the database
      c = conn.cursor()
      # Insert initial data for the run
      t=(i_runID,i_crucibleID,v_description,d_datetime,
         v_locationCode,i_preOrPost,i_loggingInterval,f_locationTemperature,
         f_locationHumidity,v_status,i_preMeasurementTimeInterval,i_repetitions,f_crucibleWeightAverage,f_crucibleWeightStdDev)
      logger.debug('insert into tblSample (i_runID,i_positionNumber,v_description,d_datetime,v_locationCode,i_preOrPost,i_loggingInterval,f_locationTemperature,f_locationHumidity,v_status,i_preMeasurementTimeInterval,i_repetitions,f_crucibleWeightAverage,f_crucibleWeightStdDev) VALUES (%d,%d,%s,%s,%s,%d,%d,%f,%f,%s,%d,%d,%f,%f)'% (t))    #

      c.execute('insert into tblSample (i_runID,i_positionNumber,v_description,d_datetime,v_locationCode,i_preOrPost,i_loggingInterval,f_locationTemperature,f_locationHumidity,v_status,i_preMeasurementTimeInterval,i_repetitions,f_crucibleWeightAverage,f_crucibleWeightStdDev) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',t)    #
      conn.commit()
      sampleID = c.lastrowid
      return (sampleID)
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;

def getCrucibleWeight(runID,positionNumber):
   try:
      c = conn.cursor()
      t=(runID,positionNumber)
      #print "RUNID:  ",runID, "PositionNumber:",positionNumber
      averageWeight=float(0.0)
      c.execute('select f_averageWeight from tblCrucible where i_runID=? and i_positionNumber=?', t)        
      logger.debug('select f_averageWeight from tblCrucible where i_runID=%d and i_positionNumber=%d'% (t))       
      data=c.fetchone()
      if (data is None):
         return False;
      returnValue=data["f_averageWeight"]
      return double(returnValue)
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;

def getCrucibleWeightStats(runID,positionNumber):
   try:
      c = conn.cursor()
      t=(runID,positionNumber)
      #print "RUNID:  ",runID, "PositionNumber:",positionNumber
      averageWeight=float(0.0)
      c.execute('select f_averageWeight, f_stdevWeight from tblCrucible where i_runID=? and i_positionNumber=?', t)
      logger.debug('select f_averageWeight,f_stdevWeight from tblCrucible where i_runID=%d and i_positionNumber=%d'% (t))
      data=c.fetchone()
      if (data is None):
         return False;
      meanVal=double(data["f_averageWeight"])
      stdevVal=double(data["f_stdevWeight"])
      return (meanVal,stdevVal)
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;

def getEndOfFiring(runID):
   try:
      c = conn.cursor()
      t=(runID,)	
      endOfFiring=""
      logger.debug('select d_endOfFiring from tblRun where i_runID=%d' % (runID)) 
      c.execute('select d_endOfFiring from tblRun where i_runID=%s '% runID)    #

      data=c.fetchone()
      if (data is None):
         return False;
      returnValue=data["d_endOfFiring"]
      return returnValue
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;

def getSampleID(runID,position):
   try:
      c= conn.cursor()
      t=(runID,position)	
      sampleID=0
      logger.debug('select i_sampleID from tblSample where i_runID=%d and i_positionNumber=%d' % (t))
      c.execute('select i_sampleID from tblSample where i_runID=%d and i_positionNumber=%d' % (t))

      data=c.fetchone()
      if (data is None):
         return False;
      else:
         returnValue=data["i_sampleID"]
         return int(returnValue)
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False

def updateRunPostFire(runID,setInitials,status,d_dateTimeFiring,
                      durationOfFiring,temperatureOfFiring,postMeasurementTimeInterval,
                      durationOfPostMeasurements,repetitions,endOfFiring,startPosition,intervalsec):

   logger.debug("updateRunPostFire (   %d,%s,%s,%s,%d,%d,%d,%d,%s,%d )" % 
                (runID,setInitials,status,d_dateTimeFiring,durationOfFiring,temperatureOfFiring,postMeasurementTimeInterval,
                 durationOfPostMeasurements,endOfFiring,intervalsec))

   t=(intervalsec,status,d_dateTimeFiring,durationOfFiring,temperatureOfFiring,postMeasurementTimeInterval,
      durationOfPostMeasurements,endOfFiring,runID)
   try:  
      # create a cursor to the database
      c = conn.cursor()
      # Insert initial data for the run
      logger.debug('update tblRun SET i_loggingInterval=%d,v_status=%s,d_dateTimeFiring=%s,i_durationOfFiring=%d,i_temperatureOfFiring=%d,i_postMeasurementTimeInterval=%d,i_durationOfPostMeasurements=%d,d_endOfFiring=%s WHERE i_runID=%d'% (t))    
      c.execute('update tblRun SET i_loggingInterval=?,v_status=?,d_dateTimeFiring=?,i_durationOfFiring=?,i_temperatureOfFiring=?,i_postMeasurementTimeInterval=?,i_durationOfPostMeasurements=?,d_endOfFiring=? WHERE i_runID=?',t)    
      # Save (commit) the changes
      conn.commit()
      # Now get the id for the run so we can update with other info as we ask...
      runID = c.lastrowid
      return runID
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;

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
   return True;

##Balance Zeroing
def BZero():
   logger.debug("zeroing the balance")
   balance.write(str.encode("ZI\r\n"))
   sleep(2)
   logger.debug("balance says: %s", balance.readline())
   return True;

def getStatsForPrefireWeightOfSample(runID,position,length):
   # first find out what the latest count is for this series of measurements
   max=int(getMaxPreFireCount(runID,position))
   limit=max-length
   t=(runID,position,limit)
   try:
      c=conn.cursor()
      logger.debug('select avg(f_weight) as avg, stdev(f_weight) as stdev ,variance(f_weight) as variance, avg(f_temperature) as preTempAverage, stdev(f_temperature) as preTempStdDev, avg(f_humidity) as preHumidityAverage, stdev(f_humidity) as preHumidityStdDev from tblMeasurement where i_runID=%d AND i_positionNumber=%d AND i_count>%d AND i_preOrPost=1' % (t))
      c.execute('select avg(f_weight) as avg, stdev(f_weight) as stdev, variance(f_weight) as variance, avg(f_temperature) as preTempAverage, stdev(f_temperature) as preTempStdDev, avg(f_humidity) as preHumidityAverage, stdev(f_humidity) as preHumidityStdDev from tblMeasurement where i_runID=? AND i_positionNumber=? AND i_count>? AND i_preOrPost=1',t)
      data=c.fetchone()
      if (data is None):
         return (0.0,0.0,0.0,0.0,0.0,0.0,0.0)
      else:
         avg=data['avg']
         stdev=data['stdev']
         variance=data['variance']
         tempMean=data['preTempAverage']
         tempStdev=data['preTempStdDev']
         humidityMean=data['preHumidityAverage']
         humidityStdev=data['preHumidityStdDev']
         return (avg,stdev,variance,tempMean,tempStdev,humidityMean,humidityStdev)
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;   

def getStatsForPostFireWeightOfSample(runID,position,length):
   # first find out what the latest count is for this series of measurements
   max=int(getMaxPostFireCount(runID,position))
   limit=max-length
   t=(runID,position,limit)
   try:
      c=conn.cursor()
      logger.debug('select avg(f_weight) as avg ,stdev(f_weight) as stdev ,variance(f_weight) as variance, ' \
                   'avg(f_temperature) as postTempAverage, stdev(f_temperature) as postTempStdDev, ' \
                   'avg(f_humidity) as postHumidityAverage, stdev(f_humidity) as postHumidityStdDev   from ' \
                   'tblMeasurement where i_runID=%d and i_positionNumber=%d and i_count>%d and i_preOrPost=2' % (t))
      c.execute('select avg(f_weight) as avg, stdev(f_weight) as stdev, variance(f_weight) as variance, avg(f_temperature) as postTempAverage, stdev(f_temperature) as postTempStdDev, avg(f_humidity) as postHumidityAverage, stdev(f_humidity) as postHumidityStdDev   from tblMeasurement where i_runID=? and i_positionNumber=? and i_count>? and i_preOrPost=2',t)
      data=c.fetchone()
      #print "DATA: ",data
      if ((data is None) or (data['avg']==0.0)):
         return (0.0,0.0,0.0,0.0,0.0,0.0,0.0);
      else:
         avg=data['avg']
         stdev=data['stdev']
         variance=data['variance']
         tempMean=data['postTempAverage']
         tempStdev=data['postTempStdDev']
         humidityMean=data['postHumidityAverage']
         humidityStdev=data['postHumidityStdDev']
         return (avg,stdev,variance,tempMean,tempStdev,humidityMean,humidityStdev)
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;

def getXYForSampleLocation(sampleLocation):
   try:
      c=xyconn.cursor()
      logger.debug('select i_xPosition, i_yPosition from tblCrucibleXY where i_samplePosition = %d' % (sampleLocation))
      c.execute('select i_xPosition, i_yPosition from tblCrucibleXY where i_samplePosition = %s' % sampleLocation)
      data=c.fetchone()
      if (data is None):
         return 0,0
      else:
         x=data['i_xPosition']
         y=data['i_yPosition']
         return (x,y)
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return 0,0

def getXYDistanceForSampleLocation(sampleLocation):
   try:
      c=xyconn.cursor()
      logger.debug('select f_xDistance, f_yDistance from tblCrucibleXY where i_samplePosition = %d' % (sampleLocation))
      c.execute('select f_xDistance, f_yDistance from tblCrucibleXY where i_samplePosition = %s' % sampleLocation)
      data=c.fetchone()
      if (data is None):
         return 0,0
      else:
         x=data['f_xDistance']
         y=data['f_yDistance']
         return (x,y)
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return 0,0


def getXYForBalance(point):
   inOrOut=""
   if point is "outside":
      inOrOut="BALANCE_OUTSIDE"
   else:
      inOrOut="BALANCE_INSIDE"
   try:
      c=xyconn.cursor()
      t=(inOrOut,)
      logger.debug('select i_xPosition, i_yPosition from tblCrucibleXY where v_type = %s' % t)
      c.execute('select i_xPosition, i_yPosition from tblCrucibleXY where v_type=?', t)
      data=c.fetchone()
      if (data is None):
         return 0,0
      else:
         x=data['i_xPosition']
         y=data['i_yPosition']
         return (x,y)
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return 0,0

def updateDistanceXYForPosition(position,x,y):
   try:
      c=xyconn.cursor()
      t=(x,y,position)
      logger.debug('update tblCrucibleXY SET f_xDistance=%d, f_yDistance=%d where i_samplePosition=%d' % t)
      c.execute('update tblCrucibleXY SET f_xDistance=?, f_yDistance=? where i_samplePosition=?', t)
      xyconn.commit()
      return True;
   except sqlite.OperationalError,msg:
      logger.error("A SQL error occurred: %s",msg)
      return False;

def updateXYForSampleLocation(sampleLocation,x,y):
   try:
      c=xyconn.cursor()
      t=(x,y,sampleLocation)
      logger.debug('update tblCrucibleXY SET i_xPosition=%d, i_yPosition=%d where i_samplePosition=%d' % t)
      c.execute('update tblCrucibleXY SET i_xPosition=?, i_yPosition=? where i_samplePosition=?', t)
      xyconn.commit()
      return True;
   except sqlite.OperationalError,msg:
      logger.error("A SQL error occurred: %s",msg)
      return False;

def updateXYForBalance(point,x,y):
   inOrOut=""
   if point is "outside":
      inOrOut="BALANCE_OUTSIDE"
   else:
      inOrOut="BALANCE_INSIDE"
   try:
      c=xyconn.cursor()
      t=(x,y,inOrOut)
      logger.debug('update tblCrucibleXY SET i_xPosition=%d, i_yPosition=%d where v_type=%s' % t)
      c.execute('update tblCrucibleXY SET i_xPosition=?, i_yPosition=? where v_type=?',t)
      xyconn.commit()
      return True;
   except sqlite.OperationalError,msg:
      logger.error("A SQL error occurred: %s",msg)
      return False;

def updateZForSampleLocation(sampleLocation,sampleZPosition):
   try:
      c=xyconn.cursor()
      t=(sampleZPosition,"crucible")
      logger.debug('update tblCrucibleXY SET f_zPosition=%d where v_type=%s' % t)
      c.execute('update tblCrucibleXY SET f_zPosition=? where v_type=?',t)
      xyconn.commit()
      return True;
   except sqlite.OperationalError,msg:
      logger.error("A SQL error occurred: %s",msg)
      return False;

def updateZForBalanceLocation(balanceZPosition):
   try:
      c=xyconn.cursor()
      logger.debug('update tblCrucibleXY SET f_zPosition=%d where rowid=27' % (balanceZPosition))
      c.execute('update tblCrucibleXY SET f_zPosition=%d where rowid=27' % balanceZPosition)
      xyconn.commit()
      return True;
   except sqlite.OperationalError,msg:
      logger.error("A SQL error occurred: %s",msg)
      return False;

def getZForSampleLocation(sampleLocation):
   try:
      c=xyconn.cursor()
      logger.debug('Select f_zPosition FROM tblCrucibleXY where i_samplePosition=%d' % (sampleLocation))
      c.execute('Select f_zPosition FROM tblCrucibleXY where i_samplePosition=%d' % sampleLocation )
      row= c.fetchone()
      return row['f_zPosition']
   except sqlite.OperationalError,msg:
      logger.error("A SQL error occurred: %s",msg)
      return False;

def getZForBalanceLocation():
   try:
      c=xyconn.cursor()
      logger.debug('Select f_zPosition FROM tblCrucibleXY where rowid=27')
      c.execute('Select f_zPosition FROM tblCrucibleXY where rowid=27' )
      row= c.fetchone()
      return row['f_zPosition']
   except sqlite.OperationalError,msg:
      logger.error("A SQL error occurred: %s",msg)
      return False;

def getCrucibleWeightOverTime(runID,sampleLocation):
   val=[]
   count=0
   try:
      c=conn.cursor()
      t=(runID,sampleLocation)
      logger.debug ('select f_weight from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=0' % t)
      c.execute('select f_weight from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=0', t)
      for row in c.fetchall():
         count += 1
         val.append(row['f_weight'])
      return val
   except sqlite.OperationalError,msg:
      logger.error("A SQL error has occurred: %s", msg)
      return False

def getPreFireWeightOverTime(runID,sampleLocation):
   val=[]
   count=0
   try:
      c=conn.cursor()
      t=(runID,sampleLocation)
      logger.debug ('select f_weight from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=0' % t)
      c.execute('select f_weight from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=1', t)
      for row in c.fetchall():
         count += 1
         val.append(row['f_weight'])
      return val
   except sqlite.OperationalError,msg:
      logger.error("A SQL error has occurred: %s", msg)
      return False

def getPostFireWeightOverTime(runID,sampleLocation):
   val=[]
   count=0
   try:
      c=conn.cursor()
      t=(runID,sampleLocation)
      logger.debug ('select f_weight from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=0' % t)
      c.execute('select f_weight from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=2', t)
      for row in c.fetchall():
         count += 1
         val.append(row['f_weight'])
      return val
   except sqlite.OperationalError,msg:
      logger.error("A SQL error has occurred: %s", msg)
      return False

def getCrucibleWeightMeasurement(runID,sampleLocation,number):
   val=0.0
   count=0
   try:
      c=conn.cursor()
      t=(runID,sampleLocation,number)
      logger.debug ('select f_weight from tblMeasurement where i_runID=%d and i_positionNumber=%d and i_preOrPost=0 and i_count=%d' % t)
      c.execute('select f_weight from tblMeasurement where i_runID=? and i_positionNumber=? and i_preOrPost=0 and i_count=?', t)
      row= c.fetchone()

      return float(row['f_weight'])
   except sqlite.OperationalError,msg:
      logger.error("A SQL error has occurred: %s", msg)
      return False

def updateSamplePreFire(i_runID,i_sampleID,i_positionNumber,
                 f_preWeightAverage, f_preWeightStdDev,
                 f_preTemperatureAverage, f_preTemperatureStdDev,
                 f_sherdWeightInitialAverage, f_sherdWeightInitialStdDev,
                 f_preHumidityAverage,f_preHumidityStdDev):
    logger.debug("update sample with weights")
    try:
        # create a cursor to the database
        c = conn.cursor()
        # Insert initial data for the run
        t=(f_preWeightAverage, f_preWeightStdDev,
           f_sherdWeightInitialAverage,f_sherdWeightInitialStdDev,
           f_preTemperatureAverage, f_preTemperatureStdDev,
           f_preHumidityAverage,f_preHumidityStdDev,
           i_runID, i_positionNumber)
        logger.debug('update tblSample SET \
        f_preWeightAverage=%d, f_preWeightStdDev=%d,  \
        f_sherdWeightInitialAverage=%d, f_sherdWeightInitialStdDev=%d, \
        f_preTempAverage=%d, f_preTempStdDev=%d, \
        f_preHumidityAverage=%d, f_preHumidityStDev=%d where i_runID=%d and i_positionNumber=%d' %t)

        c.execute('update tblSample SET \
        f_preWeightAverage=?, f_preWeightStdDev=?,  \
        f_sherdWeightInitialAverage=?, f_sherdWeightInitialStdDev=?, \
        f_preTempAverage=?, f_preTempStdDev=?, \
        f_preHumidityAverage=?, f_preHumidityStdDev=? where i_runID=? and i_positionNumber=?', t)
        return True
    except sqlite.OperationalError, msg:
        logger.error( "A SQL error occurred: %s", msg)
        return False;

def updateSamplePostFireWeight(i_runID,i_positionNumber,f_postFireWeightAverage,f_postFireWeightStdDev ):
   logger.debug("update sample with postFire environmental info")
   try:
      # create a cursor to the database
      c = conn.cursor()
      # Insert initial data for the run
      t=(f_postFireWeightAverage,f_postFireWeightStdDev, i_runID, i_positionNumber)

      c.execute('update tblSample SET \
        f_postFireWeightAverage=?, f_postFireWeightStdDev=? where i_runID=? and i_positionNumber=?', t)
      return True
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
   return False;

def updateSamplePostFire(i_runID,i_sampleID,i_positionNumber,
                         f_postTemperatureAverage, f_postTemperatureStdDev,
                         f_postHumidityAverage,f_postHumidityStdDev,
                         count,repeat,elapsedTimeMin ):
   # runID,sampleID,position,tempMean,tempStdev,humidityMean,humidityStdev,count,repeat,timeElapsed
   logger.debug("update sample with postFire environmental info")
   try:
      # create a cursor to the database
      c = conn.cursor()
      # Insert initial data for the run
      t=(f_postTemperatureAverage, f_postTemperatureStdDev,f_postHumidityAverage,
         f_postHumidityStdDev,count,elapsedTimeMin,repeat,i_runID, i_positionNumber)

      ## logger.debug('update tblSample SET \
      ## f_postTempAverage=%d, f_postTempStdDev=%d, \
      ## f_postHumidityAverage=%d, f_postHumidityStdDev=%d, i_count=%d,\
      ## f_elapsedTimeMin=%f, i_repetitions=%d where i_runID=%d and i_positionNumber=%d' %t)

      c.execute('update tblSample SET \
        f_postTempAverage=?, f_postTempStdDev=?, \
        f_postHumidityAverage=?, f_postHumidityStdDev=?, i_count=?, f_elapsedTimeMin=?, \
        i_repetitions=? where i_runID=? and i_positionNumber=?', t)
      return True
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      return False;