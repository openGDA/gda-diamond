from gda.device.scannable import PseudoDevice

class ExtraNameHider(PseudoDevice):
    
    def __init__(self, name, delegate):
        self.delegate = delegate
        self.name = name
        self.inputNames = [name]
        self.outputFormat = [delegate.outputFormat[0]]
        
    def rawAsynchronousMoveTo(self, position):
        self.delegate.asynchronousMoveTo(position)
    
    def rawGetPosition(self):
        return self.delegate.getPosition()[0]
    
    def isBusy(self):
        return self.delegate.isBusy()
    
    def stop(self):
        self.delegate.stop()