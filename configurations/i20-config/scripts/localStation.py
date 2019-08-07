from gda.device.detector import DetectorMonitorDataProvider
print "\n\n****Running the I20 startup script****\n\n"

from time import sleep

from devices import RealBlades
from devices.RealBlades import BladeAngle
from devices.RealBlades import SubtractAngle
from devices.RealBlades import AverageAngle
# from exafsscripts.exafs.config_fluoresence_detectors import XspressConfig, VortexConfig
from gdascripts.metadata.metadata_commands import meta_add,meta_ll,meta_ls,meta_rm, meta_clear_alldynamical
from gdascripts.pd.time_pds import showtimeClass, waittime
#import mono_calibration 
from vortex_elements import VortexElements
from xes.xes_offsets import XESOffsets
from xes.xes_calculate import XESCalculate

from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import NexusDataWriter
from gda.device.scannable import DummyScannable
from gda.device.scannable import TwoDScanPlotter
from gda.jython import JythonServerFacade
from gda.scan import ScanBase
from uk.ac.gda.server.exafs.scan import EnergyScan, XesScan, XesScanFactory, XasScanFactory
from uk.ac.gda.server.exafs.scan.preparers import I20DetectorPreparer, I20OutputPreparer, I20SamplePreparer, I20BeamlinePreparer


DAServer = finder.find("DAServer")
rcpController = finder.find("RCPController")
XASLoggingScriptController = Finder.getInstance().find("XASLoggingScriptController")
commandQueueProcessor = Finder.getInstance().find("commandQueueProcessor")
ExafsScriptObserver = Finder.getInstance().find("ExafsScriptObserver")
datawriterconfig = Finder.getInstance().find("datawriterconfig")
original_header = Finder.getInstance().find("datawriterconfig").getHeader()[:]

datawriterconfig_xes = Finder.getInstance().find("datawriterconfig_xes")
original_header_xes = Finder.getInstance().find("datawriterconfig").getHeader()[:]
metashop = Finder.getInstance().find("metashop")
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop")

sensitivities = [i0_stanford_sensitivity, it_stanford_sensitivity,iref_stanford_sensitivity,i1_stanford_sensitivity]
sensitivity_units = [i0_stanford_sensitivity_units,it_stanford_sensitivity_units,iref_stanford_sensitivity_units,i1_stanford_sensitivity_units]
offsets = [i0_stanford_offset,it_stanford_offset,iref_stanford_offset,i1_stanford_offset]
offset_units = [i0_stanford_offset_units,it_stanford_offset_units,iref_stanford_offset_units,i1_stanford_offset_units]

xmapController = Finder.getInstance().find("xmapcontroller")
if LocalProperties.get("gda.mode") == "live":
    from vortex_elements import VortexElements
    vortexElements = VortexElements(edxdcontroller, xmapController, xmapMca)
    vortexDetector = Finder.getInstance().find("vortexDetector")
else :
    # In dummy mode, set event processing times to be consistent with number of elements on detector.
    xmapMca.setEventProcessingTimes( [1.2039752e-7]*xmapController.getNumberOfElements() )

# Create DTC_energy scannable to set, get the XSpress4 DTC energy value
run 'xspress4_dtc_energy_scannable.py'

# Create and setup the monoOptimiser scannable
run "mono_optimisation.py"

#### preparers ###
detectorPreparer = I20DetectorPreparer(sensitivities, sensitivity_units, offsets, offset_units, ionchambers, I1, xmapMca, medipix, topupChecker)
# detectorPreparer.setFFI0(FFI0);
detectorPreparer.setMonoOptimiser(monoOptimiser)
detectorPreparer.setFFI1(FFI1)

samplePreparer = I20SamplePreparer(filterwheel)
outputPreparer = I20OutputPreparer(datawriterconfig, datawriterconfig_xes, metashop, ionchambers, xmapMca, detectorPreparer)
beamlinePreparer = I20BeamlinePreparer()

twodplotter = TwoDScanPlotter()
twodplotter.setName("twodplotter")

store_dir = LocalProperties.getVarDir() +"xes_offsets/"
xes_offsets = XESOffsets(store_dir, spectrometer)
xes_calculate = XESCalculate(xes_offsets, material, cut1, cut2, cut3, radius)
xesOffsets=Finder.getInstance().find("XesOffsets")

theFactory = XesScanFactory();
theFactory.setBeamlinePreparer(beamlinePreparer);
theFactory.setDetectorPreparer(detectorPreparer);
theFactory.setSamplePreparer(samplePreparer);
theFactory.setOutputPreparer(outputPreparer);
# theFactory.setCommandQueueProcessor(commandQueueProcessor);
theFactory.setLoggingScriptController(XASLoggingScriptController);
theFactory.setEnergyScannable(bragg1WithOffset);
theFactory.setMetashop(metashop);
theFactory.setIncludeSampleNameInNexusName(False);
# theFactory.setOriginal_header(original_header);
theFactory.setScanName("xas")
theFactory.setAnalyserAngle(XESBragg)
theFactory.setXes_energy(XESEnergy)
theFactory.setXesOffsets(xesOffsets)
xes = theFactory.createXesScan()

