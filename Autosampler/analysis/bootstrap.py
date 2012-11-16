__author__ = 'clipo'



import random
import scipy.stats as stat
import quantile #http://adorio-research.org/wordpress/?p=125

def mean(X):
   return sum(X)/ float(len(X))


def age_calculate(slope,slopeError,postfireWeight,postfireWeightStdDev,prefireWeight,prefireWeightStdDev):

   #print "Prefire weight: ", weightAverage, "+/- ", weightStdDev

   ## difference is the pre fire weight  minus intercept (post fire weight)
   diffWeight = prefireWeight - postfireWeight
   ## now divide weight by the slope
   dateQuarterPower = diffWeight/slope
   ## now exp to the 4 power
   dateMinutes = pow(abs(dateQuarterPower),4)
   ## 60 minutes per hour
   dateHours = dateMinutes/60
   ## 24 hours to day
   dateDays = dateHours/24
   ## 365 hours/year
   dateYears=dateDays/365
   ## AD/BC - subtract from this year
   ## initialize the maxDate variable with a date (today)
   ADBC=""

   mdate=date.today()

   maxDateYear=mdate.year
   ## now measure the difference-- the year at the end of the measurement minus number of years in calculations
   dateCalendar=maxDateYear - dateYears
   if dateCalendar <0:
      ADBC ="BC"
   else:
      ADBC="AD"
   if postfireWeightStdDev is None:
      postfireWeightStdDev=0.0
   dateErrorMinutes=pow(postfireWeightStdDev,4)
   dateErrorHours=dateErrorMinutes/60
   dateErrorDays=dateErrorHours/24
   dateErrorYears=dateErrorDays/365

   # now calculate error terms
   # this consists of the prefire weight error, the postfire weight error, the slope error,
   # where prefire-postfire/slope
   # so date * sqrt( ( prefireError/prefire)^2 + (postfireError/postfire)^2 + *slopeError/slope)^2)
   total_error = dateYears * sqrt( pow(prefireWeightStdDev/prefireWeight,2)+ pow(postfireWeightStdDev/postfireWeight,2)+pow(slopeError/slope, 2))

   return (dateYears,dateCalendar,ADBC,dateErrorYears)

def bootstrap(sample, samplesize = None, nsamples = 1000, statfunc = mean, sigma= None, conf = 0.95):
   """
    Arguments:
       sample - input sample of values
       nsamples - number of samples to generate
       samplesize - sample size of each generated sample
       statfunc- statistical function to apply to each generated sample.
       sigma - if not None, resmple valuew will have an added normal component
             with zero mean and sd sigma.

    Returns bootstrap sample of statistic(computed by statfunc), bias and confidence interal.
    """
   if samplesize is None:
      samplesize=len(sample)
   print "input sample = ",  sample
   n = len(sample)
   X = []
   for i in range(nsamples):
      print "i = ",  i,
      resample = [random.choice(sample) for i in range(n)]
      # resample = [sample[j] for j in stat.randint.rvs(0, n-1,\
      #	size=samplesize)]  # older version.
      if sigma and sigma > 0:  # apply smoothing?
         nnormals = scipy.normal.rvs(n, 0, sigma)
         resample = [x + z for x,z in zip (resample, nnormals)]
      x = statfunc(resample)
      X.append(x)
   bias = sum(X)/float(n) - statfunc(sample)

   plower  = (1-conf)/2.0
   pupper  = 1 -plower
   symconf = (quantile(X, plower), pupper(X, pupper))
   return X, bias,symconf
