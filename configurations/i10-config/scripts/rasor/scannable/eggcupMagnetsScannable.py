"""
Scannable for converting Field in mT into eggcup magnet position in mm

David Burn
"""

from gda.device.scannable import PseudoDevice
import math

class eggcupMagnetsScannable(PseudoDevice):
    def __init__(self,name, emecy1, emecy2, A, t, y0):
        self.name=name
        self.setInputNames([name])
        self.setExtraNames(["emecy1", "emecy2"]);
        self.iambusy = 0
        self.currentPosition = 0
        
        self.emecy1 = emecy1
        self.emecy2 = emecy2

        # H = A x e(x/t) +     exponential decay
        # -t1, A1, y0
        self.calibration = [-t, A, y0]   
        #self.calibration = [-8.16, 177.0, 18.1]   # for big magnets 
        
        #self.calibration = [-8.60797, 818.59841, 58.41583]   # for medium magnets plus three small
        #self.calibration = [-6.8507, 331.67598, 47.64438]   # for medium magnets 
        #self.calibration = [-6.54058, 10.32319, 2.69]   # for tiny magnets

    def rawGetPosition(self):
        self.currentPosition = self.emecy2()
        return [self.position2field(self.currentPosition), self.emecy1(), self.emecy2()]



    def rawAsynchronousMoveTo(self, field):
        #move both magnets, return when both magnets are in new position.
        self.iambusy = 1
        self.currentPosition = self.field2position(field)
        self.emecy1.a(-self.currentPosition)
        self.emecy2.a(self.currentPosition)
        self.emecy1.waitWhileBusy()
        self.emecy2.waitWhileBusy()
        self.iambusy = 0
    
    
    def field2position(self,field):
        # H = A x e(x/t)    exponential decay
        position = self.calibration[0]*math.log((field - self.calibration[2])/self.calibration[1]) 
        return position
    
    def position2field(self,position):
        field = self.calibration[1]*math.exp(position/self.calibration[0]) + self.calibration[2]
        #if self.emecpitch() < 0.0:
        #    field = - field
        return field
    
    def rawIsBusy(self):
        return self.iambusy


