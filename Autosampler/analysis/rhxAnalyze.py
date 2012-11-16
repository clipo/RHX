__author__ = 'clipo'

import easygui
import sys
sys.path.insert(0, "/Library/Frameworks/Python.framework/Versions/7.2/")
import pylab
import numpy
import logging
import serial
import sqlite3 as sqlite
import time
from ctypes import *
import math
import os
import io
from pylab import *
from time import sleep
import sched, time
import signal
import random
import csv
import re
from datetime import date
import numpy as np
from scipy import stats
from numpy import *
from datetime import datetime
from datetime import timedelta
import os.path
import os
from array import *
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook
import pylab
import threading
import signal
import time
from scipy import signal


def smoothListGaussian(list,strippedXs=False,degree=100):
   window=degree*2-1
   weight=numpy.array([1.0]*window)
   weightGauss=[]
   for i in range(window):
       i=i-degree+1
       frac=i/float(window)
       gauss=1/(numpy.exp((4*(frac))**2))
       weightGauss.append(gauss)
   weight=numpy.array(weightGauss)*weight
   smoothed=[0.0]*(len(list)-window)
   for i in range(len(smoothed)):
       smoothed[i]=sum(numpy.array(list[i:i+window])*weight)/sum(weight)
   return smoothed


def evenlySpacedPlot(evenPlot,evenXarray,evenYarray,liquidwater):
   evenPlot.scatter(evenXarray,evenYarray, marker='o', c='r')
   evenPlot.set_xlabel('Time (m^1/4)', fontsize=8)
   evenPlot.set_ylabel('Mass (g)', fontsize=8)
   xcoords = np.array([evenXarray[0],evenXarray[len(evenXarray)-1]])
   ycoords = np.array([liquidwater,liquidwater])
   evenPlot.plot(xcoords,ycoords, color='b', linewidth=.5, alpha=0.4)
   evenPlot.grid(True)
   plt.ion()     # turns on interactive mode
   plt.show()    # now this should be non-blocking


def temp_humidity_plot(tempPlot,humidPlot,timeArray,tempArray,humidArray):
   #tempPlot.tick(labelsize=8)
   #humidPlot.tick(labelsize=8)
   tempPlot.scatter(timeArray,tempArray, marker='^', c='r')
   humidPlot.scatter(timeArray,humidArray, marker='o', c='g')
   tempPlot.set_xlabel('Time (m^1/4)', fontsize=8)
   humidPlot.set_xlabel('Time (m^1/4)', fontsize=8)
   tempPlot.set_ylabel('Non-Filtered Temperature (C)', fontsize=8)
   humidPlot.set_ylabel('Non-Filtered Humidity (%RH)', fontsize=8)
   tempPlot.grid(True)
   humidPlot.grid(True)
   plt.ion()     # turns on interactive mode
   plt.show()    # now this should be non-blocking


def filtered_temp_humidity_plot(filteredTempPlot,filteredHumidPlot,timeArray,filteredTempArray,filteredHumidArray):
   #filteredTempPlot.tick(labelsize=8)
   filteredTempPlot.scatter(timeArray,filteredTempArray, marker='^', c='r')
   filteredHumidPlot.scatter(timeArray,filteredHumidArray, marker='o', c='g')
   filteredTempPlot.set_xlabel('Time (m^1/4)', fontsize=8)
   filteredHumidPlot.set_xlabel('Time (m^1/4)', fontsize=8)
   filteredTempPlot.set_ylabel('Filtered Temperature (C)', fontsize=8)
   filteredHumidPlot.set_ylabel('Filtered Humidity (%RH)', fontsize=8)
   plt.ion()     # turns on interactive mode
   plt.show()    # now this should be non-blocking


def overall_plot(ax1,xArray,yArray, sampleNumber,liquidwater):
   #ax1.tick(labelsize=8)
   ax1.scatter(xArray,yArray, marker='x', c='r')
   ax1.set_xlabel('Time (m^1/4)', fontsize=8)
   ax1.set_ylabel('Fractional Weight (g)', fontsize=8)
   #ax1.tick(labelsize=8)
   minx=min(xArray)
   miny=min(yArray)
   #print "minx:", minx
   label="Sample Number: "+str(sampleNumber)
   plt.text(minx+.2,miny,label,fontsize=8)
   xcoords = np.array([xArray[0],xArray[len(xArray)-1]])
   ycoords = np.array([liquidwater,liquidwater])
   ax1.plot(xcoords,ycoords, color='b', linewidth=.5, alpha=0.4)
   ax1.grid(True)
   plt.ion()     # turns on interactive mode
   plt.show()    # now this should be non-blocking

