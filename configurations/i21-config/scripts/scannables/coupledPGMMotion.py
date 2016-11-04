'''
Created on 18 Jul 2016

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caget
from gdascripts.constants import clight, hPlanck, eV, pi
from scisoftpy.jython.jymaths import arcsin, arccos, sqrt, cos, sin

print "Running coupledPGMotion..."
PV="BL21I-OP-PGM-01:ENERGY.RBV"
energyfrompgm=float(caget(PV))

class CoupledPGMMotion(ScannableMotionBase):
    '''
    classdocs
    '''

    def __init__(self, name, lineDensity1, pgmMirrorPitch1, pgmGratingPitch1):
        '''
        Constructor
        '''
        self.setName(name)
        self.lineDensity=lineDensity1
        self.mirrorPitch=pgmMirrorPitch1
        self.gratingPitch=pgmGratingPitch1
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%.5f"])
        
    def asynchronousMoveTo(self, cff):
        B=self.energy2wavelength(self.energy())*self.lineDensity/(1-cff*cff)
        self.alpha=arcsin(B+sqrt(1+B*B*cff*cff))
        self.beta=arccos(cff*cos(self.alpha))
        theta=(self.alpha+self.beta)/2
        
        #print self.alpha*180/pi, self.beta*180/pi, theta*180/pi
        self.mirrorPitch.asynchronousMoveTo(theta*180/pi)
        self.gratingPitch.asynchronousMoveTo(self.beta*180/pi)
    
    def getPosition(self):
        #return float(cos(self.beta)/cos(self.alpha))
        return float(cos(float(self.gratingPitch.getPosition())*pi/180)/cos((2*float(self.mirrorPitch.getPosition())-float(self.gratingPitch.getPosition()))*pi/180))
    
    def isBusy(self):
        return self.mirrorPitch.isBusy() or self.gratingPitch.isBusy()
    
    def energy2wavelength(self, energy):
        return hPlanck*clight/(energy*eV)
    
    def wavelength2energy(self, wavelength):
        return hPlanck*clight/(wavelength*eV)
    
    def energy(self):
        wavelength=(-sin(float(self.gratingPitch.getPosition())*pi/180)+sin((2*float(self.mirrorPitch.getPosition())-float(self.gratingPitch.getPosition()))*pi/180))/self.lineDensity
        return float(self.wavelength2energy(wavelength))
    
class pgmEnergyScannable(ScannableMotionBase):
    '''
    classdocs
    '''

    def __init__(self, name, lineDensity1, pgmMirrorPitch1, pgmGratingPitch1):
        '''
        Constenergy3=BeamEnergy("energy3",idscannable, idgap, energycff3,lut="IDCalibrationTable.txt")  # @UndefinedVariablructor
        '''
        self.setName(name)
        self.mirrorPitch=pgmMirrorPitch1
        self.gratingPitch=pgmGratingPitch1
        self.lineDensity=lineDensity1
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%.5f"])
        
    def asynchronousMoveTo(self, energy):
        B=self.lineDensity*self.energy2wavelength(energy)/(1-self.cff()*self.cff())
        alpha=arcsin(B+sqrt(1+(B*B*self.cff()*self.cff())))
        beta=arccos(cos(alpha)*self.cff())
        theta=(alpha+beta)/2
        
        #print alpha*180/pi, beta*180/pi, theta*180/pienergy1
        self.mirrorPitch.asynchronousMoveTo(theta*180/pi)
        self.gratingPitch.asynchronousMoveTo(beta*180/pi)
        
    def getPosition(self):
        wavelength=(-sin(float(self.gratingPitch.getPosition())*pi/180)+sin((2*float(self.mirrorPitch.getPosition())-float(self.gratingPitch.getPosition()))*pi/180))/self.lineDensity
        return float(self.wavelength2energy(wavelength))
    
    def isBusy(self):
        return self.mirrorPitch.isBusy() or self.gratingPitch.isBusy()
    
    def energy2wavelength(self, energy):
        return hPlanck*clight/(energy*eV)
    
    def wavelength2energy(self, wavelength):
        return hPlanck*clight/(wavelength*eV)
    
    def cff(self):
        return float(cos(float(self.gratingPitch.getPosition())*pi/180)/cos((2*float(self.mirrorPitch.getPosition())-float(self.gratingPitch.getPosition()))*pi/180))
    
try:
    cff1
except:
    cff1=CoupledPGMMotion("cff1", 600*1000, pgmMirrorPitch, pgmGratingPitch)  # @UndefinedVariable
try:
    cff2
except:
    cff2=CoupledPGMMotion("cff2", 1000*1000, pgmMirrorPitch, pgmGratingPitch)  # @UndefinedVariable
try:
    cff3
except:
    cff3=CoupledPGMMotion("cff3", 2000*1000, pgmMirrorPitch, pgmGratingPitch)  # @UndefinedVariable

try:
    energycff1
except:
    energycff1=pgmEnergyScannable("energycff1", 600*1000, pgmMirrorPitch, pgmGratingPitch)  # @UndefinedVariable

try:
    energycff2
except:
    energycff2=pgmEnergyScannable("energycff2", 1000*1000, pgmMirrorPitch, pgmGratingPitch)  # @UndefinedVariable

try:
    energycff3
except:
    energycff3=pgmEnergyScannable("energycff3", 2000*1000, pgmMirrorPitch, pgmGratingPitch)  # @UndefinedVariable

try:
   energy1
except: 
    #energy1=BeamEnergy("energy1",idscannable, idgap, energycff1,lut="IDCalibrationTable.txt")  # @UndefinedVariable
    energy1=BeamEnergy("energy1",idscannable, idgap, energycff1)
try:
    energy2
except:
    #energy2=BeamEnergy("energy2",idscannable, idgap, energycff2,lut="IDCalibrationTable.txt")  # @UndefinedVariable
    energy2=BeamEnergy("energy2",idscannable, idgap, energycff2)  # @UndefinedVariable
try:
    energy3
except:
    #energy3=BeamEnergy("energy3",idscannable, idgap, energycff3,lut="IDCalibrationTable.txt")  # @UndefinedVariable
    energy3=BeamEnergy("energy3",idscannable, idgap, energycff3)  # @UndefinedVariable
print "Finished running coupledPGMotion"