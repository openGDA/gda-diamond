'''
Created on 7 Feb 2017

@author: wvx67826

Th for area detector
'''

from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import ScannableUtils
from gdaserver import th
import scisoftpy as dnp


class ThArea(ScannableMotionBase):
    def __init__(self, name):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([]);
        self.setOutputFormat(["%5.5g"])
        self.currentposition = 0.0
        self.thetaOff = 0.0
        self.iambusy=0

    def isBusy(self):
        return self.iambusy or th.isBusy()
    
    def asynchronousMoveTo(self, theta):
        self.iambusy = 1
        self.currentposition = theta
        tempTh = 180.0 -theta +self.thetaOff 
        th.asynchronousMoveTo(tempTh)
        self.iambusy = 0
        
    def rawGetPosition(self):
        self.iambusy =1
        self.currentposition = 180-th.getPosition()+self.thetaOff
        self.iambusy = 0
        return self.currentposition
thArea = ThArea("thArea")
        
