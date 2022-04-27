print "Initialization Started";

from uk.ac.gda.server.exafs.b18.scan.preparers import B18BeamlinePreparer
from uk.ac.gda.server.exafs.b18.scan.preparers import B18DetectorPreparer
from uk.ac.gda.server.exafs.b18.scan.preparers import B18SamplePreparer
from uk.ac.gda.server.exafs.b18.scan.preparers import B18OutputPreparer
from uk.ac.gda.server.exafs.scan import EnergyScan, QexafsScan, XasScanFactory
# from exafsscripts.exafs.qexafs_scan import QexafsScan
from gda.device.scannable import TopupChecker
from gda.device.scannable import BeamMonitor
from gda.device.scannable import MonoCoolScannable
from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from gda.jython.scriptcontroller.logging import LoggingScriptController
from gda.scan import ScanBase  #this is required for skip current repetition to work BLXVIIIB-99
from gda.device.monitor import EpicsMonitor
from gda.data.scan.datawriter import NexusDataWriter
# from exafsscripts.exafs.config_fluorescence_detectors import XspressConfig, VortexConfig, Xspress3Config
from gdascripts.metadata.metadata_commands import meta_add, meta_ll, meta_ls, meta_rm, meta_clear_alldynamical

XASLoggingScriptController = Finder.find("XASLoggingScriptController")
commandQueueProcessor = Finder.find("commandQueueProcessor")
# ExafsScriptObserver = Finder.find("ExafsScriptObserver")


datawriterconfig = Finder.find("datawriterconfig")
original_header = Finder.find("datawriterconfig").getHeader()[:]
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME, "metashop")

sensitivities = [i0_stanford_sensitivity, it_stanford_sensitivity, iref_stanford_sensitivity]
sensitivity_units = [i0_stanford_sensitivity_units, it_stanford_sensitivity_units, iref_stanford_sensitivity_units]
offsets = [i0_stanford_offset, it_stanford_offset, iref_stanford_offset]
offset_units = [i0_stanford_offset_units, it_stanford_offset_units, iref_stanford_offset_units]


if (LocalProperties.get("gda.mode") == 'live'):
    #detectorPreparer = B18DetectorPreparer(qexafs_energy, mythenEpics, sensitivities, sensitivity_units ,offsets, offset_units, ionc_gas_injectors.getGroupMembers(), counterTimer01)
    detectorPreparer = B18DetectorPreparer(qexafs_energy, mythen, sensitivities, sensitivity_units ,offsets, offset_units, ionc_gas_injectors.getGroupMembers(), counterTimer01)
else :
    #detectorPreparer = B18DetectorPreparer(qexafs_energy, mythenEpics, sensitivities, sensitivity_units ,offsets, offset_units, ionc_gas_injectors.getGroupMembers(), counterTimer01, xspress2system, xmapMca, xspress3)
    detectorPreparer = B18DetectorPreparer(qexafs_energy, mythen, sensitivities, sensitivity_units ,offsets, offset_units, ionc_gas_injectors.getGroupMembers(), counterTimer01)
daServer = Finder.find("DAServer")
samplePreparer = B18SamplePreparer(sam1, sam2, cryo, lakeshore, eurotherm, pulsetube, samplewheel, userstage)
outputPreparer = B18OutputPreparer(datawriterconfig,Finder.find("metashop"))
detectorPreparer.setSamplePreparer(samplePreparer)
detectorPreparer.setPilatusDetector(pilatus_addetector)

## Setup XspressOdin 
xspress4IsPresent = 'xspress4Odin' in locals()

if xspress4IsPresent :
    print "Setting up Xspress4Odin detector objects"
    detectorPreparer.addDetectorNameMapping("xspress4Odin", "qexafs_xspress4Odin")
    detectorPreparer.addDetectorNameMapping("xspress4OdinFFI0", "qexafs_FFI0_xspress4Odin")
    qexafs_xspress4Odin.setUseSwmrFileReading(True)

    # TTL veto for step and continuous scans
    xspress4Odin.setTriggerMode(3)
    qexafs_xspress4Odin.setTriggerModeForContinuousScan(3)
    xspress4Odin.setFilePrefix("xsp4_odin")
    xspress4Odin.setFilePath("") ## use current visit/comissioning folder

