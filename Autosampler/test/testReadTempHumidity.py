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
from numpy import *
from datetime import datetime
from datetime import timedelta
import DataReadWrite

begin=0
end=20
test=0
passed=0

while begin < end:
   print "-------------------------------------------------------"
   tempCorrection=0
   rhCorrection=0
   print "readTempHumidity(",tempCorrection,",",rhCorrection,")"
   initials="CPL"
   numberOfSamples=3
   (temp,humidity,dewpoint,pressure,light)=DataReadWrite.readTempHumidity(tempCorrection,rhCorrection)
   print "Temp:",temp
   print "Humidity:",humidity
   print "Dewpoint:",dewpoint
   print "Pressure:",pressure
   print "Light:",light
   test += 1
   if temp>0:
      print "PASS"
      passed += 1
   else:
      print "FAIL"
   begin += 1