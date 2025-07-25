if __name__ != "__main__":
	raise RuntimeError("localStation should not be used in import statements")
#### Take out if causes problem - Pete won't be happy.
from scisoftpy import *
####
scannp = scan #@UndefinedVariable
vararg_alias("scannp") #@UndefinedVariable
print "*** Creating scan with no processing: scannp"
from gda.analysis import ScanFileHolder
from gda.analysis.io import PilatusTiffLoader, SRSLoader
from gda.configuration.properties import LocalProperties
from gda.device.monitor import EpicsMonitor
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient #@UnusedImport
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import alias, cmd, ls, pause, reset_namespace, run #@UnusedImport
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
from det_wrapper.DetectorDataProcessorForNexus import DetectorDataProcessorWithRoiForNexus
from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper, HardwareTriggerableProcessingDetectorWrapper, SwitchableHardwareTriggerableProcessingDetectorWrapper
from gdascripts.scannable.detector.epics.EpicsPilatus import EpicsPilatus
from gdascripts.scannable.timerelated import t, dt, w, clock, epoch #@UnusedImport
from gdascripts.scannable.dummy import SingleInputDummy #@UnusedImport
from gdascripts.utils import caget, caput #@UnusedImport
from gdascripts.visit import VisitSetter, PilatusAdapter, IPPAdapter, ProcessingDetectorWrapperAdapter, FileWritingDetectorAdapter
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
from init.energy_chcut import energy_chcut
from tomographyScan import tomoFlyScan, tomoScan

def print_banner(message):
	border_size = max([len(line) for line in message.split("\n")])
	border = "=" * border_size
	print(border)
	print(message)
	print(border)
	

print_banner("Running B16 specific initialisation code")

ENABLE_PILATUS = True
ENABLE_PCOEDGE = True
ENABLE_PCO4000 = True

ENABLE_LAKESHORE_340 = False
ENABLE_PIE_725 = False

#USE_YOU_DIFFCALC_ENGINE = True
USE_YOU_DIFFCALC_ENGINE = False  # Use old diffcalc


from gda.factory import Finder
daserver = Finder.find('daserver')
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
###                  Add useful functions and scan commands                 ###
###############################################################################

visit_setter = VisitSetter()

visit = visit_setter.visit
datadir = visit_setter.datadir
GeneralCommands.alias("datadir")
GeneralCommands.alias("visit")


def disable_nexus():
	LocalProperties.set("gda.data.scan.datawriter.dataFormat", "SrsDataFile")

def enable_nexus():
	LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusScanDataWriter")


from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()

from gdascripts.analysis.datasetprocessor.oned.CenFromSPEC import CenFromSPEC
scan_processor.processors.append(CenFromSPEC())


#from gdascripts.scannable.installStandardScannableMetadataCollection import *
meta.readFromNexus = True
meta.rootNamespaceDict=globals()
note.rootNamespaceDict=globals()

add_default(meta)

from misc_functions import createVisitSubDir


print "Adding dummy devices x,y and z"
x=SingleInputDummy("x")
y=SingleInputDummy("y")
z=SingleInputDummy("z")

print "Adding timer devices t, dt, and w, clock"

from gdascripts.pd.time_pds import waittimeClass, actualTimeClass
actualTime=actualTimeClass("actualTime") # returns UNIX timestamp

alpha.setOutputFormat(['%.5f']) #@UndefinedVariable
delta.setOutputFormat(['%.5f']) #@UndefinedVariable
omega.setOutputFormat(['%.5f']) #@UndefinedVariable
chi.setOutputFormat(['%.5f']) #@UndefinedVariable
phi.setOutputFormat(['%.5f']) #@UndefinedVariable
fcarmTheta.setOutputFormat(['%.5f']) #@UndefinedVariable
fcarm2Theta.setOutputFormat(['%.5f']) #@UndefinedVariable

def create_detector_roi(det, name):
	return DetectorDataProcessorWithRoiForNexus(name, det, [SumMaxPositionAndValue()])

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


	# Set up ProcessingDetectorWrapper using simad (area detector simulation)
	from gdaserver import _simad  # @UnresolvedImport
	simad = SwitchableHardwareTriggerableProcessingDetectorWrapper("simad", _simad, None, None, [], panel_name_rcp='simad', returnPathAsImageNumberOnly=True)
	simadpeak2d = DetectorDataProcessorWithRoiForNexus("simadpeak2d", simad, [TwodGaussianPeak()])
	simadmax2d = DetectorDataProcessorWithRoiForNexus("simadmax2d", simad, [SumMaxPositionAndValue()])
	simadintensity2d = DetectorDataProcessorWithRoiForNexus('simadintensity2d', simad, [PixelIntensity()])

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
sca.assign(9, ['ct9', 'apd2'])
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
if False and installation.isLive():
	print "Creating TCA scanables"
	vtca=device_tca.TCA('BL16B-EA-DET-01:tca1')

	vroi1 = pd_tca.tcasca('vroi1',"%4.3f",vtca,"%",'1')
	vroi2 = pd_tca.tcasca('vroi2',"%4.3f",vtca,"%",'2')
	vroi3 = pd_tca.tcasca('vroi3',"%4.3f",vtca,"%",'3')
else:
	print "* Not installing tca (as not live installation) *"


###############################################################################
###                             Analogue Outputs                            ###
###############################################################################
if installation.isLive():
	print "Manually creating Analogue Outputs from RIM card"
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
	except (Exception, java.lang.Exception), e:
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
	except (Exception, java.lang.Exception), e:
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


