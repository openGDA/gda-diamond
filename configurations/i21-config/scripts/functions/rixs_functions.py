'''
get RIXS data with hkl amd uvw metadata

Created on Jun 15, 2023

@author: fy65
'''
from gdascripts.metadata.nexus_metadata_class import meta
from scannabledevices.ToolpointMotion import uvw
from acquisition.acquire_images import acquireRIXS
from scannable.continuous.continuous_energy_scannables import m4c1
from scannabledevices.checkbeamscannables import checkbeam
from gdaserver import andor  # @UnresolvedImport
import __main__  # @UnresolvedImport

def get_rixs(number_images, exposure_time):
    
    meta.addScalar("Q", "H", __main__.hkl[0])
    meta.addScalar("Q", "K", __main__.hkl[1]) 
    meta.addScalar("Q", "L", __main__.hkl[2]) 
    meta.addScalar("T", "u", uvw[0])
    meta.addScalar("T", "v", uvw[1]) 
    meta.addScalar("T", "w", uvw[2]) 
    
    acquireRIXS(number_images, andor, exposure_time, m4c1, exposure_time, checkbeam)
       
    meta.rm("Q", "H")
    meta.rm("Q", "K") 
    meta.rm("Q", "L") 
    meta.rm("T", "u")
    meta.rm("T", "v") 
    meta.rm("T", "w") 