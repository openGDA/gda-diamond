from xspress_functions import *
from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider
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
    if not object_exists("medipix"):
        return
    
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
    

def setup_xspress3mini(collect_frame=True) :
    if not object_exists("xspress3Mini"):
        return
    
    cont = xspress3Mini.getController()
    base_pv = cont.getBasePv()
    set_hdf5_filetemplate(base_pv)
    putvalue(base_pv, ":HDF5:LazyOpen", 0)
    putvalue(base_pv, ":HDF5:NDArrayPort", "XSP3")
    putvalue(base_pv, ":HDF5:PositionMode", "0")
    if collect_frame:
        collect_software_triggered_frame(base_pv, 0.1)
        collect_software_triggered_frame(base_pv, 0.1)


def set_medipix_collection_time(acq_time, dead_time=0.1) :
    sleep_detector.setCollectionTime(acq_time+dead_time)
    async_sleep_detector.sleep_time = acq_time + dead_time
    medipix_hardware_triggered_collectionstrategy.setCollectionTime(acq_time)
    

class SetupXspressMini(ScannableBase):
    
    def __init__(self, detector, name):
        super(SetupXspressMini, self).__init__(name)
        self.name = name
        self.inputNames = [name]
        self.setOutputFormat({});
        self.setInputNames({});
        self.det_name = detector.getName()
    
    def get_scan_info(self):
        h = InterfaceProvider.getCurrentScanInformationHolder()
        if h is not None:
            return h.getCurrentScanInformation()
        return h
    
    def atScanStart(self):
        scan_info = self.get_scan_info()
        if scan_info is None:
            print("Cannot setup "+self.det_name+" no scan is running")
            return
        
        det_names = scan_info.getDetectorNames()
        if self.det_name in det_names:
            print(self.name+" - running 'setup_xspress3mini' function")
            setup_xspress3mini(collect_frame=True)

    def stop(self):
        self.atScanEnd()
 
    def atCommandFailure(self):
        self.atScanEnd()
 
    def isBusy(self):
        return False
 
    def rawAsynchronousMoveTo(self,new_position):
        pass
 
    def rawGetPosition(self):
        return None

# add default scannable to setup xspress3Mini if it's included in scan comman
if object_exists("xspress3Mini"):
    xspress3mini_setup = SetupXspressMini(xspress3Mini, "xspress3mini_setup")
    add_default(xspress3mini_setup)

run_in_try_catch(setup_andor)
run_in_try_catch(setup_xmap)
run_in_try_catch(setup_xspress3Odin)
run_in_try_catch(setup_medipix)
run_in_try_catch(setup_xspress3mini)

setup_ffi0_channel()