if installation.isLive():
	print "Creating Jena Piezo devices. Channel1 -> jpx, Channel2 -> jpy"
	#print "* Seems to work okay with Readback rate set to 0.2 s on epics panel *"
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
	print "Installing atto devices from epics BL16B-EA-ECC..."
	try:
		from scannable.epics.ecc100axis import createEcc100Axis

		attoltilt2 = createEcc100Axis("attoltilt2", "BL16B-EA-ECC-01:ACT0:")
		attoutilt2 = createEcc100Axis("attoutilt2", "BL16B-EA-ECC-01:ACT1:")
		attorot2   = createEcc100Axis("attorot2",   "BL16B-EA-ECC-01:ACT2:")

		attoltilt1 = createEcc100Axis("attoltilt1", "BL16B-EA-ECC-02:ACT0:")
		attoutilt1 = createEcc100Axis("attoutilt1", "BL16B-EA-ECC-02:ACT1:")
		attorot1   = createEcc100Axis("attorot1",   "BL16B-EA-ECC-02:ACT2:")

		attol1 = createEcc100Axis("attol1", "BL16B-EA-ECC-03:ACT0:")
		attol2 = createEcc100Axis("attol2", "BL16B-EA-ECC-03:ACT1:")
		attol3 = createEcc100Axis("attol3", "BL16B-EA-ECC-03:ACT2:")

		attol4 = createEcc100Axis("attol4", "BL16B-EA-ECC-04:ACT0:")
		attol5 = createEcc100Axis("attol5", "BL16B-EA-ECC-04:ACT1:")
		attol6 = createEcc100Axis("attol6", "BL16B-EA-ECC-04:ACT2:")
	except:
		print "Could not initialise attocube devices"
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
	monotuner=Tuner('monotuner', MaxPositionAndValue(), Scan, dcmpiezo, 0.1, 9.5, 0.1, ai1, .1) #@UndefinedVariable
	monotuner.use_backlash_correction = True

def tunemono(): 
	monotuner.tune()
	inc dcmpiezo -0.25

###############################################################################
###                                 A3 XIA Filters                          ###
###############################################################################
if installation.isLive():
	print("Creating XIA Filter objects")
	try:
		att3a = XiaFilter('att3a', 'BL16B-OP-ATTN-03', 1, timeout=5)
		att3b = XiaFilter('att3b', 'BL16B-OP-ATTN-03', 2, timeout=5)
		att3c = XiaFilter('att3c', 'BL16B-OP-ATTN-03', 3, timeout=5)
		att3d = XiaFilter('att3d', 'BL16B-OP-ATTN-03', 4, timeout=5)
	except (Exception, java.lang.Exception) as e:
		print("ERROR: Could not initialise XIA Filters")
		print(e)

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
if installation.isLive():
	print "Adding checkbeam device (rc>190mA, 60s wait after beam back)"
	print "   (change threshold with checkbeam.minumumThreshold=12345)"
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
	checkrc = WaitWhileScannableBelowThreshold('checkrc', rc, 5, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=5) #@UndefinedVariable
	checkfe = WaitForScannableState('checkfe', frontend, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=60) #@UndefinedVariable
	checkshtr1 = WaitForScannableState('checkshtr1', shtr1, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=60) #@UndefinedVariable
	checkab0 = WaitForScannableState('checkab0', ab0, secondsBetweenChecks=1,secondsToWaitAfterBeamBackUp=60) #@UndefinedVariable
	checkbeam = ScannableGroup('checkbeam', [checkrc,  checkfe, checkshtr1, checkab0])
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
if installation.isLive():
	print "** 23oct08: Adding pcocam1 and pcocam2 device to move pco optics. Note these assume all moves take 2s.  Change delay with pcocam1.delayAfterAskingToMove = num_seconds"
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
									panel_name_rcp='pil',
									iFileLoader=PilatusTiffLoader,
									fileLoadTimout=120,
									printNfsTimes=False,
									returnPathAsImageNumberOnly=True)

		#pil100kdet = EpicsPilatus('pil100kdet', 'BL16I-EA-PILAT-01:','/dls/b16/detectors/im/','test','%s%s%d.tif')
		#pil100k = ProcessingDetectorWrapper('pil100k', pil100kdet, [], toreplace=None, replacement=None, iFileLoader=PilatusTiffLoader, fileLoadTimout=15, returnPathAsImageNumberOnly=True)
		#pil100k.processors=[DetectorDataProcessorWithRoiForNexus('max', pil100k, [SumMaxPositionAndValue()], False)]
		#pil100k.printNfsTimes = True


		pil.processors=[DetectorDataProcessorWithRoiForNexus('max', pil, [SumMaxPositionAndValue()], False)]

		pil.display_image = True
		pilpeak2d = DetectorDataProcessorWithRoiForNexus('pilpeak2d', pil, [TwodGaussianPeak()])
		pilmax2d = DetectorDataProcessorWithRoiForNexus('pilmax2d', pil, [SumMaxPositionAndValue()])
		pilintensity2d = DetectorDataProcessorWithRoiForNexus('pilintensity2d', pil, [PixelIntensity()])
		pilroi1 = create_detector_roi(pil, 'pilroi1')
		pilroi2 = create_detector_roi(pil, 'pilroi2')
		pilroi3 = create_detector_roi(pil, 'pilroi3')
		pilroi4 = create_detector_roi(pil, 'pilroi4')
		pilroi5 = create_detector_roi(pil, 'pilroi5')

		pilgain = pd_setPvAndWait.SetPvAndWait('pilgain', 'BL16B-EA-PILAT-01:Gain', delayAfterAskingToMove=0.5)
		pilgain.setOutputFormat(['%.0f'])
		pilthresh = pd_setPvAndWait.SetPvAndWait('pilthresh', 'BL16B-EA-PILAT-01:ThresholdEnergy', delayAfterAskingToMove=0.5)
		pilsettings = pd_readManyPVs.ReadManyPVs('pilsettings','BL16B-EA-PILAT-01:READ',['VCMP','VRF','VTRM','VADJ','VCAL','VRFS','VDEL'])

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
																		panel_name_rcp='medipix',
																		iFileLoader=PilatusTiffLoader,
																		fileLoadTimout=60,
																		printNfsTimes=False,
									returnPathAsImageNumberOnly=True)
		medipix.disable_operation_outside_scans = True
		medipix_threshold0_kev = SetPvAndWaitForCallbackWithSeparateReadback('medipix_threshold_kev', 'BL16B-EA-DET-06:MPX:ThresholdEnergy0', 'BL16B-EA-DET-06:MPX:ThresholdEnergy0_RBV', 10)
		#pil100kdet = EpicsPilatus('pil100kdet', 'BL16I-EA-PILAT-01:','/dls/b16/detectors/im/','test','%s%s%d.tif')
		#pil100k = ProcessingDetectorWrapper('pil100k', pil100kdet, [], toreplace=None, replacement=None, iFileLoader=PilatusTiffLoader, fileLoadTimout=15, returnPathAsImageNumberOnly=True)
		#pil100k.processors=[DetectorDataProcessorWithRoiForNexus('max', pil100k, [SumMaxPositionAndValue()], False)]
		#pil100k.printNfsTimes = True

		medipix.processors=[DetectorDataProcessorWithRoiForNexus('max', medipix, [SumMaxPositionAndValue()], False)]


		medipix.display_image = True
		medipixpeak2d = DetectorDataProcessorWithRoiForNexus('medipixpeak2d', medipix, [TwodGaussianPeak()])
		medipixmax2d = DetectorDataProcessorWithRoiForNexus('medipixmax2d', medipix, [SumMaxPositionAndValue()])
		medipixintensity2d = DetectorDataProcessorWithRoiForNexus('medipixintensity2d', medipix, [PixelIntensity()])
		
		medipixroi1 = create_detector_roi(medipix, 'medipixroi1')
		medipixroi2 = create_detector_roi(medipix, 'medipixroi2')
		medipixroi3 = create_detector_roi(medipix, 'medipixroi3')


	except gda.factory.FactoryException:
		print " *** Could not connect to pilatus (FactoryException)"
	except 	java.lang.IllegalStateException:
		print " *** Could not connect to pilatus (IllegalStateException)"
	print "-------------------------------PILATUS INIT COMPLETE---------------------------------------"
