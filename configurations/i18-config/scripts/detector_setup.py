from xspress_functions import *
from uk.ac.gda.devices.detector.xspress4 import XspressPvProviderBase
from sleep_scannable import sleep_detector, async_sleep_detector

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
    xspress3Odin.setFilePath("") # clear file path, to use default data directory
    
    
def setup_ffi0_channel(i0_channel=2) : 
    print("Setting I0 channel on step scan FFI0 detectors to "+str(i0_channel))
    ffi0_detectors = [FFI0_xspress3Odin]
    if "FFI0_xmapMca" in globals() :
        ffi0_detectors.append(FFI0_xmapMca)
    
    for det in ffi0_detectors : 
        det.setI0_channel(i0_channel)

def setup_medipix() :
    
    #medipix.getNdStats().reset()
    #medipix.getNdArray().reset()
    
    base_pv = medipix.getAdBase().getBasePVName().replace(":DET:", "")
    
    CAClient.put(base_pv+":ROI:NDArrayPort", "merlin1.cam")
    CAClient.put(base_pv+":STAT:NDArrayPort", "merlin1.roi")
    CAClient.put(base_pv+":HDF5:NDArrayPort", "merlin1.cam")
    CAClient.put(base_pv+":HDF5:LazyOpen", 0)
    CAClient.put(base_pv+":HDF5:EnableCallbacks", 1)
    
    CAClient.put(base_pv+":ARR:EnableCallbacks", 1)

    # collect software triggered frame to make dimensions are set correctly in the plugin chain
    collect_software_triggered_frame(base_pv+":DET", 1.0)

    medipix_plugins = Finder.find("medipix_plugins")
    
    namespace = InterfaceProvider.getJythonNamespace()
    for k in medipix_plugins.keySet() :
        print("Adding "+k+" to Jython namespace")
        namespace.placeInJythonNamespace(k, medipix_plugins.get(k))
        
    medipix.setCollectionStrategy(medipix_hardware_triggered_collectionstrategy)
    

def setup_xspress3mini() :
    cont = xspress3Mini.getController()
    base_pv = cont.getBasePv()
    set_hdf5_filetemplate(base_pv)
    CAClient.put(base_pv+":HDF5:LazyOpen", 0)
    CAClient.put(base_pv+":HDF5:NDArrayPort", "XSP3")

    collect_software_triggered_frame(base_pv, 1.0)

def set_medipix_collection_time(acq_time, dead_time=0.1) :
    sleep_detector.setCollectionTime(acq_time+dead_time)
    async_sleep_detector.sleep_time = acq_time + dead_time
    medipix_hardware_triggered_collectionstrategy.setCollectionTime(acq_time)
    
    
run_in_try_catch(setup_andor)
run_in_try_catch(setup_xmap)
run_in_try_catch(setup_xspress3Odin)
run_in_try_catch(setup_medipix)
run_in_try_catch(setup_xspress3mini)

setup_ffi0_channel()