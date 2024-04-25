print "\nRunning detector-setup.py"

from uk.ac.gda.devices.detector.xspress4 import XspressPvProviderBase

run 'xspress_functions.py'

""" setupXspress3 and setupXSpress4 use functions from xspress_functions.py """

def connectionPvExists(basePvName) :
    return XspressPvProviderBase.pvExists(basePvName+":CONNECTED")

def setupXspress3() :
    xspress3Controller = xspress3.getController()
    basePvName = xspress3Controller.getBasePv()
    if connectionPvExists(basePvName) == False :
        print("  Not setting up Xspress3 - IOC seems to be not running");
        return

    setup_xspress_detector(basePvName)
    setupResGrades(basePvName, False)
            
    detPort = caget(basePvName+":PortName_RBV")
    set_hdf_input_port(basePvName, detPort)
    set_sca_input_port(basePvName, 4, detPort)
    set_hdf5_filetemplate(basePvName)
    print("Finished setting up Xspress3 detector")

def setupXspress3X() :
    basePvName = xspress3X.getController().getBasePv()
    
    if connectionPvExists(basePvName) == False :
        print("  Not setting up Xspress3X - IOC seems to be not running");
        return
    
    setup_xspress_detector(basePvName)
    setupResGrades(basePvName, False)
    detPort = caget(basePvName+":PortName_RBV")
    set_hdf_input_port(basePvName, detPort)
    set_sca_input_port(basePvName, 4, detPort)
    set_hdf5_filetemplate(basePvName)
    xspress3X.setMcaReadoutWaitTimeMs(3000)
    print("Finished setting up Xspress3X detector")
     
def setupXspress4() : 
    basename = xspress4.getController().getBasePv()

    if connectionPvExists(basename) == False :
        print("  Not setting up Xspress4 - IOC seems to be not running");
        return
    
    # setupResGrades(basename, True)
    setup_xspress_detector(basename)  # set the trigger mode, 1 frame of data to set data dimensions

    # Set the default deadtime correction energy if not already non-zero
    if xspress4.getDtcEnergyKev() == 0 :
        print "  Setting deadtime correction energy to 10Kev"
        xspress4.setDtcEnergyKev(10)
         
    # # Set to empty string, so that at scan start path is set to current visit directory.
    xspress4.setFilePath("");
    set_hdf5_filetemplate(basename)
    xspress4.setMcaReadoutWaitTimeMs(500)
    xspress4.getController().setCounterWaitTimeMs(50)

    print("Finished setting up Xspress4 detector")

def setupDetectors() :
    if LocalProperties.isDummyModeEnabled() :
        return
    
    print("Running detector setup functions...")
    run_in_try_catch(setupXspress3)
    run_in_try_catch(setupXspress3X)
    run_in_try_catch(setupXspress4)
    
setupDetectors()