else:
	print "*** Pilatus disabled from localStation.py "

if installation.isLive():
	print "-------------------------------MEDIPIX QUAD INIT---------------------------------------"
	try:
		medipix4 = SwitchableHardwareTriggerableProcessingDetectorWrapper('medipix4',
																		_medipix4,
																		None,
																		_medipix4_for_snaps,
																		[],
																		panel_name_rcp='medipix4',
																		iFileLoader=PilatusTiffLoader,
																		fileLoadTimout=60,
																		printNfsTimes=False,
									returnPathAsImageNumberOnly=True)
		medipix4.disable_operation_outside_scans = True
		medipix4_threshold0_kev = SetPvAndWaitForCallbackWithSeparateReadback('medipix4_threshold_kev', 'BL16B-EA-DET-20:Merlin2:ThresholdEnergy0', 'BL16B-EA-DET-20:Merlin2:ThresholdEnergy0_RBV', 10)
		from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
		medipix4.processors=[DetectorDataProcessorWithRoi('max', medipix4, [SumMaxPositionAndValue()], False)]

		medipix4.display_image = True
		medipix4peak2d = DetectorDataProcessorWithRoiForNexus('medipix4peak2d', medipix4, [TwodGaussianPeak()])
		medipix4max2d = DetectorDataProcessorWithRoiForNexus('medipix4max2d', medipix4, [SumMaxPositionAndValue()])
		medipix4intensity2d = DetectorDataProcessorWithRoiForNexus('medipix4intensity2d', medipix4, [PixelIntensity()])
		medipix4roi1 = create_detector_roi(medipix, 'medipix4roi1')
		medipix4roi2 = create_detector_roi(medipix, 'medipix4roi2')
		medipix4roi3 = create_detector_roi(medipix, 'medipix4roi3')

	except gda.factory.FactoryException:
		print " *** Could not connect to medipix4 (FactoryException)"
	except 	java.lang.IllegalStateException:
		print " *** Could not connect to medipix4 (IllegalStateException)"
	print "-------------------------------PILATUS INIT COMPLETE---------------------------------------"
else:
	print "*** medipix4 disabled from localStation.py "

if installation.isLive():
	print "-------------------------------PSL INIT---------------------------------------"
	try:

		PSL_AUTO_RECONNECT = False
		if not PSL_AUTO_RECONNECT:
			psl = SwitchableHardwareTriggerableProcessingDetectorWrapper('psl',
			                                                             _psl,
			                                                             None,
			                                                             _psl_for_snaps,
			                                                             [],
			                                                             panel_name_rcp='psl',
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
			                                                       panel_name_rcp='psl',
			                                                       fileLoadTimout=60,
			                                                       printNfsTimes=False,
			                                                       returnPathAsImageNumberOnly=True)
		psl.disable_operation_outside_scans = True
		psl.processors=[DetectorDataProcessorWithRoiForNexus('max', psl, [SumMaxPositionAndValue()], False)]
		psl.display_image = True
		pslpeak2d = DetectorDataProcessorWithRoiForNexus('pslpeak2d', psl, [TwodGaussianPeak()])
		pslmax2d = DetectorDataProcessorWithRoiForNexus('pslmax2d', psl, [SumMaxPositionAndValue()])
		pslitensity2d = DetectorDataProcessorWithRoiForNexus('pslintensity2d', psl, [PixelIntensity()])

		pslroi1 = DetectorDataProcessorWithRoiForNexus('pslroi1', psl, [SumMaxPositionAndValue()])
		pslroi2 = DetectorDataProcessorWithRoiForNexus('pslroi2', psl, [SumMaxPositionAndValue()])
		pslroi3 = DetectorDataProcessorWithRoiForNexus('pslroi3', psl, [SumMaxPositionAndValue()])

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
	try:
		import pd_setBinaryPvAndWait
		unishtr = pd_setBinaryPvAndWait.SetBinaryPvAndWait('unishtr',"BL16B-EA-SHTR-03:SHUTTER",delayAfterAskingToMove=0.1, flip = True )
		from scannable.hw.exposeUniblitzShutter import ExposeUniblitzShutter
		expuni = ExposeUniblitzShutter('expuni', 'BL16B-EA-SHTR-03')#,'BL16B-EA-DET-01:SCALER1' )

		from scannable.hw.TimingSystemScannable import TimingSystemScannable
		expunishort = TimingSystemScannable('ts', 'BL16B-EA-DIO-01:BO1','BL16B-EA-EVR-01')#, 'BL16B-EA-DET-01:SCALER1' )
	except (Exception, java.lang.Exception) as e:
		print("ERROR: Could not setup Uniblitz devices")


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
	#run('example/startup/b16fourcircle_you_engine.py')
	print("Diffcalc scripts have been deleted")