def linear_plot(ax2,xarray,yarray,minx,maxx,miny,maxy,slope,intercept,p_value,r_value,filename, sampleNumber):
   #ax2.tick(labelsize=8)
   ax2.plot(xarray, yarray, 'x')
   xls = (minx,maxx)
   yls = (miny,maxy)
   x1=0.0
   x2=0.0
   ax2.axis([xls[0], xls[1], yls[0], yls[1]])
   ax2.set_xlabel('Time (m^1/4)', fontsize=8)
   ax2.set_ylabel('Fractional Weight (g)', fontsize=8)
   ax2.ticklabel_format(style='plain', axis='both, fontsize=8')
   #title = filename + " Sample Number: " + str(sampleNumber)
   #ax2.set_title(title, fontsize=8)
   ax2.grid(True)
   if slope == 0.0 :# the line is parallel to the x axis
      x1 = xls[0]
      x2 = xls[1]
   elif slope > 0.0 :
      # if m > 0, smallest x is the larger of the x values of the points where the line intersects
      # the x = xmin(xls[0]) and y = ymin(yls[0]) lines
      # and largest x is the smaller of the x values of the points where the line intersects
      # the x = xmax(xls[1]) and y = ymax(yls[1]) lines
      x1 = max(xls[0],(yls[0] - intercept)/slope)
      x2 = min(xls[1],(yls[1] - intercept)/slope)
   else :
      # if m < 0, smallest x is the larger of the x values of the points where the line intersects
      # the x = xmin(xls[0]) and y = ymax(yls[1]) lines
      # and largest x is the smaller of the x values of the points where the line intersects
      # the x = xmax(xls[1]) and y = ymin(yls[0]) lines
      x1 = max(xls[0],(yls[1] - intercept)/slope)
      x2 = min(xls[1],(yls[0] - intercept)/slope)
   xcoords = np.array([x1,x2])
   #because of numpy entire set of xcoords can be processed at once to generate the ycoords
   ycoords = slope*xcoords + intercept

   ax2.plot(xcoords,ycoords, color='r', linewidth=4, label='y = ' + str(slope) + '*x ' +
                                                          '+-'[intercept < 0.0] + ' ' + str(abs(intercept)))
   plt.text(minx,miny,'Sample Number: '+str(sampleNumber), fontsize=8)
   plt.text(minx, miny+1,'Slope: '+str(slope), fontsize=8)
   plt.text(minx, miny+2, 'Intercept: '+str(intercept), fontsize=8)
   plt.text(minx, miny+3, 'R-value: '+str(r_value), fontsize=8)
   ax2.grid(True)
   plt.ion()     # turns on interactive mode
   plt.show()    # now this should be non-blocking

def ask_for_filter():
   msg         = "Choose a filter option"
   title       = "Filter Options"
   choices = ["None", "Temperature (mean +/- stddev)", "Humidity (mean +/- stddev)", "Both temperature and humidity"]
   choice = easygui.choicebox(msg, title, choices)
   return choice[:4]

def ask_for_minmax_values(minx,maxx):
   msg         = "Information for linear calculations"
   title       = "Linear Calculations"
   fieldNames  = ["Minimum time (m^1/4)","Maximum time (m^1/4)"]
   fieldValues = []  # we start with blanks for the values
   fieldValues = easygui.multenterbox(msg,title, fieldNames)
   # make sure that none of the fields was left blank
   while 1:  # do forever, until we find acceptable values and break out
      if fieldValues == None:
         break
      errmsg = ""
      if fieldValues[0] > fieldValues[1]:
            errmsg = errmsg + ("The minimum value must be lower than the maximum value. ")
      # look for errors in the returned values
      for i in range(len(fieldNames)):
         if fieldValues[i].strip() == "":
            errmsg = errmsg + ('"%s" is a required field.\n\n' % fieldNames[i])
      if errmsg == "":
         break # no problems found
      else:
         # show the box again, with the errmsg as the message
         errmsg = errmsg + " Invalid values. Please try again. "
         fieldValues = easygui.multenterbox(errmsg, title, fieldNames, fieldValues)

   return float(fieldValues[0]),float(fieldValues[1])

def graph_slope(sampleNumber,x,y,window):
   #window = [-1, 0, 0,0,0,0,0,0, 1]
   #slope = convolve(y, window, mode='same') / convolve(x, window, mode='same')
   # a[start,end,step]

   xs = zeros(alen(x))
   ys = zeros(alen(x))
   slopeArray=zeros(alen(x))
   interceptArray=zeros(alen(x))
   r_valueArray=zeros(alen(x))
   p_valueArray=zeros(alen(x))
   std_errArray=zeros(alen(x))
   date_Array=zeros(alen(x))
   slope=0.0
   intercept=0.0
   r_value=0.0
   p_value=0.0
   std_err=0.0
   date=0.0
   num=1
   dateYears=0.0
   dateCalendar=0.0
   ADBC=""
   dateErrorYear=0.0

   runDate = get_runDate(sampleNumber)
   preWeightAverage,preWeightStdDev=get_preWeight(sampleNumber)
   originalWeightAverage,originalWeightStdDev,prefireWeightAverage,prefireWeightStdDev,postfireWeightAverage,postfireWeightStdDev=get_originalWeight(sampleNumber)
   while num < alen(x):
      #print "Num: ", num
      if num<window:
         slopeArray[num]=0.0
         interceptArray[num]=0.0
         r_valueArray[num]=0.0
         p_valueArray[num]=0.0
         std_errArray[num]=0.0
         #print "slope: 0"
      else:
         xs=x[num-window:num:1]
         ys=y[num-window:num:1]
         #print xs
         slope, intercept, r_value, p_value, std_err = stats.linregress(xs,ys)
         #print "slope:", slope, " -- ", num

         slopeArray[num]=slope
         interceptArray[num]=intercept
         r_valueArray[num]=r_value
         p_valueArray[num]=p_value
         std_errArray[num]=std_err
         #print "Slope Array: ", alen(slopeArray)
         #print slopeArray

         dateYears,dateCalendar,ADBC,dateErrorYear=age_calculate(slope,std_err,postfireWeightAverage,
            postfireWeightStdDev,sampleNumber,runDate,prefireWeightAverage,prefireWeightStdDev)
         date_Array[num]=dateYears
         #print dateYears
      num+=1


   #print slopeArray
      #print "LENGTH: ", alen(slopeArray)
   return (slopeArray,interceptArray,r_valueArray,p_valueArray,std_errArray,date_Array)


