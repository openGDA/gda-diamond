from java import lang
from time import sleep
from gda.device.scannable import PseudoDevice
import math

#the parameters d, off (offset), are from BESTEC calibration, all in micron.
#The "sign" parameter is positive if the direction of the encoder counts is the same as the EPICS coordinates.
#the conversion between beamline coordinate and counts is: mm = counts/10000*sign
#The offset must be expressed in counts as in the BESTEC report.
        
class slitsMotorClassV2(PseudoDevice):
    #If testMode==1 the motor does not move
    def __init__(self,name,units,d,off, encoderSign, realMotor, testMode):
        self.setName(name);
        self.setInputNames([units])
        self.setOutputFormat(['%3.2f'])
        self.setExtraNames([])
        self.units = units
        self.d =  d # from BESTEC fitting (in micron)
        self.off = off # from BESTEC fitting (in counts)
        self.encoderSign = encoderSign
        self.realMotor = realMotor
        self.testMode = testMode
        self.slitWidth = 0.0
        self.L = 46e3 #slits leverage [micron]
        self.scale = 0.1 #micrometer/count
        self.setLevel(6)
        self.iambusy = False
        
       

    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def getPosition(self): 
        #slit width in microns
        S = self.realMotor.getPosition() #motor position in mm (beamline coordinate)
        U = self.encoderSign*S*1000-self.scale*self.off #convert to microns
        #print xx
        #print U
        self.slitWidth = self.d + 2*self.L*(1 - math.sqrt(1 - math.pow((U/self.L),2) ) )
        return self.slitWidth

    def asynchronousMoveTo(self, newPosition):
        #newPosition = new slit width in microns
        #self.slitWidth = newPosition 
        #U =  (self.off + self.encoderSign*self.L*math.sqrt(1 - math.pow( (1 - (newPosition-self.d)/(2*self.L) ),2)))/1000
        #S = actuator position in beamline coordinates with respect to the encoder reference mark
        S = self.encoderSign*(self.scale*self.off +self.L*math.sqrt(1 - math.pow( (1 - (newPosition-self.d)/(2*self.L) ),2)))/1000
        print self.realMotor.name, ' position =',S,' mm'
        if not(self.testMode):
            #self.realMotor.asynchronousMoveTo(S*1000-self.off)
            self.realMotor.asynchronousMoveTo(S)
        sleep(0.2)
        self.slitWidth = newPosition
        return 

    def isBusy(self):
        return self.realMotor.isBusy()