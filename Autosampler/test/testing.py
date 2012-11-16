import serial
import time
from datetime import datetime
from datetime import timedelta
import msvcrt
from pyExcelerator import *  
import os, sys
from select import select
import signal
import sys
import random
import csv
import re
import sqlite3 as sqlite

def average(myList):
	newList=[]
	for n in myList[:]:
		newList.append(float(n))

	summy = sum(newList)
	averages = float(summy)/len(newList)
	return averages

def std(myList):
	newList=[]
	for n in myList[:]:
		newList.append(float(n))
	summy = sum(newList)
	a = float(summy)/len(newList)
	r =len(newList)
	b = []
	for n in range(r-1):
		if newList[n] > a:
			b.append((newList[n] - a)**2)
		if newList[n] < a:
			b.append((a - newList[n])**2)
	SD = (float(sum(b)/r))**0.5
	return SD

def NumUp():
	global num
	num = num + 1

def StopUp():
	global stopCode
	stopCode = stopCode + 1

def StopZero():
	global stopCode
	stopCode = 0

def SampleNumUp():
	global sampleNumber
	sampleNumber=sampleNumber+1

def ItNumUp():
	global ItNum
	ItNum=ItNum+1
	global sampleNumber
	sampleNumber=1

def MoveThis():
	AutoStepper.GoToPosition()

def TimeWeigh():
	CTSec=raw_input("How long do you want to weigh the crucibles? (Minutes) ")
	CTMin=int(CTSec)*60
	global WaitTime
	WaitTime=CTMin
	MoveThis()

def StartWeighing():
	WeighSample()

def WeighSample():
	StopZero()
	scount = 1
	intervalsec=int(intervalseca)
	HackStep1=int(WaitTime/60)
	HackStep2 = 60//intervalsec
	HackSol = int(HackStep2*HackStep1)


# open the sqlite database and create a connection
conn = sqlite.connect('c:/Users/Archy/Dropbox/Rehydroxylation/RHX.sqlite')
# create a cursor to the database
c = conn.cursor()

# open the serial port for the temperature and humidity controller
tempHumidity = serial.Serial(port='COM11', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2, xonxoff=1, rtscts=0)
time.sleep(1)

# open the serial port for the balance
balance = serial.Serial(port='COM9',baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10, xonxoff=0, rtscts=0)

now = datetime.today()
today = now.strftime("%m-%d-%y %H:%M:%S")
todayString=now.strftime("%y%m%d%H%M%S")
print "The current time/date is: ", today
diffTime = now - now
endOfFiring = now

filename=""
fileokay=0
file=""
setInitials=""



preOrPost=""
while preOrPost=="":
	preOrPost = raw_input('Pre firing weight determination (0) or Post firing (1): ')

# POST firing value for preOrPost is 1
if preOrPost=="1":
	status ="Post-fired"
	# we want to just update the record during the post-fire phase
	runID=""
	while runID == "":
		runID = raw_input('Sample ID from prefiring (e.g., 1): ')
	locationCode=""
	numberOfSamples=0
	description=""
	temperature=0.0
	humidity=0.0
	c = conn.cursor()
	c.execute('select * from tblRun where i_runID = ?',runID)
	for row in cur.fetchall():
		locationCode=row[1]
		numberOfSamples=row[2]
		description=row[14]
		temperature=row[17]
		humidity=row[18]

	setInitials=""
	while setInitials == "":
		setInitials = raw_input( 'Researcher Initials (e.g., CPL): ')

	print "Enter date at which the firing started: "
	startdate = raw_input('Format: mm-dd-yyyy --> ')
	sdate=startdate.split("-",3)
	print "Enter start time of firing: "
	starttime = raw_input('Format (24 hours): hh:mm:ss -->')
	stime=starttime.split(":",3)
	startOfFiring = datetime(int(sdate[2]), int(sdate[0]), int(sdate[1]), int(stime[0]), int(stime[1]), int(stime[2]))
	durationOfFiring = raw_input('Duration of firing (minutes): ')
	endOfFiring = startOfFiring + timedelta(minutes,durationOfFiring)

	# minutes since firing ended
	diffTime = now - endOfFiring

	tempFiring=""
	while tempFiring == "":
		tempFiring=raw_input('Temperature of firing (e.g., 600, 700): ')
	intervalsec=""

	postMeasurementTimeInterval=""
	while postMeasurementTimeInterval=="":
		postMeasurementTimeInterval=raw_input('How long to measure each sample (minutes, e.g., 60): ')

	while intervalsec:
		intervalsec = raw_input('Sampling interval (how often to check balance, in seconds, e.g., 5,10,15,30,120): ')

	t=(setInitials,description,today,locationCode,1,interval,temperature,humidity,status,numberOfSamples,runID,postMeasurementTimeInterval)

	# Insert initial data for the run
	c.execute('insert into tblRun (v_operatorName,v_description,d_dateTime,v_locationCode,i_preOrPost,i_loggingInterval,f_temperature,f_humidity,v_status,i_numberOfSamples,i_linkedRun,i_postMeasurementTimeInterval) values (?,?,?,?,?,?,?,?,?,?,?,?)',t)
	# Save (commit) the changes
	conn.commit()
	# Now get the id for the run so we can update with other info as we ask...
	runID = c.lastrowid
	print "RUN ID = ",runID, " <WRITE THIS DOWN>"
	raw_input('Press any key to continue')


# must mean pre-firing
else:
	status="Pre-firing"
	setName=""
	while setName=="":
		setName = raw_input( 'Enter name of sample set (e.g., Mississippian ): ')

	setInitials=""
	while setInitials == "":
		setInitials = raw_input( 'Researcher Initials (e.g., CPL): ')

	setLocation=""
	while setLocation == "":
		setLocation = raw_input( 'Sample Location (e.g., LMV): ')
	numberOfSamples=""
	while numberOfSamples:
		numberOfSamples = raw_input('How many samples? (e.g., 1,5,10): ')

	preMeasurementTimeInterval=""
	while preMeasurementTimeInterval=="":
		preMeasurementTimeInterval=raw_input('How long to measure each sample (minutes, e.g., 60): ')

	intervalsec=""
	while intervalsec:
		intervalsec = raw_input('Sampling interval (how often to check balance, in seconds, e.g., 5,10,15,30,120): ')

	setTemperature=""
	while setTemperature == "":
		setTemperature = raw_input( 'Temperature for holding samples (e.g., 19.6): ')

	setHumidity=""
	while setHumidity == "":
		setHumidity = raw_input( 'Humidity for holding samples (e.g., 60.0): ')

	t=(setInitials,setName,today,setLocation,preOrPost,intervalsec,setTemperature,setHumidity,status,preMeasurementTimeInterval,numberOfSamples)
	# create a cursor to the database
	c = conn.cursor()
	# Insert initial data for the run
	c.execute('insert into tblRun (v_operatorName,v_description,d_dateTime,v_locationCode,i_preOrPost,i_loggingInterval,f_temperature,f_humidity,v_status,i_preMeasurementTimeInterval,i_numberOfSamples) values (?,?,?,?,?,?,?,?,?,?,?)',t)
	# Save (commit) the changes
	conn.commit()
	# Now get the id for the run so we can update with other info as we ask...
	runID = c.lastrowid
	print "RUN ID = ",runID, " <WRITE THIS DOWN>"
	raw_input('Press any key to continue')


