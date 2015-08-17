scannp = scan #@UndefinedVariable
vararg_alias("scannp") #@UndefinedVariable
print "*** Creating scan with no processing: scannp"
from gda.analysis import ScanFileHolder
from gda.analysis.io import PilatusTiffLoader, SRSLoader
from uk.ac.diamond.scisoft.analysis.io.emulated import FileSystemEmulatingTIFFImageLoader
from gda.configuration.properties import LocalProperties
from gda.device.monitor import EpicsMonitor
from gda.device.scannable import PseudoDevice
from gda.epics import CAClient #@UnusedImport
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import alias, cmd, ls, pause, reset_namespace, run, vararg_regex #@UnusedImport
from gdascripts.analysis.datasetprocessor.oned.GaussianEdge import GaussianEdge #@UnusedImport
from gdascripts.analysis.datasetprocessor.oned.MinPositionAndValue import MinPositionAndValue #@UnusedImport
from gdascripts.analysis.datasetprocessor.oned.TwoGaussianEdges import TwoGaussianEdges #@UnusedImport
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue #@UnusedImport
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.scan.gdascans import Rscan, Scan #@UnusedImport
from gdascripts.scan.process.ScannableScan import ScannableScan #@UnusedImport
from gdascripts.scan.process.tuner import Tuner #@UnusedImport
from gdascripts.scannable.ScanFileHolderScannable import ScanFileHolderScannable
from gdascripts.scannable.SelectableCollectionOfScannables import SelectableCollectionOfScannables #@UnusedImport
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper, SwitchableHardwareTriggerableProcessingDetectorWrapper
from gdascripts.scannable.detector.epics.EpicsPilatus import EpicsPilatus
from gdascripts.scannable.timerelated import t, dt, w, clock, epoch #@UnusedImport
from gdascripts.scannable.dummy import SingleInputDummy #@UnusedImport
from gdascripts.utils import caget, caput, printJythonEnvironment #@UnusedImport
from gdascripts.visit import VisitSetter, PilatusAdapter, IPPAdapter, ProcessingDetectorWrapperAdapter, FileWritingDetectorAdapter
#from init.init_scan_commands_and_processing import * #@UnusedWildImport
from gdascripts.scannable.installStandardScannableMetadataCollection import * #@UnusedWildImport
import gdascripts.scan.concurrentScanWrapper
from pd_MonitorWrapper import MonitorWrapper
from pprint import pprint #@UnusedImport
from scalerChannelAssigner import ScalerChannelAssigner
from scannable.hw.xiaFilter import XiaFilter
from scannable.shutter import Shutter, DummyEpicsShutterPositioner
from scannable.twocircle import TwoCircle
from testjy.gdascripts_test.analysis_test.datasetprocessor_test.oned_test.files.files import WIRESCANFILE
from time import sleep #@UnusedImport
from gdascripts.scannable.timerelated import TimeOfDay
import device_tca
import gda #@UnusedImport
import installation
import java
import pd_JenaPiezoChannel
import pd_epicsMcaHardwareRoiWrapper
import pd_epicsMcaWholeSpectrumWrapper
import pd_readManyPVs
import pd_readPvAfterWaiting
from pd_setPvAndWaitForCallbackWithSeparateReadback import SetPvAndWaitForCallbackWithSeparateReadback, SetPvAndWaitForCallbackWithSeparateReadback2
import pd_setPvAndWaitWithSeparateReadback
import pd_tca
import pd_toggleBinaryPvAndWait
import pd_toggleBinaryPvAndWaitFancy
import pd_waitWhileScannableBelowThreshold
import sys
from gdascripts.analysis.datasetprocessor.twod.PixelIntensity import PixelIntensity

from gdascripts.scannable.dummy import SingleInputDummy, SingleInputStringDummy
from gdascripts.scannable.beamokay import WaitWhileScannableBelowThreshold, WaitForScannableState
from gda.device.scannable.scannablegroup import ScannableGroup

print "======================================================================"
print "Running B16 specific initialisation code"
print "======================================================================"
ENABLE_PILATUS = True
ENABLE_PCOEDGE = True
ENABLE_PCO4000 = True

#USE_YOU_DIFFCALC_ENGINE = True
USE_YOU_DIFFCALC_ENGINE = False  # Use old diffcalc


from gda.factory import Finder
daserver = Finder.getInstance().find('daserver')
from scannable.laser_experiment import LaserShutterPulseController
laserxray = LaserShutterPulseController('laserxray', daserver)

#if installation.isLive():
#	from pd_setPvAndWait import SetPvAndWait
#	shutterWidth = SetPvAndWait('shutterWidth', 'BL16B-EA-EVR-01:FRONT-WIDTH:SET', .2)
#	shutterDelay = SetPvAndWait('shutterDelay', 'BL16B-EA-EVR-01:FRONT-DELAY:SET', .2)
#	caput('BL16B-EA-EVR-01:SELECT-FPS2','External')
#	caput('BL16B-EA-EVR-01:FRONT-ENABLE:SET','Enabled')
#	caput('BL16B-EA-EVR-01:FRONT-POLARITY:SET', 'Normal')

###############################################################################
###                          Print environmental info                       ###
###############################################################################
printJythonEnvironment()

###############################################################################
###                  Add useful functions and scan commands                 ###
###############################################################################

visit_setter = VisitSetter()

visit = visit_setter.visit
datadir = visit_setter.datadir
GeneralCommands.alias("datadir")
GeneralCommands.alias("visit")




#from init.init_scan_commands_and_processing import *
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()

from gdascripts.analysis.datasetprocessor.oned.CenFromSPEC import CenFromSPEC
scan_processor.processors.append(CenFromSPEC())


#from gdascripts.scannable.installStandardScannableMetadataCollection import *
meta.rootNamespaceDict=globals()
note.rootNamespaceDict=globals()


print "Adding dummy devices x,y and z"
x=SingleInputDummy("x")
y=SingleInputDummy("y")
z=SingleInputDummy("z")

print "Adding timer devices t, dt, and w, clock"

alpha.setOutputFormat(['%.5f']) #@UndefinedVariable
delta.setOutputFormat(['%.5f']) #@UndefinedVariable
omega.setOutputFormat(['%.5f']) #@UndefinedVariable
chi.setOutputFormat(['%.5f']) #@UndefinedVariable
phi.setOutputFormat(['%.5f']) #@UndefinedVariable
fcarmTheta.setOutputFormat(['%.5f']) #@UndefinedVariable
fcarm2Theta.setOutputFormat(['%.5f']) #@UndefinedVariable

###############################################################################
###                              SIMULATION MODE                            ###
###############################################################################

if installation.isDummy():
	vortexMca = None
	vortexMca2 = None
	exec('ai1l=SingleInputDummy("ai1l")')
	exec('ai2l=SingleInputDummy("ai2l")')
	exec('ai3l=SingleInputDummy("ai3l")')
	exec('ai5l=SingleInputDummy("ai5l")')
	exec('ai13l=SingleInputDummy("ai13l")')
	exec('energy = SingleInputDummy("energy")')
	exec('ct7 = SingleInputDummy("ct7")')
	from gdascripts.scannable.detector.dummy.focused_beam_dataset import CreateImageReadingDummyDetector
	x.asynchronousMoveTo(430)
	ippws4 = CreateImageReadingDummyDetector.create(x)
	sfh = ScanFileHolder()
	sfh.load(SRSLoader(WIRESCANFILE))
	data_10040 = ScanFileHolderScannable('data_10040',sfh, ('tbdiagZcoarse', 'tbdiagY'), ('rc', 'pips2'),{'tbdiagZcoarse':1, 'tbdiagY':.0005} )
	exec("tbdiagZcoarse = data_10040.scannableFactory('tbdiagZcoarse', ['tbdiagZcoarse'])")
	exec("tbdiagY = data_10040.scannableFactory('tbdiagY', ['tbdiagY'])")
	exec("rc = data_10040.scannableFactory('rc', ['rc'])")
	exec("pips2 = data_10040.scannableFactory('pips2', ['pips2'])")
	energy.asynchronousMoveTo(1.) # so that wl doesn't break!#@UndefinedVariable
	for mot in (alpha, delta, omega, chi, phi): #@UndefinedVariable
		mot.getMotor().setSpeed(3600000)

