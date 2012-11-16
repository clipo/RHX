###Simple program that moves the motors and the arms - used for finding positions.


##Imports
from Tkinter import *
import Tkinter
import tkMessageBox
import time
from datetime import datetime
from datetime import timedelta
import sys
import os
import io
import re
import cv
import serial
from ctypes import *
from time import sleep
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, InputChangeEventArgs, CurrentChangeEventArgs, StepperPositionChangeEventArgs, VelocityChangeEventArgs
from Phidgets.Devices.Stepper import Stepper
from Phidgets.Devices.AdvancedServo import AdvancedServo
from Phidgets.Devices.Servo import ServoTypes

##Balance

balance = serial.Serial(port='COM3', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=10, xonxoff=0, rtscts=0)
# open the serial port for the temperature and humidity controller
tempHumidity = serial.Serial(port='COM11', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=2, xonxoff=1, rtscts=0)



## CONSTANTS ###########################

## Stepper Motor Numbers
XMOTOR=0
YMOTOR=2

## Advanced Servo
ZMOTOR=0
GRIPPER=1

X=0
Y=1

STOPPED=1
MOVING=0

#Movement List - Position 0 is motor 0 - Position 1 is motor 2 ... made sense ...
MOVE= (   [0,0],  [-400,0],     [-800,0],     [-1200,0],    [-1600,0],
	  [0,400],    [-400,400],   [-800,400],   [-1200,400],  [-1600,400],
	  [0,800],    [-400,800],   [-800,800],   [-1200,800],  [-1600,800],
	  [0, 1200],  [-400,1200],  [-800,1200],  [-1200,1200], [-1600,1200],
          [0,1600],   [-400,1600],  [-800,1600],  [-1200,1600], [-1600,1600]   )

# This is the relative position from the uppermost Z axis point (i.e., how far down to lower the arm)
DOWN_SAMPLE_POSITION = 94
DOWN_BALANCE_POSITION = 40

UP_SAMPLE_POSITION=17
UP_BALANCE_POSITION=17

#spaces betwen sample locations going along the length of the sampler (horizontal)
HORIZONTAL_SPACING = -350

#space between sample locations going away from the sampler (vertical)
VERTICLE_SPACING = 400

# coordinates for the Balance
BALANCE_OUTSIDE = [  -2000,900 ]
BALANCE_INSIDE = [ -3500, 780  ]

# coordinates for the gripper position
GRIPPER_CLOSED = 93
GRIPPER_OPEN = 0

capture = cv.CaptureFromCAM(0)
cv.NamedWindow("Overview",1)
capture2 = cv.CaptureFromCAM(1)
cv.NamedWindow("View from Arm",2)


############INITIALIZATION########################
###Create Stepper and Servo Objects
try:
    advancedServo = AdvancedServo()
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)
    
try:
    stepper = Stepper()
except RuntimeError as e:
    print("Runtime Exception: %s" % e.details)
    print("Exiting....")
    exit(1)
#stack to keep current values in
currentList = [0,0,0,0,0,0,0,0]
velocityList = [0,0,0,0,0,0,0,0]
   
###Open Phidgets
print("Opening phidget object for Servos....")

try:
    advancedServo.openPhidget()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

print("Waiting for Arm to attach....")

try:
    advancedServo.waitForAttach(10000)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    try:
        advancedServo.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    print("Exiting....")
    exit(1)

print("Opening phidget object for steppers...")
try:
    stepper.openPhidget()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

print("Waiting for stepper motors to attach....")

try:
    stepper.waitForAttach(1000)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    try:
        stepper.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    print("Exiting....")
    exit(1)

try:
    print("Setting the servo type for motor 0 to PHIDGET_SERVO_FIRGELLI_L12_100_100_06_R ")
    advancedServo.setServoType(ZMOTOR, 17 )
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

try:
    print("Setting the servo type for motor 1 to PHIDGET_SERVO_HITEC_HS422")
    advancedServo.setServoType(GRIPPER, ServoTypes.PHIDGET_SERVO_HITEC_HS422)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Exiting....")
    exit(1)

