from gda.epics import CAClient
from org.slf4j import LoggerFactory
import traceback

print "Running detector_setup_functions.py"

run("xspress_functions.py")

# Set some scannables for Mythen, so they are added to header of output file
def setupMythen() :
    mythen.addScannableForHeader(qexafs_energy)
    mythen.addScannableForHeader(user1)
    mythenEpics.addScannableForHeader(qexafs_energy, "Energy")
    mythenEpics.addScannableForHeader(user1, "Motor angle")


# Reset XSPress3 settings : enable ROI and deadtime corrections, set to 'TTL Veto only' trigger mode
def setupXspress3() :
    if globals().has_key("xspress3") == False :
        print "Not running setupXspress3 - xspress3 detector is not present"
        return
    
    #Set the path to empty so default visit directory (and subdirectory) is used for hdf files
    xspress3.setFilePath("")
    
    if LocalProperties.isDummyModeEnabled() :
        return
    basePv = xspress3.getController().getEpicsTemplate()
    setup_xspress_detector(basePv)
    # controller.setPerformROICalculations(True) # PV doesn't exist for new IOC (17/6/2019 after shutdown upgrade)
    CAClient.put(basePv+":CTRL_DTC", 1)

def setupXspress3X() :
    basePvName = xspress3X.getController().getBasePv()

    setup_xspress_detector(basePvName)
    setupResGrades(basePvName, False)
    detPort = caget(basePvName+":PortName_RBV")
    set_hdf_input_port(basePvName, detPort)
    set_sca_input_port(basePvName, 4, detPort)
    set_hdf5_filetemplate(basePvName)
    for c in range(1, xspress3X.getController().getNumElements()+1) :
        # BL18B-EA-XSP3X-01:C2_SCAS:EnableCallbacks
        scaPv = basePvName+":C%d_SCAS:"%(c)
        mcaEnablePv = basePvName+":MCA%d:Enable"%(c)
        CAClient.put(scaPv+"EnableCallbacks", 1)
        CAClient.put(scaPv+"TS:TSNumPoints", 10000)
        CAClient.put(mcaEnablePv, 1)

    ## Set the HDf file path explicitely - for testing on beamline workstation in dummy mode
    # xspress3X.setFilePath("/dls/b18/data/2022/cm31142-4/xspress3")

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
    if globals().has_key("xspress4") == False :
        print "Not running setupXspress4 - xspress4 detector not present"
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
    
    collect_software_triggered_frame(basePv, 1.0)

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
    if medipix.isConfigured() == False :
        print "Not running setupMedipix - medipix detector has not been configured present"
        return

    CAClient.put(medipix_basePvName+":ARR:EnableCallbacks", 1)
    CAClient.put(medipix_basePvName+":ARR:MinCallbackTime", 0)
    cam_port = CAClient.get(medipix_basePvName+":CAM:PortName_RBV")
    CAClient.put(medipix_basePvName+":ARR:NDArrayPort", cam_port)

def setupPilatus() :
    print("Setting up Pilatus detector")
    
    adbase = pilatus_addetector.getAdBase()
    basePv = adbase.getBasePVName().replace("CAM:","")
    camPortName = adbase.getPortName_RBV()
    print("  Base Pilatus PV name : %s"%(basePv))
    arrayBasePv = pilatus_addetector.getNdArray().getBasePVName();
    fileBasePV = pilatus_addetector.getNdFile().getBasePVName()
    statsBasePV = pilatus_addetector.getNdStats().getBasePVName()
    
    print("  Setting array, file and stats plugin array ports to : %s"%(camPortName))
    CAClient.put(arrayBasePv+"NDArrayPort", camPortName)
    CAClient.put(fileBasePV+"NDArrayPort", camPortName)
    CAClient.put(statsBasePV+"NDArrayPort", camPortName)


def continuous_detector_scan(bufferedDetector, numReadouts, timePerReadout):
    # dummy_qexafs_energy = Finder.finf("dummy_qexafs_energy")
    qexafs_counterTimer01.setUseInternalTriggeredFrames(True)
    cvscan dummy_qexafs_energy 0.0 1.0 numReadouts numReadouts*timePerReadout bufferedDetector qexafs_counterTimer01