t2t=TwoCircle("t2t",fcTheta,fc2Theta) #@UndefinedVariable

###############################################################################
###                 Wrap all monitors to make them simply scannable         ###
###############################################################################
toPrint = ''
for objname in dir():
	if isinstance(eval(objname),EpicsMonitor):
		toPrint+= objname + " "
		exec(objname + " = MonitorWrapper(" + objname + ")")
print "Wrapped the monitors: " + toPrint

if installation.isLive():


#	bladel = MonitorWrapper(ai1, "bladel") #@UndefinedVariable
#	blader = MonitorWrapper(ai2, "blader") #@UndefinedVariable
#	bladet = MonitorWrapper(ai3, "bladet") #@UndefinedVariable
#	bladeb = MonitorWrapper(ai4, "bladeb") #@UndefinedVariable
#	pips1 = MonitorWrapper(ai5, "pips1") #@UndefinedVariable
#	pips2 = MonitorWrapper(ai6, "pips2") #@UndefinedVariable

	qbpm1 = MonitorWrapper(ai9, "qbpm1") #@UndefinedVariable
	qbpm2 = MonitorWrapper(ai10, "qbpm2") #@UndefinedVariable
	qbpm3 = MonitorWrapper(ai11, "qbpm3") #@UndefinedVariable
	qbpm4 = MonitorWrapper(ai12, "qbpm4") #@UndefinedVariable

	qbpmrange = pd_readPvAfterWaiting.ReadPvAfterWaiting("qbpmrange","BL16B-DI-QBPM-01:MR")

###############################################################################
###                       Devices connected to scaler 1                     ###
###############################################################################

if installation.isLive():
	sca = ScalerChannelAssigner(globals(), struck1, 'BL16B-EA-DET-01:SCALER1') #@UndefinedVariable
else:
	sca = ScalerChannelAssigner(globals(), struck1) #@UndefinedVariable
sca.assign(1, 'cttime')
sca.assign(2, ['ct2','apd'])
sca.assign(3, ['ct3','vsca1'])
sca.assign(4, ['ct4','vsca2'])
sca.assign(5, ['ct5','vsca3'])
sca.assign(6, ['ct6','scintillator'])
sca.assign(7, ['ct7','ionchamber'])
sca.assign(8, ['ct8','pips'])
sca.assign(9, ['ct9'])
sca.assign(10, ['ct10'])
sca.assign(11, ['ct11'])
sca.assign(12, ['ct12'])
sca.assign(13, ['ct13'])
sca.assign(14, ['ct14'])
sca.assign(15, ['ct15'])
sca.assign(16, ['ct16'])


###############################################################################
###                 TCA (sets up only, use struck for readback              ###
###############################################################################

# there is an offical server.xml device to do this. This hack taken from i16.
print "Creating TCA scanables"
if installation.isLive():
	vtca=device_tca.TCA('BL16B-EA-DET-01:tca1')

	vroi1 = pd_tca.tcasca('vroi1',"%4.3f",vtca,"%",'1')
	vroi2 = pd_tca.tcasca('vroi2',"%4.3f",vtca,"%",'2')
	vroi3 = pd_tca.tcasca('vroi3',"%4.3f",vtca,"%",'3')
else:
	print "* Not installing tca (as not live installation) *"


###############################################################################
###                             Analogue Outputs                            ###
###############################################################################
print "Manually creating Analogue Outputs from RIM card"
if installation.isLive():
	import pd_setPvAndWait;reload(pd_setPvAndWait)
	piezox=pd_setPvAndWait.SetPvAndWait("piezox","BL16B-EA-RIM-03:AO1", 0.2)
	piezoy=pd_setPvAndWait.SetPvAndWait("piezoy","BL16B-EA-RIM-03:AO2", 0.2)
	piezoz=pd_setPvAndWait.SetPvAndWait("piezoz","BL16B-EA-RIM-03:AO3", 0.2)
	piezox.setOutputFormat(['%.4f'])
	piezoy.setOutputFormat(['%.4f'])
	piezoz.setOutputFormat(['%.4f'])
else:
	print "* Not installing piezo analogue outputs (as not live installation) *"


###############################################################################
###                         Vortex detector chain                           ###
###############################################################################
if installation.isLive():
	print "Creating vmcaspect and vmcaroi wrappers for Vortex mca"
	#pips1short=pd_readPvAfterWaiting.ReadPvAfterWaiting("pips1short","BL16B-EA-RIM-01:AIAVGS5")
	#pips2short=pd_readPvAfterWaiting.ReadPvAfterWaiting("pips2short","BL16B-EA-RIM-01:AIAVGS6")
	try:
		vmcaspect = pd_epicsMcaWholeSpectrumWrapper.EpicsMcaWholeSpectrumWrapper('vmcaspect',vortexMca)
		vmcagross = pd_epicsMcaHardwareRoiWrapper.EpicsMcaHardwareRoiWrapper('vmcagross', vortexMca, 'gross')
		vmcanet =   pd_epicsMcaHardwareRoiWrapper.EpicsMcaHardwareRoiWrapper('vmcanet', vortexMca, 'net')
		vmcafancy = pd_epicsMcaHardwareRoiWrapper.EpicsMcaHardwareRoiWrapper('vmcaroi', vortexMca, 'fancy')
	except Exception, e:
		print "***********************************************************************************"
		print "***** ERROR: problem starting up vmca devices. TRY RESETING THE GDA SERVER    *****"
		print "***** (this currently needs to be done after the Epics IOC has been restarted *****"
		print "***********************************************************************************"
		print str(e)
	try:
		vmcaspect2 = pd_epicsMcaWholeSpectrumWrapper.EpicsMcaWholeSpectrumWrapper('vmcaspect2',vortexMca2)
		vmcagross2 = pd_epicsMcaHardwareRoiWrapper.EpicsMcaHardwareRoiWrapper('vmcagross2', vortexMca2, 'gross')
		vmcanet2 =   pd_epicsMcaHardwareRoiWrapper.EpicsMcaHardwareRoiWrapper('vmcanet2', vortexMca2, 'net')
		vmcafancy2 = pd_epicsMcaHardwareRoiWrapper.EpicsMcaHardwareRoiWrapper('vmcaroi2', vortexMca2, 'fancy')
	except Exception, e:
		print "***********************************************************************************"
		print "***** ERROR: problem starting up vmca devices. TRY RESETING THE GDA SERVER    *****"
		print "***** (this currently needs to be done after the Epics IOC has been restarted *****"
		print "***********************************************************************************"
		print str(e)
else:
	print "* Not installing vmca MCA wrappers (as not live installation) *"


###############################################################################
###                           Creating      Piezo devices                   ###
###############################################################################

