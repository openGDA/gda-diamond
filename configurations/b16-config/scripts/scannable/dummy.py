'''
Created on 6 Mar 2014

@author: zrb13439
'''
from gda.device.scannable import ScannableBase





class StepDummy(ScannableBase):
    '''Dummy PD Class'''
    def __init__(self, name, parameter_scanable, up_start=10, up_end=20, down_start=40, down_end=60):
        
        
        self.name = name
        self.parameter_scanable = parameter_scanable
        self.up_start = up_start
        self.up_end = up_end
        self.down_start = down_start
        self.down_end = down_end
        
        self.low = 0
        self.high = 100
        
        self.inputNames = []
        self.extraNames = [name]
        self.outputFormat = ['%.4f']
        
    def isBusy(self):
        return 0

    def rawAsynchronousMoveTo(self,new_position):
        assert False

    def getPosition(self):
        x = self.parameter_scanable()
        return self.calc_step_value(x)
    
    def calc_step_value(self, x):
        
        assert self.up_start < self.up_end < self.down_start < self.down_end
        
        if x <= self.up_start:
            return self.low
        
        if x <= self.up_end:
            d = float(x - self.up_start)
            w = float(self.up_end - self.up_start)
            return self.low * ((w - d) / w) + self.high * d / w
        
        if x <= self.down_start:
            return self.high
        
        if x <= self.down_end:
            d = float(x - self.down_start)
            w = float(self.down_end - self.down_start)
            return self.high * ((w - d) / w) + self.low * d / w
        
        # x >  self.down_end
        return self.low