def find_correction_for_RH(sampleNumber):

   tempAverage=double(0.0)
   tempStdDev=double(0.0)
   try:
      c=conn.cursor()
      c.execute('select f_preTempAverage, f_preTempStdDev, f_preHumidityAverage, f_preHumidityStdDev from tblSample where i_positionNumber = %d' % sampleNumber)
      row=c.fetchone()
      tempAverage=double(row[0])
      tempStdDev=double(row[1])
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)

   maxTemp=tempAverage+tempStdDev
   minTemp=tempAverage-tempStdDev
   maxHumidity=double(0.0)
   maxWeight=double(0.0)
   minHumidity=double(0.0)
   minWeight=double(0.0)
   # first get the weight for the max values of humidity during the prefire stage
   try:
      c=conn.cursor()
      t=(minTemp,maxTemp,sampleNumber)
      c.execute('select max(f_humidity) from tblMeasurement where f_temperature > ? and f_temperature<? and i_positionNumber = ? and i_preOrPost=2', t)
      row=c.fetchone()
      maxHumidity=double(row[0])
      t=(minTemp,maxTemp,sampleNumber,maxHumidity)
      c.execute('select f_weight from tblMeasurement where f_temperature > ? and f_temperature < ? and i_positionNumber= ? and i_preOrPost=2 and f_humidity=?', t)
      row=c.fetchone()
      maxWeight=double(row[0])
      print "max Humidity:", maxHumidity, "maxWeight:", maxWeight
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)

   # now get the weight for the min values of humidity during the prefire stage
   try:
      c=conn.cursor()
      t=(minTemp,maxTemp,sampleNumber)
      c.execute('select min(f_humidity) from tblMeasurement where f_temperature > ? and f_temperature < ? and i_positionNumber = ? and i_preOrPost=2',t)
      row=c.fetchone()
      minHumidity=double(row[0])
      t=(minTemp,maxTemp, sampleNumber,minHumidity)
      c.execute('select f_weight from tblMeasurement where f_temperature > ? and f_temperature < ? and i_positionNumber= ? and i_preOrPost=2 and f_humidity=?', t)
      row=c.fetchone()
      minWeight=double(row[0])
      print "min Humidity:", minHumidity, "minWeight:", minWeight
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)

   weightDifference = maxWeight-minWeight
   print "Difference:  ", weightDifference
   humidityDifference=maxHumidity-minHumidity
   print "Difference: ", humidityDifference
   rate_of_change = double(weightDifference/humidityDifference)
   print "Rate of Change: ", rate_of_change
   return double(rate_of_change)

def find_correction_for_Temp(sampleNumber):
   humidAverage=double(0.0)
   humidStdDev=double(0.0)
   try:
      c=conn.cursor()
      c.execute('select f_preHumidityAverage, f_preHumidityStdDev from tblSample where i_positionNumber = %d' % sampleNumber)
      row=c.fetchone()
      humidAverage=double(row[0])
      humidStdDev=double(row[1])
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)

   maxHumid=humidAverage+humidStdDev
   minHumid=humidAverage-humidStdDev
   maxTemp=double(0.0)
   maxWeight=double(0.0)
   minTemp=double(0.0)
   minWeight=double(0.0)
   # first get the weight for the max values of humidity during the prefire stage
   try:
      c=conn.cursor()
      t=(minHumid,maxHumid,sampleNumber)
      c.execute('select max(f_temperature) from tblMeasurement where f_humidity > ? and f_humidity<? and i_positionNumber = ? and i_preOrPost=2' ,t)
      row=c.fetchone()
      maxTemp=double(row[0])
      t=(minHumid,maxHumid,sampleNumber,maxTemp)
      c.execute('select f_weight from tblMeasurement where  f_humidity > ? and f_humidity<? and i_positionNumber= ? and i_preOrPost=2 and f_temperature=?', t)
      row=c.fetchone()
      maxWeight=double(row[0])
      print "max Humidity:", maxTemp, "maxWeight:", maxWeight
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)

   # now get the weight for the min values of humidity during the prefire stage
   try:
      c=conn.cursor()
      t=(minHumid,maxHumid,sampleNumber)
      c.execute('select min(f_temperature) from tblMeasurement where f_humidity > ? and f_humidity<? and  i_positionNumber =? and i_preOrPost=21', t)
      row=c.fetchone()
      minTemp=double(row[0])
      t=(minHumid,maxHumid,sampleNumber,minTemp)
      c.execute('select f_weight from tblMeasurement where  f_humidity > ? and f_humidity<? and i_positionNumber= ? and i_preOrPost=2 and f_temperature=?', t)
      row=c.fetchone()
      minWeight=double(row[0])
      print "min Temperature:", minTemp, "minWeight:", minWeight
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)

   weightDifference = maxWeight-minWeight
   print "Difference:  ", weightDifference
   tempDifference=maxTemp-minTemp
   print "Difference: ", tempDifference
   rate_of_change = double(weightDifference/tempDifference)
   print "Rate of Change: ", rate_of_change
   return double(rate_of_change)

