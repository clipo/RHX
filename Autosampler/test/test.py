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



# open the serial port for the balance
balance = serial.Serial(port='COM13', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10, xonxoff=1, rtscts=0)
n=0
balance.write("XS \r\n")
balance.write("P \r\n")
balance.write("XS \r\n")
balance.write("? \r\n")
while n<100:
    n+=1
    bline = balance.readline()
    print bline

