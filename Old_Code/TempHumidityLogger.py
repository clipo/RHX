__author__ = 'Archy'

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
import enhancedserial

# open the serial port for the temperature and humidity controller
tempHumidity = enhancedserial.EnhancedSerial(port='COM1', baudrate=9600, bytesize=8, parity='N', stopbits=1,
   timeout=2, xonxoff=1)

while n==True:
   tempHumidity.write("\n")
   value=tempHumidity.readline()
listOfValues=tline.split(",",10)
humidity=listOfValues[1]
tempC=0.0
tempF=listOfValues[2]
tempC=(float(tempF)-32)*5/9
pressure=listOfValues[4]
light=listOfValues[5]
