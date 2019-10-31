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


#Setup xspress4
def setupXspress4() :
    if LocalProperties.isDummyModeEnabled() :
        return

    basePv = xspress4.getController().getBasePv()
    CAClient.putStringAsWaveform(basePv+":HDF5:FileTemplate", "%s%s%d.h5")
    CAClient.put(basePv+":HDF5:FileWriteMode", 2) #'stream' capture mode
    CAClient.put(basePv+":HDF5:AutoIncrement", 0) # auto increment off

    # Enable callbacks on Scaler data plugins for all channels 
    for channel in range(0, xspress4.getNumberOfElements()) :
        CAClient.put(basePv+":C"+str(channel+1)+"_SCAS:EnableCallbacks", 1)

    # xspress4.setTriggerMode(0) # software trigger mode
    xspress4.setTriggerMode(3) # TTL veto only trigger mode

    from uk.ac.gda.devices.detector.xspress4.Xspress4Detector import TriggerMode
    # bufferedXspress4.setTriggerModeForContinuousScan(TriggerMode.Burst) # for testing without Tfg
    bufferedXspress4.setTriggerModeForContinuousScan(TriggerMode.TtlVeto)

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
