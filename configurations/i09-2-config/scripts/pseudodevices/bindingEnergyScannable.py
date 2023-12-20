'''
Created on 19 Dec 2023

@author: eir17846
'''
from gda.device.scannable import ScannableMotionBase
from detector.iseg_instances import kenergy
from gda.factory import Finder

class bindingEnergyScannable(ScannableMotionBase):
    
    def __init__(self, name, pgm_scannable, sample_bias_scannable, unitstring, formatstring, work_function=4.45):
        self.setName(name);
        self.setInputNames([name])
        self.pgm_scannable = pgm_scannable
        self.sample_bias_scannable = sample_bias_scannable
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
        self.setLevel(3)
        self.work_function = work_function
 
    def rawGetPosition(self):
        try:
            be = self.pgm_scannable.getPosition() - self.sample_bias_scannable.getPosition() - self.work_function
            return be
        except:
            print "Error returning position"
            return 0

    def rawAsynchronousMoveTo(self, new_position):
        try:
            result = self.pgm_scannable.getPosition() - new_position - self.work_function
            self.sample_bias_scannable.moveTo(result)
        except:
            print "error moving to position"

    def isBusy(self):
        try:
            return self.sample_bias_scannable.isBusy()
        except:
            print "problem moving: Returning busy status"
            return 0
        
    def setWF(self, value):
        try:
            self.work_function = value
            print "Work function set to new value " + value.toString()
        except:
            print "Setting work function failed"
            
    def getWF(self):
        print "Work function value is " + self.work_function.toString()
        return self.work_function
        
pgm = Finder.find("pgmenergy")
benergy=bindingEnergyScannable("benergy", pgm, kenergy, "", "%d", 4.3)