### Linox piezo stages ###
if installation.isLive():
	from scannable.hw.linosCn30Piezo import LinosCn30PiezoStage
	linosx =  LinosCn30PiezoStage("linosx",'BL16B-EA-CN30-01:X:')
	linosy =  LinosCn30PiezoStage("linosy",'BL16B-EA-CN30-01:Y:')
	linosz =  LinosCn30PiezoStage("linosz",'BL16B-EA-CN30-01:Z:')
	linos = ScannableGroup('linos', [linosx,  linosy, linosz])
	linos.configure()

print "Creating Jena Piezo devices. Channel1 -> jpx, Channel2 -> jpy"
#print "* Seems to work okay with Readback rate set to 0.2 s on epics panel *"
if installation.isLive():
	jpx=pd_JenaPiezoChannel.JenaPiezoChannel('x',"BL16B-EA-IOC-01:JENA1",distancePerStep=1, readSetPosition=0, delayAfterAskingToMove=0.2)
	jpy=pd_JenaPiezoChannel.JenaPiezoChannel('y',"BL16B-EA-IOC-01:JENA2",distancePerStep=1, readSetPosition=0, delayAfterAskingToMove=0.2)
else:
	print "* Not installing jena piezo drivers (as not live installation) *"

if installation.isLive():
	print "Installing piezo2 device from epics BL16B-EA-PIEZO-02:E625"
	piezo2=SetPvAndWaitForCallbackWithSeparateReadback("piezo2","BL16B-EA-PIEZO-02:E625:MOV:WR","BL16B-EA-PIEZO-02:E625:POS:RD" ,2*60)
else:
	print "* Not installing piezo2 device (as not live installation) *"

if installation.isLive():
	print "Installing piezo3 device from epics BL16B-EA-PIEZO-03:E625"
	piezo3=SetPvAndWaitForCallbackWithSeparateReadback("piezo3","BL16B-EA-PIEZO-03:E625B:MOV:WR","BL16B-EA-PIEZO-03:E625B:POS:RD" ,2*60)
else:
	print "* Not installing piezo3 device (as not live installation) *"

if installation.isLive():
	print "Installing piezo4 device from epics BL16B-EA-PIEZO-02:E625"
	piezo4x=SetPvAndWaitForCallbackWithSeparateReadback("piezo4x","BL16B-EA-PIEZO-04:E725:X:MOV:WR","BL16B-EA-PIEZO-04:E725:X:POS:RD" ,2*60)
	piezo4y=SetPvAndWaitForCallbackWithSeparateReadback("piezo4y","BL16B-EA-PIEZO-04:E725:Y:MOV:WR","BL16B-EA-PIEZO-04:E725:Y:POS:RD" ,2*60)
	piezo4 = ScannableGroup('piezo4', [piezo4x,  piezo4y])
	piezo4.configure()
	piezo4x.setUpperGdaLimits(200)
	piezo4x.setLowerGdaLimits(0)
	piezo4y.setUpperGdaLimits(200)
	piezo4y.setLowerGdaLimits(0)
else:
	print "* Not installing piezo4 device (as not live installation) *"


if installation.isLive():
	print "Installing micospiezo1/2 devices from epics BL16B-EA-PIEZO-03:MMC"
	micospiezo1=SetPvAndWaitForCallbackWithSeparateReadback2(
		"micospiezo1", "BL16B-EA-PIEZO-03:MMC:01:DEMAND",
					   "BL16B-EA-PIEZO-03:MMC:01:POS:RBV", 40, 0.000001)
	micospiezo2=SetPvAndWaitForCallbackWithSeparateReadback2(
		"micospiezo2", "BL16B-EA-PIEZO-03:MMC:02:DEMAND",
					   "BL16B-EA-PIEZO-03:MMC:02:POS:RBV", 40, 0.000001)
	micos = ScannableGroup('micos', [micospiezo1,  micospiezo2])
	micos.configure()
else:
	print "* Not installing micospiezo1/2 devices (as not live installation) *"


if installation.isLive():
	print "Installing atto devices from epics BL16B-EA-ATTO..."

	from scannable.epics.anc150axis import createAnc150Axis

	try:
		attorot1  = createAnc150Axis("attorot1",  "BL16B-EA-ATTO-03:PIEZO3:", 0.25)
		attorot2  = createAnc150Axis("attorot2",  "BL16B-EA-ATTO-04:PIEZO3:", 0.25)
		attotilt1 = createAnc150Axis("attotilt1", "BL16B-EA-ATTO-01:PIEZO1:", 0.25)
		attotilt2 = createAnc150Axis("attotilt2", "BL16B-EA-ATTO-02:PIEZO1:", 0.25)
		attox1    = createAnc150Axis("attox1",    "BL16B-EA-ATTO-01:PIEZO2:", 0.25)
		attox2    = createAnc150Axis("attox2",    "BL16B-EA-ATTO-02:PIEZO2:", 0.25)
		attox3    = createAnc150Axis("attox3",    "BL16B-EA-ATTO-03:PIEZO1:", 0.25)
		attoz1    = createAnc150Axis("attoz1",    "BL16B-EA-ATTO-03:PIEZO2:", 0.25)
		attoz2    = createAnc150Axis("attoz2",    "BL16B-EA-ATTO-04:PIEZO2:", 0.25)
		attoy1    = createAnc150Axis("attoy1",    "BL16B-EA-ATTO-01:PIEZO3:", 0.25)
		attoy2    = createAnc150Axis("attoy2",    "BL16B-EA-ATTO-02:PIEZO3:", 0.25)

		attorot1.setFrequency(625)
		attorot2.setFrequency(625)
		attotilt1.setFrequency(1000)
		attotilt2.setFrequency(1000)
		attox1.setFrequency(1000)
		attox2.setFrequency(1000)
		attox3.setFrequency(1000)
		attoz1.setFrequency(1000)
		attoz2.setFrequency(1000)
		attoy1.setFrequency(2000)
		attoy2.setFrequency(2000)
	except:
		print "* Failed to initialise atto devices *"
else:
	print "* Not installing atto devices (as not live installation) *"

###############################################################################
###                                 Energy from mono                        ###
###############################################################################
if installation.isLive():
	# TODO: The interface file contains tags for these PVs, replace with control point (and test)
	energy=SetPvAndWaitForCallbackWithSeparateReadback("energy","BL16B-OP-DCM-01:ENERGY.VAL","BL16B-OP-DCM-01:ENERGY_RBV" ,30*60)
	dcmEnergyControl = pd_setPvAndWait.SetPvAndWait("dcmEnergyControl","BL16B-OP-DCM-01:ENERGY_SWITCH", 0.2)
	dcmEnergyControl.setOutputFormat(['%.0f'])

else:
	print "* not installing energy device (as not live installation)"


###############################################################################
###                            MonoFinePitchTuner                      ###
###############################################################################

#NOTE: The following is now in b16/scripts/localStationUser
import pd_setPvAndWait
if installation.isLive():
	dcmpiezo=pd_setPvAndWait.SetPvAndWait("dcmpiezo","BL16B-OP-DCM-01:FB:DAC:02", 0.2)
	dcmpiezo.setOutputFormat(['%.4f'])


	bi = SelectableCollectionOfScannables('bi', [ct7, ai13, ai1])#@UndefinedVariable
	#monotuner=Tuner('monotuner', MaxPositionAndValue(), Scan, dcmPitch, .145, .16, 0.0002, bi, .5) #@UndefinedVariable
	monotuner=Tuner('monotuner', MaxPositionAndValue(), Scan, dcmpiezo, 1.0, 9.0, 0.1, ai1, .2) #@UndefinedVariable
	monotuner.use_backlash_correction = True

