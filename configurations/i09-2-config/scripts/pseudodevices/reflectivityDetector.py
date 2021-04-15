'''
Created on 27 Nov 2013

@author: fy65
'''
#from gda.device.scannable.scannablegroup import ScannableGroup
from gda.factory import Finder

SAMPLEDETECTORDISTANCE=163.6731 # mm smpmz = 2.86
SLITXOFFSET=10.85 #mm 1 mm slit
#SLITXOFFSET=-11.7 #mm 2.7 mm slit
SLITZOFFSET=2.75 #mm
TTHOFFSET=3.0 #-2.9131 #degree
SINEBARLENGTH=12.5 #mm
#XTDIRECTBEAM=-155.265 #mm -136.847
XTDIRECTBEAM=-135.878 #mm -136.847

from gdascripts.constants import pi
from math import sin, cos, tan

XTOFFSET=-SAMPLEDETECTORDISTANCE*sin(TTHOFFSET*pi/180)+XTDIRECTBEAM

#from epics.motor.positionCompareMotorWithLimitsClass import PositionCompareMotorWithLimitsClass
from gda.device.scannable import ScannableMotionBase

#rfdxt=PositionCompareMotorWithLimitsClass("rfdxt", "BL09I-MO-RFD-01:X.VAL","BL09I-MO-RFD-01:X.RBV", "BL09I-MO-RFD-01:X.STOP",0.00002, "mm","%.6f",1,-213.5)
#rfdxr=PositionCompareMotorWithLimitsClass("rfdxr", "BL09I-MO-RFD-01:TTHX.VAL","BL09I-MO-RFD-01:TTHX.RBV", "BL09I-MO-RFD-01:TTHX.STOP",0.00010, "mm","%.6f",6.5,-6.5)

class ReflectivityDetectorMotor(ScannableMotionBase):
    '''
    classdocs
    '''
    def __init__(self, name, xt, xr, unitstring, formatstring):
        '''
        Constructor
        '''
        self.setName(name);
        self.setInputNames([name])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(3)
        self.xt=xt
        self.xr=xr
        self.tth=0.0
        
    def atScanStart(self):
        pass
    
    def rawGetPosition(self):
        return self.tth
    
    def rawAsynchronousMoveTo(self,new_position):
        self.tth=float(new_position)
        angle = (float(new_position) - TTHOFFSET) * pi / 180
        Xtval=XTOFFSET-(SAMPLEDETECTORDISTANCE-SLITZOFFSET)*tan(angle)+SLITXOFFSET/cos(angle)-SLITXOFFSET
        Xrval=-SINEBARLENGTH*sin(angle)
#        if Xtval<self.xt.getLowerGdaLimits() or Xtval > self.xt.getUpperGdaLimits():
#            raise ValueError(str(self.xt.getName()) + str(" is outside limits"))
#        if Xrval<self.xr.getLowerGdaLimits() or Xrval > self.xr.getUpperGdaLimits():
#            raise ValueError(str(self.xr.getName()) + str(" is outside limits"))
        self.xt.asynchronousMoveTo(Xtval)
        self.xr.asynchronousMoveTo(Xrval)
    
    def isBusy(self):
        return (self.xt.isBusy() or self.xr.isBusy())
    
    def atScanEnd(self):
        pass
            
    def stop(self):
        self.xt.stop()
        self.xr.stop()

    def toString(self):
        return self.name + " : " + str(self.getPosition())
       
rfdtth=ReflectivityDetectorMotor("rfdtth",rfdxt,rfdxr, "degree", "%.4f")  # @UndefinedVariable
# rfd=Finder.find('rfdtth')
# rfd.addGroupMember(rfdtth)