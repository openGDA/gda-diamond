from gda.device.scannable import ScannableMotionBase

class ExtraNameHider(ScannableMotionBase):
    
    def __init__(self, name, delegate):
        self.delegate = delegate
        self.name = name
        self.inputNames = [name]
        self.outputFormat = [delegate.outputFormat[0]]
        
    def rawAsynchronousMoveTo(self, position):
        self.delegate.asynchronousMoveTo(position)
    
    def rawGetPosition(self):
        position = self.delegate.getPosition()
        try:
            return position[0]
        except TypeError:
            return position
    
    def isBusy(self):
        return self.delegate.isBusy()
    
    def stop(self):
        self.delegate.stop()