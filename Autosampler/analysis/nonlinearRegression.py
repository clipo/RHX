__author__ = 'carllipo'

import numpy as np
from scipy.optimize import leastsq


def function(a, time):
    return a * np.power(time, 0.25)


def residuals(p, y, x):
    err = y - function(x, p)
    return err


def nlinRegression(timeArray, weightChangeArray, minval, maxval):
    nlx = []
    nly = []
    count = 0
    a_guess = 0.005

    for var in timeArray:
        if minval < var < maxval:
            nlx.append(var)
            nly.append(weightChangeArray[count])
        count += 1

    kd, cov, infodict, mesg, ier = leastsq(residuals,
                                           a_guess, args=(timeArray, weightChangeArray), full_output=True)

    return kd[0]


timeArray = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
weightChangeArray = [0, .5, 1, 1.3, 3, 5, 7, 8, 10, 12, 12.5, 13.5, 14]
minval = -1
maxval = 16

alpha = nlinRegression(timeArray, weightChangeArray, minval, maxval)
print alpha