else :
    print "Xspress4Odin detector not present"



# TODO this could all be done in Sping XML
theFactory = XasScanFactory();
theFactory.setBeamlinePreparer(B18BeamlinePreparer());
theFactory.setDetectorPreparer(detectorPreparer);
theFactory.setSamplePreparer(samplePreparer);
theFactory.setOutputPreparer(outputPreparer);
theFactory.setLoggingScriptController(XASLoggingScriptController);
theFactory.setEnergyScannable(energy);
theFactory.setMetashop(Finder.find("metashop"));
theFactory.setIncludeSampleNameInNexusName(True);
theFactory.setQexafsDetectorPreparer(detectorPreparer);
theFactory.setQexafsEnergyScannable(qexafs_energy);
theFactory.setScanName("energyScan")

# qexafs_energy.setPcEncType(0) # set zebra encoder to use when capturing pulses (0..3 for enc1..3, 4 for the avg)

xas = theFactory.createEnergyScan();
xanes = xas
qexafs = theFactory.createQexafsScan()
vararg_alias("xas")
vararg_alias("xanes")
vararg_alias("qexafs")
alias("vortex")
alias("xspress")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")
alias("meta_clear_alldynamical")


from gda.jython.commands.ScannableCommands import cv as cvscan
vararg_alias("cvscan")
vararg_alias("cv")

print "Create topup, beam and mono motor temperature monitors to pause and resume scans"
topupMonitor = TopupChecker()
topupMonitor.setName("topupMonitor")
topupMonitor.setTolerance(5)
topupMonitor.setWaittime(1)
topupMonitor.setTimeout(60)
topupMonitor.setScannableToBeMonitored(topup)

beamMonitor = BeamMonitor()
beamMonitor.setName("beamMonitor")
if (LocalProperties.get("gda.mode") == 'live'):
    beamMonitor.setMachineModeMonitor(machineModeMonitor)
beamMonitor.setShutterPVs(["FE18B-PS-SHTR-01:STA", "FE18B-PS-SHTR-01:STA"])  # there are two shutters, it looks like only shutter 1 is operated!
beamMonitor.setPauseBeforeScan(True)  # for qexafs, test FE and machine current at the start of each scan
beamMonitor.configure()

monoCooler = MonoCoolScannable()
monoCooler.setName("monoCooler")
monoCooler.setMotorTempPV("BL18B-OP-DCM-01:TEMP4")
monoCooler.setCoolingTimeout(1800)
monoCooler.setTemperatureLimit(125)
monoCooler.setTemperatureCoolLevel(100)
monoCooler.configure()

from gdascripts.pd.time_pds import showtimeClass
showtime = showtimeClass("showtime")
showtime.setLevel(4) # so it is operated before anything else in a scan

if (LocalProperties.get("gda.mode") == 'live'):
    sample_temperature = EpicsMonitor()
    sample_temperature.setName("sample_temperature")
    sample_temperature.setExtraNames(["sample_temperature"])
    sample_temperature.setPvName("ME08G-EA-GIR-01:TEMP1")

    blower_temperature = EpicsMonitor()
    blower_temperature.setName("blower_temperature")
    blower_temperature.setExtraNames(["blower_temperature"])
    blower_temperature.setPvName("ME08G-EA-GIR-01:TCTRL1:PV:RBV")

    add_default(topupMonitor)
    add_default(beamMonitor)
    add_default(detectorMonitorDataProvider)
    add_default(daServerChecker)
else :
    print "Moving dummy DCM's to useful positions..."
    energy(7000) # start the simulation with an energy in a useful range
    qexafs_energy(7000)
    print "...moves done";
    print "Switching off Xspress3 file writing"
    xspress3.setWriteHDF5Files(False)


# TODO move this to Spring config?
from uk.ac.gda.beamline.b18.scannable import SimpleEpicsTemperatureController
generic_cryostat = SimpleEpicsTemperatureController()
generic_cryostat.setName("generic_cryostat")
generic_cryostat.setSetPointPVName("BL18B-EA-TEMPC-06:TTEMP")  # currently OxInst ITC4 Cryojet
generic_cryostat.setReadBackPVName("BL18B-EA-TEMPC-06:STEMP")
generic_cryostat.configure()

