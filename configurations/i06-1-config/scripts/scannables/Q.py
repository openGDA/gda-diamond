'''
Created on 2 Feb 2017

@author: wvx67826


Quick hacK for fix Q scan

2.0 changed scannable to take Q rather than having to hard code in d spacing, also added areaDector option where it will 
allow user to choose to run fixQ upside down. I should also readback the current Q position.

to run this marco type :

Q = Q("Q", True)

type: pos Q (new Q)

to get to new Q position

type: Q

to return current Q position
'''


from gda.device.scannable import ScannableBase
import scisoftpy as dnp

class Q(ScannableBase):
    def __init__(self, name, tth=dd2th, th=ddth, pgm_energy=pgmenergy, areaDetector = False):  # @UndefinedVariable
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([]);
        self.setOutputFormat(["%5.5g"])
        self.currentposition = 0.0
        self.thetaOff = 0.0
        self.tth=tth
        self.th=th
        self.energy=pgm_energy
        if areaDetector:
            self.twoThOff = 90.0
            self.twoThSign = -1.0
        else:
            self.twoThOff = 0.0
            self.twoThSign = 1.0
        

    def isBusy(self):
        return self.tth.isBusy() or self.th.isBusy()
    
    def asynchronousMoveTo(self, Q):
        self.currentposition = Q
        wlen = self.getWaveLenght()
        #theta = 180.0*dnp.arcsin(wlen/2.0/self.currentposition)/dnp.pi
        theta = 180.0/dnp.pi*dnp.arcsin(self.currentposition*wlen/4.0/dnp.pi) 
        if (theta>-0.01 and theta <80):
            twoTheta = self.twoThOff + 2.0*theta*self.twoThSign 
            self.tth.asynchronousMoveTo(twoTheta)
            self.th.asynchronousMoveTo(2.0*self.twoThOff+self.twoThSign*theta+self.thetaOff)
        else:
            print "Q is out of range"
        
    def rawGetPosition(self):
        wlen = self.getWaveLenght()
#        twoTheta = self.twoThOff + 2.0*theta*self.twoThSign
        theta = self.twoThSign*(float(self.tth.getPosition())- self.twoThOff)/2.0
        self.currentposition = float(4.0*dnp.pi/wlen*dnp.sin(theta*dnp.pi/180))
        return self.currentposition
    
    def getWaveLenght(self):
        return 12400.0/(float(self.energy.getPosition()))
        
q=Q("q", tth=dd2th, th=ddth, pgm_energy=pgmenergy, areaDetector = False)        # @UndefinedVariable
