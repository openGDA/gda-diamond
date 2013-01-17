from gda.device.scannable import ScannableBase
from gdascripts.parameters import beamline_parameters
from gda.device import DeviceException
from gda.device.scannable import PositionCallableProvider
from java.util.concurrent import Callable

class roi_DiffCallable(Callable):

    def __init__(self, datasetDetName, datasetName1, datasetName2, detReadout):
        self.datasetDetName = datasetDetName
        self.datasetName1 = datasetName1
        self.datasetName2 = datasetName2
        self.detReadout=detReadout
        
    def call(self):
        val1= self.detReadout.getData(self.datasetDetName,self.datasetName1,"SDS").getFirstValue()
        val2= self.detReadout.getData(self.datasetDetName,self.datasetName2,"SDS").getFirstValue()
        return val1-val2


class roi_diff(ScannableBase, PositionCallableProvider):
    """
    Class to handle 
    """
    def __init__(self, name, extraName,det, datasetDetName="mpx", datasetName1="image_data.total", datasetName2="image_data.total2"):
        self.name = name
        self.inputNames = []
        self.outputFormat = ["%5.5g"]
        self.extraNames=[extraName]
        self.det = det
        self.datasetDetName = datasetDetName
        self.datasetName1 = datasetName1
        self.datasetName2 = datasetName2

    def isBusy(self):
        return False
    
    def rawAsynchronousMoveTo(self,new_position):
        pass
    
    def rawGetPosition(self):
        return self.getPositionCallable().call()
    
    def getPositionCallable(self):
        return roi_DiffCallable(self.datasetDetName, self.datasetName1, self.datasetName2, self.det.readout())
