from gda.epics import CAClient
from java import lang
from time import sleep
import math
from gda.device.scannable import PseudoDevice
from gda.device import DeviceException
from gda.device.motor import EpicsMotor

class TensileTester(PseudoDevice):
    '''Create PD to operate Tensile Tester'''
    def __init__(self, name, mot1pv, mot2pv, strainpv):
        self.setName(name)
        self.setInputNames(["strain"])
        self.setExtraNames(["load", "m1Position", "m2position"])
        self.setOutputFormat(["%4.3f", "%4.3f", "%4.3f", "%4.3f"])
        self.m1 = self._createMotor("m1", mot1pv)
        self.m2 = self._createMotor("m2", mot2pv)
        self.strain=CAClient(strainpv)
        self.strain.configure()
        # positive motion moves motors apart, negative towards the centre
        self.setZero()
        self.length = 10
        self.target = None

    def setSampleLength(self, length):
        self.length = length
        
    def setZero(self):
        self.zero = self.m1.getPosition() + self.m2.getPosition()

    def _createMotor(self, name, pv):
        motor = EpicsMotor()
        motor.setName(self.getName()+"-"+name)
        motor.setPvName(pv)
        motor.configure()
        return motor
    
    def atScanStart(self):
        pass

    def atScanEnd(self):
        pass
    
    def getM1Speed(self):
        return self.m1.getSpeed()
    
    def getM2Speed(self):
        return self.m2.getSpeed()
            
    def setM1Speed(self, speed):
        self.m1.setSpeed(speed)
        self.asynchronousMoveTo(self.target)
    
    def setM2Speed(self, speed):
        self.m2.setSpeed(speed)
        self.asynchronousMoveTo(self.target)
    
    def getStress(self):
        return 100.0 * ((self.m1.getPosition() + self.m2.getPosition()) - self.zero + self.length) / (self.length)
        
    def getPosition(self):
        return [ self.getStress(), float(self.strain.caget()),
                self.m1.getPosition(), self.m2.getPosition() ]
        
    def asynchronousMoveTo(self,p):
        if p == None:
            return
        self.target = p
        dist = self.getNewMotorDistance(p)
        (m1, m2) = self.distributeDistance(dist)
        self.m1.moveTo(m1)
        self.m2.moveTo(m2)
       # print m1, m2
        
    def distributeDistance(self, d):
        (m1p, m2p) = (self.m1.getPosition(), self.m2.getPosition())
        togo = d - (m1p + m2p)
        (m1s, m2s) = (self.m1.getSpeed(), self.m2.getSpeed())
        m1d = m1p + togo * m1s / (m1s + m2s)
        m2d = m2p + togo * m2s / (m1s + m2s)
       # print m1d, m2d
        return (m1d, m2d)
    
    def getNewMotorDistance(self, p):
        return ((p/100.0-1) * self.length) + self.zero
        
    def isBusy(self):
        busy = self.m1.isMoving() or self.m2.isMoving()
        if not busy:
            self.target = None
        return busy

if __name__ == "__main__":
    mtens2 = TensileTester("mtens2", "BL22I-EA-TENS-01:M1", "BL22I-EA-TENS-01:M2", "BL22I-EA-TENS-01:SG:POLLVALUE")
