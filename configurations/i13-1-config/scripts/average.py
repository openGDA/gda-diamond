import time
from gda.device.scannable import ScannableBase
class Average(ScannableBase):
    def __init__(self, scannable, numPoints=10, timeBetweenReadings=1):
        self.scannable = scannable
        self.name = "avg_" + self.scannable.getName()
        self.inputNames = []
        self.extraNames = [ self.name]
        self.outputFormat = ["%5.5g"]
        self.numPoints=numPoints
        self.timeBetweenReadings = timeBetweenReadings
    def isBusy(self):
        return False
    
    def rawAsynchronousMoveTo(self,new_position):
        pass
    
    def rawGetPosition(self):
        sum=0;
        for i in range(self.numPoints):
            time.sleep(self.timeBetweenReadings)
            sum += self.scannable()
            
        return sum/self.numPoints