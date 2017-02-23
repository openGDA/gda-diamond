from time import sleep
from gda.device.scannable import PseudoDevice
import math


#the parameters d, off (offset), are from BESTEC calibration, all in micron.
#The "sign" parameter is positive if the direction of the encoder counts is the same as the EPICS coordinates.
#the conversion between beamline coordinate and counts is: mm = counts/10000*sign
#The offset must be expressed in beamline coordinates (while in the BESTEC report is expressed in counts).

class slitslMotorClass(PseudoDevice):
    def __init__(self,name,units,d,off, encoderSign, realMotor):
        self.setName(name);
        self.setInputNames([units])
        self.setOutputFormat(['%3.2f'])
        self.setExtraNames([])
        self.units = units
        self.d =  d # from BESTEC fitting (in micron)
        self.off = off # from BESTEC fitting (in micron of beamline coordinate)
        self.encoderSign = encoderSign
        self.realMotor = realMotor
        self.slitWidth = 0.0
        self.L = 46e3 #slits leverage [micron]
        self.setLevel(6)
        self.iambusy = False
        
    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def getPosition(self): 
        xx = self.realMotor.getPosition()
        U = self.encoderSign*(xx*1000-self.off)
        #print xx
        #print U
        #print self.d + 2*self.L*(1 - math.sqrt(1 - math.pow((U/self.L),2) ) )
        self.slitWidth = self.d + 2*self.L*(1 - math.sqrt(1 - math.pow((U/self.L),2) ) )
        return self.slitWidth

    def asynchronousMoveTo(self, newPosition):
        
        #self.slitWidth = newPosition
        U =  (self.off + self.encoderSign*self.L*math.sqrt(1 - math.pow( (1 - (newPosition-self.d)/(2*self.L) ),2)))/1000
        print 's4x position =',U,' mm'
        self.realMotor.asynchronousMoveTo(U)
        sleep(0.1)
        self.slitWidth = newPosition
        return 

    def isBusy(self):
        return self.realMotor.isBusy()