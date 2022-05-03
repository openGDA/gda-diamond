'''
This module provides a class that processes output from two EpicsBekHoffAdc
detector objects and a list of supported functions that define how the output
from the two detector objects will be processed.
Objects of this class can be configured with a constant by using setConstant
to further configure a supported function and allow more flexibility to the user


@author: svz41317
'''
from gda.device.scannable import ScannableMotionBase
from gda.device import Detector
from gda.device.currentamplifier import EpicsBekhoffAdc


class BekhoffAdcOutputProcessing(ScannableMotionBase):
    """
    Process output of two EpicsBekHoffAdc detectors using the given function named.
    """
    
    def __init__(self, name, det_a, det_b, function_name, constant=1):
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames([name])
        self.function_name = function_name
        if isinstance(det_a, EpicsBekhoffAdc):
            self.detector_a = det_a
        else:
            raise RuntimeError('This class can only be used with EpicsBekhoffAdc type detector')
        if isinstance(det_b, EpicsBekhoffAdc):
            self.detector_b = det_b
        else:
            raise RuntimeError('This class can only be used with EpicsBekhoffAdc type detector')
        self.constant = constant
        
    # Scan framework methods
    def setConstant(self, constant):
        """
        Set a constant to be used by any supported function
        """
        self.constant = constant
    
    def getPosition(self):
       
        current_a = self.detector_a.getPosition()
        current_b = self.detector_b.getPosition()
        
        return globals()[self.function_name](current_a, current_b, self.constant);
    
    def isBusy(self):
        return self.detector_a.getStatus() == Detector.BUSY or self.detector_b.getStatus() == Detector.BUSY
    
        
    def asynchronousMoveTo(self):
        raise RuntimeError('This scannable is read-only')

# Supported functions    
def divide_detector_output(a, b, constant):
    return (a * constant) / b 