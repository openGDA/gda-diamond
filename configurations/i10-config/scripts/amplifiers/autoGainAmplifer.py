'''
An instance of this class automatically switching gain setting during a scan when the current reading reaches the given limits.

Instance of this class requires a root PV name for the amplifier with at least 2 end points (:I and :GAIN) to work!
You need to provide a Gain dictionary which maps enum position to actual gain value (see example below).

Example usages:      
    rca1=AutoGainAmplifier("rca1", "ME01D-EA-IAMP-01", 0.5, 9.5, "%.4e")

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
    def __init__(self, name, root_pv_name, lowerthreshold, upperthreshold,formatstring, gain_map=gainmap):
        '''
        Constructor
        '''
        self.setName(name);
        self.setInputNames([name])
        self.setExtraNames(["Actual_Value"])
        self.setOutputFormat([formatstring,  formatstring])
        self.setLevel(5)
        self.current = CAClient(root_pv_name+":I")
        self.gain = CAClient(root_pv_name+":GAIN")
        self.lowerthreshold = lowerthreshold
        self.upperthreshold = upperthreshold
        self.gainMap = gain_map
        self.gainAtScanStart = 1
        
    def atScanStart(self):
        if not self.current.isConfigured():
            self.current.configure()
        if not self.gain.isConfigured():
            self.gain.configure()
        self.gainAtScanStart=int(self.gain.caget())
    
    def atPointStart(self):
        current_gain = int(self.gain.caget())
        current_value = float(self.current.caget())
        while current_value < self.lowerthreshold and current_gain < len(self.gainMap) - 1:
            #up gain
            self.gain.caputWait(current_gain + 1)
            current_gain = int(self.gain.caget())
            sleep(0.1)
            current_value = float(self.current.caget())
        while current_value > self.upperthreshold and current_gain != 0:
            #down gain
            self.gain.caputWait(current_gain - 1)
            current_gain = int(self.gain.caget())
            sleep(0.1)
            current_value = float(self.current.caget())
    
    def rawGetPosition(self):
        if not self.gain.isConfigured():
            self.gain.configure()
        if not self.current.isConfigured():
            self.current.configure()
        current_gain = int(self.gain.caget())
        current_value = float(self.current.caget())
        return [current_value, current_value / float(gainmap[current_gain])] 
    
    def rawAsynchronousMoveTo(self,new_position):
        #read-only
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

