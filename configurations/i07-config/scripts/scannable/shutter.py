from gda.device.scannable import ScannableBase


class _ScannableToggler(ScannableBase):

    def __init__(self, name, scannable, start_value=1, end_value=0):
        self.inputNames = []
        self.extraNames = []
        self.outputFormat = []
        self.name = name
        
        self._scannable = scannable
        self._start_value = start_value
        self._end_value = end_value
        
    def moveToStartValue(self):
        self._scannable.moveTo(self._start_value)

    def moveToEndValue(self):
        self._scannable.moveTo(self._end_value)
    
    def asynchronousMoveTo(self, target):
        raise Exception("Not supported")
    
    def getPosition(self):
        return
    
    def isBusy(self):
        return False
    
    def waitWhileBusy(self):
        return
    
    def stop(self):
        self.moveToEndValue()
        
    def atCommandFailure(self):
        self.moveToEndValue()
    

        
class ScanStartToggler(_ScannableToggler):
    
    def atScanStart(self):
        self.moveToStartValue()

    def atScanEnd(self):
        self.moveToEndValue()
        
       
class ScanLineStartToggler(_ScannableToggler):
    
    def atScanLineStart(self):
        self.moveToStartValue()

    def atScanLineEnd(self):
        self.moveToEndValue()


class ScanPointToggler(_ScannableToggler):
    
    def atPointStart(self):
        self.moveToStartValue()

    def atPointEnd(self):
        self.moveToEndValue()


    