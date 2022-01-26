from gda.device.scannable import ScannableMotionBase

class MonitorWrapper(ScannableMotionBase):
    '''Simply wraps a monitor so it apperas as a regular scannable, and is hence
    moved in scans.'''
    
    def __init__(self, monitor, name=None):
        self.monitor = monitor
        if name is None:
            self.name = monitor.getName()        
        else:
            self.name = name
        self.setInputNames([self.name])
        self.setOutputFormat(monitor.getOutputFormat())
        self.setLevel(9)

    def isBusy(self):
        return self.monitor.isBusy()

    def getPosition(self):
        return self.monitor.getPosition()

    def asynchronousMoveTo(self,waittime):
        self.monitor.asynchronousMoveTo(waittime)