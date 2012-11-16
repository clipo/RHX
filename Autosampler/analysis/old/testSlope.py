__author__ = 'clipo'


import matplotlib.pyplot as plt
from numpy import *
from scipy import stats

def graph_slope(x,y,window):
   #window = [-1, 0, 0,0,0,0,0,0, 1]
   #slope = convolve(y, window, mode='same') / convolve(x, window, mode='same')
   # a[start,end,step]

   xs = zeros(alen(x))
   ys = zeros(alen(x))
   slopeArray=zeros(alen(x))
   interceptArray=zeros(alen(x))
   r_valueArray=zeros(alen(x))
   p_valueArray=zeros(alen(x))
   std_errArray=zeros(alen(x))
   slope=0.0
   intercept=0.0
   r_value=0.0
   p_value=0.0
   std_err=0.0
   num=1

   while num < alen(x):
      print "Num: ", num
      if num<window:
         slopeArray[num]=0.0
         interceptArray[num]=0.0
         r_valueArray[num]=0.0
         p_valueArray[num]=0.0
         std_errArray[num]=0.0
         #print "slope: 0"
      else:
         xs=x[num-window:num:1]
         ys=y[num-window:num:1]
         #print xs
         slope, intercept, r_value, p_value, std_err = stats.linregress(xs,ys)
         print "slope:", slope, " -- ", num

         slopeArray[num]=slope
         interceptArray[num]=slope
         r_valueArray[num]=slope
         p_valueArray[num]=slope
         std_errArray[num]=slope
         print "Slope Array: ", alen(slopeArray)
         print slopeArray
      num+=1


   print slopeArray
   print "LENGTH: ", alen(slopeArray)
   return (slopeArray,interceptArray,r_valueArray,p_valueArray,std_errArray)



xArray=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30]

yArray=[1,2,3,4,5,6,7,8,3,5,3,3,1,3,4,1,22,18,19,20,21,22,1,4,11,26,27,28,29,30]
aslopeArray=zeros(alen(xArray))
ainterceptArray=zeros(alen(xArray))
ar_valueArray=zeros(alen(xArray))
ap_valueArray=zeros(alen(xArray))
astd_errArray=zeros(alen(xArray))

(aslopeArray,ainterceptArray,ar_valueArray,ap_valueArray,astd_errArray)=graph_slope(xArray,yArray,3)
#print aslopeArray
print alen(aslopeArray)
print alen(xArray)
plt.plot(xArray, yArray, '.')
plt.plot(xArray,aslopeArray,'-')
plt.plot(xArray,ainterceptArray,'x')
plt.plot(xArray,ap_valueArray,'+')
##plt.plot(x,slopeArray,'-')

plt.show()
