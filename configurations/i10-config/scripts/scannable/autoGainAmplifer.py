'''
An instance of this class automatically switching gain setting during a scan when the current reading reaches the given limits.

Instance of this class requires a root PV name for the amplifier with at least 2 end points (:I and :GAIN) to work!
You need to provide a Gain dictionary which maps enum position to actual gain value (see example below).

Example usages:      
    rca1=AutoGainAmplifier("rca1", "ME01D-EA-IAMP-01", 0.5, 9.0, "%.4e")

Created on 13 September 2018

@author: fy65
'''
# CONSTANTS HERE

from gda.device.scannable import ScannableMotionBase
from time import sleep
from gda.epics import CAClient
#Gain map for ME01D-EA-IAMP-01:GAIN,ME01D-EA-IAMP-02:GAIN,ME01D-EA-IAMP-03:GAIN
gainmap={0:10**4,
         1:10**5,
         2:10**6,
         3:10**7,
         4:10**8,
         5:10**9,       
         6:10**10,
         7:10**11,
         8:10**12,
         9:10**13
         } 

class AutoGainAmplifier(ScannableMotionBase):
    '''
    classdocs
    '''
    def __init__(self, name, rootPvName, lowerthreshold, upperthreshold,formatstring, gainMap=gainmap):
        '''
        Constructor
        '''
        self.setName(name);
        self.setInputNames([name])
        self.setExtraNames(["Actual_Value"])
        self.setOutputFormat([formatstring,  formatstring])
        self.setLevel(5)
        self.current=CAClient(rootPvName+":I")
        self.gain=CAClient(rootPvName+":GAIN")
        self.lowerthreshold=lowerthreshold
        self.upperthreshold=upperthreshold
        self.gainMap=gainMap
        self.gainAtScanStart=1
        
    def atScanStart(self):
        if not self.current.isConfigured():
            self.current.configure()
        if not self.gain.isConfigured():
            self.gain.configure()
        self.gainAtScanStart=int(self.gain.caget())
    
    def atPointStart(self):
        currentGain=int(self.gain.caget())
        currentValue=float(self.current.caget())
        while currentValue < self.lowerthreshold and currentGain < len(self.gainMap)-1:
            #up gain
            self.gain.caputWait(currentValue+1)
            currentGain=int(self.gain.caget())
            sleep(0.1)
            currentValue=float(self.current.caget())
        while currentValue>self.upperthreshold and currentGain!=0:
            #down gain
            self.gain.caputWait(currentValue-1)
            currentGain=int(self.gain.caget())
            sleep(0.1)
            currentValue=float(self.current.caget())
    
    def rawGetPosition(self):
        if not self.gain.isConfigured():
            self.gain.configure()
        if not self.current.isConfigured():
            self.current.configure()
        currentGain=int(self.gain.caget())
        currentValue=float(self.current.caget())
        return [currentValue, currentValue/float(gainmap[currentGain])] 
    
    def rawAsynchronousMoveTo(self,new_position):
        pass
    
    def isBusy(self):
        return False
    
    def atPointEnd(self):
        pass
    
    def atScanEnd(self):
        self.gain.caput(self.gainAtScanStart)
            
    def stop(self):
        pass

    def toFormattedString(self):
        return self.name + " : " + self.getInputNames()[0] +" : " + str(self.getPosition()[0]) + ", " + self.getExtraNames()[0] +" : "+ str(self.getPosition()[1])

