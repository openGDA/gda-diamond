print "\n\n****Running the I20 startup script****\n\n"

from time import sleep

from gda.device.detector import DetectorMonitorDataProvider

from gdascripts.metadata.metadata_commands import meta_add,meta_ll,meta_ls,meta_rm, meta_clear_alldynamical
from gdascripts.pd.time_pds import showtimeClass, waittime
#import mono_calibration 
from vortex_elements import VortexElements

from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import NexusDataWriter
from gda.device.scannable import TwoDScanPlotter
from gda.factory import Finder

from uk.ac.gda.server.exafs.scan import EnergyScan, XesScan, XesScanFactory, XasScanFactory
from uk.ac.gda.server.exafs.scan.preparers import I20DetectorPreparer, I20OutputPreparer, I20SamplePreparer, I20BeamlinePreparer

DAServer = Finder.find("DAServer")
XASLoggingScriptController = Finder.find("XASLoggingScriptController")
datawriterconfig = Finder.find("datawriterconfig")

datawriterconfig_xes = Finder.find("datawriterconfig_xes")
metashop = Finder.find("metashop")
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop")

sensitivities = [i0_stanford_sensitivity, it_stanford_sensitivity,iref_stanford_sensitivity,i1_stanford_sensitivity]
sensitivity_units = [i0_stanford_sensitivity_units,it_stanford_sensitivity_units,iref_stanford_sensitivity_units,i1_stanford_sensitivity_units]
offsets = [i0_stanford_offset,it_stanford_offset,iref_stanford_offset,i1_stanford_offset]
offset_units = [i0_stanford_offset_units,it_stanford_offset_units,iref_stanford_offset_units,i1_stanford_offset_units]

xmapController = Finder.find("xmapcontroller")
if LocalProperties.get("gda.mode") == "live":
    from vortex_elements import VortexElements
    vortexElements = VortexElements(edxdcontroller, xmapController, xmapMca)
    vortexDetector = Finder.find("vortexDetector")
else :
    # In dummy mode, set event processing times to be consistent with number of elements on detector.
    xmapMca.setEventProcessingTimes( [1.2039752e-7]*xmapController.getNumberOfElements() )

# Create DTC_energy scannable to set, get the XSpress4 DTC energy value
run 'xspress4_dtc_energy_scannable.py'

# Create and setup the monoOptimiser scannable
run "mono_optimisation.py"

# Create some functions useful for setting up and controlling the medipix ROIs
run "medipix_functions.py"

#### preparers ###
detectorPreparer = I20DetectorPreparer(sensitivities, sensitivity_units, offsets, offset_units, ionchambers, I1, xmapMca, medipix, topupChecker)
# detectorPreparer.setFFI0(FFI0);
detectorPreparer.setMonoOptimiser(monoOptimiser)
detectorPreparer.setFFI1(FFI1)
detectorPreparer.setPluginsForMutableRoi(plugins_mutable_roi)
detectorPreparer.setMutableRoi(medipix_roi)
detectorPreparer.setMedipixDefaultBasePvName(medipix_basePvName)

samplePreparer = I20SamplePreparer(filterwheel)
outputPreparer = I20OutputPreparer(datawriterconfig, datawriterconfig_xes, metashop, ionchambers, xmapMca, detectorPreparer)
beamlinePreparer = I20BeamlinePreparer()

xesOffsets=Finder.find("XesOffsets")

theFactory = XesScanFactory();
theFactory.setBeamlinePreparer(beamlinePreparer);
theFactory.setDetectorPreparer(detectorPreparer);
theFactory.setSamplePreparer(samplePreparer);
theFactory.setOutputPreparer(outputPreparer);
theFactory.setLoggingScriptController(XASLoggingScriptController);
theFactory.setEnergyScannable(bragg1WithOffset);
theFactory.setMetashop(metashop);
theFactory.setIncludeSampleNameInNexusName(False);
theFactory.setScanName("xas")
theFactory.setAnalyserAngle(XESBragg)
theFactory.setXes_energy(XESEnergy)
theFactory.setXesOffsets(xesOffsets)
xes = theFactory.createXesScan()
xes.setTwoDPlotter(xes_2d_plotter)

theFactory = XasScanFactory();
theFactory.setBeamlinePreparer(beamlinePreparer);
theFactory.setDetectorPreparer(detectorPreparer);
theFactory.setSamplePreparer(samplePreparer);
theFactory.setOutputPreparer(outputPreparer);
theFactory.setLoggingScriptController(XASLoggingScriptController);
theFactory.setEnergyScannable(bragg1WithOffset);
theFactory.setMetashop(metashop);
theFactory.setIncludeSampleNameInNexusName(False);
theFactory.setScanName("energyScan")

xas = theFactory.createEnergyScan();
xanes = xas

vararg_alias("xas")
vararg_alias("xanes")
vararg_alias("xes")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")
alias("meta_clear_alldynamical")

current_store_tracker = "none"

scansReturnToOriginalPositions = 0

print "Creating some scannables useful for recording time during scans..."
print "Creating scannable 'w' which will delay scan points until a time has been reached during a scan."\
+ "\nusage of 'w':    scan <motor> <start> <stop> <step> w 0 <delay between points in s>\n\n"

w = showtimeClass("w")
w.setLevel(10)

def stopCryostat() :
    setpoint = cryostat.getController().getSetpoint()
    print "Stopping cryostat status thread and reapplying the original setpoint ("+str(setpoint)+" K)"
    cryostat.stop() ## to stop the monitor thread; also overwrites setpoint with current temperature
    # Re-apply the original setpoint value
    cryostat.getController().setSetpointControl( setpoint )