###############################################################################
###                                 A3 XIA Filters                          ###
###############################################################################
if installation.isLive():
	att3a = XiaFilter('att3a', 'BL16B-OP-ATTN-03', 1, timeout=5)
	att3b = XiaFilter('att3b', 'BL16B-OP-ATTN-03', 2, timeout=5)
	att3c = XiaFilter('att3c', 'BL16B-OP-ATTN-03', 3, timeout=5)
	att3d = XiaFilter('att3d', 'BL16B-OP-ATTN-03', 4, timeout=5)

###############################################################################
###                      Setting device levels and formats                  ###
###############################################################################
print "Setting device levels and output formats"
#apdt.setLevel(9)
#apd.setLevel(9)



tb2y.setOutputFormat(['%5.7g']) #@UndefinedVariable
tb2x.setOutputFormat(['%5.7g']) #@UndefinedVariable
tb1x.setOutputFormat(['%5.7g']) #@UndefinedVariable
tb1y.setOutputFormat(['%5.7g']) #@UndefinedVariable
tb3x.setOutputFormat(['%5.7g']) #@UndefinedVariable
tb3y.setOutputFormat(['%5.7g']) #@UndefinedVariable
ippws4.setLevel(9)
t.setOutputFormat(['%6.6f'])
try:
	kbwireX.setOutputFormat(['%.3f'])
	kbwireY.setOutputFormat(['%.3f'])
except NameError:
	pass
###############################################################################
###                           Wait for beam device                          ###
###############################################################################
print "Adding checkbeam device (rc>190mA, 60s wait after beam back)"
print "   (change threshold with checkbeam.minumumThreshold=12345)"
if installation.isLive():
	oldcheckbeam = pd_waitWhileScannableBelowThreshold.WaitWhileScannableBelowThreshold('checkbeam', rc, minumumThreshold=190, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=180) #@UndefinedVariable
	oldcheckbeam = pd_waitWhileScannableBelowThreshold.WaitWhileScannableBelowThreshold('checkbeam', rc, minumumThreshold=190, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=180) #@UndefinedVariable
	oldcheckbeam.setLevel(6)
	checkct15 = pd_waitWhileScannableBelowThreshold.WaitWhileScannableBelowThreshold('checkcttime', ct15, minumumThreshold=160000, secondsBetweenChecks=0.5, secondsToWaitAfterBeamBackUp=10) #@UndefinedVariable
	checkct15.setLevel(6)

	print "Adding checky device (y>0.17, 15s wait after beam back)"
	#checky = pd_waitWhileScannableBelowThreshold.WaitWhileScannableBelowThreshold('checky', ct15, minumumThreshold=150000, #secondsBetweenChecks=0.5, secondsToWaitAfterBeamBackUp=10)
	checky = pd_waitWhileScannableBelowThreshold.WaitWhileScannableBelowThreshold('checky', y, minumumThreshold=0.17, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=15)
	checky.setLevel(6)
	checky.scannableToMonitor = ai5#@UndefinedVariable


if installation.isLive():
	checkrc = WaitWhileScannableBelowThreshold('checkrc', rc, 10, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=5) #@UndefinedVariable
	checkfe = WaitForScannableState('checkfe', frontend, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=60) #@UndefinedVariable
	checkshtr1 = WaitForScannableState('checkshtr1', shtr1, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=60) #@UndefinedVariable
	checkbeam = ScannableGroup('checkbeam', [checkrc,  checkfe, checkshtr1])
	checkbeam.configure()


###############################################################################
###                             HARDWARE WORKAROUND                             ###
###############################################################################
	print "*** Creating tarmTheta and tarm2Theta to bypass dodgy DMOV flag with 30s second timeout***"
	print ""
	print "    CAUTION: The gda does not know about limits on these devices and"
	print "             will not know if a move has failed."

	tarmTheta = SetPvAndWaitForCallbackWithSeparateReadback("tarmTheta","BL16B-MO-DIFF-01:A:THETA:A.VAL","BL16B-MO-DIFF-01:A:THETA:A.RBV" ,30)
	tarm2Theta = SetPvAndWaitForCallbackWithSeparateReadback("tarm2Theta","BL16B-MO-DIFF-01:A:2THETA:A.VAL","BL16B-MO-DIFF-01:A:2THETA:A.RBV" ,30)
	tarmTheta.setOutputFormat(['%6.5f'])
	tarm2Theta.setOutputFormat(['%6.5f'])

	fcTheta.setOutputFormat(['%6.5f']) #@UndefinedVariable
	fc2Theta.setOutputFormat(['%6.5f'])#@UndefinedVariable


###############################################################################
###                            PCO optics motors                            ###
###############################################################################
print "** 23oct08: Adding pcocam1 and pcocam2 device to move pco optics. Note these assume all moves take 2s.  Change delay with pcocam1.delayAfterAskingToMove = num_seconds"
if installation.isLive():
	pcocam1=pd_setPvAndWaitWithSeparateReadback.SetPvAndWaitWithSeparateReadback("pcocam1","BL16B-EA-DET-02:CAM1:DEMAND","BL16B-EA-DET-02:CAM1:RBV" ,2)
	pcocam2=pd_setPvAndWaitWithSeparateReadback.SetPvAndWaitWithSeparateReadback("pcocam2","BL16B-EA-DET-02:CAM2:DEMAND","BL16B-EA-DET-02:CAM2:RBV" ,2)
	pcocam3=pd_setPvAndWaitWithSeparateReadback.SetPvAndWaitWithSeparateReadback("pcocam3","BL16B-EA-DET-02:CAM3:DEMAND","BL16B-EA-DET-02:CAM3:RBV" ,2)


###############################################################################
###                                     Pilatus                             ###
###############################################################################
if installation.isLive() and ENABLE_PILATUS:
	print "-------------------------------PILATUS INIT---------------------------------------"
	try:

		pil = SwitchableHardwareTriggerableProcessingDetectorWrapper('pil',
									_pilatus,
									None,
									_pilatus_for_snaps,
									[],
									panel_name='Detector Plot',
									panel_name_rcp='Plot 1',
									iFileLoader=PilatusTiffLoader,
									fileLoadTimout=60,
									printNfsTimes=False,
									returnPathAsImageNumberOnly=True)

		#pil100kdet = EpicsPilatus('pil100kdet', 'BL16I-EA-PILAT-01:','/dls/b16/detectors/im/','test','%s%s%d.tif')
		#pil100k = ProcessingDetectorWrapper('pil100k', pil100kdet, [], panel_name='Pilatus100k', toreplace=None, replacement=None, iFileLoader=PilatusTiffLoader, fileLoadTimout=15, returnPathAsImageNumberOnly=True)
		#pil100k.processors=[DetectorDataProcessorWithRoi('max', pil100k, [SumMaxPositionAndValue()], False)]
		#pil100k.printNfsTimes = True


		pil.processors=[DetectorDataProcessorWithRoi('max', pil, [SumMaxPositionAndValue()], False)]

		pil.display_image = True
		pilpeak2d = DetectorDataProcessorWithRoi('pilpeak2d', pil, [TwodGaussianPeak()])
		pilmax2d = DetectorDataProcessorWithRoi('pilmax2d', pil, [SumMaxPositionAndValue()])
		pilintensity2d = DetectorDataProcessorWithRoi('pilintensity2d', pil, [PixelIntensity()])
		pilroi1 = DetectorDataProcessorWithRoi('pilroi1', pil, [SumMaxPositionAndValue()])
		pilroi2 = DetectorDataProcessorWithRoi('pilroi2', pil, [SumMaxPositionAndValue()])
		pilroi3 = DetectorDataProcessorWithRoi('pilroi3', pil, [SumMaxPositionAndValue()])
		pilroi4 = DetectorDataProcessorWithRoi('pilroi4', pil, [SumMaxPositionAndValue()])
		pilroi5 = DetectorDataProcessorWithRoi('pilroi5', pil, [SumMaxPositionAndValue()])

		pilgain = pd_setPvAndWait.SetPvAndWait('pilgain', 'BL16B-EA-PILAT-01:Gain', delayAfterAskingToMove=0.5)
		pilgain.setOutputFormat(['%.0f'])
		pilthresh = pd_setPvAndWait.SetPvAndWait('pilthresh', 'BL16B-EA-PILAT-01:ThresholdEnergy', delayAfterAskingToMove=0.5)
		pilsettings = pd_readManyPVs.ReadManyPVs('pilsettings','BL16B-EA-PILAT-01:READ',['VCMP','VRF','VTRM','VADJ','VCAL','VRFS','VDEL'])


		roi1 = DetectorDataProcessorWithRoi('roi1', pil, [SumMaxPositionAndValue()])
		#roi1.setRoi(0,0,50,50)


	except gda.factory.FactoryException:
		print " *** Could not connect to pilatus (FactoryException)"
	except 	java.lang.IllegalStateException:
		print " *** Could not connect to pilatus (IllegalStateException)"
	print "-------------------------------PILATUS INIT COMPLETE---------------------------------------"
