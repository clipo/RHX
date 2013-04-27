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
import serial
from time import sleep
import sched, time
from datetime import datetime
from datetime import timedelta
import msvcrt
import os, sys
from Tkinter import *
#from numpy import *
import array
import math
import ComPorts
from Tkinter import *
import tkFileDialog
from tkMessageBox import *
from tkColorChooser import askcolor
from tkFileDialog import askopenfilename
from statlib import stats
import easygui


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


logger = logging.getLogger("weighSingleSamples")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
today_date = datetime.today()
datestring = today_date.strftime("%Y-%m-%d-%H-%M")
debugfilename = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Logs/weighSingleSamples-" + datestring + "_debug.log"
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
weighSamples = Toplevel()
weighSamples.withdraw()
weighSamples.wm_title("Weigh Sample")
result = Toplevel()
result.wm_title("Result")
result.withdraw()
statusWindow = Toplevel()
statusWindow.withdraw()
alertWindow = Toplevel()
alertWindow.withdraw()


def alert(message):
    title = "RHX ERROR!"
    easygui.msgbox(message, title, ok_button="Exit")     # show a Continue/Cancel dialog
    return


try:
    standard_balance = serial.Serial(port=ComPorts.SampleBalance, baudrate=9600, bytesize=8, parity='N', stopbits=1,
                                     timeout=1, xonxoff=0)
except:
    message = "Cannot open serial port Com %s for the standard balance. Check CompPorts.py.  Quitting." % ComPorts.SampleBalance
    alert(message)

MCOUNT = IntVar()
MCOUNT.set(0)
STATUS = StringVar()
AVERAGEWEIGHT = DoubleVar()
AVERAGEWEIGHT.set(0.0)
STDDEVWEIGHT = DoubleVar()
STDDEVWEIGHT.set(0.0)
ACOUNT = IntVar()
STOPPED = IntVar()
NEXTSTEP = IntVar()


def readStandardBalance():
    standard_balance.write('P\n\r')
    out = standard_balance.readline()
    #print "Balance reports: ", out
    #print "how many gs", out.count(' g')
    if out.count(' g') == 1:
        out = out.replace('g', '')
        out = out.replace(' ', '')
        out = out.rstrip()
        return float(out)
    else:
        return False


def update_windows():
    value = 0


def quitProgram():
    STOPPED.set(1)
    print "Quitting!"
    sys.exit()


def alertWindows(message):
    alertWindow.deiconify()
    Message(alertWindow, text=message, bg='red', fg='ivory', relief=GROOVE)
    return


def weighSample():
    NEXTSTEP.set(0)
    weighSamples.deiconify()
    menubar = Menu(weighSamples)
    #File Bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=quitProgram)
    menubar.add_cascade(label="File", menu=filemenu)
    #Help Menu
    helpmenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=helpmenu)
    #Display the Menus

    weighSamples.config(menu=menubar)

    Button(weighSamples, text="Start", command=startWeigh).grid(row=4, column=0, sticky=W, padx=2, pady=2)
    Button(weighSamples, text="Quit", command=quitProgram).grid(row=4, column=1, sticky=W, padx=2, pady=2)


def startWeigh():
    weighSamples.withdraw()
    statusWindow.deiconify()
    #first create a new run so we have an ID.
    #logger.debug("DataReadWrite.insertRun( %s,%s,%d )" %(initials,today,numberOfSamples))
    now = datetime.today()
    today = now.strftime("%m-%d-%y %H:%M:%S")
    ACOUNT.set(0)
    MCOUNT.set(0)
    statusWindow.update()
    nextWeigh()


def nextWeigh():
    AVERAGEWEIGHT.set(0.0)
    STDDEVWEIGHT.set(0.0)
    ACOUNT.set(0)
    MCOUNT.set(0)
    Label(statusWindow, text="Current measurement attempts:").grid(row=3, column=0, sticky=W)
    Label(statusWindow, textvariable=ACOUNT).grid(row=3, column=1, sticky=W)
    Label(statusWindow, text="Current measurement count:").grid(row=4, column=0, sticky=W)
    Label(statusWindow, textvariable=MCOUNT).grid(row=4, column=1, sticky=W)

    Label(statusWindow, text="Status").grid(row=7, column=0, sticky=W)
    Label(statusWindow, textvariable=STATUS).grid(row=7, column=1, sticky=W)
    Button(statusWindow, text="Pause", command=ask_for_pause).grid(row=8, column=0, padx=2, pady=2)
    Button(statusWindow, text="Weigh Next Sample", command=loopSample).grid(row=8, column=1, padx=2, pady=2)
    Button(statusWindow, text="Quit", command=quitProgram).grid(row=8, column=2, padx=2, pady=2)
    loopSample()


