# testing.py


import xyzRobot
import DataReadWrite

   
x=1
while x<4:
   xyzRobot.gotoSamplePosition(x)
   xyzRobot.samplePickUp(x)
   xyzRobot.putSampleOnBalance()
   xyzRobot.pickUpSampleFromBalance()
   xyzRobot.gotoSamplePosition(x)
   xyzRobot.samplePutDown(x)
   xyzRobot.goHome()
   x=x+1
   
xyzRobot.end()

exit();

