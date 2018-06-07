'''
Created on 31 Jul 2017

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from math import cos, sin

class CoupledSampleStageMotion(ScannableMotionBase):
    '''
    classdocs
    '''


    def __init__(self, name, sax, say, sapolar):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.sax=sax
        self.say=say
        self.sapolar=sapolar
        
    def getPosition(self):
        if self.getName()=="sapara":
            return self.getPositionFromSapara()
        elif self.getName()=="saperp":
            return self.getPositionFromSaperp()
        else:
            raise Exception("Scannable name must be 'sapara' or 'saperp'")
        
    def asynchronousMoveTo(self, newpos):
        sapolar = float(self.sapolar.getPosition())
        if self.getName()=="sapara":
            position_from_saperp = self.getPositionFromSaperp()
            sax=position_from_saperp*cos(sapolar)-float(newpos)*sin(sapolar)
            say=position_from_saperp*sin(sapolar)+float(newpos)*cos(sapolar)
        elif self.getName()=="saperp":
            position_from_sapara = self.getPositionFromSapara()
            sax=float(newpos)*cos(sapolar)-position_from_sapara*sin(sapolar)
            say=float(newpos)*sin(sapolar)+position_from_sapara*cos(sapolar)
        self.sax.asynchronousMoveTo(sax)
        self.say.asynchronousMoveTo(say)
        
    def isBusy(self):
        return self.sax.isBusy() or self.say.isBusy()
            
    def getPositionFromSaperp(self):
        sapolar = float(self.sapolar.getPosition())
        return float(self.say.getPosition())*sin(sapolar)+float(self.sax.getPosition())*cos(sapolar)
    
    def getPositionFromSapara(self):
        sapolar = float(self.sapolar.getPosition())
        return float(self.say.getPosition())*cos(sapolar)-float(self.sax.getPosition())*sin(sapolar)
    

