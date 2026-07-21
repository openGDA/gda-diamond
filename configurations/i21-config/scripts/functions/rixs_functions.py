'''
get RIXS data with hkl and uvw metadata

Created on Jun 15, 2023

@author: fy65
'''
from acquisition.acquire_images import acquireRIXS
from scannable.continuous.continuous_energy_scannables import m4c1
from scannabledevices.checkbeamscannables import checkbeam
from gdaserver import andor  # @UnresolvedImport

def get_rixs(number_images, exposure_time):
    acquireRIXS(number_images, andor, exposure_time, m4c1, exposure_time, checkbeam)