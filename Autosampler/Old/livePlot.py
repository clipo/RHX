
import time
import plotTest
import math
import random

plotGraph= plotTest.Viewer()


# Pop up the windows for the two objects
plotGraph.configure_traits()

count =1

while count < 1000:
   count +=1
   var = random.random()*100
   #print var
   plotGraph.add_data_point(5.23231)

   time.sleep(.2)