#get current postiopn   
try:
   xpos=stepper.getCurrentPosition(XMOTOR)
   ypos=stepper.getCurrentPosition(YMOTOR)
except PhidgetException as e:
   print("Phidget Exception %i: %s" % (e.code, e.details))
   print("Exiting....")
   exit(1)
      
#Set Current position as Start Position    
#print ("Set Positions of SERVOs and STEPPER MOTORS to 0")
#try:
#   stepper.setCurrentPosition(XMOTOR, 0)
#   stepper.setCurrentPosition(YMOTOR, 0)
#   advancedServo.setPosition(ZMOTOR,UP_SAMPLE_POSITION)
#   advancedServo.setPosition(GRIPPER,GRIPPER_OPEN)
#except PhidgetException as e:
#   print("Phidget Exception %i: %s" % (e.code, e.details))
#   print("Exiting....")
#   exit(1)

##User Defined Variable




def openGripper():

   print "now open gripper"
   #  Set the gripper to be open
   try:
      advancedServo.setEngaged(GRIPPER, True)
      advancedServo.setPosition(GRIPPER, GRIPPER_OPEN)
      while advancedServo.getStopped(GRIPPER) !=STOPPED:
         pass
      sleep(1)
      advancedServo.setEngaged(GRIPPER, False)
   except PhidgetException as e:
        print("Gripper Open Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)   

   
   
def closeGripper():
   print "now close gripper"
   #  Set the gripper to be open
   try:
      advancedServo.setEngaged(GRIPPER, True)
      advancedServo.setPosition(GRIPPER, GRIPPER_CLOSED)
      while advancedServo.getStopped(GRIPPER) !=STOPPED:
         pass
      sleep(1)
      advancedServo.setEngaged(GRIPPER, False)
   except PhidgetException as e:
        print("Grupper Close Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)   


##Motor Movers
##+numbers go away from the balance    
def M0Mover():
    print ("The input value is:", M0EE1.get())
    MB1V1.set("0")
    MV.set(M0EE1.get())
    try:
        Mover()
    except:
        pass
##+numbers go towards the motors    
def M1Mover():
    print ("The input value is:", M1EE1.get())
    MB1V1.set("1")
    MV.set(M1EE1.get())
    try:
        Mover()
    except:
        pass
##+numbers go up
def M2Mover():
    print ("The input value is:", M2EE1.get())
    MB1V1.set("2")
    MV.set(M2EE1.get())
    try:
        Mover()
    except:
        pass
#0 out Position
def M0SetP():
    print ("Current position of Motor 0 is now start position")
    MB2V1.set("0")
    try:
        MotorPosition()
    except:
        pass
    M0EE1.set("0")
def M1SetP():
    print ("Current position of Motor 1 is now start position")
    MB2V1.set("1")
    try:
        MotorPosition()
    except:
        pass
def M2SetP():
    print ("Current position of Motor 2 is now start position")
    MB2V1.set("2")
    try:
        MotorPosition()
    except:
        pass
    M2EE1.set("0")
def MotorPosition():
    try:
        print("Set the current position as start position...")
        stepper.setCurrentPosition(MB2V1.get(), 0)
        sleep(1)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
def MotorMove():
    try:
        print("Set the motor as engaged...")
        stepper.setEngaged(MB1V1.get(), True)
        sleep(1)
        stepper.setTargetPosition(MB1V1.get(), MV.get())
        while stepper.getCurrentPosition(MB1V1.get()) != MV.get():
            pass
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    print ("Finished Move...")
def KillMotors():
    print ("Killing Motors and Phidget")
    try:
        stepper.setEngaged(0, False)
        sleep(1)
        stepper.setEngaged(1, False)
        sleep(1)
        stepper.setEngaged(2, False)
        sleep(1)
        advanceServo.setEngaged(0, False)
        stepper.closePhidget()
        advancedServo.closePhidget()
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")

def Mover():
    try:
        MotorMove()
    except:
        pass
###Arm Controls
def ArmMove():
    try:
        advancedServo.setEngaged(0, True)
        sleep(2)
        advancedServo.setPosition(0, AV.get())
        while advancedServo.getPosition(0) != AV.get():
            pass
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    sleep(2)
    try:
        advancedServo.setEngaged(0, False)
        sleep(1)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    AV.set("0")
def ArmMax():
    try:
        advancedServo.setEngaged(0, True)
        sleep(2)
        advancedServo.setPosition(0, advancedServo.getPositionMax(0))
        while advancedServo.getPosition(0) != advancedServo.getPositionMax(0):
            pass
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    sleep(2)
    try:
        advancedServo.setEngaged(0, False)
        sleep(1)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
def ArmMin():
    try:
        advancedServo.setEngaged(0, True)
        sleep(2)
        advancedServo.setPosition(0, advancedServo.getPositionMin(0))
        while advancedServo.getPosition(0) != advancedServo.getPositionMin(0):
            pass
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)
    sleep(2)
    try:
        advancedServo.setEngaged(0, False)
        sleep(1)
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Exiting....")
        exit(1)

def getMotorPositions():
   try:
      xpos=stepper.getCurrentPosition(XMOTOR)
      ypos=stepper.getCurrentPosition(YMOTOR)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   return (xpos,ypos)      

def getXMotorPosition():
   #get current postiopn   
   try:
      ypos=stepper.getCurrentPosition(YMOTOR)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   return xpos  

def getYMotorPosition():
   #get current postiopn   
   try:
      ypos=stepper.getCurrentPosition(YMOTOR)
   except PhidgetException as e:
      print("Phidget Exception %i: %s" % (e.code, e.details))
      print("Exiting....")
      exit(1)
   return ypos

def printValues():
    print "XMotor: ",getXMotorPosition(), " YMotor: ",getYMotorPosition()
    print "Balance: ", readBalance()
    print "-------------------------------------------------"
    

##Balance Door Controls
def BDOpen():
    balance.write(str.encode("WS 1\r\n"))
def BDClose():
    balance.write(str.encode("WS 0\r\n"))

##Balance Zeroing
def BZero():
    balance.write(str.encode("ZI \r\n"))

def readBalance():
   ## balance read
   non_decimal = re.compile(r'[^\d.]+')
   balance.write("S\n\r")
   bline = balance.readline()
   #print "Balance Ouput:  ", bline
   weight=0.0
   if len(bline) == 18:	
      bbline = bline.lstrip("S S   ")
      weight = bbline.replace(" g", "")
      weight=weight.rstrip()
      weight = non_decimal.sub('', weight)
      weight=float(weight)
      if weight=="":
         weight=0.0
      if weight.count('.')>1:
         weight=0.0
      
   return float(weight)

def readTH():
   ## temp Humidity Read
   tline=" "
   readOne=""
   ## Example string:  $,57.8,79,51.4,1009.48,0.0,0.0,-1,0.00,0.00,*
   ##                  $,57.8,79,51.5,1009.28,0.0,0.0,-1,0.00,0.00,*
   random.seed()
   non_decimal = re.compile(r'[^\d.]+')
   time.sleep(1)
   tempHumidity.write("\n")
   while(readOne <> "$"):
      readOne =tempHumidity.read(1)
      tline = "$"+tempHumidity.read(46)
      while( tline.find("$") <> 0 and tline.find("*") < 44 ):
         print "Incorrect string. try again."
         time.sleep(0.5*random.random())
         print "TempHumidity Reading: ", tline
         tline="$".tempHumidity.read(46)

   listOfValues=tline.split(",",10)
   humidity=listOfValues[1]
   tempC=0.0
   tempF=listOfValues[2]
   tempC=(float(tempF)-32)*5/9
   pressure=listOfValues[4]
   light=listOfValues[5]
   
   listOfValues=(tempC,humidity,pressure,light)
   return listOfValues

def isBalanceDoorOpen():
   balance.write(str.encode("WS\r\n"))
   bline = balance.readline()
   vals=bline.split(" ",3)
   print vals
   val=vals[2]
   status=val.rstrip()
   # 0 is the CLOSED status
   # 2 or 1 is the OPEN status
   return status
    
#Program Controls
    
def restart_program():
    try:
        KillMotors()
    except:
        pass
    python = sys.executable
    os.execl(python, python, * sys.argv)
def KillProgram():
    try:
        KillMotors()
    except:
        pass
    balance.close()
    root.quit()


#Run Main Loop
root = Tk()
root.wm_title("RHX Measurement")
root.BZL5 = Tkinter.Label(text="")
root.BZL7 = Tkinter.Label(text="")
root.MOE1=  Tkinter.IntVar()
root.MOL1 = Tkinter.Label(text="")
root.MOB1 = Tkinter.Button(text="")
root.MOB2 = Tkinter.Button()
root.M1L1 = Tkinter.Label()
root.M1E1 = Tkinter.IntVar()
root.M1B1 = Tkinter.Button()
root.M1B2 = Tkinter.Button()
root.ACL1 = Tkinter.Label()
root.ACB1 = Tkinter.Button()
root.ACB2 = Tkinter.Button()

##Arm Controls  
root.AML1 = Tkinter.Label()
root.AME1 = Tkinter.Entry()
root.AMB1=Tkinter.Button()


##Balance Door controller
root.BDL1 =Tkinter.Label()

root.BDB1 = Tkinter.Button()

root.BDB2 = Tkinter.Button()


      ##Balance Zeroing
root.BZL1=Tkinter.Label()

root.BZB1=Tkinter.Button()


root.BZL2=Tkinter.Label()

root.BZL3=Tkinter.Label()


root.BZL4=Tkinter.Button()

root.BZL5=Tkinter.Label()


root.BZL6=Tkinter.Button()

root.BZL7=Tkinter.Label()


root.M1B3 = Tkinter.Button()

root.M1B4 = Tkinter.Button()


root.M1B5 = Tkinter.Button()
root.M0EE1=Tkinter.IntVar()
root.M1EE1=Tkinter.IntVar()
root.M2EE1=Tkinter.IntVar()
root.MB1V1=Tkinter.IntVar()
root.MB2V1=Tkinter.IntVar()

root.MV=Tkinter.IntVar()
root.AV=Tkinter.DoubleVar()

#root.destroy()
class Start:
   ##Establish GUI

   def __init__(self):

     # self.root = Tkinter.Tk()

      #Create Menus
      root.menubar = Menu(root)
      #File Bar 
      root.filemenu = Menu(root.menubar, tearoff=0)
      root.filemenu.add_command(label="New", command=restart_program)
      root.filemenu.add_separator()
      root.filemenu.add_command(label="Exit", command=KillProgram)
      root.menubar.add_cascade(label="File", menu=root.filemenu)

      #Help Menu
      root.helpmenu = Menu(root.menubar, tearoff=0)
      root.menubar.add_cascade(label="Help", menu=root.helpmenu)
      #Display the Menus
      root.config(menu=root.menubar)

      ##Motor 0 Controls  
      root.M0L1 = Label(root, text="X-Axis")
      root.M0L1.grid(row=0, column=0, sticky=W)
      root.M0E1 = Entry(root, textvariable=root.M0EE1)
      root.M0E1.grid(row=1, column=0, sticky=W)
      root.M0B1 = Button(root, text="Move 0", command=M0Mover)
      root.M0B1.grid(row=1, column=1, padx=2, pady=2)
      root.M0B2 = Button(root, text="Set Current Position 0", command=M0SetP)
      root.M0B2.grid(row=1, column=2, padx=2, pady=2)

      ##Motor 2 Controls
      root.M1L1 = Label(root, text="Y-Axis")
      root.M1L1.grid(row=2, column=0, sticky=W)
      root.M1E1 = Entry(root, textvariable=root.M2EE1)
      root.M1E1.grid(row=3, column=0, sticky=W)
      root.M1B1 = Button(root, text="Move 1", command=M2Mover)
      root.M1B1.grid(row=3, column=1, padx=2, pady=2)
      root.M1B2 = Button(root, text="Set Current Position 0", command=M2SetP)
      root.M1B2.grid(row=3, column=2, padx=2, pady=2)

      ##Arm Controller
      root.ACL1 = Label(root, text="Arm Controller (Z Axis)")
      root.ACL1.grid(row=6, column=0, sticky=W)
      root.ACB1 = Button(root, text="Min", command=ArmMin)
      root.ACB1.grid(row=7, column=0, sticky=W, padx=2, pady=2)
      root.ACB2 = Button(root, text="Max", command=ArmMax)
      root.ACB2.grid(row=7, column=1, sticky=W, padx=2, pady=2)

      ##Arm Controls  
      root.AML1 = Label(root, text="Arm Controller (Z-Axis)")
      root.AML1.grid(row=8, column=0, sticky=W)
      root.AME1 = Entry(root, textvariable=root.AV)
      root.AME1.grid(row=8, column=1, sticky=W)
      root.AMB1=Button(root, text="Move", command=ArmMove)
      root.AMB1.grid(row=8, column=2, sticky=W)

      ##Balance Door controller
      root.BDL1 =Label(root, text="Balance Door")
      root.BDL1.grid(row=9, column=0, sticky=W)
      root.BDB1 = Button(root, text="Open", command=BDOpen)
      root.BDB1.grid(row=10, column=0, sticky=W, padx=2, pady=2)
      root.BDB2 = Button(root, text="Close", command=BDClose)
      root.BDB2.grid(row=10, column=1, sticky=W, padx=2, pady=2)

      ##Balance Zeroing
      root.BZL1=Label(root, text="Zero Balance" )
      root.BZL1.grid(row=11, column=0, sticky=W)
      root.BZB1=Button(root, text="Zero", command=BZero)
      root.BZB1.grid(row=12, column=0, sticky=W, padx=2, pady=2)

      root.BZL2=Label(root, text="Current Balance Reading")
      root.BZL2.grid(row=13,column=0,sticky=W)
      root.BZL3=Label(root, textvariable=readBalance)
      root.BZL3.pack()
      root.BZL3.grid(row=13,column=1,sticky=W)

      root.BZL4=Button(root, text="X Motor")
      root.BZL4.grid(row=14,column=0,sticky=W)
      root.BZL5=Label(root, textvariable=getXMotorPosition)
      root.BZL5.pack()
      root.BZL5.grid(row=14,column=1,sticky=W)

      root.BZL6=Button(root, text="Y Motor")
      root.BZL6.grid(row=14,column=2,sticky=W)
      root.BZL7=Label(root, textvariable=getYMotorPosition)
      root.BZL7.pack()
      root.BZL7.grid(row=14,column=3,sticky=W)

      root.M1B3 = Button(root, text="Open Gripper", command=openGripper)
      root.M1B3.grid(row=16, column=0, padx=2, pady=2)
      root.M1B4 = Button(root, text="Close Gripper", command=closeGripper)
      root.M1B4.grid(row=16, column=1, padx=2, pady=2)

      root.M1B5 = Button(root, text="Update Values", command=printValues)
      root.M1B5.grid(row=17,column=2,padx=2,pady=2)

      self.update_windows()

      root.mainloop()

   ##-----------------------------------------------------------------
   def getit(self) :
      print "getit: variable passed is", self.str_1.get()

   def update_windows(self):
      xpos=getXMotorPosition()
      ypos=getYMotorPosition()
      root.BZL5.configure(text=xpos)
      root.BZL5.pack()
      root.BZL7.configure(text=ypos)
      root.BZL7.pack()
      frame=cv.QueryFrame(capture)
      frame2=cv.QueryFrame(capture2)
      cv.ShowImage("Overview",frame)
      cv.ShowImage("View from Arm",frame2)
      print "X: ",xpos, "Y: ", ypos
      root.after(1000, self.update_windows())

##===============================================================

if "__main__" == __name__  :
   ET=Start()