else:
	print "*** Pilatus disabled from localStation.py "

if installation.isLive():
	print "-------------------------------MEDIPIX INIT---------------------------------------"
	try:

		#visit_setter.addDetectorAdapter(FileWritingDetectorAdapter(_medipix_det, create_folder=True, subfolder='medipix'))

		medipix = SwitchableHardwareTriggerableProcessingDetectorWrapper('medipix',
																		_medipix,
																		None,
																		_medipix_for_snaps,
																		[],
																		panel_name='Data Vector',
																		panel_name_rcp='Plot 1',
																		iFileLoader=PilatusTiffLoader,
																		fileLoadTimout=60,
																		printNfsTimes=False,
									returnPathAsImageNumberOnly=True)
		medipix.disable_operation_outside_scans = True
		medipix_threshold0_kev = SetPvAndWaitForCallbackWithSeparateReadback('medipix_threshold_kev', 'BL16B-EA-DET-06:MPX:ThresholdEnergy0', 'BL16B-EA-DET-06:MPX:ThresholdEnergy0_RBV', 10)
		#pil100kdet = EpicsPilatus('pil100kdet', 'BL16I-EA-PILAT-01:','/dls/b16/detectors/im/','test','%s%s%d.tif')
		#pil100k = ProcessingDetectorWrapper('pil100k', pil100kdet, [], panel_name='Pilatus100k', toreplace=None, replacement=None, iFileLoader=PilatusTiffLoader, fileLoadTimout=15, returnPathAsImageNumberOnly=True)
		#pil100k.processors=[DetectorDataProcessorWithRoi('max', pil100k, [SumMaxPositionAndValue()], False)]
		#pil100k.printNfsTimes = True

		medipix.processors=[DetectorDataProcessorWithRoi('max', medipix, [SumMaxPositionAndValue()], False)]

		# TODO: MBB Start - Rob, please check this
		medipix.display_image = True
		medipixpeak2d = DetectorDataProcessorWithRoi('medipixpeak2d', medipix, [TwodGaussianPeak()])
		medipixmax2d = DetectorDataProcessorWithRoi('medipixmax2d', medipix, [SumMaxPositionAndValue()])
		medipixintensity2d = DetectorDataProcessorWithRoi('medipixintensity2d', medipix, [PixelIntensity()])
		# TODO: MBB End


	except gda.factory.FactoryException:
		print " *** Could not connect to pilatus (FactoryException)"
	except 	java.lang.IllegalStateException:
		print " *** Could not connect to pilatus (IllegalStateException)"
	print "-------------------------------PILATUS INIT COMPLETE---------------------------------------"
else:
	print "*** Pilatus disabled from localStation.py "

if installation.isLive():
	print "-------------------------------PSL INIT---------------------------------------"
	try:

		PSL_AUTO_RECONNECT = True
		if not PSL_AUTO_RECONNECT:
			psl = SwitchableHardwareTriggerableProcessingDetectorWrapper('psl',
			                                                             _psl,
			                                                             None,
			                                                             _psl_for_snaps,
			                                                             [],
			                                                             panel_name='Data Vector',
			                                                             panel_name_rcp='Plot 1',
			                                                             fileLoadTimout=60,
			                                                             printNfsTimes=False,
			                                                             returnPathAsImageNumberOnly=True)
		else:
			from scannable.SwitchableProcessingDetectorWrapperWithReconnect import SwitchableProcessingDetectorWrapperWithReconnect
			psl = SwitchableProcessingDetectorWrapperWithReconnect('psl',
			                                                       _psl,
			                                                       None,
			                                                       _psl_for_snaps,
			                                                       "BL16B-EA-DET-07:CAM:RESET.PROC",
			                                                       [],
			                                                       panel_name='Data Vector',
			                                                       panel_name_rcp='Plot 1',
			                                                       fileLoadTimout=60,
			                                                       printNfsTimes=False,
			                                                       returnPathAsImageNumberOnly=True)
		psl.disable_operation_outside_scans = True
		psl.processors=[DetectorDataProcessorWithRoi('max', psl, [SumMaxPositionAndValue()], False)]
		psl.display_image = True
		pslpeak2d = DetectorDataProcessorWithRoi('pslpeak2d', psl, [TwodGaussianPeak()])
		pslmax2d = DetectorDataProcessorWithRoi('pslmax2d', psl, [SumMaxPositionAndValue()])
		pslitensity2d = DetectorDataProcessorWithRoi('pslintensity2d', psl, [PixelIntensity()])

		pslroi1 = DetectorDataProcessorWithRoi('pslroi1', psl, [SumMaxPositionAndValue()])
		pslroi2 = DetectorDataProcessorWithRoi('pslroi2', psl, [SumMaxPositionAndValue()])
		pslroi3 = DetectorDataProcessorWithRoi('pslroi3', psl, [SumMaxPositionAndValue()])

	except gda.factory.FactoryException:
		print " *** Could not connect to PSL SCMOS (FactoryException)"
	except java.lang.IllegalStateException:
		print " *** Could not connect to PSL SCMOS (IllegalStateException)"
	print "-------------------------------PSL SCMOS INIT COMPLETE---------------------------------------"
else:
	print "*** PSL SCMOS disabled from localStation.py "

###############################################################################
###                                Uniblitz                                 ###
###############################################################################
if installation.isLive():

	import pd_setBinaryPvAndWait
	unishtr = pd_setBinaryPvAndWait.SetBinaryPvAndWait('unishtr',"BL16B-EA-SHTR-03:SHUTTER",delayAfterAskingToMove=0.1, flip = True )
	from scannable.hw.exposeUniblitzShutter import ExposeUniblitzShutter
	expuni = ExposeUniblitzShutter('expuni', 'BL16B-EA-SHTR-03')#,'BL16B-EA-DET-01:SCALER1' )

	from scannable.hw.TimingSystemScannable import TimingSystemScannable
	expunishort = TimingSystemScannable('ts', 'BL16B-EA-DIO-01:BO0','BL16B-EA-EVR-01')#, 'BL16B-EA-DET-01:SCALER1' )


