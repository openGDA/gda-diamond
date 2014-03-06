print "\n\n****Running the I20 startup script****\n\n"
from org.jscience.physics.quantities import Quantity
from org.jscience.physics.units import Unit
from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable
from gda.jython import JythonServerFacade
from gda.scan import ScanBase
from devices import RealBlades
from devices.RealBlades import BladeAngle
from devices.RealBlades import SubtractAngle
from devices.RealBlades import AverageAngle
from exafsscripts.exafs.i20DetectorPreparer import I20DetectorPreparer
from exafsscripts.exafs.i20SamplePreparer import I20SamplePreparer
from exafsscripts.exafs.i20OutputPreparer import I20OutputPreparer
from exafsscripts.exafs.xas_scan import XasScan
from exafsscripts.exafs.xes_scan import I20XesScan
from time import sleep
from exafsscripts.exafs.config_fluoresence_detectors import XspressConfig, VortexConfig
from gda.device.scannable import TwoDScanPlotter
from xes.xes_offsets import XESOffsets
from xes.xes_calculate import XESCalculate
from gdascripts.pd.time_pds import showtimeClass, waittime
import mono_calibration 
from vortex_elements import VortexElements
from gdascripts.metadata.metadata_commands import meta_add,meta_ll,meta_ls,meta_rm,meta_clear
from gda.data.scan.datawriter import NexusDataWriter

ScanBase.interrupted = False
ScriptBase.interrupted = False

XASLoggingScriptController = Finder.getInstance().find("XASLoggingScriptController")
commandQueueProcessor = Finder.getInstance().find("commandQueueProcessor")
ExafsScriptObserver = Finder.getInstance().find("ExafsScriptObserver")
datawriterconfig = Finder.getInstance().find("datawriterconfig")
original_header = Finder.getInstance().find("datawriterconfig").getHeader()[:]
datawriterconfig_xes = Finder.getInstance().find("datawriterconfig_xes")
original_header_xes = Finder.getInstance().find("datawriterconfig").getHeader()[:]
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop")

sensitivities = [i0_stanford_sensitivity, it_stanford_sensitivity,iref_stanford_sensitivity,i1_stanford_sensitivity]
sensitivity_units = [i0_stanford_sensitivity_units,it_stanford_sensitivity_units,iref_stanford_sensitivity_units,i1_stanford_sensitivity_units]
offsets = [i0_stanford_offset,it_stanford_offset,iref_stanford_offset,i1_stanford_offset]
offset_units = [i0_stanford_offset_units,it_stanford_offset_units,iref_stanford_offset_units,i1_stanford_offset_units]

if LocalProperties.get("gda.mode") == "live":
    xmapController = Finder.getInstance().find("xmapcontroller")
    from vortex_elements import VortexElements
    vortexElements = VortexElements(edxdcontroller, xmapController, xmapMca)

xspressConfig = XspressConfig(xspress2system, ExafsScriptObserver)

xspressConfig.initialize()
alias("xspressConfig")

vortexConfig = VortexConfig(xmapMca, ExafsScriptObserver)
vortexConfig.initialize()
alias("vortexConfig")

detectorPreparer = I20DetectorPreparer(xspress2system, XASLoggingScriptController,sensitivities, sensitivity_units ,offsets, offset_units,cryostat,ionchambers,I1,xmapMca,topupChecker,xspressConfig, vortexConfig)
samplePreparer = I20SamplePreparer(sample_x,sample_y,sample_z,sample_rot,sample_fine_rot,sample_roll,sample_pitch,filterwheel, cryostat, cryostick_pos)
outputPreparer = I20OutputPreparer(datawriterconfig,datawriterconfig_xes)
twodplotter = TwoDScanPlotter()
twodplotter.setName("twodplotter")

store_dir = LocalProperties.getVarDir() +"xes_offsets/"
xes_offsets = XESOffsets(store_dir, spectrometer)

xes_calculate = XESCalculate(xes_offsets, material, cut1, cut2, cut3, radius)

xas = XasScan(detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, ExafsScriptObserver, XASLoggingScriptController, datawriterconfig, original_header, bragg1, ionchambers, False, True, True, False, False)
xes = I20XesScan(xas,XASLoggingScriptController, detectorPreparer, samplePreparer, outputPreparer, commandQueueProcessor, XASLoggingScriptController, ExafsScriptObserver, sample_x, sample_y, sample_z, sample_rot, sample_fine_rot,twodplotter,I1,bragg1,XESEnergy,XESBragg)
xanes = xas

alias("xas")
alias("xanes")
alias("xes")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")
alias("meta_clear")

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
    remove_default([shutterChecker])

#
# XES offsets section
#
from xes import offsetsStore, setOffsets
offsetsStore = offsetsStore.XESOffsets()
offsetsStore.removeAllOffsets()
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
    testVortexWiredCorrectly()
    calibrate_mono = mono_calibration.calibrate_mono()

else :
    if material() == None:
        material('Si')
print "****GDA startup script complete.****\n\n"