def correct_weight_for_Temp(sampleNumber, weight, temp, temp_rate_of_change):
   tempAverage=double(0.0)
   # now get the mean temp value from the pre-fire stage
   try:
      c=conn.cursor()
      c.execute('select f_postTempAverage from tblSample where i_positionNumber = %d ' % sampleNumber)
      logger.debug ('select f_postTempAverage from tblSample where i_positionNumber = %d ' % sampleNumber)
      row=c.fetchone()
      tempAverage=double(row)
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)

   newWeight = double(weight + ((temp-tempAverage) * double(temp_rate_of_change)))
   #print "original weight: ", weight, " tempAverage: ", tempAverage, "temp: ", temp, "rate of change: ", temp_rate_of_change, "New weight: ", newWeight
   return newWeight


def correct_weight_for_RH(sampleNumber, weight, rh, humid_rate_of_change):
   # now get the mean humidity value from the pre-fire stage
   humidityAverage=0.0
   try:
      c=conn.cursor()
      c.execute('select f_postHumidityAverage from tblSample where i_positionNumber = %d ' % sampleNumber)
      logger.debug ('select f_postHumidityAverage from tblSample where i_positionNumber = %d ' % sampleNumber)
      row=c.fetchone()
      humidityAverage=double(row)
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)

   newWeight = double(weight + ((rh-humidityAverage) * double(humid_rate_of_change)))
   #print "original weight: ", weight, " humidityAverage: ", humidityAverage, "humidity: ", rh, "rate of change: ", humid_rate_of_change, "New weight: ", newWeight
   return newWeight

def get_preWeight(n):
   weightAverage=0.0
   weightStdDev=0.0
   count=0
   try:
      c=conn.cursor()
      c.execute('select f_preWeightAverage, f_preWeightStdDev from tblSample where i_positionNumber = %d' % n)
      for row in c.fetchall():
         count += 1
         ##x.append(row['f_weight'])
         ##y.append(row['f_elapsedTimeQuarterPower'])
         weightAverage=row[0]
         weightStdDev=row[1]
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
   return (weightAverage,weightStdDev)

def get_runDate(n):
   maxDate=""
   try:
      c=conn.cursor()
      c.execute('select max(d_dateTime) from tblMeasurement where i_positionNumber = %d and i_preOrPost=2' % n)
      #print ('select max(d_dateTime) from tblMeasurement where i_positionNumber = %d and i_preOrPost=2' % n)
      row=c.fetchone()
      maxDate=row[0]
      #print "max date:", maxDate
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
   ## get the year from the date
   #print "Max Date:  ", maxDate
   return maxDate


def age_calculate(slope,slopeError, postfireWeight,postfireWeightStdDev,n,maxDate,prefireWeight,prefireWeightStdDev):

   #print "Prefire weight: ", weightAverage, "+/- ", weightStdDev

   ## difference is the pre fire weight  minus intercept (post fire weight)
   diffWeight = prefireWeight - postfireWeight
   ## now divide weight by the slope
   dateQuarterPower = diffWeight/slope
   ## now exp to the 4 power
   dateMinutes = pow(abs(dateQuarterPower),4)
   ## 60 minutes per hour
   dateHours = dateMinutes/60
   ## 24 hours to day
   dateDays = dateHours/24
   ## 365 hours/year
   dateYears=dateDays/365
   ## AD/BC - subtract from this year
   ## initialize the maxDate variable with a date (today)
   ADBC=""

   mdate=datetime

   if maxDate.find('.')>0:
      mdate = datetime.strptime(maxDate, '%Y-%m-%d %H:%M:%S.%f')
   else:
      mdate= datetime.strptime(maxDate, '%Y-%m-%d %H:%M:%S')

   maxDateYear=mdate.year
   ## now measure the difference-- the year at the end of the measurement minus number of years in calculations
   dateCalendar=maxDateYear - dateYears
   if dateCalendar <0:
      ADBC ="BC"
   else:
      ADBC="AD"
   if postfireWeightStdDev is None:
      postfireWeightStdDev=0.0
   dateErrorMinutes=pow(postfireWeightStdDev,4)
   dateErrorHours=dateErrorMinutes/60
   dateErrorDays=dateErrorHours/24
   dateErrorYears=dateErrorDays/365

   # now calculate error terms
   # this consists of the prefire weight error, the postfire weight error, the slope error,
   # where prefire-postfire/slope
   # so date * sqrt( ( prefireError/prefire)^2 + (postfireError/postfire)^2 + *slopeError/slope)^2)
   total_error = dateYears * sqrt( pow(prefireWeightStdDev/prefireWeight,2)+ pow(postfireWeightStdDev/postfireWeight,2)+pow(slopeError/slope, 2))

   return (dateYears,dateCalendar,ADBC,total_error)

