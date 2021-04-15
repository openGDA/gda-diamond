'''
Created on 27 Nov 2013

@author: fy65
'''
# CONSTANTS HERE

from gda.device.scannable import ScannableMotionBase
from gda.device.currentamplifier import EpicsCurrAmpSingle
gainmap={0:10**3,
         1:10**4,
         2:10**5,
         3:10**6,
         4:10**7,
         5:10**8,
         6:10**9,       #low noise
         7:10**5,
         8:10**6,
         9:10**7,
         10:10**8,
         11:10**9,
         12:10**10,
         13:10**11
         } # high speed
gainpositions={"10^3 low noise":0,
               "10^4 low noise":1,
               "10^5 low noise":2,
               "10^6 low noise":3,
               "10^7 low noise":4,
               "10^8 low noise":5,
               "10^9 low noise":6,
               "10^5 high speed":7,
               "10^6 high speed":8,
               "10^7 high speed":9,
               "10^8 high speed":10,
               "10^9 high speed":11,
               "10^10 high spd":12,
               "10^11 high spd":13
               }

class CleverAmplifier(ScannableMotionBase):
    '''
    classdocs
    '''
    def __init__(self, name, amp, lowerthreshold, upperthreshold,formatstring1,formatstring2):
        '''
        Constructor
        '''
        self.setName(name);
        self.setInputNames([name])
        self.setExtraNames(["Actual_Value"])
        self.setOutputFormat([formatstring2,  formatstring2])
        self.setLevel(5)
        self.amp=amp    #EpicsCurrAmpSingle()
        self.lowerthreshold=lowerthreshold
        self.upperthreshold=upperthreshold
        
    def atScanStart(self):
        pass
    
    def atPointStart(self):
        currentGain=str(self.amp.getGain())
        currentValue=float(self.amp.getPosition())
        while currentValue<self.lowerthreshold and gainpositions[currentGain]<6:
            self.amp.setGain(gainpositions.keys()[(gainpositions.values()).index(gainpositions[currentGain]+1)])
            currentGain=str(self.amp.getGain())
            sleep(0.1)
            currentValue=float(self.amp.getPosition())
        while currentValue>self.upperthreshold and gainpositions[currentGain]!=0:
            self.amp.setGain(gainpositions.keys()[(gainpositions.values()).index(gainpositions[currentGain]-1)])
            currentGain=str(self.amp.getGain())
            sleep(0.1)
            currentValue=float(self.amp.getPosition())
    
    def rawGetPosition(self):
        currentGain=str(self.amp.getGain())
        currentValue=float(self.amp.getPosition())
        return [currentValue, currentValue/float(gainmap[gainpositions[currentGain]])] 
    
    def rawAsynchronousMoveTo(self,new_position):
        pass
    
    def isBusy(self):
        return False
    
    def atPointEnd(self):
        pass
    
    def atScanEnd(self):
        pass
            
    def stop(self):
        pass

    def toString(self):
        return self.name + " : " + str(self.getPosition())
       
cleverIamp10=CleverAmplifier("cleverIamp10", smpmiamp39, 0.5, 9.0, "%.4f", "%.4e")  # @UndefinedVariable