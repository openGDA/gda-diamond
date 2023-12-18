'''
Created on 27 Nov 2013

@author: fy65
'''

SMPMPOLAR0NEG=-88.995 # degree
SMPMPOLAR0POS=90.22 # degree
SMPMX0=4.71 #mm
SMPMZ0=2.83 #mm 
SMPMXOFFSET=-0.128 #mm positive when sample is too thin
SMPMZOFFSET=0 #mm positive if the sample is on the upstream side of the polar axis when facing away from the analyser

if smpmpolar()<0:
    SMPMPOLAR0=SMPMPOLAR0NEG
    sign=-1
else:
    SMPMPOLAR0=SMPMPOLAR0POS
    sign=1
     

from gdascripts.constants import pi
from math import sin, cos, atan, asin, sqrt
from gda.device.scannable import ScannableMotionBase

xzoffsetradius=sqrt(SMPMXOFFSET**2+SMPMZOFFSET**2)

if SMPMXOFFSET==0 and SMPMZOFFSET==0:
    xzoffsetanglerad=0
else:
    xzoffsetanglerad=abs(asin(SMPMZOFFSET/xzoffsetradius))
    if SMPMXOFFSET<0 and SMPMZOFFSET>0:
        xzoffsetanglerad=xzoffsetanglerad+0.5*pi
    if SMPMXOFFSET<0 and SMPMZOFFSET<=0:
        xzoffsetanglerad=xzoffsetanglerad+pi
    if SMPMXOFFSET>=0 and SMPMZOFFSET<0:
        xzoffsetanglerad=xzoffsetanglerad+1.5*pi

class SmpmthRotation(ScannableMotionBase):
    '''
    classdocs
    '''
    def __init__(self, name, smpmx, smpmz, smpmpolar, unitstring, formatstring):
        '''
        Constructor
        '''
        self.setName(name);
        self.setInputNames([name])
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(3)
        self.smpmx=smpmx
        self.smpmz=smpmz
        self.smpmpolar=smpmpolar
        self.smpmth=0.0
        
    def rawGetPosition(self):
        return self.smpmth
    
    def rawAsynchronousMoveTo(self,new_position):
        anglerad = (float(new_position)) * pi / 180
        samplepolar=SMPMPOLAR0+float(new_position)
        samplex=SMPMX0+sign*xzoffsetradius*cos(anglerad+xzoffsetanglerad)
        samplez=SMPMZ0+sign*xzoffsetradius*sin(anglerad+xzoffsetanglerad)
        self.smpmpolar.asynchronousMoveTo(samplepolar)
        self.smpmx.asynchronousMoveTo(samplex)
        self.smpmz.asynchronousMoveTo(samplez)
        self.smpmth=float(new_position)
    
    def isBusy(self):
        return (self.smpmx.isBusy() or self.smpmz.isBusy() or self.smpmpolar.isBusy())
    
    def stop(self):
        self.smpmx.stop()
        self.smpmz.stop()
        self.smpmpolar.stop()

    def toString(self):
        return self.name + " : " + str(self.getPosition())
       
smpmth=SmpmthRotation("smpmth",smpmx,smpmz, smpmpolar,"degree", "%.4f")  # @UndefinedVariable