def machineMode() :
    try :
        return machineMode()
    except Exception :
        # in case the machine mode monitor is missing
        return "Shutdown"
    

if LocalProperties.get("gda.mode") == "live":
    # to speed up step scans
    LocalProperties.set("gda.scan.concurrentScan.readoutConcurrently","true")
    LocalProperties.set("gda.scan.multithreadedScanDataPointPipeline.length","10")
    
    noBeam = ["Shutdown", "No Beam", "Mach. Dev."]
    print "Machine mode = ", machineModeMonitor.getPosition()
    if machineModeMonitor.getPosition() in noBeam :
        print "Removing absorber, shutter and topup checkers"        
        remove_default([topupChecker])
        remove_default([absorberChecker])
        remove_default([shutterChecker])
        stopCryostat()
    else:
        add_default([topupChecker])
        add_default([absorberChecker])
        add_default([shutterChecker])
else:
    remove_default([topupChecker])
    remove_default([absorberChecker])

# Make sure xes offset start at zero every time
xesOffsets.removeAll()


if LocalProperties.get("gda.mode") == "live":
    run "adc_monitor"
    #Don't include 'count_time' in medipix readout values. imh 18/1/2018 
    medipix.getCollectionStrategy().setReadAcquisitionTime(False)
else :
    if material() == None:
        material('Si')
    # Set positions of some scannables to reasonable positions so that XESBragg calculation has a chance of working
    pos det_y 475.0
    pos xtal_x 1000.0
    pos radius 1000.0

    # Set ROI plugin base pv name : real detector uses 'ROI1', simulated area detector uses 'ROI:'
    detectorPreparer.setRoiPvName("ROI:")


bragg1WithOffset.setAdjustBraggOffset(True) # True = Adjust bragg offset when moving to new energy

LocalProperties.set("gda.exafs.mono.energy.rate", "0.01");
LocalProperties.set("gda.exafs.read.out.time", "1000.0");
add_default detectorMonitorDataProvider

# cryostat.stop() # To stop the 'status' thread from running on the Lakeshore cryostat (fills logpanel with debug messages)

from gda.epics import CAClient

# Set default output format xspress4 ascii numbers
xspress4.setOutputFormat(["%.6f"])

print "Setting Tfg veto options to normal values for output 0"
DAServer.sendCommand("tfg setup-veto veto0-inv 0")
DAServer.sendCommand("tfg setup-veto veto0-drive 1")
DAServer.sendCommand("tfg alternate-veto veto0-normal")

print "Reconnect daserver command : reconnect_daserver() "
def reconnect_daserver() :
    print "Trying to reconnect to DAServer and rerun ~config..."
    DAServer.reconnect()
    sleep(1)
    # xspress2system.reconfigure()
    print "Configuring ionchambers..."
    ionchambers.configure()
    sleep(1)
    print "Ignore this error (it's 'normal'...)"
    ionchambers.getScaler().clear()


print "\nNew reconnect daserver command : reconnect_daserver_new() "
def reconnect_daserver_new() :
    print "Closing connection to DAServer..."
    mem = ionchambers.getScaler()
    mem.close()
    sleep(1)
    DAServer.close()
    sleep(1)
    
    print "Trying to reconnect to DAServer..."
    DAServer.reconfigure()
    sleep(1)
    mem.clear()

# Set initial values of allowedToMove scannables for XES spectrometer crystals
for scn in [ minusCrystalAllowedToMove, centreCrystalAllowedToMove, plusCrystalAllowedToMove ] :
    if scn.getPosition() == None :
        print "Setting initial value of {0} to true".format(scn.getName())
        scn.moveTo("true")

for scn in [ cut1, cut2, cut3 ] :
    if scn.getPosition() == None :
        print "Setting initial value of {0} to 1".format(scn.getName())
        scn.moveTo(1)


run 'xspress_functions.py'

""" setupXspress3 and setupXSpress4 use functions from xspress_functions.py """

def setupXspress3() :
    xspress3Controller = xspress3.getController()
    basePvName = xspress3Controller.getEpicsTemplate()
    setup_xspress_detector(basePvName)
            
    detPort = caget(basePvName+":PortName_RBV")
    set_hdf_input_port(basePvName, detPort)

def setupXspress4() : 
    hdf5Values = { "FileTemplate" : "%s%s%d.hdf"}
    print "Setting up XSpress4 : "
    basename = xspress4.getController().getBasePv()
    setup_xspress_detector(basename)  # set the trigger mode, 1 frame of data to set data dimensions

    # Set the default deadtime correction energy if not already non-zero
    if xspress4.getDtcEnergyKev() == 0 :
        print "  Setting deadtime correction energy to 10Kev"
        xspress4.setDtcEnergyKev(10)
         
    # # Set to empty string, so that at scan start path is set to current visit directory.
    xspress4.setFilePath("");
    for key in hdf5Values :
        pv = basename + ":HDF5:" + key
        print "  Setting " + pv + " to " + hdf5Values[key]
        CAClient.putStringAsWaveform(pv, hdf5Values[key])

def setupMedipix() :
    global medipix_basePvName
    print "Setting up Medipix"
    collect_software_triggered_frame(medipix_basePvName+":CAM", 1.0)
    
run_in_try_catch(setupXspress3)
run_in_try_catch(setupXspress4)
run_in_try_catch(setupMedipix)

print "****GDA startup script complete.****\n\n"
