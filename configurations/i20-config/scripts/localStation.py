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

from org.jscience.physics.quantities import Quantity
from org.jscience.physics.units import Unit

from gda.configuration.properties import LocalProperties
from gda.data.scan.datawriter import NexusDataWriter
from gda.device.scannable import DummyScannable
from gda.device.scannable import TwoDScanPlotter
from gda.jython import JythonServerFacade
from gda.scan import ScanBase
from uk.ac.gda.server.exafs.scan import EnergyScan, XesScan, XesScanFactory, XasScanFactory
from uk.ac.gda.server.exafs.scan.preparers import I20DetectorPreparer, I20OutputPreparer, I20SamplePreparer, I20BeamlinePreparer


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

if LocalProperties.get("gda.mode") == "live":
    xmapController = Finder.getInstance().find("xmapcontroller")
    from vortex_elements import VortexElements
    vortexElements = VortexElements(edxdcontroller, xmapController, xmapMca)
    vortexDetector = Finder.getInstance().find("vortexDetector")
# xspressConfig = XspressConfig(xspress2system, ExafsScriptObserver)
# xspressConfig.initialize()
# alias("xspressConfig")
# 
# vortexConfig = VortexConfig(xmapMca, ExafsScriptObserver)
# vortexConfig.initialize()
# alias("vortexConfig")

#detectorPreparer = I20DetectorPreparer(xspress2system, XASLoggingScriptController,sensitivities, sensitivity_units ,offsets, offset_units,cryostat,ionchambers,I1,xmapMca,topupChecker,xspressConfig, vortexConfig)
#samplePreparer = I20SamplePreparer(sample_x,sample_y,sample_z,sample_rot,sample_fine_rot,sample_roll,sample_pitch,filterwheel, cryostat, cryostick_pos, rcpController)
#outputPreparer = I20OutputPreparer(datawriterconfig,datawriterconfig_xes)

# Create mono optimiser object - this will also need sending into one of the preparers... imh 31/8/2016
from gda.device.scannable import MonoOptimisation
if LocalProperties.get("gda.mode") == "live":
    monoOptimiser = MonoOptimisation( braggoffset, ionchambers )
else :
    #Setup gaussian used to provide signal when optimising mono
    from gda.device.scannable import ScannableGaussian
    scannableGaussian = ScannableGaussian("scannableGaussian", 0.1, 5, 1)
    scannableGaussian.setScannableToMonitorForPosition(braggoffset) # position of braggoffset determines value returned by scannable
    monoOptimiser = MonoOptimisation( braggoffset, scannableGaussian )
monoOptimiser.setBraggScannable(bragg1WithOffset)

#### preparers ###
detectorPreparer = I20DetectorPreparer(xspress2system, sensitivities, sensitivity_units, offsets, offset_units, ionchambers, I1, xmapMca, medipix, topupChecker)
detectorPreparer.setMonoOptimiser(monoOptimiser)
samplePreparer = I20SamplePreparer(sample_x, sample_y, sample_z, sample_rot, sample_fine_rot, sample_roll, sample_pitch, filterwheel, cryostat, cryostick_pos, rcpController)
outputPreparer = I20OutputPreparer(datawriterconfig, datawriterconfig_xes, metashop, ionchambers, xspress2system, xmapMca, detectorPreparer)
beamlinePreparer = I20BeamlinePreparer()

twodplotter = TwoDScanPlotter()
twodplotter.setName("twodplotter")

store_dir = LocalProperties.getVarDir() +"xes_offsets/"
xes_offsets = XESOffsets(store_dir, spectrometer)
xes_calculate = XESCalculate(xes_offsets, material, cut1, cut2, cut3, radius)

theFactory = XesScanFactory();
theFactory.setBeamlinePreparer(beamlinePreparer);
theFactory.setDetectorPreparer(detectorPreparer);
theFactory.setSamplePreparer(samplePreparer);
theFactory.setOutputPreparer(outputPreparer);
# theFactory.setCommandQueueProcessor(commandQueueProcessor);
theFactory.setLoggingScriptController(XASLoggingScriptController);
theFactory.setDatawriterconfig(datawriterconfig);
theFactory.setEnergyScannable(bragg1);
theFactory.setMetashop(metashop);
theFactory.setIncludeSampleNameInNexusName(True);
# theFactory.setOriginal_header(original_header);
theFactory.setScanName("xas")
theFactory.setAnalyserAngle(XESBragg)
theFactory.setXes_energy(XESEnergy)
xes = theFactory.createXesScan()

theFactory = XasScanFactory();
theFactory.setBeamlinePreparer(beamlinePreparer);
theFactory.setDetectorPreparer(detectorPreparer);
theFactory.setSamplePreparer(samplePreparer);
theFactory.setOutputPreparer(outputPreparer);
theFactory.setLoggingScriptController(XASLoggingScriptController);
theFactory.setDatawriterconfig(datawriterconfig);
theFactory.setEnergyScannable(bragg1);
theFactory.setMetashop(metashop);
theFactory.setIncludeSampleNameInNexusName(True);
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

scansReturnToOriginalPositions = 1

print "Creating some scannables useful for recording time during scans..."
print "Creating scannable 'w' which will delay scan points until a time has been reached during a scan."\
+ "\nusage of 'w':    scan <motor> <start> <stop> <step> w 0 <delay between points in s>\n\n"

w = showtimeClass("w")
w.setLevel(10)

if LocalProperties.get("gda.mode") == "live":
    # to speed up step scans
    LocalProperties.set("gda.scan.concurrentScan.readoutConcurrently","true")
    LocalProperties.set("gda.scan.multithreadedScanDataPointPipeline.length","10")
    if (machineMode() == "No Beam"):
        remove_default([topupChecker])
        remove_default([absorberChecker])
        remove_default([shutterChecker])
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

xes_offsets.removeAll()

# do nothing more so that offsets start at zero everytime

if LocalProperties.get("gda.mode") == "live":
    run "adc_monitor"
    run "xspress_config"
    print "\nXspress detector set to high (>8KeV) mode."\
    + "\nIf you wish to collect predominately at lower energies, type:"\
    + "\nswitchXspressToLowEnergyMode()"\
    + "\nto change the Xspress settings. Type:"\
    + "\nswitchXspressToHighEnergyMode()"\
    + "\n to changes the settings back again."\
    + "\n"\
    + "To find out current mode type:\n"\
    + "finder.find(\"DAServer\").getStartupCommands()\n"
    
    FFI0.setInputNames([])
    run "vortexLiveTime"
    #testVortexWiredCorrectly()
    #calibrate_mono = mono_calibration.calibrate_mono()
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


#ws146-AD-SIM-01:HDF5:MinCallbackTime
print "****GDA startup script complete.****\n\n"