else:
	#run('example/startup/b16fivecircle.py')
	print("Diffcalc scripts have been deleted")
energy.setLevel(4) # Not sure if need this when there is no diffcalc
#hkl.setLevel(5) #@UndefinedVariable


###############################################################################
###                          IPP image processor                            ###
###############################################################################
if not installation.isLive():
	ipp = ProcessingDetectorWrapper('ipp', ippws4, [], panel_name_rcp="ipp")
	#setIPPWrapperDir( '/scratch/ws/trunk/plugins/uk.ac.gda.core/scripts/gdascripts/scannable/detector/dummy/focused_beam_dataset//') #@UndefinedVariable
	ipp.returnPathAsImageNumberOnly = True

else:
	ipp = ProcessingDetectorWrapper('ipp', ippws4, [], toreplace='N://', replacement='/dls/b16/data/', panel_name_rcp='ipp')
	ipp2 = ProcessingDetectorWrapper('ipp2', ippws10, [], toreplace='N://', replacement='/dls/b16/data/', panel_name_rcp='ipp2', returnPathAsImageNumberOnly=True)
#	ipp3 = ProcessingDetectorWrapper('ipp3', ippwsme07m, [], toreplace='X://', replacement='/dls/b16/', panel_name_rcp='Plot 1')
	ipp3 = ProcessingDetectorWrapper('ipp3', ippwsme07m, [], toreplace='X://', replacement='/dls/b16/', panel_name_rcp='ipp3', returnPathAsImageNumberOnly=True)
	visit_setter.addDetectorAdapter(IPPAdapter(ippws4, subfolder='ippimages', create_folder=True, toreplace='/dls/b16/data', replacement='N:/')) #@UndefinedVariable)
	visit_setter.addDetectorAdapter(ProcessingDetectorWrapperAdapter(ipp, report_path = False))
	visit_setter.addDetectorAdapter(IPPAdapter(ippws10, subfolder='ippimages', create_folder=True, toreplace='/dls/b16/data', replacement='N:/')) #@UndefinedVariable)
	visit_setter.addDetectorAdapter(ProcessingDetectorWrapperAdapter(ipp2, report_path = False))
	visit_setter.addDetectorAdapter(IPPAdapter(ippwsme07m, subfolder='ippimages', create_folder=True, toreplace='/dls/b16', replacement='X:/')) #@UndefinedVariable)
	visit_setter.addDetectorAdapter(ProcessingDetectorWrapperAdapter(ipp3, report_path = False))

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


ipppeak2d = DetectorDataProcessorWithRoiForNexus('peak2d', ipp, [TwodGaussianPeak()])
ippmax2d = DetectorDataProcessorWithRoiForNexus('max2d', ipp, [SumMaxPositionAndValue()])
ippintensity2d = DetectorDataProcessorWithRoiForNexus('intensity2d', ipp, [PixelIntensity()])

if installation.isLive():
	ipp2peak2d = DetectorDataProcessorWithRoiForNexus('ipp2peak2d', ipp2, [TwodGaussianPeak()])
	ipp2max2d = DetectorDataProcessorWithRoiForNexus('ipp2max2d', ipp2, [SumMaxPositionAndValue()])
	ipp2intensity2d = DetectorDataProcessorWithRoiForNexus('ipp2intensity2d', ipp2, [PixelIntensity()])
	
	ipp2roi1 = create_detector_roi(ipp2, 'ipp2roi1')
	ipp2roi2 = create_detector_roi(ipp2, 'ipp2roi2')
	ipp2roi3 = create_detector_roi(ipp2, 'ipp2roi3')
	
	ipp3peak2d = DetectorDataProcessorWithRoiForNexus('ipp3peak2d', ipp3, [TwodGaussianPeak()])
	ipp3max2d = DetectorDataProcessorWithRoiForNexus('ipp3max2d', ipp3, [SumMaxPositionAndValue()])
	ipp3intensity2d = DetectorDataProcessorWithRoiForNexus('ipp3intensity2d', ipp3, [PixelIntensity()])



#ipp = ProcessingDetectorWrapper('ipp', ippws4, [p_peak], toreplace='N:/', replacement='/dls/b16/data/', iFileLoader=ConvertedTIFFImageLoader)
#ipp_plot_only = ProcessingDetectorWrapper('ipp', ippws4, [], toreplace='N:/', replacement='/dls/b16/data/', iFileLoader=ConvertedTIFFImageLoader)
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
		panel_name_rcp='pcoedge',
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)

	pcoedge.poke_inactive_detector = False # TODO: set to True for temp hack - remove ASAP

	pcoedgepeak2d = DetectorDataProcessorWithRoiForNexus('peak2d', pcoedge, [TwodGaussianPeak()],prefix_name_to_extranames=True) # modified to work with bimorph script
	pcoedgemax2d = DetectorDataProcessorWithRoiForNexus('max2d', pcoedge, [SumMaxPositionAndValue()],prefix_name_to_extranames=False)
	pcoedgeintensity2d = DetectorDataProcessorWithRoiForNexus('intensity2d', pcoedge, [PixelIntensity()],prefix_name_to_extranames=False)

	pcoedge_multi = SwitchableHardwareTriggerableProcessingDetectorWrapper(
		'pcoedge_multi',
		_pcoedge_multi,  # @UndefinedVariable
		None,
		_pcoedge_for_snaps,  # @UndefinedVariable
		[],
		panel_name_rcp='pcoedge',
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)

	pcoedge_multi_peak2d = DetectorDataProcessorWithRoiForNexus('peak2d', pcoedge_multi, [TwodGaussianPeak()],prefix_name_to_extranames=True) # modified to work with bimorph script
	pcoedge_multi_max2d = DetectorDataProcessorWithRoiForNexus('max2d', pcoedge_multi, [SumMaxPositionAndValue()],prefix_name_to_extranames=False)
	pcoedge_multi_intensity2d = DetectorDataProcessorWithRoiForNexus('intensity2d', pcoedge_multi, [PixelIntensity()],prefix_name_to_extranames=False)


