__author__ = 'clipo'
import numpy as np
import matplotlib.pyplot as plt
from pylab import *
matplotlib.rc('axes',grid=True)
rcParams['axes.formatter.limits']=(0,0)
import DataReadWrite

#print rcParams.keys()
dbName="TEST"
dbDir="c:/Users/Archy/Dropbox/Rehydroxylation/"

data= np.array([])
value=DataReadWrite.openDatabase(dbDir,dbName)
runID=1
sampleLocation=1
count =0

data=DataReadWrite.getPreFireWeightOverTime(runID,sampleLocation)

print data
if data is False:
   print "no data"
   exit(1)

x=[]
y=[]
weight=0.0
maximumVal=0
minimumVal=100000

#print data
for row in data:
   count +=1
   weight=float(row)
   print weight
   if weight>maximumVal:
      maximumVal=weight
   if weight <minimumVal:
      minimumVal=weight
   plt.scatter(count,weight)
plt.ticklabel_format(style='plain')
plt.axis([0,count,minimumVal,maximumVal])
plt.axis(set_scientific=False)
plt.axis(ticklabel_format='plain', axis='y')
ax=gca()
ax.ticklabel_format(set_scientific=False)
ax.yaxis.major.formatter.set_scientific(False)
ax.xaxis.major.formatter.set_scientific(False)
ax.ticklabel_format(style='plain', axis='y')
ax.ticklabel_format(style='plain', axis='y', set_scientific=False)
ax.yaxis.major.formatter.set_powerlimits((-2999,10000))


plt.show()