theFactory = XasScanFactory();
theFactory.setBeamlinePreparer(beamlinePreparer);
theFactory.setDetectorPreparer(detectorPreparer);
theFactory.setSamplePreparer(samplePreparer);
theFactory.setOutputPreparer(outputPreparer);
theFactory.setLoggingScriptController(XASLoggingScriptController);
theFactory.setEnergyScannable(bragg1WithOffset);
theFactory.setMetashop(metashop);
theFactory.setIncludeSampleNameInNexusName(False);
#theFactory.setQexafsDetectorPreparer(detectorPreparer);
#theFactory.setQexafsEnergyScannable(qexafs_energy);
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
        cryostat.stop()
    else:
        add_default([topupChecker])
        add_default([absorberChecker])
        add_default([shutterChecker])
else:
    remove_default([topupChecker])
    remove_default([absorberChecker])

#
# XES offsets section
#
#from xes import offsetsStore, setOffsets
#offsetsStore = offsetsStore.XESOffsets()
#offsetsStore.removeAllOffsets()

# Make sure xes offset start at zero every time
xes_offsets.removeAll()


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

    #Set medupux base PV name (using areadetector)
    simulated_addetector_pv=medipix_addetector.getAdBase().getBasePVName()
    detectorPreparer.setMedipixDefaultBasePvName(simulated_addetector_pv)
    # PVs to use for ROI and STAT area detector plugins (real detector usings ROI1, STAT1,
    # which are not available in simulated area detector)
    detectorPreparer.setRoiPvName("ROI:")
    detectorPreparer.setStatPvName("STAT:")


bragg1WithOffset.setAdjustBraggOffset(True) # True = Adjust bragg offset when moving to new energy

LocalProperties.set("gda.exafs.mono.energy.rate", "0.01");
LocalProperties.set("gda.exafs.read.out.time", "1000.0");
add_default detectorMonitorDataProvider

# cryostat.stop() # To stop the 'status' thread from running on the Lakeshore cryostat (fills logpanel with debug messages)

from gda.epics import CAClient
## Set file path and filename format if using 'real' XSpress4 detector
hdf5Values = { "FileTemplate" : "%s%s%d.hdf"}
if xspress4.isConfigured() == True and xspress4.getXspress3Controller().isConfigured() and LocalProperties.get("gda.mode") == "live" :
     xspress4.setTriggerMode(3) # set 'TTL only' trigger mode
     ## Set to empty string, so that at scan start path is set to current visit directory.
     xspress4.setFilePath("");
     basename = xspress4.getController().getBasePv()
     for key in hdf5Values :
        pv = basename+":HDF5:"+key
        print "Setting "+pv+" to "+hdf5Values[key]
        CAClient.putStringAsWaveform(pv, hdf5Values[key])

# Set default output format xspress4 ascii numbers
xspress4.setOutputFormat(["%.6g"])

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

# Function for setting exposure time and setting continuous acquisition
# Called in ADControllerBase.setExposure(time) - see client side medipixADController bean
# (injected using setExposureTimeCmd )
def setMedipixExposureAndStart(exposureTime) :
    continuousModeIndex = 2 # ImageMode.CONTINUOUS.ordinal()
    adbase = medipix_addetector.getAdBase()

    adbase.setAcquireTime(exposureTime);
    adbase.setAcquirePeriod(0.0);
    adbase.setImageMode(continuousModeIndex);
    adbase.startAcquiring();

# Set initial values of allowedToMove scannables for XES spectrometer crystals
for scn in [ minusCrystalAllowedToMove, centreCrystalAllowedToMove, plusCrystalAllowedToMove ] :
    if scn.getPosition() == None :
        print "Setting initial value of {0} to true".format(scn.getName())
        scn.moveTo("true")

#Set xspress3 triggermode to TTL veto and array port for HDF5 writing
# (this is copied from i20-1's localStation ...)  imh 4/7/2019
if LocalProperties.isDummyModeEnabled() == False :
    xspress3Controller = xspress3.getController()
    if xspress3Controller != None and xspress3Controller.isConfigured() :
        print "Setting up XSpress3 : "
        print "  Trigger mode = 'TTL Veto Only'"
        from uk.ac.gda.devices.detector.xspress3 import TRIGGER_MODE
        xspress3Controller.setTriggerMode(TRIGGER_MODE.TTl_Veto_Only)

	basePvName = xspress3Controller.getEpicsTemplate()
        detPort = CAClient.get(basePvName+":PortName_RBV")
        print "  HDF5 array port name = ", detPort
        CAClient.put(basePvName+":HDF5:NDArrayPort", detPort)

print "****GDA startup script complete.****\n\n"