if installation.isLive():

	sydor = SwitchableHardwareTriggerableProcessingDetectorWrapper(
		'sydor',
		_sydor,  # @UndefinedVariable
		None,
		_sydor_for_snaps,  # @UndefinedVariable
		[],
		panel_name_rcp='sydor',
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)

	sydorpeak2d = DetectorDataProcessorWithRoiForNexus('peak2d', sydor, [TwodGaussianPeak()],prefix_name_to_extranames=True) 
	sydormax2d = DetectorDataProcessorWithRoiForNexus('max2d', sydor, [SumMaxPositionAndValue()],prefix_name_to_extranames=False)
	sydorintensity2d = DetectorDataProcessorWithRoiForNexus('intensity2d', sydor, [PixelIntensity()],prefix_name_to_extranames=False)
	
	
if installation.isLive() and ENABLE_PCO4000:

	pco4000 = SwitchableHardwareTriggerableProcessingDetectorWrapper(
		'pco4000',
		_pco4000,  # @UndefinedVariable
		None,
		_pco4000_for_snaps,  # @UndefinedVariable
		[],
		panel_name_rcp='pco4000',
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)

	pco4000peak2d = DetectorDataProcessorWithRoiForNexus('peak2d', pco4000, [TwodGaussianPeak()],prefix_name_to_extranames=True) # modified to work with bimorph script
	pco4000max2d = DetectorDataProcessorWithRoiForNexus('max2d', pco4000, [SumMaxPositionAndValue()],prefix_name_to_extranames=False)
	pco4000intensity2d = DetectorDataProcessorWithRoiForNexus('intensity2d', pco4000, [PixelIntensity()],prefix_name_to_extranames=False)


	#visit_setter.addDetectorAdapter(FileWritingDetectorAdapter(_pcoedge, subfolder='pcoedge', create_folder=True, toreplace='/dls/b16/', replacement='N:/')) #@UndefinedVariable)
	#visit_setter.addDetectorAdapter(ProcessingDetectorWrapperAdapter(pcoedge, report_path = False))
	pcoedge.disable_operation_outside_scans = True
	pcoedgepeak2d = DetectorDataProcessorWithRoiForNexus('pcoedgepeak2d', pcoedge, [TwodGaussianPeak()],prefix_name_to_extranames=False)
	pcoedgemax2d = DetectorDataProcessorWithRoiForNexus('pcoedgemax2d', pcoedge, [SumMaxPositionAndValue()],prefix_name_to_extranames=False)
	pcoedgeintensity2d = DetectorDataProcessorWithRoiForNexus('pcoedgeintensity2d', pcoedge, [PixelIntensity()],prefix_name_to_extranames=False)

if installation.isLive() :
	dcam9 = SwitchableHardwareTriggerableProcessingDetectorWrapper(
		'dcam9',
		_dcam9,  # @UndefinedVariable
		None,
		_dcam9,
		[],
		panel_name_rcp='dcam9',
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)

	dcam9peak2d = DetectorDataProcessorWithRoiForNexus('dcam9peak2d', dcam9, [TwodGaussianPeak()]) # modified to work with bimorph script
	dcam9max2d = DetectorDataProcessorWithRoiForNexus('dcam9max2d', dcam9, [SumMaxPositionAndValue()])
	dcam9intensity2d = DetectorDataProcessorWithRoiForNexus('dcam9intensity2d', dcam9, [PixelIntensity()])
	dcam9roi = create_detector_roi(dcam9, 'dcam9roi')
	
	dcam10 = SwitchableHardwareTriggerableProcessingDetectorWrapper(
		'dcam10',
		_dcam10,  # @UndefinedVariable
		None,
		_dcam10,
		[],
		panel_name_rcp='dcam10',
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)

	dcam10peak2d = DetectorDataProcessorWithRoiForNexus('dcam10peak2d', dcam10, [TwodGaussianPeak()]) # modified to work with bimorph script
	dcam10max2d = DetectorDataProcessorWithRoiForNexus('dcam10max2d', dcam10, [SumMaxPositionAndValue()])
	dcam10intensity2d = DetectorDataProcessorWithRoiForNexus('dcam10intensity2d', dcam10, [PixelIntensity()])
	dcam10roi = create_detector_roi(dcam10, 'dcam10roi')

def configure_fds(name, detector, snaps_detector):
	wrapper = SwitchableHardwareTriggerableProcessingDetectorWrapper(
		name, detector,	None, snaps_detector,
		[],	panel_name_rcp=name,
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)
	peak2d = DetectorDataProcessorWithRoiForNexus(name + "_peak2d", wrapper, [TwodGaussianPeak()])
	max2d = DetectorDataProcessorWithRoiForNexus(name + "_max2d", wrapper, [SumMaxPositionAndValue()])
	intensity2d = DetectorDataProcessorWithRoiForNexus(name + "_intensity2d", wrapper, [PixelIntensity()])
	roi = create_detector_roi(wrapper, name + "_roi")
	return [wrapper, peak2d, max2d, intensity2d, roi]
	
if installation.isLive() :
	[
	fds1,
	fds1_peak2d,
	fds1_max2d,
	fds1_intensity2d,
	fds1_roi
	] = configure_fds("fds1", _fds1, _fds1_for_snaps)

	[
	fds2, fds2_peak2d,
	fds2_max2d,
	fds2_intensity2d,
	fds2_roi
	] = configure_fds("fds2", _fds2, _fds2_for_snaps)