###############################################################################
###                          PSU01 (Agilent E364xA)                         ###
###############################################################################
if installation.isLive():
	psu1v = SetPvAndWaitForCallbackWithSeparateReadback('psu1v','BL16B-EA-PSU-01:CPCB:SETDEMAND', 'BL16B-EA-PSU-01:VOLT:MEAS', 10)




###############################################################################
###                                  I04                                    ###
###############################################################################
if installation.isLive():
	import scannable.i04Scannable
	io4cam = scannable.i04Scannable.I04Scannable('i04cam', expuni)


###############################################################################
###                                Diffcalc                                 ###
###############################################################################

if USE_YOU_DIFFCALC_ENGINE:
	run('example/startup/b16fourcircle_you_engine.py')
else:
	run('example/startup/b16fivecircle.py')
energy.setLevel(4)
hkl.setLevel(5) #@UndefinedVariable


###############################################################################
###                          IPP image processor                            ###
###############################################################################
if not installation.isLive():
	ipp = ProcessingDetectorWrapper('ipp', ippws4, [], panel_name='Detector Plot', panel_name_rcp="Plot 1")
	#setIPPWrapperDir( '/scratch/ws/trunk/plugins/uk.ac.gda.core/scripts/gdascripts/scannable/detector/dummy/focused_beam_dataset//') #@UndefinedVariable
	ipp.returnPathAsImageNumberOnly = True
	def emulateSlowFileSystem(makeSlow = True):
		if makeSlow:
			ipp.iFileLoader = FileSystemEmulatingTIFFImageLoader
			FileSystemEmulatingTIFFImageLoader.setEmulatedFileAvailabilityLatencyMillis(2000)
			FileSystemEmulatingTIFFImageLoader.setEmulatedFileLoadTimeMillis(1000)
			print "Emulating file system for ipp:"
			print "   File availability latency is 2s"
			print "   File load time is 1s"
		else:
			print "*Not* emulating file system for ipp"

else:
	ipp = ProcessingDetectorWrapper('ipp', ippws4, [], panel_name='Detector Plot', toreplace='N://', replacement='/dls/b16/data/', panel_name_rcp='Plot 1')
	ipp2 = ProcessingDetectorWrapper('ipp2', ippws10, [], panel_name='Detector Plot', toreplace='N://', replacement='/dls/b16/data/', panel_name_rcp='Plot 1')
	visit_setter.addDetectorAdapter(IPPAdapter(ippws4, subfolder='ippimages', create_folder=True, toreplace='/dls/b16/data', replacement='N:/')) #@UndefinedVariable)
	visit_setter.addDetectorAdapter(ProcessingDetectorWrapperAdapter(ipp, report_path = False))
	visit_setter.addDetectorAdapter(IPPAdapter(ippws10, subfolder='ippimages', create_folder=True, toreplace='/dls/b16/data', replacement='N:/')) #@UndefinedVariable)
	visit_setter.addDetectorAdapter(ProcessingDetectorWrapperAdapter(ipp2, report_path = False))

def configureScanPipeline(length = None, simultaneousPoints = None):
	lengthProp = LocalProperties.GDA_SCAN_MULTITHREADED_SCANDATA_POINT_PIPElINE_LENGTH
	simultaneousProp = LocalProperties.GDA_SCAN_MULTITHREADED_SCANDATA_POINT_PIPElINE_POINTS_TO_COMPUTE_SIMULTANEOUSELY
	def show():
		print "ScanDataPoint pipeline:"
		print " " + lengthProp + " = " + LocalProperties.get(lengthProp, '4') # duplicated in ScannableCommands @UndefinedVariable
		print " " + simultaneousProp + " = " + LocalProperties.get(simultaneousProp, '3') # duplicated in ScannableCommands @UndefinedVariable
	if (length == None) or (simultaneousPoints == None):
		show()
	else:
		LocalProperties.set(lengthProp, `length`) #@UndefinedVariable
		LocalProperties.set(simultaneousProp, `simultaneousPoints`) #@UndefinedVariable
		show()


ipppeak2d = DetectorDataProcessorWithRoi('peak2d', ipp, [TwodGaussianPeak()])
ippmax2d = DetectorDataProcessorWithRoi('max2d', ipp, [SumMaxPositionAndValue()])
ippintensity2d = DetectorDataProcessorWithRoi('intensity2d', ipp, [PixelIntensity()])


#ipp = ProcessingDetectorWrapper('ipp', ippws4, [p_peak], panel_name='ImageProPlus Plot', toreplace='N:/', replacement='/dls/b16/data/', iFileLoader=ConvertedTIFFImageLoader)
#ipp_plot_only = ProcessingDetectorWrapper('ipp', ippws4, [], panel_name='ImageProPlus Plot', toreplace='N:/', replacement='/dls/b16/data/', iFileLoader=ConvertedTIFFImageLoader)
#p_peak.det = ipp_plot_only
#p_max.det = ipp_plot_only
#p_peak.det = ipp_plot_only
#p_max.det = ipp_plot_only


### Shutter ###
if not installation.isLive():
	ehshutter = Shutter('ehshutter', DummyEpicsShutterPositioner())
#	ohshutter = Shutter('ohshutter', DummyEpicsShutterPositioner())
else:
	pass
	ehshutter = Shutter('ehshutter', shtr1) #@UndefinedVariable
#	ohshutter = Shutter('ohshutter', shtr0) #@UndefinedVariable


if installation.isLive():
	from scannable.hw.cryostream700 import Cryostream700
	cryo = Cryostream700('cryo', 'BL16B-EA-CSTRM-01:')

	from scannable.hw.agilentpsu import AgilentPsuCurrent, AgilentPsuVoltage
	psu1c = AgilentPsuCurrent('psu1c', 'BL16B-EA-PSU-01:', 5, .001)
	psu1v = AgilentPsuVoltage('psu1v','BL16B-EA-PSU-01:', 5)


if installation.isLive() and ENABLE_PCOEDGE:

	pcoedge = SwitchableHardwareTriggerableProcessingDetectorWrapper(
		'pcoedge',
		_pcoedge,  # @UndefinedVariable
		None,
		_pcoedge_for_snaps,  # @UndefinedVariable
		[],
		panel_name='Detector Plot',
		panel_name_rcp='Plot 1',
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)

	pcoedgepeak2d = DetectorDataProcessorWithRoi('peak2d', pcoedge, [TwodGaussianPeak()],prefix_name_to_extranames=True) # modified to work with bimorph script
	pcoedgemax2d = DetectorDataProcessorWithRoi('max2d', pcoedge, [SumMaxPositionAndValue()],prefix_name_to_extranames=False)
	pcoedgeintensity2d = DetectorDataProcessorWithRoi('intensity2d', pcoedge, [PixelIntensity()],prefix_name_to_extranames=False)


