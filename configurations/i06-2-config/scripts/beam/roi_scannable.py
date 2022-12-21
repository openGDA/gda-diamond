'''
Created on Jun 24, 2022

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.device import Detector
from beam.AreaDetectorROIs import RoiStatPairClass

Input_must_be_a_list_of_ROIs = "Input must be a list of ROIs, each provides a list specifies [x_start,y_start,x_size,y_size]"

class RoiStatScannable(ScannableMotionBase):
    '''
    classdocs
    '''


    def __init__(self, name, det, roi, roi_index, pv_root_name="BL06I-EA-DET-02"):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.det = det
        self.roi = roi
        self.roi_index = roi_index
        self.roistatpair = RoiStatPairClass(pv_root_name)
        
    def configure(self):
        self.roistatpair.set_roi(self.roi_index, self.roi[0], self.roi[1], self.roi[2], self.roi[3])        
        
    def asynchronousMoveTo(self, newpos):
        pass #do-nothing
    
    def getPosition(self):
        try:
            output = self.roistatpair.get_roi_average(self.roi_index)
            return output
        except Exception as e:
            print("%s: get roi %r average value failed - %s" % (self.getName(), self.roi, e.getMessage()))
            
    def isBusy(self):
        return self.det.getStatus() == Detector.BUSY
    
    def deconfigure(self):
        self.roistatpair.deactivate_roi(self.roi_index)
        self.roistatpair.deactivate_stat(self.roi_index)