if installation.isLive():
	pslv1 = SwitchableHardwareTriggerableProcessingDetectorWrapper(
		'pslv1',
		_pslv1,  # @UndefinedVariable
		None,
		_pslv1_for_snaps,  # @UndefinedVariable
		[],
		panel_name_rcp='pslv1',
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)

	pslv1peak2d = DetectorDataProcessorWithRoiForNexus('pslv1peak2d', pslv1, [TwodGaussianPeak()],prefix_name_to_extranames=False)
	pslv1max2d = DetectorDataProcessorWithRoiForNexus('pslv1max2d', pslv1, [SumMaxPositionAndValue()],prefix_name_to_extranames=False)
	pslv1intensity2d = DetectorDataProcessorWithRoiForNexus('pslv1intensity2d', pslv1, [PixelIntensity()],prefix_name_to_extranames=False)


if installation.isLive():

	balor = SwitchableHardwareTriggerableProcessingDetectorWrapper(
		'balor',
		_balor,  # @UndefinedVariable
		None,
		_balor_for_snaps,  # @UndefinedVariable
		[],
		panel_name_rcp='balor',
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)

	#balor.poke_inactive_detector = False # TODO: set to True for temp hack - remove ASAP

	balorpeak2d = DetectorDataProcessorWithRoiForNexus('peak2d', balor, [TwodGaussianPeak()],prefix_name_to_extranames=True) # modified to work with bimorph script
	balormax2d = DetectorDataProcessorWithRoiForNexus('max2d', balor, [SumMaxPositionAndValue()],prefix_name_to_extranames=False)
	balorintensity2d = DetectorDataProcessorWithRoiForNexus('intensity2d', balor, [PixelIntensity()],prefix_name_to_extranames=False)

	"""balor_multi = SwitchableHardwareTriggerableProcessingDetectorWrapper(
		'balor_multi',
		_balor_multi,  # @UndefinedVariable
		None,
		_balor_for_snaps,  # @UndefinedVariable
		[],
		panel_name_rcp='balor',
		returnPathAsImageNumberOnly=True,
		fileLoadTimout=60)"""

def setup_xspress3_detector(detector):
	try:
		print "Setting up "+ detector.getName() + " detector."
		run("xspress_functions.py")
		basePvName = detector.getController().getBasePv()
		
		# this collects a software frame if necessary, but sets trigger mode to TTL Veto Only
		setup_xspress_detector(basePvName)
		
		# so correct here
		detector.setTriggerMode(0) # Software trigger mode
		
		setupResGrades(basePvName, False)
		
		set_hdf5_filetemplate(basePvName)
		for c in range(1, detector.getController().getNumElements()+1) :
			# BL18B-EA-XSP3X-01:C2_SCAS:EnableCallbacks
			scaPv = basePvName+":C%d_SCAS:"%(c)
			mcaEnablePv = basePvName+":MCA%d:Enable"%(c)
			CAClient.put(scaPv+"EnableCallbacks", 1)
			CAClient.put(scaPv+"TS:TSNumPoints", 10000)
			# Refresh the time series data 1 time per second
			CAClient.put(scaPv+"TS:TSRead.SCAN", 6)
			CAClient.put(mcaEnablePv, 1)
			
		
		print "Set detector to not apply DTC factors"
		set_xspress_use_dtc(basePvName, False)
	except:
		print("Failed to configure " + detector.getName())

if installation.isLive():
	from gdaserver import xspress3X, xspress3Xsingle
	setup_xspress3_detector(xspress3X)
	setup_xspress3_detector(xspress3Xsingle)

###############################################################################
###                                TEMPORARY                                ###
###############################################################################
class Bladesum(ScannableMotionBase):
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


class Bladevdif(ScannableMotionBase):
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

 	bo1trigBasic = pd_toggleBinaryPvAndWait.ToggleBinaryPvAndWait('bo1trig','BL16B-EA-DIO-01:BO1',False )
	bo1trigFancy = pd_toggleBinaryPvAndWaitFancy.ToggleBinaryPvAndWaitFancy('bo1trig','BL16B-EA-DIO-01:BO1',True )
	bo1trig = bo1trigBasic

	bo2trigBasic = pd_toggleBinaryPvAndWait.ToggleBinaryPvAndWait('bo2trig','BL16B-EA-DIO-01:BO2',True )
	bo2trigFancy = pd_toggleBinaryPvAndWaitFancy.ToggleBinaryPvAndWaitFancy('bo2trig','BL16B-EA-DIO-01:BO2',True )
	bo2trig = bo2trigBasic

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
print_banner(visit_setter.__str__())


#femtos are gone - Igor 27-06-18
#if installation.isLive():
#	run('femtogains')

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

from pd_bimorph_caenels import BimorphCaenels
bmcaenels_g1 = BimorphCaenels("bmcaenels_g1", range(1, 9), "BL16B-OP-PSU-01:METLAB:", "BL16B-OP-PSU-01:METLAB:GROUP0:")
bmcaenels_g2 = BimorphCaenels("bmcaenels_g2", range(1, 9), "BL16B-OP-PSU-01:METLAB:", "BL16B-OP-PSU-01:METLAB:GROUP1:")

from gdascripts.pd.dummy_pds import DummyPD
dummy_x = DummyPD("x")
dummy_x.asynchronousMoveTo(430)

dummy_rawDet = CreateImageReadingDummyDetector.create(dummy_x)
dummy_det = ProcessingDetectorWrapper('dummy_det', dummy_rawDet, [])
dummy_det.display_image=False
dummy_peak2d = DetectorDataProcessor('dummy_peak2d', dummy_det, [TwodGaussianPeak()])


print "Attempting to run localStationUser.py for users script directory"
try:
	run("localStationUser")
	print "localStationUser.py completed."
except java.io.FileNotFoundException, e:
	print "No localStationUser run"
except:
	print "Error running localStationUser"
	print sys.exc_info()
finally:
	print "="*80

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

print "Creating stanford1sensitivity, stanford2sensitivity, stanford1unit and stanford2unit scannables"