def regression_figure(evenWeightPlot,xEvenArray, yEvenArray,weightSubPlot,xarray,yarray,xminval,xmaxval,dbfilename,sampleNumber):
   #weightSubPlot.tick(labelsize=8)
   sx=array('d',[])
   sy=array('d',[])
   ex=array('d',[])
   ey=array('d',[])
   count=0
   scount=0
   originalWeight=0.0
   ecount=0
   secount=0

   for var in xarray:
      if var>xminval and var<xmaxval:
         sx.append(var)
         sy.append(yarray[count])
         scount+=1
      count += 1

   for var in xEvenArray:
      if var>xminval and var<xmaxval:
         ex.append(var)
         ey.append(yEvenArray[ecount])
         secount+=1
      ecount += 1

   minx=sx[1]
   maxx=sx[len(sx)-1]
   miny=sy[1]
   maxy=sy[len(sy)-1]
   sy=smoothListGaussian(sy)
   sx=smoothListGaussian(sx)
   #print xEvenArray
   slope, intercept, r_value, p_value, std_err = stats.linregress(sx,sy)
   results=""
   eslope,eintercept,er_value,ep_value,estd_err = stats.linregress(ex,ey)
   runDate=get_runDate(sampleNumber)
   preWeightAverage,preWeightStdDev=get_preWeight(sampleNumber)

   linear_plot(evenWeightPlot,ex,ey,ex[1],ex[len(ex)-1],ey[1],ey[len(ey)-1],
   eslope,eintercept,ep_value,er_value,dbfilename,sampleNumber)

   linear_plot(weightSubPlot,sx,sy,minx,maxx,miny,maxy,slope,intercept,p_value,r_value,dbfilename,sampleNumber)
   originalWeightAverage,originalWeightStdDev,prefireWeightAverage,prefireWeightStdDev,postfireWeightAverage,postfireWeightStdDev=get_originalWeight(sampleNumber)

   print "Original Weight", originalWeightAverage

   (dateYears,dateCalendar,ADBC,dateErrorYears)=age_calculate(slope,std_err, postfireWeightAverage,
      postfireWeightStdDev,sampleNumber,runDate,prefireWeightAverage,prefireWeightStdDev)
   #results += "Results for sample: " + str(sampleNumber) + " from file: " +dbfilename + "\n\r"
   #results += "Slope:           " + str(slope) +"\n\r"
   #results += "Intercept:       " + str(intercept)+"\n\r"
   #results += "Original Weight (equilbrated): " +str(originalWeightAverage)+" +/-" + str(originalWeightStdDev)+"\n\r"
   #results += "Weight due to liquid H20:  "+ str(originalWeightAverage - prefireWeightAverage)+"\n\r"
   #results += "Prefire Weight: " + str(prefireWeightAverage)  + "+/-" + str(prefireWeightStdDev)+"\n\r"
   #results += "Postfire Weight: " + str(postfireWeightAverage) + "+/-" + str(postfireWeightStdDev)+"\n\r"
   #results += "Difference:      " + str(prefireWeightAverage - postfireWeightAverage)+"\n\r"
   #results += "Slope r-value:         " + str(r_value)+"\n\r"
   #results += "Slope p-value:         " + str(p_value)+"\n\r"
   #results += "Slope std_err:         " + str(std_err)+"\n\r"
   #results += "Age (Years):     " + str(dateYears) + " +/- "  + str(dateErrorYears)+"\n\r"
   #results += "Date:            " + str(dateCalendar) + " " + str(ADBC) + " +/-" + str(dateErrorYears)+"\n\r"
   #results += "----------------------------------------------"+"\n\r"
   (dateYears,dateCalendar,ADBC,dateErrorYears)=age_calculate(eslope,estd_err,postfireWeightAverage,
      postfireWeightStdDev,sampleNumber,runDate,prefireWeightAverage,prefireWeightStdDev)
   results += "Results for sample: " + str(sampleNumber) + " from file: " +dbfilename + "\n\r"
   results += "Slope:           " + str(eslope) +"\n\r"
   results += "Intercept:       " + str(eintercept)+"\n\r"
   results += "Original Weight (equilbrated): " +str(originalWeightAverage)+" +/-" + str(originalWeightStdDev)+"\n\r"
   results += "Weight due to liquid H20:  "+ str(originalWeightAverage - prefireWeightAverage)+"\n\r"
   results += "Critical point: " + str(postfireWeightAverage+(originalWeightAverage-prefireWeightAverage))+"\r\n"
   results += "Prefire Weight: " + str(prefireWeightAverage)  + "+/-" + str(prefireWeightStdDev)+"\n\r"
   results += "Postfire Weight: " + str(postfireWeightAverage) + "+/-" + str(postfireWeightStdDev)+"\n\r"
   results += "Difference:      " + str(prefireWeightAverage - postfireWeightAverage)+"\n\r"
   results += "Slope r-value:         " + str(er_value)+"\n\r"
   #results += "Slope p-value:         " + str(p_value)+"\n\r"
   results += "Slope std_err:         " + str(estd_err)+"\n\r"
   results += "Age (Years):     " + str(dateYears) + " +/- "  + str(dateErrorYears)+"\n\r"
   results += "Date:            " + str(dateCalendar) + " " + str(ADBC) + " +/-" + str(dateErrorYears)+"\n\r"
   results += "----------------------------------------------"+"\n\r"

   print results

   return results

def  get_originalWeight(sampleNumber):
   originalWeightAverage=0.0
   originalWeightStdDev=0.0
   prefireWeightAverage=0.0
   prefireWeightStdDev=0.0
   postfireWeightAverage=0.0
   postfireWeightStdDev=0.0
   try:
      c=conn.cursor()
      c.execute('select f_sherdWeightInitialAverage, f_sherdWeightInitialStdDev, f_preWeightAverage, f_preWeightStdDev, f_postfireWeightAverage, f_postfireWeightStdDev from tblSample where i_positionNumber = %d' % sampleNumber)
      #print ('select f_preWeightAverage, f_preWeightStdDev, f_postfireWeightAverage,
      # f_postfireWeightStdDev from tblsample where i_positionNumber = %d ' % sampleNumber)
      row=c.fetchone()

      originalWeightAverage=row[0]
      originalWeightStdDev=row[1]
      prefireWeightAverage=row[2]
      prefireWeightStdDev=row[3]
      postfireWeightAverage=row[4]
      postfireWeightStdDev=row[5]
      #print "max date:", maxDate
   except sqlite.OperationalError, msg:
      logger.error( "A SQL error occurred: %s", msg)
      ## get the year from the date
      #print "Max Date:  ", maxDate
      #return False
   #print originalWeightAverage
   #print originalWeightStdDev
   #print prefireWeightAverage
   #print prefireWeightStdDev
   #print postfireWeightAverage
   #print postfireWeightStdDev

   return originalWeightAverage,originalWeightStdDev,prefireWeightAverage, prefireWeightStdDev, postfireWeightAverage,postfireWeightStdDev

