'''
Created on 18 Jul 2016

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caget
from gdascripts.constants import clight, hPlanck, eV, pi
from scisoftpy.jython.jymaths import arcsin, arccos, sqrt, cos


PV="BL21I-OP-PGM-01:ENERGY.RBV"
energyfrompgm=float(caget(PV))

class CoupledPGMMotion(ScannableMotionBase):
    '''
    classdocs
    '''


    def __init__(self, name, vpgGroup, pgmMirrorPitch1, pgmGratingPitch1):
        '''
        Constructor
        '''
        self.setName(name)
        self.vpg=vpgGroup
        self.mirrorPitch=pgmMirrorPitch1
        self.gratingPitch=pgmGratingPitch1
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%.5f"])
        
    def asynchronousMoveTo(self, cff):
        B=self.wavelength()*self.vpg/(1-cff*cff)
        self.alpha=arcsin(B+sqrt(1+B*B*cff*cff))
        self.beta=arccos(cff*cos(self.alpha))
        theta=(self.alpha+self.beta)/2
#        print self.alpha*180/pi, self.beta*180/pi, theta*180/pi
        self.mirrorPitch.asynchronousMoveTo(theta*180/pi)
        self.gratingPitch.asynchronousMoveTo(self.beta*180/pi)
    
    def getPosition(self):
        return float(cos(self.beta)/cos(self.alpha))
    
    def isBusy(self):
        return self.mirrorPitch.isBusy() or self.gratingPitch.isBusy()
    
    def wavelength(self):
        return hPlanck*clight/(energyfrompgm*eV)
    
    
cff1=CoupledPGMMotion("cff1", 600*1000, pgmMirrorPitch, pgmGratingPitch)  # @UndefinedVariable
cff2=CoupledPGMMotion("cff2", 1000*1000, pgmMirrorPitch, pgmGratingPitch)  # @UndefinedVariable
cff3=CoupledPGMMotion("cff3", 2000*1000, pgmMirrorPitch, pgmGratingPitch)  # @UndefinedVariable