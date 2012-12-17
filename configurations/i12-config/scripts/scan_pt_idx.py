from gda.device.scannable import PseudoDevice


class ScanPtIdx(PseudoDevice):
    # constructor
    def __init__(self, name, min_inc=0, step_size=1):
        self.setName(name) 
        self.min_inc=min_inc
        self.step_size=step_size
        self.current_idx=min_inc

    # returns the value this scannable represents
    def rawGetPosition(self):
        return self.current_idx

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        return

    # Returns the status of this Scannable
    def rawIsBusy(self):
        return
        
    def atPointStart(self):
        pass
        
    def atPointEnd(self):
        self.current_idx += self.step_size
    
    def stop(self):
        pass
    
    def atScanEnd(self):
        self.current_idx=0
    
    def atCommandFailure(self):
        self.current_idx=0
    
zidx=ScanPtIdx('zidx')
