'''
I21 specific functions provided by i21 scientists - see https://jira.diamond.ac.uk/browse/I21-1057

Created on Jun 15, 2023

@author: fy65
'''
from gdaserver import m5tth, difftth, gv17  # @UnresolvedImport
from shutters.detectorShutterControl import erio
from scan.cvscan import cvscan
from scannable.continuous.continuous_energy_scannables import energy, diff1_c,\
    draincurrent_c, fy2_c, m4c1_c
from lights.chamberLight import lightOff
from scannabledevices.checkbeamscannables import checkbeamcv

def xas(start, stop, step = 0.05, exposure_time = 0.1):
    current_position = float(m5tth())
    difftth.moveTo(current_position + 1.5)
    gv17('Close')
    erio()
    lightOff()
    cvscan(energy, start, stop, step, diff1_c, exposure_time, fy2_c, exposure_time, draincurrent_c, exposure_time, m4c1_c, exposure_time, checkbeamcv)
    
    
def repeat_xas(start, stop, number, step = 0.05, exposure_time = 0.1):
    current_position = float(m5tth())
    difftth.moveTo(current_position + 1.5)
    erio()
    lightOff()
    for i in range(number):
        cvscan(energy, start, stop, step, diff1_c, exposure_time, fy2_c, exposure_time, draincurrent_c, exposure_time, m4c1_c, exposure_time, checkbeamcv)

   
    

    
    
