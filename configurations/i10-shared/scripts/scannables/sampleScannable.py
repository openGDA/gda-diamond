'''
Created on 22 Jan 2025

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase

class SampleName(ScannableMotionBase):
    '''
    classdocs
    '''


    def __init__(self, name, sample_name = "name not given"):
        '''
        Constructor
        '''
        self.setName(name)
        self.setINputNames(["name"])
        self.setOutputFormat(["%s"])
        self.sampleName = sample_name

    def getPosition(self):
        return self.sampleName

    def asynchronousMoveTo(self, v):
        self.sampleName = v

    def isBusy(self):
        return False