if installation.isLive() and ENABLE_PCO4000:

	pco4000 = SwitchableHardwareTriggerableProcessingDetectorWrapper(
		'pco4000',
		_pco4000,  # @UndefinedVariable
		None,
		_pco4000_for_snaps,  # @UndefinedVariable
		[],
		panel_name='Detector Plot',
		panel_name_rcp='Plot 1',
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)

	pco4000peak2d = DetectorDataProcessorWithRoi('peak2d', pco4000, [TwodGaussianPeak()],prefix_name_to_extranames=True) # modified to work with bimorph script
	pco4000max2d = DetectorDataProcessorWithRoi('max2d', pco4000, [SumMaxPositionAndValue()],prefix_name_to_extranames=False)
	pco4000intensity2d = DetectorDataProcessorWithRoi('intensity2d', pco4000, [PixelIntensity()],prefix_name_to_extranames=False)


	#visit_setter.addDetectorAdapter(FileWritingDetectorAdapter(_pcoedge, subfolder='pcoedge', create_folder=True, toreplace='/dls/b16/', replacement='N:/')) #@UndefinedVariable)
	#visit_setter.addDetectorAdapter(ProcessingDetectorWrapperAdapter(pcoedge, report_path = False))
	pcoedge.disable_operation_outside_scans = True
	pcoedgepeak2d = DetectorDataProcessorWithRoi('pcoedgepeak2d', pcoedge, [TwodGaussianPeak()],prefix_name_to_extranames=False)
	pcoedgemax2d = DetectorDataProcessorWithRoi('pcoedgemax2d', pcoedge, [SumMaxPositionAndValue()],prefix_name_to_extranames=False)
	pcoedgeintensity2d = DetectorDataProcessorWithRoi('pcoedgeintensity2d', pcoedge, [PixelIntensity()],prefix_name_to_extranames=False)
###############################################################################
###                                   TEMPORARY                              ###
###############################################################################
class Bladesum(PseudoDevice):
	def __init__(self,a,b,c,d):
		self.a = a
		self.b = b
		self.c = c
		self.d = d
		self.name = "bladesum"

		self.setExtraNames(['bladesum']);
		self.setOutputFormat(['%6.6f'])
		self.setInputNames([])

	def getPosition(self):
		return self.a.getPosition() + self.b.getPosition() + self.c.getPosition() + self.d.getPosition()

	def asynchronousMoveTo(self,waitUntilTime):
		pass

	def isBusy(self):
		return False


class Bladevdif(PseudoDevice):
	def __init__(self,c,d):
		self.c = c
		self.d = d
		self.name = "bladevdif"

		self.setExtraNames(['bladevdif']);
		self.setOutputFormat(['%6.6f'])
		self.setInputNames([])

	def getPosition(self):
		return self.c.getPosition() - self.d.getPosition()

	def asynchronousMoveTo(self,waitUntilTime):
		pass

	def isBusy(self):
		return False

if installation.isLive():
#	bladesum = Bladesum(bladel,blader,bladet,bladeb)
#	bladevdif = Bladevdif(bladet,bladeb)
	b16angle = pd_readPvAfterWaiting.ReadPvAfterWaiting("b16angle","FE16B-DI-BEAM-01:Y:ANGLE")
	ai4prompt=pd_readPvAfterWaiting.ReadPvAfterWaiting("ai4prompt","BL16B-EA-RIM-01:AI4")
	ai5prompt=pd_readPvAfterWaiting.ReadPvAfterWaiting("ai5prompt","BL16B-EA-RIM-01:AI5")
	ai6prompt=pd_readPvAfterWaiting.ReadPvAfterWaiting("ai6prompt","BL16B-EA-RIM-01:AI6")
	ai7prompt=pd_readPvAfterWaiting.ReadPvAfterWaiting("ai7prompt","BL16B-EA-RIM-01:AI7")
	Braggtemp=pd_readPvAfterWaiting.ReadPvAfterWaiting("Braggtemp","BL16B-OP-DCM-01:TEMP:BRAGG")

	bo1trigBasic = pd_toggleBinaryPvAndWait.ToggleBinaryPvAndWait('bo1trig','BL16B-EA-DIO-01:BO1',True )
	bo1trigFancy = pd_toggleBinaryPvAndWaitFancy.ToggleBinaryPvAndWaitFancy('bo1trig','BL16B-EA-DIO-01:BO1',True )
	bo1trig = bo1trigBasic

	vortlivet = pd_readPvAfterWaiting.ReadPvAfterWaiting("vlivet","BL16B-EA-DET-01:aim_adc1.ELTM")
	vortrealt = pd_readPvAfterWaiting.ReadPvAfterWaiting("vrealt","BL16B-EA-DET-01:aim_adc1.ERTM")
	vortroi1lo = pd_readPvAfterWaiting.ReadPvAfterWaiting("roi1lo","BL16B-EA-DET-01:aim_adc1.R1LO")
	vortroi1hi = pd_readPvAfterWaiting.ReadPvAfterWaiting("roi1hi","BL16B-EA-DET-01:aim_adc1.R1HI")

	test2mot5.outputFormat = ['%.4f'] #@UndefinedVariable
	test2mot6.outputFormat = ['%.4f']#@UndefinedVariable
	fcX.outputFormat = ['%.4f']#@UndefinedVariable
	fcY.outputFormat = ['%.4f']#@UndefinedVariable
	fcZ.outputFormat = ['%.4f']#@UndefinedVariable

	FBDAC2level=pd_readPvAfterWaiting.ReadPvAfterWaiting("FBDAC2level","BL16B-OP-DCM-01:FB:DAC:02")

	topup_time=pd_readPvAfterWaiting.ReadPvAfterWaiting("topup_time","SR-CS-FILL-01:COUNTDOWN")
	topup_gate_short=pd_readPvAfterWaiting.ReadPvAfterWaiting("topup_gate_short","BL16B-EA-EVR-01:SR-PRE-INJ-GATE")

	topup_time.setOutputFormat(['%6.5f'])#@UndefinedVariable

##################################################################################
# C Bloomer PVs
cb1=pd_readPvAfterWaiting.ReadPvAfterWaiting("cb1","BL16B-EA-RIM-05:A:WAVE1")
cb2=pd_readPvAfterWaiting.ReadPvAfterWaiting("cb2","BL16B-EA-RIM-05:A:WAVE2")


from scannable.epicsArray import EpicsArrayAverageScannable
waveA1 = EpicsArrayAverageScannable("waveA1", "BL16B-EA-RIM-05:A:WAVE1")
waveA2 = EpicsArrayAverageScannable("waveA2", "BL16B-EA-RIM-05:A:WAVE2")
waveA3 = EpicsArrayAverageScannable("waveA3", "BL16B-EA-RIM-05:A:WAVE3")
waveA4 = EpicsArrayAverageScannable("waveA4", "BL16B-EA-RIM-05:A:WAVE4")
waveA5 = EpicsArrayAverageScannable("waveA5", "BL16B-EA-RIM-05:A:WAVE5")
waveA6 = EpicsArrayAverageScannable("waveA6", "BL16B-EA-RIM-05:A:WAVE6")
waveA7 = EpicsArrayAverageScannable("waveA7", "BL16B-EA-RIM-05:A:WAVE7")
waveA8 = EpicsArrayAverageScannable("waveA8", "BL16B-EA-RIM-05:A:WAVE8")
waveB1 = EpicsArrayAverageScannable("waveB1", "BL16B-EA-RIM-05:B:WAVE1")
waveB2 = EpicsArrayAverageScannable("waveB2", "BL16B-EA-RIM-05:B:WAVE2")
waveB3 = EpicsArrayAverageScannable("waveB3", "BL16B-EA-RIM-05:B:WAVE3")
waveB4 = EpicsArrayAverageScannable("waveB4", "BL16B-EA-RIM-05:B:WAVE4")
waveB5 = EpicsArrayAverageScannable("waveB5", "BL16B-EA-RIM-05:B:WAVE5")
waveB6 = EpicsArrayAverageScannable("waveB6", "BL16B-EA-RIM-05:B:WAVE6")
waveB7 = EpicsArrayAverageScannable("waveB7", "BL16B-EA-RIM-05:B:WAVE7")
waveB8 = EpicsArrayAverageScannable("waveB8", "BL16B-EA-RIM-05:B:WAVE8")
waveC1 = EpicsArrayAverageScannable("waveC1", "BL16B-EA-RIM-06:C:WAVE1")
waveC2 = EpicsArrayAverageScannable("waveC2", "BL16B-EA-RIM-06:C:WAVE2")
waveC3 = EpicsArrayAverageScannable("waveC3", "BL16B-EA-RIM-06:C:WAVE3")
waveC4 = EpicsArrayAverageScannable("waveC4", "BL16B-EA-RIM-06:C:WAVE4")
waveC5 = EpicsArrayAverageScannable("waveC5", "BL16B-EA-RIM-06:C:WAVE5")
waveC6 = EpicsArrayAverageScannable("waveC6", "BL16B-EA-RIM-06:C:WAVE6")
waveC7 = EpicsArrayAverageScannable("waveC7", "BL16B-EA-RIM-06:C:WAVE7")
waveC8 = EpicsArrayAverageScannable("waveC8", "BL16B-EA-RIM-06:C:WAVE8")

