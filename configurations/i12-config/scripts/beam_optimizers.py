from gda.device.scannable import ScannableMotionBase
from gda.jython.commands import ScannableCommands
#from gda.scan import BasicScanDataPointPipeline
class beam_optimizer(ScannableMotionBase):
    def __init__(self, name, dummy, motor=None, start=None, end=None, step=None, monitor=None):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%5.5g"])
        self.pos = 0.
        self.dummy = True
        self. motor = motor
        self.start = start
        self.end=end
        self.step = step
        self.monitor = monitor
        
        
    def isBusy(self):
        return False

    def rawGetPosition(self):
        return self.pos

    def rawAsynchronousMoveTo(self, new_position):
        self.pos = new_position
        if self.dummy:
            return
        sc=ScannableCommands.createConcurrentScan([self. motor , self.start, self.end, self.step, self.monitor])
        #sc.setScanDataPointPipeline( BasicScanDataPointPipeline())
        
        