print "Reconnect daserver command : reconnect_daserver() "
def reconnect_daserver() :
    print "Trying to reconnect to DAServer..."
    daServer.reconnect()
    xspress2system.reconfigure()
    counterTimer01.configure()
    print "Ignore this error (it's 'normal'...)"
    counterTimer01.getScaler().clear()

# Set nexusTreeWriter flag for buffered xspress2
qexafs_xspress.setUseNexusTreeWriter(True)
# qexafs_xspress.setUseNexusTreeWriter(False) # needs to be False when used for 2d scan with continuous scan for inner axis.

samplewheel_names.setPositions( samplewheel.getFilterNames() )

# Set the zebra PC_pulse output for triggering the TFG. 3/4/2019
zebra_device = Finder.find("zebra_device")
zebra_device.setOutTTL(1, 31)

# Setup the plugin listst used to control the medipix ROI
run("medipix_functions.py")
setUseMedipixRoiFromGui(False)
setMedipixRoi(0, 0, 512, 512)

# Set the plugin list and ROI object to use for setting the medipix ROI
detectorPreparer.setMedipixPlugins(plugins_mutable_roi)
detectorPreparer.setMedipixMutableRoi(medipix_roi)

run("detector_setup_functions.py")
run_in_try_catch(setupMedipix)
run_in_try_catch(setupXspress3)
run_in_try_catch(setupXspress4)
run_in_try_catch(setupMythen)
run_in_try_catch(setupPilatus)

run("continuous_scans.py")
# run("meca_status.py")

from gda.data.metadata import GDAMetadataProvider
def setVisit(visitStr) :
    metaDataProv=GDAMetadataProvider.getInstance()
    currentVisit=metaDataProv.getMetadataValue("visit") # current visit
    metaDataProv.setMetadataValue("visit", visitStr) # set the new visit
    print "Changing visit from ",currentVisit," to ",visitStr

def pwd() :
    return InterfaceProvider.getPathConstructor().createFromDefaultProperty()

#Setup xspress4Odin for testng continuus scans (dummy mode, with 'live' detector, software and burst mode triggering)
def setup_xspressOdin(filename="") :

    # Write files to comissioning directory
    xspress4Odin.setFilePath("/dls/b18/data/2022/cm31142-3/tmp")

    # Setup trigger modes for testing : Software triggered mode for scans :
    xspress4Odin.setTriggerMode(0)

    # 'Burst mode' for continuous scan
    qexafs_xspress4Odin.setTriggerModeForContinuousScan(2)


# Times for 10000 frame scans : ~6sec (maxReadFrames=2000), ~7 sec (maxReadFrames=1000)
def test_xspressOdin(numPoints=10000, maxReadFrames=1000, scanTime=10) :
    from time import time
    #setup_xspressOdin("/dls/p99/data/2022/cm31335-2/tmp/test_10000frames_meta.h5")
    
    # setup_xspressOdin("/dls/b18/data/2022/cm31142-3/tmp/xsp4_odin_544490_meta.h5")
    
    qexafs_xspress4Odin.setMaximumReadFrames(maxReadFrames) 
    qexafs_counterTimer01.setUseInternalTriggeredFrames(True)
    startTime = time()
    #qexafs_counterTimer0
    cv(dummy_qexafs_energy,2000,3000,numPoints, scanTime, [qexafs_xspress4Odin])
    print("Scan with %d num points (readframes = %d) : %.2f sec"%(numPoints, maxReadFrames, time()-startTime) )



alias("pwd")

if (LocalProperties.get("gda.mode") == 'live'):
    print "Running user startup script"
    run("userStartupScript")
    print "User startup scripts finished"

# Set the scaler dead frame time (for continuous detector scans with medipix)
print 'Tfg frame dead time : set using qexafs_counterTimer01.setFrameDeadTime(1e-6) (time in seconds)'
print 'Deadtime is currently set to : '+str(qexafs_counterTimer01.getFrameDeadTime())+" secs"

print "Initialization Complete";
