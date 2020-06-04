'''
Created on 7 Feb 2017

@author: wvx67826

Th for area detector
'''

from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import ScannableUtils
from gdaserver import tth
import scisoftpy as dnp


class TthArea(ScannableMotionBase):
    def __init__(self, name):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([]);
        self.setOutputFormat(["%5.5g"])
        self.currentposition = 0.0
        self.twoThetaOff = 0.0
        self.iambusy=0

    def rawIsBusy(self):
        return self.iambusy or tth.isBusy()
    
    def asynchronousMoveTo(self, twoTheta):
        self.iambusy = 1
        self.currentposition = twoTheta
        tempTth = 90.0 - twoTheta + self.twoThetaOff
        tth.asynchronousMoveTo(tempTth)
        self.iambusy = 0
        
    def rawGetPosition(self):
        self.iambusy =1
        self.currentposition = 90-tth.getPosition() + self.twoThetaOff
        self.iambusy = 0
        return self.currentposition
tthArea = TthArea("tthArea")
        
