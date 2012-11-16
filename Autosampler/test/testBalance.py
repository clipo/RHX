
import sys
sys.path.insert(0, "/usr/local/lib/python2.7/site-packages/")
from time import sleep
import sched, time
import signal
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
import serial
import time
import string



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
   #print "out->", out
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
   out=out.lstrip()
   out=out.replace('g','')
   out=out.rstrip()
   value=float(out)
   return value
print readStandardBalance()
