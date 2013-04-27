__author__ = 'clipo'

from lmfit import minimize, Parameters, Parameter, report_errors
import numpy as np
import pprint

# create data to be fitted

x = np.array([0.1, 0.6, 1.6, 2.6, 3.6, 4.6, 5.6, 6.6, 7.6, 9.6, 11.6, 13.6, 15.6, 17.6, 19.6, 21.6, 23.6, 25.6, 27.6, 29.6, 31.6, 33.6, 35.6, 37.6,39.6,41.6,43.6,45.6,47.6])

data = np.array([0.000000, 0.251526, 0.522766, 0.725586, 0.889343, 1.027466, 1.146546, 1.250366, 1.342468, 1.501099, 1.635498, 1.752686, 1.858277, 1.954102, 2.042725, 2.107483, 2.150269, 2.191284, 2.231079, 2.270691, 2.310181, 2.348999, 2.388245, 2.427063, 2.464722, 2.502259, 2.540772, 2.578491, 2.616883])

# define objective function: returns the array to be minimized

def fcn2min(params, x, data):
    """ model decaying sine wave, subtract data"""
    alpha = params['alpha'].value
    power = params['power'].value
    #model = pow((data/alpha),power)
    model = alpha * pow( x, power)
    return model - x

def quarterPowerFunction(params, x,  data):
    alpha = params['alpha'].value
    model = alpha * pow( x, 0.25)
    return model - data


# create a set of Parameters
params1 = Parameters()
params1.add('alpha', value= 1,  min=0)
#params.add('power', value= 1)

# do fit, here with leastsq model
result1 = minimize(quarterPowerFunction, params1, args=(x, data))


params2 = Parameters()
params2.add('alpha', value= 1,  min=0)
params2.add('power', value= 1)
result2 = minimize(fcn2min, params2, args=(x, data))

# calculate final result
final1 = data + result1.residual

final2 = data + result2.residual

# write error report
report_errors(params1)

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(params1)
print params1.get('alpha')
p=params1.get('alpha')
print "standard error ", p.stderr

total= np.sum(result1.residual)

print "sum of residuals: ", total
#print "xtol: ", result1.xtol
print "reduced chi-square: ", result1.redchi
#print "asteval", result1.asteval
print "message:", result1.message
print "ier:", result1.ier
print "chisqr:", result1.chisqr
print "redchi:", result1.redchi
pp.pprint(result1)

report_errors(params2)
pp.pprint(params2)
print params2.get('alpha')
p=params2.get('alpha')
print p.stderr


# try to plot results
try:
    import pylab
    pylab.plot(x, data, 'k+')
    pylab.plot(x, final1, 'r')
    pylab.plot(x, final2, 'b')
    pylab.show()
except:
    pass