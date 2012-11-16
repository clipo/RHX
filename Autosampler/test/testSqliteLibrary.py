
import logging
import serial
import sqlite3 as sqlite
import time
from ctypes import *
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

path='./libsqlitefunctions.so'

t=(path)

# open the sqlite database and create a connection
conn = sqlite.connect("c:/Users/Archy/Dropbox/Rehydroxylation/RHX.sqlite")
# create a cursor to the database
conn.enable_load_extension(True)
conn.load_extension(path)

c=conn.cursor()

c.execute('select stdev(f_averageWeight) as stdev from tblCrucible')
stdev=c.fetchone()[0]
print stdev

   