from scannable.hw.stanford_sensitivity import StanfordSensitivity
stanford1sensitivity = StanfordSensitivity('stanford1sensitivity', "BL16B-EA-STANF-01:SENS:")
stanford2sensitivity = StanfordSensitivity('stanford2sensitivity', "BL16B-EA-STANF-02:SENS:")

from scannable.hw.stanford_unit import StanfordUnit
stanford1unit = StanfordUnit('stanford1unit', "BL16B-EA-STANF-01:SENS:")
stanford2unit = StanfordUnit('stanford2unit', "BL16B-EA-STANF-02:SENS:")

from scannable.smartamps import Keithley, Stanford
from gdaserver import ai1, ai2, ai3  # @UnresolvedImport
keithley = Keithley("keithley", keithley1gain, ai1)
stanford1 = Stanford("stanford1", stanford1sensitivity, stanford1unit, ai2)
stanford2 = Stanford("stanford2", stanford2sensitivity, stanford2unit, ai3)
print("Created smart amplifiers: %s, %s and %s (https://confluence.diamond.ac.uk/x/JAUPF)" % (keithley.name, stanford1.name, stanford2.name))

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

from scannable.fluorescence_roi_plotter import FluorescenceROIPlotter
if installation.isLive():  # TODO add dummy one! This detector is a permanent beamline fixture
	try:
		from gdaserver import xmapFluorescenceDetector2
		xmap2plotter = FluorescenceROIPlotter("xmap2plotter", xmapFluorescenceDetector2)
	except:
		print("Could not create xmap2plotter - is the detector configured?")
	
try:
	from gdaserver import xspress3X, xspress3Xsingle
	xsp3plotter = FluorescenceROIPlotter("xsp3plotter", xspress3X, roi_column_prefix="Element 0_")
	xsp3singleplotter = FluorescenceROIPlotter("xsp3singleplotter", xspress3Xsingle, roi_column_prefix="Element 0_")
except:
	print("Could not create xsp3plotter - is xspress3X configured?")

if installation.isLive():
	#ensure xmapMca settings are correct (no epics screen) - one off
	try:
		caput("ME13C-EA-DET-01:CollectMode", 0) #MCA Spectra
		caput("ME13C-EA-DET-01:PresetMode", 1) #Real mode
		caput("ME13C-EA-DET-01:MCA1.NUSE", 2048) #binning
		caput("ME13C-EA-DET-01:DXP1:MaxEnergy", 20.48)
		caput("ME13C-EA-DET-01:DXP2:MaxEnergy", 20.48)
		caput("ME13C-EA-DET-01:DXP3:MaxEnergy", 20.48)
		caput("ME13C-EA-DET-01:DXP4:MaxEnergy", 20.48)
	except:
		print "WARNING: Could not ensure xmapMca settings are correct"
	
	
	#ensure xmapMca2 settings are correct (no epics screen) - one off
	try:
		#xmap2.getController().getEdxdController().getSubDetector(0).setReadingDoneIfNotAquiring(True)
		caput("BL16B-EA-XMAP-02:CollectMode", 0) #MCA Spectra
		caput("BL16B-EA-XMAP-02:PresetMode", 1) #Real mode
		caput("BL16B-EA-XMAP-02:MCA1.NUSE", 2048) #binning
		caput("BL16B-EA-XMAP-02:DXP1:MaxEnergy", 20.48)
		caput("BL16B-EA-XMAP-02:DXP2:MaxEnergy", 20.48)
		caput("BL16B-EA-XMAP-02:DXP3:MaxEnergy", 20.48)
		caput("BL16B-EA-XMAP-02:DXP4:MaxEnergy", 20.48)
		caput("BL16B-EA-XMAP-02:ReadAll.SCAN", 0)
	except:
		print "WARNING: Could not ensure xmapMca settings are correct"




# Create scannable to check that the nexus writer is enabled when the xmapMca is used
# If only dat files are written then the full spectrum is not recorded
from scannable.utility.check_data_writer import CheckDataWriter
_xmapNexusDataWriterChecker = CheckDataWriter('_xmapNexusDataWriterChecker', ['xmapMca', 'xmapMca2'], 'NexusScanDataWriter')
add_default(_xmapNexusDataWriterChecker)

def pcoedge_multi_n(n):
	pcoedge_multi.detector.collectionStrategy.numberOfImagesPerCollection = n

def pcoedge_multi_period(t):
	pcoedge_multi.detector.collectionStrategy.acquirePeriod = t

#Configure scan interrupters
from scannable.scan_stopper import ScanStopper, ThresholdInterrupt
ai2thresh = ThresholdInterrupt(ai2, 0.02)
#ai2thresh.threshold = newThreshold
ai2stop = ScanStopper('ai2stop', ai2thresh)

#print "*" * 80
#print "mt8886-2: Writing NeXus files and medpix to return images only"
#print "*" * 80
#
#medipix.returnPathAsImageNumberOnly = True
#LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusScanDataWriter")

if installation.isLive():
	print "Setting up Zyla detector"
	zyla = SwitchableHardwareTriggerableProcessingDetectorWrapper(
			'zyla',
			_zyla,
			None,
			_zyla_for_snaps,
			[],
			panel_name_rcp='zyla',
			fileLoadTimout=60,
			printNfsTimes=False,
			returnPathAsImageNumberOnly=True)
	
	zyla.display_image = True
	zylamax2d = DetectorDataProcessorWithRoiForNexus('zylamax2d', zyla, [SumMaxPositionAndValue()])
	zylapeak2d = DetectorDataProcessorWithRoiForNexus('zylapeak2d', zyla, [TwodGaussianPeak()])
	zylaintensity2d = DetectorDataProcessorWithRoiForNexus('zylaintensity2d', zyla, [PixelIntensity()])
	
	#zyla.processors=[DetectorDataProcessorWithRoiForNexus('peak', zyla, [SumMaxPositionAndValue(), TwodGaussianPeakWithCalibration()], False)]
	#zyla needs scaling factors?
	#zyla.processors[0].processors[1].setScalingFactors(1, 1)
	
	zylaroi1 = create_detector_roi(zyla, 'zylaroi1')
	zylaroi2 = create_detector_roi(zyla, 'zylaroi2')
	zylaroi3 = create_detector_roi(zyla, 'zylaroi3')
	
	print "zyla setup"