def markEvenlySpacedPoints( x, y,interval):
   number=1
   nextline=0
   x=smoothListGaussian(x)
   y=smoothListGaussian(y)

   evenlySpacedXArray=array('d',[])
   evenlySpacedYArray=array('d',[])
   markcount=0
   skipcount=1
   for xval in x:
      if number == 1 or number==nextline:
         markcount += 1
         #print "number: ", number, "-", x[number],"-",y[number]
         evenlySpacedXArray.append(x[number])
         evenlySpacedYArray.append(y[number])
         ## update sql table
         #try:
            #c=conn.cursor()
            #c.execute('update tblMeasurement set i_evenSpacePoint=1 where i_measurementID=%d' % row_list[number])
            #conn.commit()
         #except sqlite.OperationalError, msg:
            #logger.error( "A SQL error occurred: %s", msg)
         nextline=int(number+int(pow(skipcount,1.25)))
         skipcount += 1
         #print "X: ", xval, " Y:", y[number], " MARK"
      #print "X: ", xval, " Y:", y[number]
      number +=1
   return evenlySpacedXArray, evenlySpacedYArray

############################################################################################
############################################################################################
f = [-3,-6,-1,8,-6,3,-1,-9,-9,3,-2,5,2,-2,-7,-1]
g = [24,75,71,-34,3,22,-45,23,245,25,52,25,-67,-96,96,31,55,36,29,-43,-7]
#outfilter=signal.deconvolve(g,f)
#print outfilter

logger=logging.getLogger("rhxAnalyze")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('analyze.log')
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

directory=''
if  os.name == 'nt':
   directory='c:\\Users\\Archy\\Dropbox\\Rehydroxylation\\'
elif os.name == 'mac':
   directory='/Users/clipo/Dropbox/Rehydroxylation/'

dbfilename= easygui.fileopenbox(msg='SQLLite Filename', title='select file', filetypes=['*.sqlite'], default=directory)
conn = sqlite.connect(dbfilename,detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)

numberOfSamples=0

try:
   c=conn.cursor()
   logger.debug('select i_numberOfSamples from tblRun')
   c.execute('select i_numberOfSamples from tblRun')
   for row in c.fetchall():
      ## numberOfSamples=row["i_numberOfSamples"]
      numberOfSamples=row[0]
except sqlite.OperationalError, msg:
   logger.error( "A SQL error occurred: %s", msg)

print "Number of samples: ", numberOfSamples

## for each sample get the data for the post-fire
sampleNumber=1