waves = ScannableGroup("waves",
		[waveA1, waveA2, waveA3, waveA4, waveA5, waveA6, waveA7, waveA8,
		waveB1, waveB2, waveB3, waveB4, waveB5, waveB6, waveB7, waveB8,
		waveC1, waveC2, waveC3, waveC4, waveC5, waveC6, waveC7, waveC8])

##################################################################################




###################################################################################
######         Setup for I18 experiment                                     #######
###################################################################################
#execfile('/dls_sw/b16/software/gda/config/scripts/I18VortexUtilities.py')
#execfile('/dls_sw/b16/software/gda/config/scripts/pd_metadata.py')
#execfile('/dls_sw/b16/software/gda/config/scripts/i18_scans.py')
#ScanDataPoint.delimiter = " "
#import scannable.fileWritingXmap
#xmap = scannable.fileWritingXmap.FileWritingXmap("xmap", xmapMca)
#scannable.fileWritingXmap.configureScannableLevels(tbdetX ,tbdetY)
#s#canMetaData = MetaDataPD("scanMetaData")
#add_default(scanMetaData)
#print("finished running xmap")
###############################################################################
###                           Run localStationUser                          ###
###############################################################################

visit_setter.setDetectorDirectories()
print "======================================================================"
print visit_setter
print "======================================================================"


if installation.isLive():
	run('femtogains')

run('setup_bimorph')

from bimorph import runOptimisation
import bimorph
from bimorph_mirror_optimising import SlitScanner
from gdascripts.scannable.detector.dummy.focused_beam_dataset import CreateImageReadingDummyDetector
from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessor

# NOTE: BimorphParameters beans added in server/main/common/plumbing.xml
# TODO: There is no server/main/common/plumbing.xml (MBB)
#BeansFactory.setClasses([BimorphParameters])
#b16beansfactory.setClassList(["uk.ac.gda.beans.exafs.DetectorParameters", "uk.ac.gda.beans.vortex.VortexParameters", "uk.ac.gda.beans.microfocus.MicroFocusScanParameters"])

#slitscanner = SlitScanner(peak2dName="pcoedgepeak2d") # MBB Use new parameterised SlitScanner
slitscanner = SlitScanner()
from bimorph_mirror_optimising import ScanAborter
scanAborter = ScanAborter("scanAborter",rc, 100) #@UndefinedVariable
slitscanner.setScanAborter(scanAborter)

bm=eembimorph # temporary workaround of bug in gui @UndefinedVariable

from dummy_pd_bimorph import Bimorph

dummy_bimorph = Bimorph("dummy_bimorph", 0, 8)

from gdascripts.pd.dummy_pds import DummyPD
dummy_x = DummyPD("x")
dummy_x.asynchronousMoveTo(430)

dummy_rawDet = CreateImageReadingDummyDetector.create(dummy_x)
dummy_det = ProcessingDetectorWrapper('dummy_det', dummy_rawDet, [], panel_name='Detector Plot')
dummy_det.display_image=False
dummy_peak2d = DetectorDataProcessor('dummy_peak2d', dummy_det, [TwodGaussianPeak()])


print "Attempting to run localStationUser.py for users script directory"
try:
	run("localStationUser")
except java.io.FileNotFoundException, e:
	print "No localStationUser run"

#from scannable.performance import LogTimeSinceLastGetPositionLessConstant
#twrite = LogTimeSinceLastGetPositionLessConstant('twrite', 'BL16B-EA-IOC-10:TWRITE')

#print "Adding ai5 default detector"
#addmeta ai5

from scannable.sampler import RmsProcessor, Sampler

print "Creating ai6sampler. This takes a vector argument comprised of collection time and number of samples"
print "e.g. 'scan x 1 3 1 ai6sampler [.5 3]' takes three .5s second exposures."

ai1sampler = Sampler(ai1, [RmsProcessor()], True) #@UndefinedVariable
ai2sampler = Sampler(ai2, [RmsProcessor()], True) #@UndefinedVariable
ai3sampler = Sampler(ai3, [RmsProcessor()], True) #@UndefinedVariable
ai4sampler = Sampler(ai4, [RmsProcessor()], True) #@UndefinedVariable
ai5sampler = Sampler(ai5, [RmsProcessor()], True) #@UndefinedVariable
ai6sampler = Sampler(ai6, [RmsProcessor()], True) #@UndefinedVariable
ai7sampler = Sampler(ai7, [RmsProcessor()], True) #@UndefinedVariable

print "Creating keithley1gain, keithley2gain and keithley3gain"
import scannable.hw.keithley
keithley1gain = scannable.hw.keithley.KeithleyGain('keithley1gain', 'BL16B-EA-IAMP-01')
keithley2gain = scannable.hw.keithley.KeithleyGain('keithley2gain', 'BL16B-EA-IAMP-02')
keithley3gain = scannable.hw.keithley.KeithleyGain('keithley3gain', 'BL16B-EA-IAMP-03')


print "creating waitForAi8 (to be less than .1)"
import scannable.condition
waitForAi8 = scannable.condition.WaitForCondition('waitForAi8', ai8, 'val<1')  # @UndefinedVariable

if installation.isLive():
	micospiezo1.outputFormat = ['%f']
	micospiezo2.outputFormat = ['%f']


print "Creating caen0 & caen1"
from scannable.hw.caenhvsupply import CaenHvSupply
caen0 = CaenHvSupply('caen0', 'BL16B-EA-CAEN-01:', 0)
caen1 = CaenHvSupply('caen1', 'BL16B-EA-CAEN-01:', 1)

#print "*" * 80
#print "mt8886-2: Writing NeXus files and medpix to return images only"
#print "*" * 80
#
#medipix.returnPathAsImageNumberOnly = True
#LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusDataWriter")
print "Done!"
from epics_scripts.device.scannable.pvscannables_with_logic import PVWithSeparateReadbackAndToleranceScannable
furnace = PVWithSeparateReadbackAndToleranceScannable('furnace', pv_set='BL16B-EA-TEMPC-01:RAMP:LIMIT:SET', pv_read='BL16B-EA-TEMPC-01:TEMP', timeout=36000, tolerance = .1)
run('startup_pie725')


#print "!!!! Renaming pcoedgepeak2d --> peak2d for bimorph scripts !!!!"
#exec('peak2d = pcoedgepeak2d')
print "!!!! Using pcoedgepeak2d for peak2d for bimorph scripts !!!!"

peak2d=pcoedgepeak2d
max2d=pcoedgemax2d
intensity2d=pcoedgeintensity2d
