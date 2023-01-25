'''
Created on Jan 24, 2023

@author: fy65
'''
from gdascripts.utils import caput

XSPRESS3_PV_ROOT = "BL07B-EA-XSP3-01:"

def proc4xspress3_num_frames(num_int, pv_root = XSPRESS3_PV_ROOT):
    caput(pv_root + "PROC:NumFilter", num_int)
    caput(pv_root + "NumImages", num_int)
    caput(pv_root + "PROC:ResetFilter", 1)
    caput(pv_root + "ArrayCounter", 0)
    
    
def proc4xspress3_setup_ports(pv_root = XSPRESS3_PV_ROOT):
    caput(pv_root + "PROC:NDArrayPort", "XSP3.DTC")
    caput(pv_root + "ROI1:NDArrayPort", "XSP3.DTC")
    caput(pv_root + "ROISUM1:NDArrayPort", "XSP3.PROC")
