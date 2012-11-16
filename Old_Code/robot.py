
# Import the Serial module
import serial;
import time;

EOL = "\r";
command = "";

# Set the SSC-32 port - "COM1:" for Windows, "/dev/ttyS0" for Linux
SSC32_Port = "COM5:";

BaseChan = 0;
BaseHome=1250;
BaseREnd=2250;
BaseLEnd=750;

ShoulderChan =1;
ShoulderHome=1500
ShoulderLEnd=2500;
ShoulderREnd=500;

ElbowChan=3;
ElbowHome=1500
ElbowREnd=2500
ElbowLEnd=500

WristChan=5;
WristHome=1500
WristREnd=2500
WristLEnd=500

GripperChan=7;
GripperHome=1250;
Open=750;
Close=2250;


#position of each of the servos -- from 1 to 8
Row1M=(0,1126,1566,1050,1470,676,1480)
# position varies from 2500 - 1200 by 100
Row1M0=(2500,2400,2300,2200,2100,2000,1900,1800,1700,1600,1500,1400,1300,1200)

#M3 -- up is 1050
#M3 -- down is 940


# Reads single characters until a CR is read
def Response (port):
   ich = "";
   resp = "";

   while (ich <> '\r'):
      ich = port.read(1);
      
      if (ich <> '\r'):
         resp = resp + ich;
   return resp;
      

# Converts a servo position in degrees to uS for the SSC-32
def To_Degrees (uS):
   result = 0;
   
   result = (uS - 1500) / 10;
   
   return result;

# Converts an SSC-32 servo position in uS to degrees
def To_uS (degrees):
   result = 0;
   
   result = (degrees * 10) + 1500;
   
   return result;

# Wait for a servo move to be completed
def Wait_for_Servos (port):
   ich = "";
   
   while (ich <> "."):
      Send_Command (port, "Q", True);
      
      ich = port.read(1);
   
   return;

# Send EOL to the SSC-32 to start a command executing
def Send_EOL (port):

   result = port.write(EOL);
   
   return result;

# Send a command to the SSC-32 with or without an EOL
def Send_Command (port, cmd, sendeol):
   
   result = port.write (cmd);
   
   if (sendeol):
      Send_EOL (port);
   
   return result;
   
#   Open the port at 115200 Bps - defaults to 8N1
ssc32 = serial.Serial(SSC32_Port, 115200);

def openGripper():
   print "now open gripper"
   #  Set the gripper to be open
   command = "#" + str(GripperChan) + " P" + str(Open);
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(2)

def closeGripper():
   print "now close gripper"
   #  Set the gripper to be open
   command = "#" + str(GripperChan) + " P" + str(Close);
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(2)


def gotoSamplePosition(row,position):

   print "now go to row:", row, " and position: ", position
   command = "#0 P" + str(Row1M0[position]) + " #1 P"+str(Row1M[1])+" T3000" 
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   command = " #2 P" + str(Row1M[2]) +" T3000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   command = " #3 P" + str(Row1M[3]) +" T3000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   command = " #4 P" + str(Row1M[4]) +" T3000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   command = " #5 P" + str(Row1M[5]) +" T3000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   command = " #6 P" + str(Row1M[6]) +" T3000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)

def samplePickUp():
   # first make sure gripper is open
   openGripper() 
   # now lower arm
   command = "#3 P940 T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(2)   
   # close gripper
   closeGripper()
   # raise arm to moving position
   command = "#3 P1050 T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(2)
   
   
def samplePutDown():    
   # now lower arm
   command = "#3 P940 T1000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   
   # close gripper
   openGripper()
   # raise arm to moving position
   command = "#3 P1050 T1000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)
   
   
def gotoBalance():
   command = "#3 P829 #1 P1500 T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   
   
   command = "#0 P750 T3000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   
   
   
def putSampleOnBalance():
   #move arm close and high
      # first make sure gripper is open
   # now lower arm
   command = "#3 P1500 #1 P829 T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   
   
   # now lower the arm
   command = "#3 P750 #1 P1280 T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)
   
   # OPEN gripper to release
   openGripper()
   # raise arm to moving position
   command = "#3 P1500 #3 P829 T3000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)

def pickUpSampleFromBalance():   
   print "open the gripper"
   openGripper()
   print "move to point above sample"
   command = "#3 P1500 #1 P829 T3000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)
   print "lower to sample"
   command = "#3 P750 #1 P1280 T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)   
   # close gripper
   closeGripper()
   command = "#3 P1500 #1 P829 T2000"
   print command
   Send_Command (ssc32, command, True);
   Wait_for_Servos (ssc32);
   time.sleep(1)

	
x=0
while x<12:
   gotoSamplePosition(1,x)
   samplePickUp()
   gotoBalance()
   putSampleOnBalance()
   pickUpSampleFromBalance()
   gotoSamplePosition(1,x)
   x=x+1
   
ssc32.close();
exit();