def ask_for_sample():
    msg = "Please place sample on balance and hit continue when stabilized"
    title = "Add sample"
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


def loopSample():
    statustext = ""
    if AVERAGEWEIGHT.get() > 0.0:
        avg = float(AVERAGEWEIGHT.get())
        stdev = float(STDDEVWEIGHT.get())
        m = int(MCOUNT.get())
        statustext = "Result of last run:  Measurements: %i  Average: %f  Std Dev: %f \n" % (m, avg, stdev)

    statustext += "Place the next sample on balance and hit WEIGH"
    STATUS.set(statustext)
    statusWindow.update()
    value = ask_for_sample()
    if value == "exit":
        return
    else:
        now = datetime.today()
        m, avg, stdev = weighSample()
        statustext = "Result of last run. Measurements: %d  Average: %f  Std Dev: %f" % (m, avg, stdev)
        STATUS.set(statustext)
        statusWindow.update()
        return


def is_there_a_sample():
    msg = "The balance reported a weight of 0.0000 g. Is there a sample on the balance?"
    title = "Missing sample?"
    if easygui.ccbox(msg, title):     # show a Continue/Cancel dialog
        return "continue"
    else:
        return "cancel"


def weighSample():
    listOfValues = []
    weight = float(0.0)
    count = 0
    kcount = 0
    averageWeight = 0.0
    stdevWeight = 0.0
    statustext = "Weighing sample"
    STATUS.set(statustext)
    statusWindow.update()
    a = []
    ACOUNT.set(0)
    MCOUNT.set(0)
    AVERAGEWEIGHT.set(0.0)
    STDDEVWEIGHT.set(0.0)
    STATUS.set("")
    statusWindow.update()
    weightArray = []
    stopCheck = STOPPED.get()
    averageWeight = 0.0
    stdevWeight = 0.0
    while STOPPED.get() < 1:
        statusWindow.update()
        result = []
        weight = readStandardBalance()
        #print "WEIGHT: ", weight
        ACOUNT.set(ACOUNT.get() + 1)
        statusWindow.update()
        if weight is FALSE:
            pass
        elif weight > 0.0:
            count += 1
            weightArray.append(weight)
            if (STOPPED.get() < 1 ):
                if count > 4:
                    averageWeight = stats.mean(weightArray)
                    stdevWeight = stats.stdev(weightArray)
                MCOUNT.set(count)
                if count < 5:
                    statustext = " Count: %d the average weight of sample is <need at least 5 measurements>" % (count)
                else:
                    statustext = "Count: %d the average weight of sample is: %f with stdev of: %f" % (
                        count, averageWeight, stdevWeight)
                STATUS.set(statustext)
                AVERAGEWEIGHT.set(averageWeight)
                STDDEVWEIGHT.set(stdevWeight)
                statusWindow.update()
                stopCheck = STOPPED.get()
        else:
            is_there_a_sample()

        sleep(1)
    NEXTSTEP.set(1)
    AVERAGEWEIGHT.set(averageWeight)
    STDDEVWEIGHT.set(stdevWeight)
    MCOUNT.set(count)
    return count, averageWeight, stdevWeight


def done():
    STOPPED.set(1)
    NEXTSTEP.set(1)
    msg = "Done. Continue or exit?"
    mtitle = "Continue or Exit"
    if easygui.ccbox(msg, title=mtitle):     # show a Continue/Cancel dialog
        return "continue"  # user chose Continue
    else:
        sys.exit(0)

#############################################################

Button(root, text="Weigh samples", command=startWeigh).grid(row=2, column=0)
Button(root, text="Quit", command=quit).grid(row=2, column=1, padx=2, pady=2)

root.mainloop()