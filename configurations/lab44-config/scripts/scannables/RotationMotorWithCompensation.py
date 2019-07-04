'''
Created on 29 Jun 2016

@author: fy65
'''
from math import pi, sin

#Motor X compensation parameters
XP0=-34.7603/1000
XP1=-253.459/1000
XP2=0.790996
XP3=-88.1243

#Motor Y compensation parameters
YP0=96.76121/1000
YP1=146.7816/1000
YP2=1.280899
YP3=-90.3257


from gda.device.scannable import ScannableMotionBase

class CompensedMotionScannable(ScannableMotionBase):
    '''
    classdocs
    '''


    def __init__(self, name, mainmotor, xmotor, ymotor):
        '''
        Constructor
        '''
        self.setName(name)
        self.motorToBeMoved=mainmotor
        self.xmotor=xmotor
        self.ymotor=ymotor
        
    def rawAsynchronousMoveTo(self, position):
        
        currentPos = float(self.motorToBeMoved.getPosition())
        
        xcur=float(self.xmotor.getPosition())
        ycur=float(self.ymotor.getPosition())
        
        xdiffCurrent=self.compensationValue(XP0, XP1, XP2, XP3, float(currentPos))
        ydiffCurrent=self.compensationValue(YP0, YP1, YP2, YP3, float(currentPos))
        
        xdiffNew=self.compensationValue(XP0, XP1, XP2, XP3, float(position))
        ydiffNew=self.compensationValue(YP0, YP1, YP2, YP3, float(position))
        
        xdiff = xdiffNew-xdiffCurrent
        ydiff = ydiffNew-ydiffCurrent
        
        print xcur,xdiff, ycur,ydiff
        self.motorToBeMoved.asynchronousMoveTo(position)
        self.xmotor.asynchronousMoveTo(xcur+xdiff)
        self.ymotor.asynchronousMoveTo(ycur+ydiff)
        
    def compensationValue(self, P0, P1, P2, P3, position):
        return P0+P1*sin(P2*position*pi/180+P3)
    
    def getPosition(self):
        return self.motorToBeMoved.getPosition()
    
    def rawIsBusy(self):
        return self.motorToBeMoved.isBusy() or self.xmotor.isBusy() or self.ymotor.isBusy()
    