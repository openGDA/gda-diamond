from gda.epics import CAClient
from org.slf4j import LoggerFactory
import traceback

print "Running detector_setup_functions.py"

# Set some scannables for Mythen, so they are added to header of output file
def setupMythen() :
    mythen.addScannableForHeader(qexafs_energy)
    mythen.addScannableForHeader(user1)
    mythenEpics.addScannableForHeader(qexafs_energy, "Energy")
    mythenEpics.addScannableForHeader(user1, "Motor angle")


# Reset XSPress3 settings : enable ROI and deadtime corrections, set to 'TTL Veto only' trigger mode
def setupXspress3() :
    #Set the path to empty so default visit directory (and subdirectory) is used for hdf files
    xspress3.setFilePath("")

    if LocalProperties.isDummyModeEnabled() :
        return

    from uk.ac.gda.devices.detector.xspress3 import TRIGGER_MODE
    controller=xspress3.getController()
    # controller.setPerformROICalculations(True) # PV doesn't exist for new IOC (17/6/2019 after shutdown upgrade)
    controller.setTriggerMode(TRIGGER_MODE.TTl_Veto_Only)
    CAClient.put(controller.getEpicsTemplate()+":CTRL_DTC", 1)


def caputXspress4(pv, value) :
    basePv = xspress4.getController().getBasePv()
    print "Setting Xspress4 PV : "+basePv+pv+" = "+str(value)
    CAClient.put(basePv+pv, value)

def caputXspress4Elements(format, value):
    for channel in range(1, xspress4.getNumberOfElements()+1) :
        caputXspress4(format%(channel), value)
   
#Setup xspress4
def setupXspress4() :
    if LocalProperties.isDummyModeEnabled() :
        return

    basePv = xspress4.getController().getBasePv()
    CAClient.putStringAsWaveform(basePv+":HDF5:FileTemplate", "%s%s%d.h5")
    caputXspress4(":HDF5:FileWriteMode", 2) #'stream' capture mode
    caputXspress4(":HDF5:AutoIncrement", 0) # auto increment off
    caputXspress4(":HDF5:EnableCallbacks", 1)

    # Enable callbacks on Scaler data plugins for all channels , set the max number of points
    # on array data to a large value
    caputXspress4Elements(":C%d_SCAS:EnableCallbacks", 1)
    caputXspress4Elements(":C%d_SCAS:TS:TSNumPoints", 10000)

    #Switch off callback for the 8 ROI and ARR plugins
    for num in range(1, 9) : 
        caputXspress4(":ROI"+str(num)+":EnableCallbacks", 0)
        caputXspress4(":ARR"+str(num)+":EnableCallbacks", 0)
    # xspress4.setTriggerMode(0) # software trigger mode
    xspress4.setTriggerMode(3) # TTL veto only trigger mode

    from uk.ac.gda.devices.detector.xspress4.Xspress4Detector import TriggerMode
    #qexafs_xspress4.setTriggerModeForContinuousScan(TriggerMode.Burst) # for testing without Tfg
    qexafs_xspress4.setTriggerModeForContinuousScan(TriggerMode.TtlVeto)
    
    qexafs_xspress4.setUseNexusTreeWriter(True)
    
    setEnableDtc(True)
    setEnableMca(False)

# Set array input port name for the scaler pluginss (one for each detector element)
def setScaArrayPorts(value) :
    caputXspress4Elements(":C%d_SCAS:NDArrayPort", value)

def setEnableMca(enable) :
    value = 0
    if enable :       
        value = 1
    
    caputXspress4Elements(":MCA%d:Enable", value)

def setEnableDtc(enable) :
    if enable :       
        print "Switching on Xspress4 DTC"
        setScaArrayPorts("XSP4.DTC")
        caputXspress4(":DTC:EnableCallbacks", 1)
        caputXspress4(":HDF5:EnableCallbacks", 1)
    else :
        print "Switching off Xspress4 DTC"
        setScaArrayPorts("XSP4")
        caputXspress4(":DTC:EnableCallbacks", 0)
        caputXspress4(":HDF5:EnableCallbacks", 0)
        
     
def setupMedipix() :
    CAClient.put(medipix_basePvName+":ARR:EnableCallbacks", 1)
    CAClient.put(medipix_basePvName+":ARR:MinCallbackTime", 0)
    cam_port = CAClient.get(medipix_basePvName+":CAM:PortName_RBV")
    CAClient.put(medipix_basePvName+":ARR:NDArrayPort", cam_port)

def run_in_try_catch(function):
    logger = LoggerFactory.getLogger("run_in_try_catch")

    try :
        print "Running ",function.__name__," function"
        function()
    except (Exception, java.lang.Throwable) as ex:
        stacktrace=traceback.format_exc()
        print("Problem running ",function.__name__," - see log for more details")
        print "Stack trace : ", stacktrace
        logger.warn("Problem running jython function {} {}", function.__name__, stacktrace)


def continuous_detector_scan(bufferedDetector, numReadouts, timePerReadout):
    # dummy_qexafs_energy = Finder.getInstance().finf("dummy_qexafs_energy")
    qexafs_counterTimer01.setUseInternalTriggeredFrames(True)
    cvscan dummy_qexafs_energy 0.0 1.0 numReadouts numReadouts*timePerReadout bufferedDetector qexafs_counterTimer01

