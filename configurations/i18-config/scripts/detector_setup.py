from xspress_functions import *
from uk.ac.gda.devices.detector.xspress4 import XspressPvProviderBase

andor_camera_control = Finder.find("andor_camera_control")

def object_exists(object_name) :
    return object_name in globals().keys()

def setup_andor() :
    if not object_exists("andor") :
        return 
    
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
    if not object_exists("xmapMca") :
        return 

    xmapMca.setHardwareTriggeredMode(True)
    xmapMca.setSleepTimeBeforeReadoutMs(200)
    CAClient.put("BL18I-EA-DET-07:StatusAll.SCAN", 9)
    CAClient.put("BL18I-EA-DET-07:ReadAll.SCAN", 9)
    
def setup_xspress3Odin() :
    if LocalProperties.isDummyModeEnabled() :
        return 
    
    basePv = xspress3Odin.getController().getBasePv()
    if not XspressPvProviderBase.pvExists(basePv+":CAM:DetectorState_RBV") :
        print("Not setting up xspress3Odin - PVs are not present")
        return
    xspress3Odin.getController().afterPropertiesSet()
    
    
def setup_ffi0_channel(i0_channel=2) : 
    print("Setting I0 channel on FFI0 detectors to "+str(i0_channel))
    ffi0_detectors = [FFI0_xspress3Odin, qexafs_FFI0_xspress3Odin, FFI0_xmapMca]

    for det in ffi0_detectors : 
        det.setI0_channel(i0_channel)

run_in_try_catch(setup_andor)
run_in_try_catch(setup_xmap)
run_in_try_catch(setup_xspress3Odin)

setup_ffi0_channel()