if installation.isLive():
	from gdaserver import _imagestar, _imagestar_for_snaps  # @UnresolvedImport
	imagestar = SwitchableHardwareTriggerableProcessingDetectorWrapper(
			'imagestar',
			_imagestar,
			None,
			_imagestar_for_snaps,
			[],
			panel_name_rcp='imagestar',
			fileLoadTimout=60,
			printNfsTimes=False,
			returnPathAsImageNumberOnly=True)
	imagestarmax2d = DetectorDataProcessorWithRoiForNexus('imagestarmax2d', imagestar, [SumMaxPositionAndValue()])
	imagestarpeak2d = DetectorDataProcessorWithRoiForNexus('imagestarpeak2d', imagestar, [TwodGaussianPeak()])
	imagestarintensity2d = DetectorDataProcessorWithRoiForNexus('imagestarintensity2d', imagestar, [PixelIntensity()])

######################################################################################################################################
#Linkam temperature controller
print "Setting up Linkam TS1500 hot stage from I18"

run("linkam.py")
lkts1500 = Linkam("lkts1500", "BL16B-EA-TEMPC-01:")


######################################################################################################################################
#LakeShore Temperature controller
if ENABLE_LAKESHORE_340:
	print "Setting up LakeShore 340 Temperature Controller from I16"

	run('pd_LS340control.py')
#tset = EpicsLScontrol('tset','BL16B-EA-LS340-01:','K','%5.2f','0','1')
	ls340set = EpicsLScontrol('ls340set','BL16B-EA-LS340-01:','K','%5.2f','0','1')

	from gda.device.scannable import EpicsScannable
	Tc = EpicsScannable()
	Tc.name = 'Tc'
	Tc.pvName = 'BL16B-EA-LS340-01:KRDG2'
	Tc.userUnits = 'K'
	Tc.extraNames = ['Tc']
	Tc.outputFormat = ['%6f']
	Tc.configure()

	Td = EpicsScannable()
	Td.name = 'Td'
	Td.pvName = 'BL16B-EA-LS340-01:KRDG3'
	Td.userUnits = 'K'
	Td.extraNames = ['Td']
	Td.outputFormat = ['%6f']
	Td.configure()

	ls340ramp = EpicsScannable()
	ls340ramp.name = 'ls340ramp'
	ls340ramp.pvName = 'BL16B-EA-LS340-01:RAMP_S'
	ls340ramp.userUnits = 'K'
	ls340ramp.extraNames = ['ls340ramp']
	ls340ramp.outputFormat = ['%6f']
	ls340ramp.configure()

	ls340target=EpicsScannable()
	ls340target.name = 'ls340target'
	ls340target.pvName = 'BL16B-EA-LS340-01:SETP_S'
	ls340target.userUnits = 'K'
	ls340target.extraNames = ['ls340target']
#ls340target.inputFormat = ['%6f']
	ls340target.outputFormat = ['%6f']
	ls340target.configure()

	print "Done!"
######################################################################################################################################

from epics_scripts.device.scannable.pvscannables_with_logic import PVWithSeparateReadbackAndToleranceScannable
furnace = PVWithSeparateReadbackAndToleranceScannable('furnace', pv_set='BL16B-EA-TEMPC-01:RAMP:LIMIT:SET', pv_read='BL16B-EA-TEMPC-01:TEMP', timeout=36000, tolerance = .1)

if ENABLE_PIE_725:
	run('startup_pie725')


#print "!!!! Renaming pcoedgepeak2d --> peak2d for bimorph scripts !!!!"
#exec('peak2d = pcoedgepeak2d')
#print "!!!! Using pcoedgepeak2d for peak2d for bimorph scripts !!!!"

#peak2d=pcoedgepeak2d
#max2d=pcoedgemax2d
#intensity2d=pcoedgeintensity2d

DebenRigEnabled = True

if DebenRigEnabled:
	from scannable.hw.user.debenRig import DebenRig
	deben = DebenRig('deben', 'BL16B-EA-DEBEN-01:')

# From 1/10 Experiment
# scan dummyx 0 20 1 bo1trig 0.1 waitForDetectorStart waitForDetectorStop w 10
if installation.isLive():
	waitForDetectorStart = scannable.condition.WaitForCondition('waitForDetectorStart', zebra_pulse1_input, 'val>0')
	waitForDetectorStop = scannable.condition.WaitForCondition('waitForDetectorStop', zebra_pulse1_input, 'val<1')
	waitForDetectorStop.setLevel(11)
	w.setLevel(12)
	
	# Piezo oscillation stuff - remove after experiment is finished
	from scannable.epics.piezo_oscillator import create_osc_devices, OscillationDetectorWrapper, MotorWithBackgroundOscillations
	
	try:
		(amc100_osc, amc100_det) = create_osc_devices("amc100", "BL16B-EA-AMC-01:AXIS0:OSC:")
	except:
		print("amc100 objects not created - see logs")
	
	try:
		(amc100ofb_osc, amc100ofb_det) = create_osc_devices("amc100ofb", "BL16B-EA-AMC-02:AXIS0:OSC:")
	except:
		print("amc100ofb objects not created - see logs")
	
	try:
		(aerotech_osc, aerotech_det) = create_osc_devices("aerotech", "BL16B-MO-ATCH-01:OSC:")
		oscillate = OscillationDetectorWrapper(aerotech_det, aerotech_osc)
		aerotech = MotorWithBackgroundOscillations(aeropiezo, aerotech_osc)
	except:
		print("aerotech objects not created - see logs")



from mapscan import mapscan
alias(mapscan)
print("Imported `mapscan` for 2D map visualisation (see help(mapscan) for more information)")


print_banner("Initialisation complete")
