print "Running detector-setup.py"

run 'xspress_functions.py'

""" setupXspress3 and setupXSpress4 use functions from xspress_functions.py """

def setupXspress3() :
    xspress3Controller = xspress3.getController()
    basePvName = xspress3Controller.getEpicsTemplate()
    setup_xspress_detector(basePvName)
    setupResGrades(basePvName, False)
            
    detPort = caget(basePvName+":PortName_RBV")
    set_hdf_input_port(basePvName, detPort)
    set_sca_input_port(basePvName, 4, detPort)
    set_hdf5_filetemplate(basePvName)

def setupXspress3X() :
    basePvName = xspress3X.getController().getBasePv()

    setup_xspress_detector(basePvName)
    setupResGrades(basePvName, False)
    detPort = caget(basePvName+":PortName_RBV")
    set_hdf_input_port(basePvName, detPort)
    set_sca_input_port(basePvName, 4, detPort)
    set_hdf5_filetemplate(basePvName)
         
def setupXspress4() : 
    print "Setting up XSpress4 : "
    
    #arrayCounter = ":ArrayCounter_RBV" # Old Xspress4 IOC
    arrayCounter = ":ARR:ArrayCounter_RBV" # New Xspress4 IOC (13April2022)
    print("Setting Array counter RBV PV to :%s"%(arrayCounter))
    xspress4.getController().setArrayCounterRbvName(arrayCounter)
    # Recreate the PVs
    xspress4.getController().afterPropertiesSet()
    
    basename = xspress4.getController().getBasePv()
    
    # setupResGrades(basename, True)
    setup_xspress_detector(basename)  # set the trigger mode, 1 frame of data to set data dimensions

    # Set the default deadtime correction energy if not already non-zero
    if xspress4.getDtcEnergyKev() == 0 :
        print "  Setting deadtime correction energy to 10Kev"
        xspress4.setDtcEnergyKev(10)
         
    # # Set to empty string, so that at scan start path is set to current visit directory.
    xspress4.setFilePath("");
    set_hdf5_filetemplate(basename)

def setupMedipix() :
    global medipix_basePvName
    print "Setting up Medipix"
    collect_software_triggered_frame(medipix_basePvName+":CAM", 1.0)

def setupDetectors() :
    if LocalProperties.isDummyModeEnabled() :
        return
    
    print("Running detector setup functions...")
    run_in_try_catch(setupXspress3)
    run_in_try_catch(setupXspress3X)
    run_in_try_catch(setupXspress4)
    run_in_try_catch(setupMedipix)
    
setupDetectors()