while sampleNumber<=numberOfSamples:

   params = {'figure.figsize': [8,8],'text.fontsize': 8, 'xtick.labelsize': 8,'ytick.labelsize': 8, 'axes.fontsize':8,'axes.style' : 'plain', 'axes.axis':'both'}
   plt.rcParams.update(params)
   fig=plt.figure(sampleNumber)
   fig.suptitle(dbfilename, fontsize=10)

   ## define all of the plots in the figure
   ax1 = fig.add_subplot(4,2,1)
   weightSubPlot = fig.add_subplot(4,2,2)
   #filteredWeightPlot=fig.add_subplot(6,2,3)
   tempPlot = fig.add_subplot(4,2,3)               # filtered weight graph
   humidPlot = fig.add_subplot(4,2,4)              # the humidity graph
   slopeGraph = fig.add_subplot(4,2,5)
   dateGraph = fig.add_subplot(4,2,6)
   evenPlot = fig.add_subplot(4,2,7)
   evenPlotRegression = fig.add_subplot(4,2,8)

   finish=0

   preFireWeight=0.0
   postFireWeight=0.0
   print "Sample Number:  ", sampleNumber
   while (finish==0):

      count=0
      x=array('d',[])
      y=array('d',[])
      temp=array('d',[])
      humid=array('d',[])
      tempSmooth=array('d',[])
      humidSmooth=array('d',[])
      y_correct=array('d',[])
      row_list=array('I',[])
      humidAverage=0.0
      humidStdDev=0.0
      tempAverage=0.0
      tempStdDev=0.0
      rowNumber=0
      #rhCorrection=double(find_correction_for_RH(sampleNumber))
      #tempCorrection=double(find_correction_for_Temp(sampleNumber))
      try:
         c=conn.cursor()
         c.execute('select f_preHumidityAverage, f_preHumidityStdDev,f_preTempAverage, f_preTempStdDev,f_preWeightAverage,f_postFireWeightAverage from tblSample where i_positionNumber = %d' % sampleNumber)
         for row in c.fetchall():
            ## numberOfSamples=row["i_numberOfSamples"]

            humidAverage=row[0]
            humidStdDev=row[1]
            tempAverage=row[2]
            tempStdDev=row[3]
            preFireWeight=row[4]
            postFireWeight=row[5]
      except sqlite.OperationalError, msg:
         logger.error( "A SQL error occurred: %s", msg)
      if humidAverage==None:
         humidMax=0
         humidMin=0
      else:
         humidMax=humidAverage+humidStdDev
         humidMin=humidAverage-humidStdDev
      if tempMax==None:
         tempMax=0
         tempMin=0
      else:
         tempMax=tempAverage+tempStdDev
         tempMin=tempAverage-tempStdDev

      try:
         c=conn.cursor()
         c.execute('select  f_weight, f_elapsedTimeQuarterPower, f_temperature, f_humidity from tblMeasurement where i_positionNumber=%d and i_preOrPost=2  ' % sampleNumber)
         logger.debug('select f_weight, f_elapsedTimeQuarterPower, f_temperature, f_humidity from tblMeasurement where i_positionNumber=%d and i_preOrPost=2 ' % sampleNumber)
         for row in c.fetchall():
            count += 1
            if count >0:
               row_list.append(count)
               x.append(row[1])
               y.append(row[0])
               temp.append(row[2])
               humid.append(row[3])
               #newRHWeight=correct_weight_for_RH(sampleNumber,row[0],row[3],rhCorrection)
               #newTempWeight=correct_weight_for_Temp(sampleNumber,newRHWeight,row[2], tempCorrection)
               #y_correct.append(newTempWeight)
               #print "Old Weight: %f", row[0], "Correction: %f", correction, " New Weight: %f", newWeight
      except sqlite.OperationalError,msg:
         logger.error("A SQL error has occurred: %s", msg)

      evenlySpacedXArray=array('d',[])
      evenlySpacedYArray=array('d',[])
      ## now create an array that has the evenly spaced values (and update the sql table with these values)
      interval=50
      originalWeightAverage,originalWeightStdDev,prefireWeightAverage,prefireWeightStdDev,postfireWeightAverage,postfireWeightStdDev=get_originalWeight(sampleNumber)
      liquidwater=originalWeightAverage-prefireWeightAverage
      evenlySpacedXArray, evenlySpacedYArray = markEvenlySpacedPoints(x, y,interval)
      evenlySpacedPlot(evenPlot,evenlySpacedXArray,evenlySpacedYArray,liquidwater)

      overall_plot(ax1,x,y,sampleNumber,liquidwater)
      temp_humidity_plot(tempPlot,humidPlot,x,temp,humid)
      #weightPlotCorrected = fig.add_subplot(4,2,4)
      #overall_plot(weightPlotCorrected,x,y_correct,sampleNumber,originalWeightAverage)

      #filterFlag=ask_for_filter()
      filterFlag="None"

      fx=array('d',[])
      fy=array('d',[])
      ftemp=array('d',[])
      fhumid=array('d',[])

      try:
         c=conn.cursor()
         if (filterFlag=="Both"):
            t=(sampleNumber,humidMin,humidMax, tempMin, tempMax)
            c.execute('select f_weight, f_elapsedTimeQuarterPower, f_temperature, f_humidity from tblMeasurement where i_positionNumber=? and i_preOrPost=2 and f_humidity>? and f_humidity<? and f_temperature>? and f_temperature<? ', t)
            logger.debug('select f_weight, f_elapsedTimeQuarterPower, f_temperature, f_humidity from tblMeasurement where i_positionNumber=%d and i_preOrPost=2 and f_humidity>%f and f_humidity<%f and f_temperature>%f and f_temperature<%f' % t)
            for row in c.fetchall():
               count += 1
               ##x.append(row['f_weight'])
               ##y.append(row['f_elapsedTimeQuarterPower'])
               if count >0:
                  fx.append(row[1])
                  fy.append(row[0])
                  ftemp.append(row[2])
                  fhumid.append(row[3])
               ##print "X: ", x, "Y: ", y
         elif (filterFlag=="Temp"):
               t=(sampleNumber,tempMin, tempMax)
               c.execute('select f_weight, f_elapsedTimeQuarterPower, f_temperature, f_humidity from tblMeasurement where i_positionNumber=? and i_preOrPost=2 and f_temperature>? and f_temperature<? ', t)
               logger.debug('select f_weight, f_elapsedTimeQuarterPower, f_temperature, f_humidity from tblMeasurement where i_positionNumber=%d and i_preOrPost=2 and f_temperature>%f and f_temperature<%f' % t)
               for row in c.fetchall():
                  count += 1
                  ##x.append(row['f_weight'])
                  ##y.append(row['f_elapsedTimeQuarterPower'])
                  if count >0:
                     fx.append(row[1])
                     fy.append(row[0])
                     ftemp.append(row[2])
                     fhumid.append(row[3])
                     ##print "X: ", x, "Y: ", y
         elif (filterFlag=="Humi"):
               t=(sampleNumber,humidMin,humidMax)
               c.execute('select f_weight, f_elapsedTimeQuarterPower, f_temperature, f_humidity from tblMeasurement where i_positionNumber=? and i_preOrPost=2 and f_humidity>? and f_humidity<? ', t)
               logger.debug('select f_weight, f_elapsedTimeQuarterPower, f_temperature, f_humidity from tblMeasurement where i_positionNumber=%d and i_preOrPost=2 and f_humidity>%f and f_humidity<%f' % t)
               for row in c.fetchall():
                  count += 1
                  ##x.append(row['f_weight'])
                  ##y.append(row['f_elapsedTimeQuarterPower'])
                  if count >0:
                     fx.append(row[1])
                     fy.append(row[0])
                     ftemp.append(row[2])
                     fhumid.append(row[3])
                     ##print "X: ", x, "Y: ", y
         else:
            c.execute('select f_weight, f_elapsedTimeQuarterPower, f_temperature, f_humidity from tblMeasurement where i_positionNumber=%d and i_preOrPost=2  ' % sampleNumber)
            logger.debug('select f_weight, f_elapsedTimeQuarterPower, f_temperature, f_humidity from tblMeasurement where i_positionNumber=%d and i_preOrPost=2 ' % sampleNumber)
            for row in c.fetchall():
               count += 1
               ##x.append(row['f_weight'])
               ##y.append(row['f_elapsedTimeQuarterPower'])
               if count >0:
                  fx.append(row[1])
                  #newRHWeight=correct_weight_for_RH(sampleNumber,row[0],row[3],rhCorrection)
                  #newTempWeight=correct_weight_for_Temp(sampleNumber,newRHWeight,row[2], tempCorrection)
                  ## weight differential (m-m0)/m0
                  value=(row[0]-postFireWeight)/postFireWeight
                  fy.append(value)
                  ftemp.append(row[2])
                  fhumid.append(row[3])
                  ##print "X: ", x, "Y: ", y

      except sqlite.OperationalError,msg:
         logger.error("A SQL error has occurred: %s", msg)

      #outfilter=signal.deconvolve(fy,fhumid)
      #print outfilter
      #fig2 = plt.figure()
      #fout = fig2.add_subplot(111)
      #fout.plot(outfilter, 'o-')

      #overall_plot(filteredWeightPlot,fx,fy,sampleNumber,originalWeightAverage)

      #filteredTempPlot = fig.add_subplot(7,2,7)     # the filtered temperature graph
      #filteredHumidPlot = fig.add_subplot(7,2,8)              # the filtered humidity graph
      tempSmooth = smoothListGaussian(temp)
      humidSmooth = smoothListGaussian(humid)
      #filtered_temp_humidity_plot(filteredTempPlot,filteredHumidPlot,fx,ftemp,fhumid)

      fig2=plt.figure(sampleNumber)
      fig2.suptitle("SLOPE", fontsize=10)


      slopeArray=zeros(alen(x))
      interceptArray=zeros(alen(x))
      r_valueArray=zeros(alen(x))
      p_valueArray=zeros(alen(x))
      std_errArray=zeros(alen(x))
      dateArray=zeros(alen(x))

      ### size of the window to calculate slope, intercept, etc. ####
      window = 3
      #########################################

      (slopeArray,interceptArray,r_valueArray,p_valueArray,std_errArray,dateArray)=graph_slope(sampleNumber,evenlySpacedXArray,evenlySpacedYArray,window)
      slopeGraph.plot(evenlySpacedXArray, slopeArray, '.')
      slopeGraph.set_xlabel('Time (m^1/4)', fontsize=8)
      slopeGraph.set_ylabel('Slope', fontsize=8)
      slopeGraph.ticklabel_format(style='plain', axis='both, fontsize=8')
      slopeGraph.grid(True)
      #interceptGraph = fig2.add_subplot(7,2,10)
      #interceptGraph.set_xlabel('Time (m^1/4)', fontsize=8)
      #interceptGraph.set_ylabel('Intercept (g)', fontsize=8)
      #interceptGraph.ticklabel_format(style='plain', axis='both, fontsize=8')
      #rvalueGraph = fig2.add_subplot(7,2,11)
      #pvalueGraph = fig2.add_subplot(7,2,10)
      #rvalueGraph.set_xlabel('Time (m^1/4)', fontsize=8)
      #rvalueGraph.set_ylabel('r-value', fontsize=8)
      #rvalueGraph.ticklabel_format(style='plain', axis='both, fontsize=8')

      dateGraph.set_xlabel('Time (m^1/4)', fontsize=8)
      dateGraph.set_ylabel('Date (Years)', fontsize=8)
      dateGraph.ticklabel_format(style='plain', axis='both, fontsize=8')
      dateGraph.grid(True)

      #interceptGraph.plot(x,interceptArray,'--')
      #rvalueGraph.plot(x,r_valueArray,'--')
      dateGraph.plot(evenlySpacedXArray,dateArray,'--')
      #plt.plot(xArray,ainterceptArray,'x')
      plt.ion()     # turns on interactive mode
      plt.show()    # now this should be non-blocking\

      minval=""
      maxval=""
      results=""

      minval, maxval=ask_for_minmax_values(min(x),max(x))

      results += "NON FILTERED RESULTS"+"\n\r"
      results += regression_figure(evenPlotRegression,
         evenlySpacedXArray,evenlySpacedYArray,
         weightSubPlot,
         x,y,minval,maxval,
         dbfilename,sampleNumber)

      #weightFilteredSubPlot=fig.add_subplot(6,2,4)
      #results2 = regression_figure(weightFilteredSubPlot,fx,fy,minval,maxval,dbfilename,sampleNumber)
      #results += "FILTERED RESULTS "+ filterFlag+"\n\r"
      #results += results2+"\n\r"

      easygui.codebox(msg=None, title='Results ', text=results)

      test=""




      #plt.plot(xArray,ap_valueArray,'+')
      msg     = "What would you like to do?"
      choices = ["Try Again","Next Sample","Quit"]
      reply   = easygui.buttonbox(msg,image=None,choices=choices)

      if reply=="Next Sample":
         plt.clf()
         sampleNumber += 1
         break
      elif reply=="Try Again":
         plt.clf()
         break
      else:
         exit()





