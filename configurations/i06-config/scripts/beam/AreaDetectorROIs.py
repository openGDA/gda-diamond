from gda.epics import CAClient
from time import sleep

PV_ROOT_NAME="BL06I-EA-DET-01"

class RoiStatPairClass():

    def __init__(self, pv_root_name = PV_ROOT_NAME):
        self.pv_root_name = pv_root_name
        self.ca = CAClient()
   
    def set_roi(self, roi_num, xstart, ystart, xsize, ysize):
        roi_x_start_pv = self.pv_root_name+":ROI"+str(roi_num)+":MinX"
        roi_y_start_pv = self.pv_root_name+":ROI"+str(roi_num)+":MinY"
        roi_x_size_pv = self.pv_root_name+":ROI"+str(roi_num)+":SizeX"
        roi_y_size_pv = self.pv_root_name+":ROI"+str(roi_num)+":SizeY"
        self.ca.caput(roi_x_start_pv, xstart)
        self.ca.caput(roi_y_start_pv, ystart)
        self.ca.caput(roi_x_size_pv, xsize)
        self.ca.caput(roi_y_size_pv, ysize)
        sleep(0.1)
        self.activate_stat(roi_num)
        self.activate_roi(roi_num)
    
    def activate_stat(self, roi_num):
        stat_enable_pv = self.pv_root_name+":STAT"+str(roi_num)+":EnableCallbacks"
        self.ca.caput(stat_enable_pv, "Enable")        
        stat_on_pv = self.pv_root_name+":STAT"+str(roi_num)+":ComputeStatistics"
        self.ca.caput(stat_on_pv, "Yes")
    
    def activate_roi(self, roi_num):
        roi_enable_pv = self.pv_root_name+":ROI"+str(roi_num)+":EnableCallbacks"
        self.ca.caput(roi_enable_pv, "Enable")        
        roi_x_enable_pv = self.pv_root_name+":ROI"+str(roi_num)+":EnableX"
        self.ca.caput(roi_x_enable_pv, "Enable")        
        roi_y_enable_pv = self.pv_root_name+":ROI"+str(roi_num)+":EnableY"
        self.ca.caput(roi_y_enable_pv, "Enable")
        
    def deactivate_stat(self, roi_num):
        stat_enable_pv = self.pv_root_name+":STAT"+str(roi_num)+":EnableCallbacks"
        self.ca.caput(stat_enable_pv, "Disable")        
        stat_on_pv = self.pv_root_name+":STAT"+str(roi_num)+":ComputeStatistics"
        self.ca.caput(stat_on_pv, "No")
    
    def deactivate_roi(self, roi_num):
        roi_enable_pv = self.pv_root_name+":ROI"+str(roi_num)+":EnableCallbacks"
        self.ca.caput(roi_enable_pv, "Disable")       
        roi_x_enable_pv = self.pv_root_name+":ROI"+str(roi_num)+":EnableX"
        self.ca.caput(roi_x_enable_pv, "Disable")        
        roi_y_enable_pv = self.pv_root_name+":ROI"+str(roi_num)+":EnableY"
        self.ca.caput(roi_y_enable_pv, "Disable")

    def get_roi_average(self, roi_num):
        roi_avg_pv = self.pv_root_name+":STAT"+str(roi_num)+":MeanValue_RBV"
        return float(self.ca.caget(roi_avg_pv))
    