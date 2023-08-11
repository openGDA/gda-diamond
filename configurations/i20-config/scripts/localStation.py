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

run "test-ionchamber-output.py"

# Create some functions useful for setting up and controlling the medipix ROIs
run "medipix_functions.py"

#  Make the spectrometer setup functions available
run "spectrometer-setup.py"

#  Run the detector setup functions
run "detector-setup.py"

# Create the 'energy transfer' scannables
run "energy-transfer-scannable.py"

# Create and setup topup checker with shutter
run "topup-scannable.py"

#### preparers ###
detectorPreparer = I20DetectorPreparer(sensitivities, sensitivity_units, offsets, offset_units, ionchambers, I1, xmapMca, medipix1, topupChecker)
# detectorPreparer.setFFI0(FFI0);
detectorPreparer.setMonoOptimiser(monoOptimiser)
detectorPreparer.setFFI1(FFI1)
detectorPreparer.setPluginsForMutableRoi(medipix1, getMedipixMutableRoiPlugins(medipix1))
detectorPreparer.setMutableRoi(medipix1, getMedipixMutableRoi(medipix1))
detectorPreparer.setPluginsForMutableRoi(medipix2, getMedipixMutableRoiPlugins(medipix2))
detectorPreparer.setMutableRoi(medipix2, getMedipixMutableRoi(medipix2))
detectorPreparer.setIonchamberChecker(ionchamberChecker)
detectorPreparer.setRunIonchamberChecker(True)

samplePreparer = I20SamplePreparer(filterwheel)
outputPreparer = I20OutputPreparer(datawriterconfig, datawriterconfig_xes, metashop, ionchambers, xmapMca, detectorPreparer)
beamlinePreparer = I20BeamlinePreparer()

XesOffsetsLower=Finder.find("XesOffsetsLower")
XesOffsetsUpper=Finder.find("XesOffsetsUpper")

theFactory = XesScanFactory();
theFactory.setBeamlinePreparer(beamlinePreparer);
theFactory.setDetectorPreparer(detectorPreparer);
theFactory.setSamplePreparer(samplePreparer);
theFactory.setOutputPreparer(outputPreparer);
theFactory.setLoggingScriptController(XASLoggingScriptController);
theFactory.setEnergyScannable(bragg1WithOffset);
theFactory.setMetashop(metashop);
theFactory.setIncludeSampleNameInNexusName(False);
theFactory.setScanName("")
theFactory.setXesBraggGroup(XESBraggGroup)
theFactory.setXesEnergyBoth(XESEnergyBoth)
theFactory.setXesEnergyGroup(XESEnergyGroup)
theFactory.setXesOffsetsList([XesOffsetsUpper, XesOffsetsLower])
xes = theFactory.createXesScan()
xes.setTwoDPlotter(xes_2d_plotter)
xes.setDetectorOrder([I1])

# Set the energy transfer scannables
energyTransferScnMap = {XESEnergyLower:XESEnergyTransferLower, XESEnergyUpper:XESEnergyTransferUpper, XESEnergyBoth:XESEnergyTransferBoth}
xes.setEnergyTransferScannables(energyTransferScnMap)

theFactory = XasScanFactory();
theFactory.setBeamlinePreparer(beamlinePreparer);
theFactory.setDetectorPreparer(detectorPreparer);
theFactory.setSamplePreparer(samplePreparer);
theFactory.setOutputPreparer(outputPreparer);
theFactory.setLoggingScriptController(XASLoggingScriptController);
theFactory.setEnergyScannable(bragg1WithOffset);
theFactory.setMetashop(metashop);
theFactory.setIncludeSampleNameInNexusName(False);
theFactory.setScanName("")

xas = theFactory.createEnergyScan();
xas.setDetectorOrder([ionchambers])
xas.setNexusTemplateFiles(["/dls_sw/i20/software/gda/config/yaml/xspress4-energy-link.yaml"])
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
    
if LocalProperties.isDummyModeEnabled() :
    print("\nSetting default scannables for GDA 'dummy' mode")
    remove_default([topupChecker])
    remove_default([absorberChecker])
else : 
    # to speed up step scans
    LocalProperties.set("gda.scan.concurrentScan.readoutConcurrently","true")
    LocalProperties.set("gda.scan.multithreadedScanDataPointPipeline.length","10")
    
    noBeam = ["Shutdown", "No Beam", "Mach. Dev."]
    print("\nSetting default scannables for current machine mode (%s)"%(machineModeMonitor.getPosition()))
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
add_default(detectorMonitorDataProvider)

# Make sure xes offset start at zero every time
XesOffsetsLower.removeAll()
XesOffsetsUpper.removeAll()

if LocalProperties.get("gda.mode") == "live":
    run "adc_monitor"
    #Don't include 'count_time' in medipix readout values. imh 18/1/2018 
    medipix1.getCollectionStrategy().setReadAcquisitionTime(False)
    medipix2.getCollectionStrategy().setReadAcquisitionTime(False)

else :        
    # Set collection time to ensure detector does not run too fast for scans that don't explicitly
    # set the collection time for the medipix 
    medipix1.setCollectionTime(0.5)
    medipix2.setCollectionTime(0.5)

set_initial_crystal_values(XESEnergyLower)
set_initial_crystal_values(XESEnergyUpper)
XesMotorOffsetsLower = Finder.find("XesMotorOffsetsLower")
XesMotorOffsetsUpper = Finder.find("XesMotorOffsetsUpper")

bragg1WithOffset.setAdjustBraggOffset(True) # True = Adjust bragg offset when moving to new energy

LocalProperties.set("gda.exafs.mono.energy.rate", "0.01");
LocalProperties.set("gda.exafs.read.out.time", "1000.0");

# cryostat.stop() # To stop the 'status' thread from running on the Lakeshore cryostat (fills logpanel with debug messages)

from gda.epics import CAClient

# Set default output format xspress4 ascii numbers
xspress4.setOutputFormat(["%.6f"])
xspress3X.setOutputFormat(["%.6f"])

print "\nSetting Tfg veto options to normal values for output 0"
DAServer.sendCommand("tfg setup-veto veto0-inv 0")
DAServer.sendCommand("tfg setup-veto veto0-drive 1")
DAServer.sendCommand("tfg alternate-veto veto0-normal")

print "\nReconnect daserver command : reconnect_daserver() "
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

# Increase speed of dummy test motor
test.setSpeed(10000)

# Sometimes the script logging controls does not connect to database initially -
# run 'reconfigure' to try connect again.
XASLoggingScriptController.reconfigure()

print "\n****GDA startup script complete.****\n\n"
