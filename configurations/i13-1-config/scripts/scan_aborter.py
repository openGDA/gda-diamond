from gda.device.scannable import ScannableBase
from gdascripts.parameters import beamline_parameters
from gda.device import DeviceException
class scan_aborter(ScannableBase):
    """
    Class to handle 
    """
    def __init__(self, name, valuesIndex, maxvalue, msg):
        self.name = name
        self.inputNames = []
        self.outputFormat = []
        jns=beamline_parameters.JythonNameSpaceMapping()
        self.lastScanDataPointFunction =  jns.lastScanDataPoint
        self.valuesIndex = valuesIndex
        self.maxvalue = maxvalue
        self.msg = msg
        self.point=0
    def isBusy(self):
        return False
    
    def atPointStart(self):
        lsdp = self.lastScanDataPointFunction()
        if lsdp.getCurrentPointNumber()>0:
            vals = lsdp.getAllValuesAsDoubles()
            if len(vals) > self.valuesIndex:
                if vals[self.valuesIndex] > self.maxvalue:
                    raise DeviceException(self.msg + ". max:" + `self.maxvalue` + " actual:" + `vals[self.valuesIndex]`)
                print self.name + ":Value is OK : " + `vals[self.valuesIndex]`
        else:
            print self.name + " waiting for next point"
        self.point +=1
        
    def rawAsynchronousMoveTo(self,new_position):
        pass
    
    def rawGetPosition(self):
        return None
