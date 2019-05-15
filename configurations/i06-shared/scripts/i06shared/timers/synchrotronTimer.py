'''
fix https://jira.diamond.ac.uk/browse/I06-579
reworked algorithm to remove circular reference between frequency divisor and tick delay.

1. pulse delay controls EPICS timer pulse,
2. frequency divisor uses pulse delay in EPICS to calculate divisor number,
3. tick delay uses frequency divisor result to calculate new delay for pulse delay control.

IMPORTANT:  set an allowed range of 0 <= x <= 824 for tickDelay scannable
            make 4 scannable each kind (tickDelay1, tickDelay2,..., tickDelay4, chDelay1,...,chDelay4, divisor1,...,divisor4) changing the PVs accordingly
            
Created on 7 Dec 2018

@author: fy65
'''
MAXIMUM_BUNCH_NUMBER=936
MAXIMUM_DELAY_UNITS=824

from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class EpicsReadPvWritePvClass(ScannableMotionBase):
    def __init__(self,name,pvSet, pvGet, formatstring):
        self.setName(name);
        self.setInputNames([name])
        self.setOutputFormat([formatstring])
        self.setLevel(6)
        self.chIn=CAClient(pvSet)
        self.chOut=CAClient(pvGet)

    def atScanStart(self):
        if not self.chIn.isConfigured():
            self.chIn.configure()
        if not self.chOut.isConfigured():
            self.chOut.configure()            

    def atScanEnd(self):
        if self.chIn.isConfigured():
            self.chIn.clearup()
        if self.chOut.isConfigured():
            self.chOut.clearup()

    def getPosition(self):
        output=0.0
        try:
            if not self.chOut.isConfigured():
                self.chOut.configure()
            output=float(self.chOut.caget())
            return float(output)
        except:
            print "Error returning position"
            return 0
        
    def asynchronousMoveTo(self, newpos):
        try:
            if not self.chIn.isConfigured():
                self.outcli.configure()
            self.chIn.caput(newpos)
        except:
            print "error moving to position %f" % float(newpos)

    def isBusy(self):
        return False 

class chdelay_scannable(ScannableMotionBase):
    def __init__(self, name, pulseDelay, freqDivisor, formatstring):
        self.setName(name);
        self.setInputNames([name])
        self.setOutputFormat([formatstring])
        self.setLevel(6)
        self.pulseDelay=pulseDelay
        self.freqDivisor=freqDivisor
        
        self.currentPosition = int(0)
        self.freqDiv = 1 

    def atScanStart(self):
        self.pulseDelay.atScanStart()

    def atScanEnd(self):
        self.pulseDelay.atScanEnd()
    
    def getPosition(self):
        delay = int(self.pulseDelay.getPosition())
        self.freqDiv=self.freqDivisor.getPosition()       
        self.currentPosition = delay-int( ( MAXIMUM_BUNCH_NUMBER*(self.freqDiv-2) +MAXIMUM_DELAY_UNITS)*(self.freqDiv>1))
        return self.currentPosition

    def asynchronousMoveTo(self, newpos):
        if int(newpos)<0 or int(newpos)>MAXIMUM_DELAY_UNITS:
            raise Exception("Input is outside limits [0,%d]" % (MAXIMUM_DELAY_UNITS))
        self.freqDiv=self.freqDivisor.getPosition()       
        delay = int((MAXIMUM_BUNCH_NUMBER*(self.freqDiv-2)+MAXIMUM_DELAY_UNITS)*(self.freqDiv>1)+newpos)
        self.pulseDelay.asynchronousMoveTo(delay)

    def isBusy(self):
        return False 

class freqDivisor_scannable(ScannableMotionBase):
    def __init__(self,name,pulseDelay):
        self.setName(name);
        self.setInputNames([name])
        self.setOutputFormat(['%2.0f'])
        self.setLevel(6)
        self.pulseDelay = pulseDelay

    def getPosition(self):
        delay = int(self.pulseDelay.getPosition())
        if (delay < MAXIMUM_DELAY_UNITS):
            self.freqDiv = 1
        else:
            self.freqDiv = int( (delay-(MAXIMUM_DELAY_UNITS-1))/MAXIMUM_BUNCH_NUMBER ) + 2
        return self.freqDiv

    def asynchronousMoveTo(self, newpos):
        delay = self.pulseDelay.getPosition()
        self.freqDiv = newpos
        delay = int((MAXIMUM_BUNCH_NUMBER*(self.freqDiv-2)+MAXIMUM_DELAY_UNITS)*(self.freqDiv>1)+delay)
        self.pulseDelay.asynchronousMoveTo(delay)

    def isBusy(self):
        return False 

# create instances for 4 channel timers
pulseDelay1 = EpicsReadPvWritePvClass("pulseDelay1","BL06I-TI-TIMER-01:SET1-DELAY","BL06I-TI-TIMER-01:GET1-DELAY", "%2.4f")
pulseDelay2 = EpicsReadPvWritePvClass("pulseDelay2","BL06I-TI-TIMER-01:SET2-DELAY","BL06I-TI-TIMER-01:GET2-DELAY", "%2.4f")
pulseDelay3 = EpicsReadPvWritePvClass("pulseDelay3","BL06I-TI-TIMER-01:SET3-DELAY","BL06I-TI-TIMER-01:GET3-DELAY", "%2.4f")
pulseDelay4 = EpicsReadPvWritePvClass("pulseDelay4","BL06I-TI-TIMER-01:SET4-DELAY","BL06I-TI-TIMER-01:GET4-DELAY", "%2.4f")
divisor1=freqDivisor_scannable("divisor1", pulseDelay1)
divisor2=freqDivisor_scannable("divisor2", pulseDelay2)
divisor3=freqDivisor_scannable("divisor3", pulseDelay3)
divisor4=freqDivisor_scannable("divisor4", pulseDelay4)
tickDelay1 = chdelay_scannable("tickDelay1", pulseDelay1, divisor1, "%2.4f")
tickDelay2 = chdelay_scannable("tickDelay2", pulseDelay2, divisor2, "%2.4f")
tickDelay3 = chdelay_scannable("tickDelay3", pulseDelay3, divisor3, "%2.4f")
tickDelay4 = chdelay_scannable("tickDelay4", pulseDelay4, divisor4, "%2.4f")
