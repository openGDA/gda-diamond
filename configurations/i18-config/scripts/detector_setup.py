from xspress_functions import *
from uk.ac.gda.devices.detector.xspress4 import XspressPvProviderBase

andor_camera_control = Finder.find("andor_camera_control")

def setup_andor() :
    basePv = andor.getAdBase().getBasePVName().replace("CAM:","")

    if not XspressPvProviderBase.pvExists(basePv+":CAM:Status_RBV") :
        print("Not setting up Andor - PVs are not present")
        return 

    # Make sure using continuous image mode For live stream view
    if not LocalProperties.isDummyModeEnabled() :
        andor_camera_control.setContinuousImageMode(1) # continuous mode = 1 for Andor
        
    # Make sure the array plugin has callbacks enabled (may need to do this after scans?)    
    CAClient.put(basePv+"ARR:EnableCallbacks", 1)
    
def setup_xmap() :
    xmapMca.setHardwareTriggeredMode(True)


def setup_xspress3() :
    xspress3.setPrefix("xspress3")
    xspress3.setDefaultSubDirectory("nexus")
    xspress3.setFileTemplate("%s%s%d.hdf5")
    xspress3.setFilePath("")
    xspress3.setReadDataFromFile(True) # to ensure Hdf file writing is used during scans

    cont = xspress3.getController()
    basePv = cont.getEpicsTemplate()
    
    setup_xspress_detector(basePv)
    
def setup_ffi0_channel(i0_channel=2) : 
    print("Setting I0 channel on FFI0 detectors to "+str(i0_channel))
    ffi0_detectors = [FFI0_xspress3, raster_FFI0_xspress3, FFI0_xspress3Odin, qexafs_FFI0_xspress3Odin, FFI0_xmapMca]
    for det in ffi0_detectors : 
        det.setI0_channel(i0_channel)

run_in_try_catch(setup_andor)
run_in_try_catch(setup_xmap)
run_in_try_catch(setup_xspress3)
setup_ffi0_channel()