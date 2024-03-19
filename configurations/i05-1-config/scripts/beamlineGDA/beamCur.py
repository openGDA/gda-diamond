from time import sleep
from gda.epics import CAClient
"""
    Purpose: pause the scan on beam dump
"""


class BeamCurrent(ScannableMotionBase):

   def __init__(self, name):
    self.setName(name)
    self.setInputNames([])
    self.setExtraNames([])
    self.setOutputFormat([])
    self.setLevel(7)
    self.MinLevel = 1
    self.ricur = CAClient("SR21C-DI-DCCT-01:SIGNAL")
    self.ricur.configure()
    self.shutter = CAClient("FE05I-PS-SHTR-02:STA")
    self.shutter.configure()
    self.wasOff = False


   def isBusy(self):
       if float(self.ricur.caget())<self.MinLevel:
           if self.wasOff = False:
               self.wasOff = True
           return True
       return False

   def getPosition(self):
       return None

   def asynchronousMoveTo(self,newPosition):
       self.MinLevel=newPosition
       
       
beamCur = BeamCurrent("beamCur")
