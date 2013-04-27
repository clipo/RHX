#!/usr/bin/env python


#Basic imports
import sys
from time import sleep
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetErrorCodes, PhidgetException
from Phidgets.Events.Events import AttachEventArgs, DetachEventArgs, ErrorEventArgs, EncoderPositionChangeEventArgs, InputChangeEventArgs
from Phidgets.Devices.Encoder import Encoder

# constants - set these to reflect which index the encoders are using
XENCODER = 1  # X axis encoder
YENCODER = 0  # Y axis encoder
ZENCODER = 2  # Z axis encoder

## set to 1 if you want to debug
DEBUG = 0


class Location:
    try:
        encoder = Encoder()
    except PhidgetException as e:
        print("Phidget Exception in creating the Location Object %i: %s" % (e.code, e.details))
        sys.exit()
    zPosition = 0

    def encoderError(self):
        try:
            source = self.encoder.device
        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))

    def getXPosition(self):
        try:
            X = self.encoder.getPosition(XENCODER)
        except PhidgetException as e:
            print("Phidget Error in Location:getPositions  %i: %s" % (e.code, e.details))
            return 0
        return X

    def getYPosition(self):
        try:
            Y = self.encoder.getPosition(YENCODER)
        except PhidgetException as e:
            print("Phidget Error in Location:getYPosition  %i: %s" % (e.code, e.details))
            return 0
        return Y

    def getZPosition(self):
        return self.zPosition
        #return self.encoder.getPosition(ZENCODER)

    def getPositions(self):
        try:
            X = self.encoder.getPosition(XENCODER)
            Y = self.encoder.getPosition(YENCODER)
        except PhidgetException as e:
            print("Phidget Error in Location:getPositions  %i: %s" % (e.code, e.details))
            return 0, 0
        return X, Y

    def setXZero(self):
        try:
            self.encoder.setPosition(XENCODER, 0)
        except PhidgetException as e:
            print("Phidget Error in Location:setXZero  %i: %s" % (e.code, e.details))
            return False
        return True

    def setYZero(self):
        try:
            self.encoder.setPosition(YENCODER, 0)
        except PhidgetException as e:
            print("Phidget Error in Location:setYPosition  %i: %s" % (e.code, e.details))
            return False
        return True

    def setZZero(self):
        self.zPosition = 0
        #self.encoder.setPosition(ZENCODER,0)
        return True

    def setXYZero(self):
        self.setXPosition(0)
        self.setYPosition(0)
        return True

    def close(self):
        try:
            self.encoder.closePhidget()
        except PhidgetException as e:
            print("Phidget Error in Location:close %i: %s" % (e.code, e.details))
            return False
        return True

    def setXPosition(self, location):
        if location is None or location < 0:
            location = 0
        try:
            self.encoder.setPosition(XENCODER, location)
        except PhidgetException as e:
            print("Phidget Error in Location:setXPosition  %i: %s" % (e.code, e.details))
            return False
        return True

    def setYPosition(self, location):
        if location is None or location < 0:
            location = 0
        try:
            self.encoder.setPosition(YENCODER, location)
        except PhidgetException as e:
            print("Phidget Error in Location:setYPosition  %i: %s" % (e.code, e.details))
            return False
        return True

    def setZPosition(self, location):
        if location is None or location < 0:
            location = 0
        self.zPosition = location
        #self.encoder.setPosition(ZENCODER,location)
        return True

    def bumpZ(self, bump):
        self.zPosition = self.zPosition + bump
        #self.encoder.setPosition(ZENCODER,(self.encoder.getPosition(ZENCODER)+bump))
        return True

    def setPositions(self, X, Y):
        if X is None or X < 0:
            X = 0
        if Y is None or Y < 0:
            Y = 0
        try:
            self.encoder.setPosition(XENCODER, X)
            self.encoder.setPosition(YENCODER, Y)
        except PhidgetException as e:
            print("Phidget Error in Location:setPositions  %i: %s" % (e.code, e.details))
            return False
        return True

    try:
        encoder.openPhidget()
    except PhidgetException as e:
        print("Phidget Error %i: %s" % (e.code, e.details))
    try:
        encoder.waitForAttach(10000)
    except PhidgetException as e:
        print("Phidget Error %i: %s" % (e.code, e.details))
        try:
            encoder.closePhidget()
        except PhidgetException as e:
            print("Phidget Error %i: %s" % (e.code, e.details))
            exit(1)
        exit(1)

    try:
        encoder.setEnabled(YENCODER, 1)
        encoder.setEnabled(XENCODER, 1)
        #encoder.setEnabled(ZENCODER,1)
        encoder.setPosition(XENCODER, 0)
        encoder.setPosition(YENCODER, 0)
        #encoder.setPosition(ZENCODER,0)
    except PhidgetException as e:
        print("Phidget Error in setting initial parameters for encoders %i: %s" % (e.code, e.details))
        sys.exit(1)

### main body

if DEBUG is 1:
    myLocation = Location()

    #while True:
    print "X Location: ", myLocation.getXPosition()
    print "Y Location: ", myLocation.getYPosition()
    print "Z Location: ", myLocation.getZPosition()
    ##   sleep(1)

    print "Set X Location to 100: "
    myLocation.setXPosition(100)

    print "Set Y Location to 1000: "
    myLocation.setYPosition(1000)

    print "Set Z Location to 1000: "
    myLocation.setZPosition(1000)

    print "X Location: ", myLocation.getXPosition()
    print "Y Location: ", myLocation.getYPosition()
    print "Z Location: ", myLocation.getYPosition()

    myLocation.close()
