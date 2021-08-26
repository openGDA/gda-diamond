'''
An instance of this class automatically switching gain setting during a scan when the current reading reaches the given limits.

You need to provide a Gain dictionary which maps enum position to actual gain value (see example below).

Example usages:      
    rca1=DummyAutoGainAmplifier("rca1", 10.0, 0.5, 9.5, "%.4e")

Created on 23 August 2021

@author: fy65
'''

from gda.device.scannable import ScannableMotionBase
import random
#Gain map set to be the same as AutoGainAmplifier (please don't import as it will create an dependency to PVs)
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

class DummyAutoGainAmplifier(ScannableMotionBase):
    '''
    classdocs
    '''
    def __init__(self, name, scale, lowerthreshold, upperthreshold,formatstring, gain_map=gainmap):
        '''
        Constructor
        '''
        self.setName(name);
        self.setInputNames([name])
        self.setExtraNames(["Actual_Value"])
        self.setOutputFormat([formatstring,  formatstring])
        self.setLevel(5)
        self.scale = scale
        self.lowerthreshold = lowerthreshold
        self.upperthreshold = upperthreshold
        self.gainMap = gain_map
        self.current_gain = int(random.choice(list(self.gainMap.keys())))
        self.current_value = None

    def atPointStart(self):
        self.current_value = random.random()*self.scale
        while self.current_alue < self.lowerthreshold and self.current_gain < len(self.gainMap)-1:
            self.current_gain = self.current_gain + 1
            self.current_value = self.current_value / 10.0
        while self.current_value > self.upperthreshold and self.current_gain != 0:
            self.current_gain = self.current_gain - 1
            self.current_value = self.current_value * 10.0
    
    def rawGetPosition(self):
        return [self.current_value, self.current_value/float(gainmap[self.current_gain])] 
    
    def rawAsynchronousMoveTo(self,new_position):
        # read only 
        pass
    
    def isBusy(self):
        return False
    
    def toFormattedString(self):
        return self.name + " : " + self.getInputNames()[0] +" : " + str(self.getPosition()[0]) + ", " + self.getExtraNames()[0] +" : "+ str(self.getPosition()[1])

