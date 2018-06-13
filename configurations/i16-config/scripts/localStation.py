print "============================================================="
print "Running I16 specific initialisation code from localStation.py"
print "============================================================="

from gda.configuration.properties import LocalProperties
LocalProperties.set('gda.scan.clearInterruptAtScanEnd', "False")

import installation

USE_NEXUS = True
if installation.isDummy():
	USE_DIFFCALC = True
	USE_CRYO_GEOMETRY = False

else:
	# see also notes below
	# Changed for Allesandro's experiment on Jan 20 2015 -- RobW
	#USE_DIFFCALC = False  # <-- change here for live gda!
	#USE_CRYO_GEOMETRY = False
	USE_DIFFCALC = False  # <-- change here for live gda!
	USE_CRYO_GEOMETRY = False # < -- chi will not move if True


USE_DUMMY_IDGAP_MOTOR = False
#USE_DUMMY_IDGAP_MOTOR = True
USE_XMAP= True

# Java
import java
from Jama import Matrix

# Python
import time
from time import sleep
from math import *
from javashell import *

# Gda 
from gda.analysis.io import  PilatusTiffLoader
from gda.configuration.properties import LocalProperties
from gda.device.epicsdevice import ReturnType
from gda.device.scannable import PseudoDevice
from gda.device.scannable import PseudoDevice, ScannableBase
from gda.epics import CAClient
from gda.epics import CAClient
from gda.jython.commands.GeneralCommands import alias, run
from uk.ac.diamond.daq.persistence.jythonshelf import LocalJythonShelfManager

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeakWithCalibration import TwodGaussianPeakWithCalibration
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.scan_stitching import Lcen, Rcen
from gdascripts.analysis.datasetprocessor.oned.GaussianEdge import GaussianEdge
import gdascripts.scan.concurrentScanWrapper
from gdascripts.utils import jobs
from gdascripts.scan import gdascans
from gdascripts.scannable.installStandardScannableMetadataCollection import * #@UnusedWildImport
from gdascripts.scannable.detector.epics.EpicsPilatus import EpicsPilatus
from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper, HardwareTriggerableProcessingDetectorWrapper, SwitchableHardwareTriggerableProcessingDetectorWrapper
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessor, DetectorDataProcessorWithRoi, HardwareTriggerableDetectorDataProcessor
from gdascripts.scannable.dummy import MultiInputExtraFieldsDummy, SingleInputDummy
from gdascripts.scannable.detector.epics.EpicsFirewireCamera import EpicsFirewireCamera

from epics.detector.NxProcessingDetectorWrapper import NxProcessingDetectorWrapper

# I16
import installation
import ShelveIO

### Configure shelveIO path
print "Configuring ShelveIO system"
installation.setLoadOldShelf(0)
shelveIoDir = LocalProperties.get("gda.var")
shelveIoDir  = shelveIoDir + "/oldStyleShelveIO/"
ShelveIO.ShelvePath = shelveIoDir
print "  ShelveIO path = ", shelveIoDir

from constants import *
from element_library import *
from scannable.toggleBinaryPvAndWaitScannable import ToggleBinaryPvAndWait
from misc_functions import list_scannables, listprint, frange, attributes, caput, caget, cagetArray, add, mult
import pd_offset
from analysis_FindScanPeak import FindScanPeak
from analysis_FindScanCentroid import findCentroidPoint, FindScanCentroid, readSRSDataFile
from device_serial import SerialDevice
from device_serial_ace import ace
from device_tca import TCA
from pd_epics import SingleEpicsPositionerSetAndGetOnlyClass
from pd_readSingleValueFromVectorScannable import ReadSingleValueFromVectorPDClass
from pd_time import tictoc, showtimeClass, mrwolfClass, showincrementaltimeClass, waittimeClass, TimeScannable, absoluteTimeClass
from pd_dummy import dummyClass
from pd_foilinserter import Foilinserter
from pd_attenuator import Atten
from pd_polarizationAnalyser_new_alpha import PolarizationAnalyser
from pd_epics import DisplayEpicsPVClass, SingleEpicsPositionerClass, SingleEpicsPositionerNoStatusClass, SingleEpicsPositionerSetAndGetOnlyClass, SingleEpicsPositionerNoStatusClass2, Epics_Shutter
from pd_ionpump import AllPumpsOnPD, EpicsIonpClass
from pd_struck import Struck
from pd_struck2 import Struck2
from pd_MoveScalarPDsToPresetValues import MoveScalarPDsToPresetValuesClass
from pd_qbpm import EPICSODQBPMClass, EPICSODQBPMClass2
from pd_tca import tcasca
from pd_mcachannel import McaChannel
from pd_mca import Mca
from pd_LS340readback import DisplayEpicsPVClassLS, DisplayEpicsPVClassLS2
from pd_LS340control import EpicsLScontrol
from pd_LS340setpoint import EpicsLSsetpoint
from pd_LakeshorePID import EpicsLakeshorePID
from pd_WaitForBeam import WaitForBeamPDClass, TimeToMachineInjectionClass, WaitForInjectionPDClass, WaitForInjectionPDClass2 
from pd_metadata_group import ReadPDGroupClass
from PhasePlateClass import PPPClass
from pd_diffractometerbase import DiffoBaseClass
from pd_x2000 import x2000scaClass
from pd_acescaler import acesca1
from device_serial_x2000 import x2000class
from pd_azihklClass import AzihklClass
from spechelp import * # aliases man objects
from scannable.MoveThroughOrigin import MoveThroughOriginScannable
from gda.device.scannable.scannablegroup import DeferredScannableGroup

# Configure here as nested beans are not configured
if USE_CRYO_GEOMETRY:
	eulerNames = ["phi", "chi", "eta", "mu", "delta", "gam"]
	for motor, name in zip(euler_cryo.getScannableMotors(), eulerNames):
		motor.name = name
		motor.configure()

##CHANGED TO USE LIMIT CRYOPHI
if USE_CRYO_GEOMETRY:
	_cryophi = euler_cryo.phi
	_cryophi.setUpperGdaLimits(165)
	_cryophi.setLowerGdaLimits(-165)
	exec("cryophi = MoveThroughOriginScannable(euler_cryo.phi)")
	#cryophi.name = "cryophi"
	exec("sixckappa_cryo = DeferredScannableGroup()")
	sixckappa_cryo.setGroupMembers([cryophi, kap, kth, kmu, kdelta, kgam])
	sixckappa_cryo.setName("sixckappa_cryo")
	sixckappa_cryo.deferredControlPoint = sixckappa.getDeferredControlPoint()
	sixckappa_cryo.deferOnValue = sixckappa.deferOnValue
	sixckappa_cryo.configure()


alias("jobs")

if USE_NEXUS:
	LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusDataWriter")
else:
	LocalProperties.set("gda.data.scan.datawriter.dataFormat", "SrsDataFile")


USE_NEXUS_METADATA_COMMANDS = True and USE_NEXUS

if USE_NEXUS_METADATA_COMMANDS:
	
	from gdascripts.metadata.metadata_commands import setTitle, getTitle, meta_add, meta_ll, meta_ls, meta_rm, meta_clear_alldynamical
	alias("setTitle")
	alias("getTitle")
	alias("meta_add")
	alias("meta_ll")
	alias("meta_ls")
	alias("meta_rm")
	
	meta.readFromNexus = True

	from gda.data.scan.datawriter import NexusDataWriter
	LocalProperties.set( NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME, "metashop" )

meta.rootNamespaceDict=globals()
note.rootNamespaceDict=globals()

###############################################################################
###                        Diffractometer axes                                #
###############################################################################
### Expose wrapped motors for Coordinated motion
print "Replacing ScannableMotors kphi, kap. kth, kmu, kdelta and kgam with wrappers supporting coordinated movement"
if USE_CRYO_GEOMETRY:
	sixc = sixckappa_cryo #@UndefinedVariable
	# NOTE: To switch cryophi between a real epics motor and the dummy axis sometimes used edit:
	#    /i16-config/servers/main/common/scannable/motor/sixckappa.xml
	# This axis is found on the Epics synoptic under 'ANC1' button: BL16I-MO-ANC-01:P1
	#
	# Diffcalc instructions here: http://confluence.diamond.ac.uk/display/I16/Diffcalc or http://confluence.diamond.ac.uk/x/855TAQ
else:
	sixc = sixckappa #@UndefinedVariable  NOTE: sixc is overwritten by diffcalc later
if USE_CRYO_GEOMETRY:	
	pass # TThere is already a cryophi
else:
	exec("kphi=sixc.kphi")
	
exec("kap=sixc.kap")
exec("kth=sixc.kth")
exec("kmu=sixc.kmu")
exec("kdelta=sixc.kdelta")
exec("kgam=sixc.kgam")

SIXC_MOTOR_NAMES = ['sixcKphiMotor', 'sixcKappaMotor', 'sixcKthMotor', 'sixcMuMotor', 'sixcDeltaMotor','sixcGammaMotor'] 
SIXC_SCANNABLEMOTOR_NAMES = ['kphi', 'kap', 'kth', 'kmu', 'kdelta', 'kgam']

print "Creating post_xps_restart"
def post_xps_restart():
	for mot in [Finder.getInstance().find(n) for n in SIXC_MOTOR_NAMES]:
		mot.forceCallback()

print "Creating set_assert_sixc_home_before_moving(True|False)"
def set_assert_sixc_homed_before_moving(b):
	for mot in [Finder.getInstance().find(n) for n in SIXC_MOTOR_NAMES]:
		mot.setAssertHomedBeforeMoving(b)

print "Creating set_sixc_returns_demand_position(True|False)"
def set_sixc_returns_demand_position(b):
	for scnmot in [Finder.getInstance().find(n) for n in SIXC_SCANNABLEMOTOR_NAMES]:
		scnmot.setReturnDemandPosition(b)

###############################################################################
###                            Generic Scannables                             #
###############################################################################

### Dummy IDGAP
if USE_DUMMY_IDGAP_MOTOR:
	exec("idgap=dummyClass('idgap')")

### Wrap all monitors into non Detectors
from gda.device.monitor import EpicsMonitor
from scannable.MonitorWrapper import MonitorWrapper
toPrint = ''
for objname in dir():
	if isinstance(eval(objname),EpicsMonitor):
		toPrint+= objname + " "
		exec(objname + " = MonitorWrapper(" + objname + ")")
print "Wrapped the monitors: " + toPrint

### Create dummy Scannables
print "Creating dummy scannables"
dummy = dummyClass('Dummy')
x=dummyClass('x')
y=dummyClass('y')
z=dummyClass('z')
q=dummyClass('q')
qq=dummyClass('qq')
progress=dummyClass('progress')
mie = MultiInputExtraFieldsDummy('mie', ['i1', 'i2'], ['e1'])


### Create time Scannables
print "Creating time scannables"
tim = TimeScannable('Time')
showtime=showtimeClass('Showtime')
inctime=showincrementaltimeClass('inctime')
waittime=waittimeClass('Waittime')
atime=absoluteTimeClass('atime')
w=waittime	#abreviated name
mrwolf=mrwolfClass('mrwolf')

### Create offset devices
print "Running startup_offsets.py: Starting database system..."
run("startup_offsets")
print "...Database system started"
offsetshelf=LocalJythonShelfManager.open('offsets')
print "  use 'offsetshelf' to see summary of offsets"
#delta_axis_offset.pil=9.5 
#delta_axis_offset.pil=9.0 #new offset 31/01/12 (179)
#delta_axis_offset.pil=9.2#new offset 12/09/13
delta_axis_offset.pil=8.6#new offset 19/02/17
do=delta_axis_offset

###############################################################################
###                            Generic Functions                            ###
###############################################################################

### Override gda's standard help command
print "Overriding gda's standard help command"
_gdahelp_orig = _gdahelp #@UndefinedVariable
def _gdahelp(o):
	_gdahelp_orig(o)
	try:
		print  o.__doc__
	except:
		pass
	
alias("help")

### Disable pos listing all Scannables when called with no args
pos_orig = pos
def pos(*args):
	if not args:
		print "pos command listing is disabled on I16"
	else:
		print pos_orig(*args)

### Create datadir functions
print "Running startup_dataDirFunctions.py"
print "  use 'datadir' to read the current directory or 'datadir name' to change it"
run("startup_dataDirFunctions") # depends on globals pil2mdet and pil100kdet
alias('datadir')

### Pipeline	
def configureScanPipeline(length = None, simultaneousPoints = None):
	lengthProp = LocalProperties.GDA_SCAN_MULTITHREADED_SCANDATA_POINT_PIPElINE_LENGTH
	simultaneousProp = LocalProperties.GDA_SCAN_MULTITHREADED_SCANDATA_POINT_PIPElINE_POINTS_TO_COMPUTE_SIMULTANEOUSELY
	def show():
		print "ScanDataPoint pipeline:"
		print " " + lengthProp + " = " + LocalProperties.get(lengthProp, '4') # duplicated in ScannableCommands
		print " " + simultaneousProp + " = " + LocalProperties.get(simultaneousProp, '3') # duplicated in ScannableCommands
	if (length == None) or (simultaneousPoints == None):
		show()
	else:
		LocalProperties.set(lengthProp, `length`)
		LocalProperties.set(simultaneousProp, `simultaneousPoints`)
		show()

alias('configureScanPipeline')



###############################################################################
###                   Configure scan data processing                        ###
###############################################################################

print "Importing analysis commands (peak, centroid & peak optimisation)"
#peak=FindScanPeak #@UndefinedVariable
cen=FindScanCentroid #@UndefinedVariable


from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
gdascripts.scan.concurrentScanWrapper.PRINTTIME = True
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()
scancn=gdascans.Scancn([scan_processor])
alias('scancn');print scancn.__doc__.split('\n')[2]
lup = dscan # line up apparently!
alias('lup')

scan_processor.rootNamespaceDict=globals()
scan_processor.duplicate_names = {'maxval':'maxpos', 'minval':'minpos'}
scan_processor.processors.append(Lcen())
scan_processor.processors.append(Rcen())
# Removed on May 1st 2014 as taking 100s
# scan_processor.processors.append(GaussianEdge(name='spedge')) # edge already maps to a function edgeDetectRobust



###############################################################################
###                        	 Diffractometer and hkl                         ###
###############################################################################

# Create diffractometer base scannable
print "Creating diffractometer base scannable base_z"
#base_z= DiffoBaseClass(basez1, basez2, basez3, [1.52,-0.37,0.]) #measured 28/11/07
base_z= DiffoBaseClass(basez1, basez2, basez3, [0.,0.,0.]) #jacks recal to zero in epics 8 keV direct beam 20/10/15

if installation.isLive():
	sixckappa.getContinuousMoveController().setScannableForMovingGroupToStart(_sixckappa_deffered_only)

if USE_CRYO_GEOMETRY:
	# u'phi', u'chi', u'eta', u'mu', u'delta', u'gam'
	# The standard euler device causes an offset to be applied to phi to account for any kappa rotation.
	# This correction is not applicable to the cryo-phi geometry. Create a coordinated motion group which
	# will ensure kmu, kdelta & kgam are moved in a coordinated way (cryophi will not).
	euler =  DeferredScannableGroup()
	euler.setName("euler")
	euler.setGroupMembers([cryophi, euler_cryo.chi, euler_cryo.eta, euler_cryo.mu, euler_cryo.delta, euler_cryo.gam])
	euler.deferredControlPoint = sixckappa.getDeferredControlPoint()
	euler.deferOnValue = sixckappa.deferOnValue
	euler.numberToMoveControlPoint = sixckappa.getNumberToMoveControlPoint()
	euler.checkStartControlPoint = sixckappa.getCheckStartControlPoint()
	euler.configure()
	phi = euler.phi
	chi = euler.chi
	eta = euler.eta
	exec("mu=euler.mu")
	exec("delta=euler.delta")
	exec("gam=euler.gam")
else:
	run("startup_diffractometer_euler")

if installation.isLive():
	thp=SingleEpicsPositionerClass('thp','BL16I-EA-POLAN-01:THETAp.VAL','BL16I-EA-POLAN-01:THETAp.RBV','BL16I-EA-POLAN-01:THETAp.DMOV','BL16I-EA-POLAN-01:THETAp.STOP','deg','%.4f')
	tthp=SingleEpicsPositionerClass('tthp','BL16I-EA-POLAN-01:DET1:2THETAp.VAL','BL16I-EA-POLAN-01:DET1:2THETAp.RBV','BL16I-EA-POLAN-01:DET1:2THETAp.DMOV','BL16I-EA-POLAN-01:DET1:2THETAp.STOP','deg','%.3f')
	dettrans=SingleEpicsPositionerClass('dettrans','BL16I-EA-POLAN-01:DET2:2THETAp.VAL','BL16I-EA-POLAN-01:DET2:2THETAp.RBV','BL16I-EA-POLAN-01:DET2:2THETAp.DMOV','BL16I-EA-POLAN-01:DET2:2THETAp.STOP','mm','%.3f')

if not USE_DIFFCALC:
	run("startup_diffractometer_hkl")
	azihkl=AzihklClass('aziref')
	azihkl.azir_function = azir
	psi.setInputNames(['psi'])
	psic.setInputNames(['psic'])
else:
	del sixc
	import diffcalc
	diffcalc_root = os.path.realpath(diffcalc.__file__).split('diffcalc/__init__.py')[0]
	diffcalc_startup_script = os.path.join(diffcalc_root, 'startup', 'i16.py')
	print "Starting Diffcalc by running: ", diffcalc_startup_script
	run(diffcalc_startup_script)
	exec("phi=euler.phi")
	exec("chi=euler.chi")
	exec("eta=euler.eta")
	exec("mu=euler.mu")
	exec("delta=euler.delta")
	exec("gam=euler.gam")

hkl.setLevel(6)


###############################################################################
###							       kbm tripod                               ###
###############################################################################

from scannable.tripod import TripodToolBase

#_kbm_common_geom = {'l':[134.2, 134.2, 134.2],
#		't':[219.129, 219.129, 84.963],
#		'psi':[-pi / 3, pi / 3, 0],
#		'theta':[pi / 4, pi / 4, -pi / 4],
#		'BX':[0.0, 0.0, 357.313],
#		'BY':[249.324, 0.0, 249.324 / 2] }

# New ball assembly - new leg lenths (need to check t values as well)
_kbm_common_geom = {'l':[142.0, 142.0, 142.0],
		't':[219.129, 219.129, 84.963],
		'psi':[-pi / 3, pi / 3, 0],
		'theta':[pi / 4, pi / 4, -pi / 4],
		'BX':[0.0, 0.0, 357.313],
		'BY':[249.324, 0.0, 249.324 / 2] }

import copy

# offets for KB mirrors
vmpitch_offset=pd_offset.Offset('vmpitch_offset', warningIfChangeGreaterThan=.5)
hmpitch_offset=pd_offset.Offset('hmpitch_offset', warningIfChangeGreaterThan=.5)
vmtrans_offset=pd_offset.Offset('vmtrans_offset', warningIfChangeGreaterThan=5)
hmtrans_offset=pd_offset.Offset('hmtrans_offset', warningIfChangeGreaterThan=5)
kbmx_offset=pd_offset.Offset('kbmx_offset', warningIfChangeGreaterThan=5)
kbmroll_offset=pd_offset.Offset('kbmroll_offset', warningIfChangeGreaterThan=.5)

try:
	kbm1 = TripodToolBase("kbm1", kbmbase, c=[152, 42.5, 63], **copy.deepcopy(_kbm_common_geom))				

	kbm2 = TripodToolBase("kbm2", kbmbase, c=[42, 42.5, 63], **copy.deepcopy(_kbm_common_geom))

	from pd_single_element_of_vector_pd import *
	#kbmx=single_element_of_vector_pd_class('kbmxx', kbm1, 'kbm1_x', help='Distance along beam (mm) for KBM2')
	#vmpitch=single_element_of_vector_pd_class('vfm_pitch', kbm1, 'kbm1_alpha3', help='KBM1 (VFM) pitch: positive degrees ~ 0.2 deg')
	#hmpitch=single_element_of_vector_pd_class('hfm_pitch', kbm2, 'kbm2_alpha2', help='KBM2 (HFM) pitch: positive degrees ~ 0.2 deg')
	#vmtrans=single_element_of_vector_pd_class('vfm_trans', kbm1, 'kbm1_y', help='KBM1 (VFM) translation perp to surface: +ve = down (away from beam)')
	#hmtrans=single_element_of_vector_pd_class('hfm_trans', kbm2, 'kbm2_z', help='KBM2 (HFM) translation perp to surface: +ve = towards ring (towards beam)')

    ##### new devices for KBM pitch and trans. Now with offsets.
	vmpitch=single_element_of_vector_pd_with_offset_and_scalefactor_class('vfm_pitch', kbm1, 'kbm1_alpha3', vmpitch_offset, help='KBM1 (VFM) pitch: positive degrees ~ 0.2 deg')
	hmpitch=single_element_of_vector_pd_with_offset_and_scalefactor_class('hfm_pitch', kbm2, 'kbm2_alpha2', hmpitch_offset, help='KBM2 (HFM) pitch: positive degrees ~ 0.2 deg')
	vmtrans=single_element_of_vector_pd_with_offset_and_scalefactor_class('vfm_trans', kbm1, 'kbm1_y', vmtrans_offset, help='KBM1 (VFM) translation perp to surface: +ve = down (away from beam)')
	hmtrans=single_element_of_vector_pd_with_offset_and_scalefactor_class('hfm_trans', kbm2, 'kbm2_z', hmtrans_offset, help='KBM2 (HFM) translation perp to surface: +ve = towards ring (towards beam)')
	kbmx=single_element_of_vector_pd_with_offset_and_scalefactor_class('kbm_x', kbm2, 'kbm2_z', kbmx_offset, help='Distance along beam (mm) for KBM2 - normally zero when box-face to sample is about 83 mm')
	kbmroll=single_element_of_vector_pd_with_offset_and_scalefactor_class('kbm_roll', kbm2, 'kbm2_alpha1', kbmroll_offset, help='KBM1/2 roll: usually close to zero')
	RsV=ReadSingleValueFromVectorPDClass
	kbm=ReadPDGroupClass('kbm calibrated mirror values',[RsV(vmtrans,0,'vmtrans','%.3f'),RsV(hmtrans,0,'hmtrans','%.3f'),RsV(vmpitch,0,'vmpitch','%.3f'),RsV(hmpitch,0,'hmpitch','%.3f'),RsV(kbmx,0,'kbmx','%.3f'),RsV(kbmroll,0,'kbmroll','%.3f')], help='Use help vmpitch etc for help on each. Use kbm1/kbm2 for raw values\nCalibrated values all close to zero when mirrors aligned with zero pitch ')

	###########################################

except NameError:
	print "Not creating kbm1 and kbm2 as the transient kbmbase device is not available"

###############################################################################
###############################################################################
###############################################################################
###############################################################################
#                           
#                             END OF DUMMYSTARTUP
#
if installation.isDummy():
	print "Running localStation.test_only.py ..."
	run("localStation.test_only")
	print "... completed localStation.test_only.py"
	print
	setDatadirPropertyFromPersistanceDatabase()
	raise Exception("Manually INTERRUPTING localStation.py run as this is a test installation")

###############################################################################
###############################################################################
###############################################################################
###############################################################################


###############################################################################
###                          Tune finepitch using QBPM                      ###
###############################################################################
print "Tuning finepitch using QBPM *Use with care*"
run("pitchup") # GLOBALS: qbpm6inserter, finepitch, ic1, atten, , vpos 
pitchup=pitchupClass()


###############################################################################
###                   HOMEBREW Hardware support                             ###
###############################################################################

### vortex
#print "Creating Vortex detector chain scannables"
#vortexName = "epicsMca01"
#print "creating Vortex objects for ", vortexName
#import mca_utils
#reload(mca_utils)
#vortexName = "epicsMca02"
#print "creating Vortex objects for ", vortexName
#import mca_utils
#reload(mca_utils)
#mca=finder.find(vortexName)
#if (mca != None):
#	ctmca=mca_utils.ctmcaClass('ctmca',mca)
#	rdmca=mca_utils.rdmcaClass('rdmca',mca)
#	mcaROI1=mca_utils.rdROIClass('rdROI1',mca,910,917)
#	mcaROI2=mca_utils.rdROIClass('rdROI2',mca,913,914)
#	mcaSca1 = mca_utils.rdScaClass('mcaSca1',mca,910,917)
#	mcaSca2 = mca_utils.rdScaClass('mcaSca2',mca,913,914)

if installation.isLive():

	### Various ###
	print "   running startup_epics_monitors.py"      # [TODO: Replace with imports]
	run("startup_epics_monitors")

	print "   running startup_epics_positioners.py"
	run("startup_epics_positioners")

	print "   running startup_cryocooler.py"          #[NOTE: Also creates commands]
	run("startup_cryocooler")

	print "   running pd_femto_adc_current2.py"
	try:
		run("pd_femto_adc_current2.py")
	except java.lang.IllegalStateException, e:
		print " Could not run pd_femto_adc_current2.py "
		print e
	
	print "   running pd_xyslit.py"
	run("pd_xyslit.py")

	
	print "   creating ion pump scannables"
	run("startup_ionpumps")
	
	print "   creating shutter scannable"
	shutter= Epics_Shutter('shutter','BL16I-PS-SHTR-01:CON')
	
	### Struck ###
	print "   Creating struck counter/timer scannables: ct1-ct11"
	ct1=Struck('ct1',"BL16I-EA-DET-01:SCALER",1,"%.0f")
	ct2=Struck('ct2',"BL16I-EA-DET-01:SCALER",2,"%.0f")		
	ct3=Struck('ct3',"BL16I-EA-DET-01:SCALER",3,"%.0f")
	ct4=Struck('ct4',"BL16I-EA-DET-01:SCALER",4,"%.0f")
	ct5=Struck('ct5',"BL16I-EA-DET-01:SCALER",5,"%.0f")
	ct6=Struck('ct6',"BL16I-EA-DET-01:SCALER",6,"%.0f")
	ct9=Struck('ct9',"BL16I-EA-DET-01:SCALER",9,"%.0f")		
	ct10=Struck('ct10',"BL16I-EA-DET-01:SCALER",10,"%.0f")
	ct3.setInputNames(['ct3'])
	ct9.setInputNames(['ct9'])
	
	### QBPM ###
	print "   creating QBPM scannables"
	qbpm1=EPICSODQBPMClass('QBPM1','BL16I-DI-IAMP-01',help='Current amp in optics hutch\nc1: White beam diode\nc2: broken\nc3: d3d diode\nc4: d4d diode')
	qbpm7=EPICSODQBPMClass('QBPM7','BL16I-DI-IAMP-07',help='Current amp1 in experimental hutch\nc1: S5 diagnostic diode\nc2-4: not used')
	qbpm6=EPICSODQBPMClass('QBPM6','BL16I-DI-IAMP-06',help='Current amp for QBPM in experimental hutch')
	#pmon=qbpm8=EPICSODQBPMClass2('QBPM8','BL16I-DI-IAMP-08',help='Current amp for polarimeter QBPM in experimental hutch')
	#vpos=ReadSingleValueFromVectorPDClass(qbpm6,6,'vpos','%.4f',help='qbpm vertical position (Y)')
	#hpos=ReadSingleValueFromVectorPDClass(qbpm6,5,'hpos','%.4f',help='qbpm horizontal position (X)')
	
	### Foil inserters ###
	print "   creating foil inserter scannables"
	Al10u=Foilinserter('Al10u',"BL16I-OP-ATTN-04:F1TRIGGER","BL16I-OP-ATTN-04:F1STATE",AlBulk,10)#,0.82674)
	Al20u=Foilinserter('Al20u',"BL16I-OP-ATTN-04:F2TRIGGER","BL16I-OP-ATTN-04:F2STATE",AlBulk,20)#,0.68349)
	Al40u=Foilinserter('Al40u',"BL16I-OP-ATTN-04:F3TRIGGER","BL16I-OP-ATTN-04:F3STATE",AlBulk,40)#,0.46716)
	Al75u=Foilinserter('Al75u',"BL16I-OP-ATTN-04:F4TRIGGER","BL16I-OP-ATTN-04:F4STATE",AlBulk,75)#,0.24002)
	Al150u=Foilinserter('Al150u',"BL16I-OP-ATTN-03:F1TRIGGER","BL16I-OP-ATTN-03:F1STATE",AlBulk,150)#5.76114e-2)
	Al300u=Foilinserter('Al300u' , "BL16I-OP-ATTN-03:F2TRIGGER","BL16I-OP-ATTN-03:F2STATE",AlBulk,300)#3.31907e-3)
	Al500u=Foilinserter('Al500u',"BL16I-OP-ATTN-03:F3TRIGGER","BL16I-OP-ATTN-03:F3STATE",AlBulk,500)#7.38516e-5)
	#Pb100u=Foilinserter('Pb100u',"BL16I-OP-ATTN-03:F4TRIGGER","BL16I-OP-ATTN-03:F4STATE",PbBulk,100)#1.41623e-16)
	Al880u=Foilinserter('Al880u',"BL16I-OP-ATTN-03:F4TRIGGER","BL16I-OP-ATTN-03:F4STATE",AlBulk,880)#1.41623e-16)
	Pb0=Foilinserter('Pb100u',"BL16I-OP-ATTN-03:F4TRIGGER","BL16I-OP-ATTN-03:F4STATE",PbBulk,0)
	Al75u0=Foilinserter('Al75u',"BL16I-OP-ATTN-04:F4TRIGGER","BL16I-OP-ATTN-04:F4STATE",AlBulk,0)
	atten = Atten('Attenuator',[Al10u,Al20u,Al40u,Al75u,Al150u,Al300u,Al500u,Al880u])
	atten.setOutputFormat(['%.0f', '%.4g'])
	
	### Polarization analyser ###
	print "   creating polarisation analyser scannable: pol"
#	pol=PolarizationAnalyser("Polarization Analyser",stoke,thp,tthp,zp,thp_offset,thp_offset_sigma,thp_offset_pi,tthp_offset,tthp_detoffset,cry_offset,ref_offset)
	pol=PolarizationAnalyser("Polarization Analyser",stoke,thp,tthp,zp,thp_offset,thp_offset_sigma,thp_offset_pi,tthp_offset_sigma,tthp_detoffset,cry_offset,ref_offset,dettrans,tthp_offset_pi,detector_lateral_offset_zero,detector_lateral_offset_ninety)

	
	### TCA  ###
	print "   creating TCA scanables"
	tca=TCA('BL16I-EA-DET-01:tca1')
	tcasca1=tcasca('TCAsca1',"%4.3f",tca,"%",'1')
	tcasca2=tcasca('TCAsca2',"%4.3f",tca,"%",'2')
	tcasca3=tcasca('TCAsca3',"%4.3f",tca,"%",'3')  

	### MCA ###
	print "Creating MCA scannables: mca1, mca"
	try:
		mca1=Mca('MCA1','BL16I-EA-DET-01:aim_adc1')
	except java.lang.IllegalStateException,e :
		print "Could not initiliase mca1 scannable"
		print e
	#mca2=Mca('MCA2','BL16I-EA-DET-02:aim_adc1') 
  	#(RobW) Removed March 21st 2011 to reflect this devices romoval from the Epics experimaental IOC
  	
  	### LS340 ###
	print "Creating LS340 scannables"
	try:
		Treg=DisplayEpicsPVClassLS('T1',"BL16I-EA-LS340-01:",'K','%7f','0',7)
		Tsam=DisplayEpicsPVClassLS('T1',"BL16I-EA-LS340-01:",'K','%7f','1',8)
		tset=EpicsLScontrol('tset','BL16I-EA-LS340-01:','K','%5.2f','0','1')
		T1=EpicsLSsetpoint('Tset1','SETP? 1','SETP 1','K','%5.2f')
		T2=EpicsLSsetpoint('Tset2','SETP? 2','SETP 2','K','%5.2f')

		Ta=DisplayEpicsPVClass('Ta','BL16I-EA-LS340-01:KRDG0','K','%6f')
		Tb=DisplayEpicsPVClass('Tb','BL16I-EA-LS340-01:KRDG1','K','%6f')
		Tc=DisplayEpicsPVClass('Tc','BL16I-EA-LS340-01:KRDG2','K','%6f')
		Td=DisplayEpicsPVClass('Td','BL16I-EA-LS340-01:KRDG3','K','%6f')

		Tas=DisplayEpicsPVClass('Tas','BL16I-EA-LS340-01:SRDG0','K','%6f')
		Tbs=DisplayEpicsPVClass('Tbs','BL16I-EA-LS340-01:SRDG1','K','%6f')
		Tcs=DisplayEpicsPVClass('Tcs','BL16I-EA-LS340-01:SRDG2','K','%6f')
		Tds=DisplayEpicsPVClass('Tds','BL16I-EA-LS340-01:SRDG3','K','%6f')

#		Ta=DisplayEpicsPVClassLS('Ta_diode',"BL16I-EA-LS340-01:",'K','%4f','0',8); Ta.setInputNames(['Ta'])
#		Tb=DisplayEpicsPVClassLS('Tb_Pt',"BL16I-EA-LS340-01:",'K','%4f','1',8); Tb.setInputNames(['Tb'])
#		Tc=DisplayEpicsPVClassLS('Tc_TCtypeE',"BL16I-EA-LS340-01:",'K','%4f','2',8); Tc.setInputNames(['Tc'])
#		Td=DisplayEpicsPVClassLS('Td_TCAuFe',"BL16I-EA-LS340-01:",'K','%4f','3',8); Td.setInputNames(['Td'])
		
#		Ta2=DisplayEpicsPVClassLS2('Ta2',"BL16I-EA-LS340-01:",'K','%4f','0',8); Ta2.setInputNames(['Tas']);
#		Tb2=DisplayEpicsPVClassLS2('Tb2',"BL16I-EA-LS340-01:",'K','%4f','1',8); Tb2.setInputNames(['Tbs']);
#		Tc2=DisplayEpicsPVClassLS2('Tc2',"BL16I-EA-LS340-01:",'K','%4f','2',8); Tc2.setInputNames(['Tcs']);
#		Td2=DisplayEpicsPVClassLS2('Td2',"BL16I-EA-LS340-01:",'K','%4f','3',8); Td2.setInputNames(['Tds']);
	except java.lang.IllegalStateException:
		print "*** Could not connect to epics PVs for BL16I-EA-LS340-01 ***"
		print "*** failed to create Scannables: Treg, Tsam, tset, T1, T1, Ta, Tb, Tc, Td, Ta2, Tb2, Tc2 & Td2 ***"
	LSP=SingleEpicsPositionerSetAndGetOnlyClass('LS_P','BL16I-EA-LS340-01:P_S','BL16I-EA-LS340-01:P','P','%4f')
	LSI=SingleEpicsPositionerSetAndGetOnlyClass('LS_I','BL16I-EA-LS340-01:I_S','BL16I-EA-LS340-01:I','I','%4f')
	LSD=SingleEpicsPositionerSetAndGetOnlyClass('LS_D','BL16I-EA-LS340-01:D_S','BL16I-EA-LS340-01:D','D','%4f')
	#LSPID=ReadPDGroupClass('LS_PID',[LSP,LSI,LSD])
	pid1=EpicsLakeshorePID('PID_1','PID? 1','PID 1','','%4f')
	pid2=EpicsLakeshorePID('PID_2','PID? 2','PID 2','','%4f')
	
	
	### Struck ###
	print "   creating new Stuck counter-timet object, t    Type help t"
	t=Struck2('t',"BL16I-EA-DET-01:SCALER",[3])
	t.setname(3,'APD'); t.setname(4,'Scintillator1'); t.setname(5,'APD2'); t.setname(9,'SCA1'); t.setname(10,'SCA2'); t.setname(11,'SCA3'); t.setname(15,'IC2');

	### Wait for beam ###
	print "   creating checkbeam scannables"
	checkbeamcurrent=WaitForBeamPDClass('BeamOK',rc,10)
#	checkbeam=WaitForBeamPDClass('BeamOK',ic1monitor,1); checkbeam.command_string='fill_if_needed()'	#fill cryocooler vessel while waiting for beam
	checkbeam=WaitForBeamPDClass('BeamOK',ic1monitor,1); checkbeam.command_string='None'
	timetoinjection=TimeToMachineInjectionClass('TimeToInjection','SR-CS-FILL-01:COUNTDOWN', 'sec', '%.1f')
	waitforinjection=WaitForInjectionPDClass('WaitForInjection',timetoinjection, 5, 5)

	### x1trig and x2trig ###
	print "Creating x1trig and x2trig"
	x1trig = ToggleBinaryPvAndWait('x1trig', 'BL16I-EA-USER-01:BO1')
	x1trig.triggerLength=0.1
	x2trig = ToggleBinaryPvAndWait('x2trig', 'BL16I-EA-USER-01:BO2') 
	x2trig.triggerLength=0.2
	
	### Phase Plates ###
	ppa111=PPPClass('ppa111',3.559/sqrt(3),ppth, ppp_xtal1_111_offset,help='Phase plate device for 111 reflection from crystal A (0.4 mm diamond)')
	ppa220=PPPClass('ppa220',3.559/sqrt(8),ppth, ppp_xtal1_220_offset,help='Phase plate device for 220 reflection from crystal A (0.4 mm diamond)')
	ppam220=PPPClass('ppam220',-3.559/sqrt(8),ppth, ppp_xtal1_m220_offset,help='Phase plate device for -2-20 reflection from crystal A (0.4 mm diamond)') #experimental
	ppa440=PPPClass('ppa440',3.559/sqrt(8)/2,ppth, ppp_xtal1_440_offset,help='Phase plate device for 440 reflection from crystal A (0.4 mm diamond)')
	ppb111=PPPClass('ppb111',3.559/sqrt(3),ppth, ppp_xtal2_111_offset,help='Phase plate device for 111 reflection from crystal B (0.1 mm diamond)')
	#ppb220=PPPClass('ppb220',3.559/sqrt(8),ppth, ppp_xtal2_220_offset,help='Phase plate device for 220 reflection from crystal B (0.1 mm diamond)')


	
else:
	print "NOT LIVE :SKIPPED EPICS DEVICES/MONITORS"
	print "      Creating dummy bragg motor should be on PV:BL16I-MO-DCM-01:BRMTR:MOT.RBV"
	bragg = dummyClass('bragg')
	bragg.asynchronousMoveTo(-23.2997)
	print "      Creating dummy perp motor should be on PV:BL16I-MO-DCM-01:FPMTR:PREAD"
	perp = dummyClass('perp')
	bragg.asynchronousMoveTo(0.033523)


### Homebrew positioners
print 'Creating positioners with preset values: mono_screens, mono_diode'
mono_screens=MoveScalarPDsToPresetValuesClass('mono_screens',[d3a,d3d,d4a,d4d,d5a,d5d],[[90,33,20,33,20,35],[60,0,20,0,20,0]],help='0=all out; 1=fluo foils and d3a Al in, rest out')
mono_diode=MoveScalarPDsToPresetValuesClass('mono_diodes',[d3a,d3d,d4a,d4d,d5a,d5d],[[90,33,20,33,20,35],[90,76.3,20,33,20,35],[90,33,20,75.5,20,35],[90,33,20,33,20,76.5]],help='0=all out; 1=d3d diode in, 2=d4d diode in; 3=d5diode in')

### Homebrew groups
print "Creating OD current amplifier monitors"
run("startup_currents")
run("startup_currents2")
sleep(1)


###  Serial devices: Ace, X2000
if installation.isLive():	
	print "   Creating raw serial devices for x2000 and Ace cards"
	try:
		acedict = {'reset':"RESET",'ver':"VER",'help':"HELP",'tlvl':"TLVL",'sout':"SOUT",'sca':"SCA",'alcur':"ALCURR",'alarm':"ALARM",'hcurr':"HCURR",'scaps':"OUT",'hvolt':"HVOLT",'hvmon':"HVMON",'info':"INFO",'ht':"HTEMP"}
		ace1=ace("BL16I-EA-DET-04:asyn",acedict)		
		ace2=ace("BL16I-EA-SPARE-05:asyn",acedict)		

		if False: # Has not been used for years
			print "Creating x2000sca & x2003 scannables"
			x2000dict={'gain' : ":INP0:GAIN",'reset':"*RST0",'scaupp' : ":SENS0:SCA:UPP", 'scalow' : ":SENS0:SCA:LOW",'pkt' : ":SENS0:PKT",'volt' : ":SOUR0:VOLT",'sat' : ":SENS0:SAT",'fail' : ":SENS0:HVFAIL"}
			x2000sca=x2000scaClass('X2000 sca1',"%4.3f",x2000,"cts")
			x2003sca=x2000scaClass('X2003 sca1',"%4.3f",x2003,"cts")
			x2003=x2000class("BL16I-EA-DET-03:asyn","\\006",x2000dict)
			x2000=x2000class("BL16I-EA-DET-05:asyn","\\006",x2000dict)
	
		print "Creating Ace scannable: acesca"
		acesca=acesca1('APDsca',"%4.3f",ace1,"V")		
		acesca2=acesca1('APDsca2',"%4.3f",ace2,"V")		

	except java.lang.IllegalStateException, e:
		print "*** WARNING: could not connect to Epics for x2000 and Ace cards"
	
	
###############################################################################
###                      Monitor kth, delta, kappa                          ###
###############################################################################
print "Creating more scannables to monitor kth, delta and kap."
kthshow=ReadPDGroupClass('kthshow',[kth]); kthshow.setLevel(8); #kthshow.setExtraNames(['kthshow']);kthshow.setOutputFormat(['%.6f'])
delshow=ReadPDGroupClass('delshow',[delta]); delshow.setLevel(8); #delshow.setExtraNames(['delshow']);delshow.setOutputFormat(['%.6f'])
kapshow=ReadPDGroupClass('kapshow',[kap]); kapshow.setLevel(8); #kapshow.setExtraNames(['kapshow']);kapshow.setOutputFormat(['%.6f'])

if installation.isLive():
	print "Creating kth_read and delta_read"
	kth_read=EpicsMonitor()
	kth_read.setPvName('BL16I-MO-DIFF-01:SAMPLE:KTHETA.RBV')
	kth_read.name='kth_read'
	kth_read.outputFormat=['%.6f']
	kth_read.configure()
	
	delta_read=EpicsMonitor()
	delta_read.setPvName('BL16I-MO-DIFF-01:DELTA:RBV')
	delta_read.name='delta_read'
	delta_read.outputFormat=['%.6f']
	delta_read.configure()


###############################################################################
###                                 Energy                                  ###
###############################################################################
import beamline_info as BLi #contains energy and wavelength
run("startup_energy_related")
#defaults changed by SPC on 29/6/11 comment out next two lines to go back to previous settings
energy.maxEnergyChangeBeforeMovingMirrors=0.01	#energy value to prevent mirrors or diffractomter moving for small energy step
energy.moveDiffWhenNotMovingMirrors=True	#set this to True to move diffractometer to compensate for inverted beam movement

if USE_DIFFCALC:
	# This could not be done earlier because energy was not available when diffcalc was started
	simple_energy.delegate = energy


###############################################################################
###                             Tweak scannables                            ###
###############################################################################
eta.setOutputFormat(['%.4f'])
delta.setOutputFormat(['%.4f'])
delta.setOutputFormat(['%.5f'])
gam.setOutputFormat(['%.5f'])


###############################################################################
###                               Peak Optimiser                            ###
###############################################################################
if installation.isLive():
	run("OptimizePeak") #--> ptimizePeak, OP2, OP3 commands



###############################################################################
###                              Set user limits                            ###
###############################################################################
import limits
reload(limits)
from limits import * #@UnusedWildImport
limits.ROOT_NAMESPACE = globals()
print "Setting user limits (running ConfigureLimits.py)"
run("ConfigureLimits")


###############################################################################
###                             Configure Pilatus                           ###
###############################################################################
from scannable.detector.DetectorWithShutter import DetectorWithShutter
### 2m ###
#pil2mdet = EpicsPilatus('pil2mdet', 'BL16I-EA-PILAT-02:','/dls/i16/detectors/im/','test','%s%s%d.tif')
pil2mdet = pilatus2
_pilatus2_counter_monitor = Finder.getInstance().find("pilatus2_plugins").get('pilatus2_counter_monitor')

#pil2m = SwitchableHardwareTriggerableProcessingDetectorWrapper('pil2m',
pil2m = NxProcessingDetectorWrapper('pil2m',
		pilatus2,
		pilatus2_hardware_triggered,
		pilatus2_for_snaps,
		[],
		panel_name='Pilatus2M',
		panel_name_rcp='Plot 1',
		toreplace=None,
		replacement=None,
		iFileLoader=PilatusTiffLoader,
		fileLoadTimout=60,
		returnPathAsImageNumberOnly=True,
		array_monitor_for_hardware_triggering = _pilatus2_counter_monitor
		)
pil2m.processors=[DetectorDataProcessorWithRoi('max', pil2m, [SumMaxPositionAndValue()], False)]
pil2m.printNfsTimes = True
pil2m.display_image = True
pil2ms = DetectorWithShutter(pil2m, x1)

### 100k ###
pil100kdet = pilatus1
_pilatus1_counter_monitor = Finder.getInstance().find("pilatus1_plugins").get('pilatus1_counter_monitor')

#pil100k = SwitchableHardwareTriggerableProcessingDetectorWrapper('pil100k',
pil100k = NxProcessingDetectorWrapper('pil100k',
		pilatus1,
		zebrapil1,
		pilatus1_for_snaps,
		[],
		panel_name='Pilatus100k',
		panel_name_rcp='Plot 1',
		toreplace=None,
		replacement=None,
		iFileLoader=PilatusTiffLoader,
		fileLoadTimout=60,
		returnPathAsImageNumberOnly=True,
		array_monitor_for_hardware_triggering = _pilatus1_counter_monitor)
pil100k.processors=[DetectorDataProcessorWithRoi('max', pil100k, [SumMaxPositionAndValue()], False)]
pil100k.printNfsTimes = False
pil100ks = DetectorWithShutter(pil100k, x1)
pil = pil100k
pils = pil100ks
#pil100kvrf=SingleEpicsPositionerSetAndGetOnlyClass('P100k_VRF','BL16I-EA-PILAT-01:VRF','BL16I-EA-PILAT-01:VRF','V','%.3f',help='set VRF (gain) for pilatus\nReturns set value rather than true readback\n-0.05=very high\n-0.15=high\n-0.2=med\n-0.3=low')
#pil100kvcmp=SingleEpicsPositionerSetAndGetOnlyClass('P100k_VCMP','BL16I-EA-PILAT-01:VCMP','BL16I-EA-PILAT-01:VCMP','V','%.3f',help='set VCMP (threshold) for pilatus\nReturns set value rather than true readback\n0-1 V')
#pil100kgain=SingleEpicsPositionerSetAndGetOnlyClass('P100k_gain','BL16I-EA-PILAT-01:Gain','BL16I-EA-PILAT-01:Gain','','%.3f',help='set gain for pilatus\nReturns set value rather than true readback\n3=very high\n2=high\n1=med\n0=low')
#pil100kthresh=SingleEpicsPositionerSetAndGetOnlyClass('P100k_threshold','BL16I-EA-PILAT-01:ThresholdEnergy','BL16I-EA-PILAT-01:ThresholdEnergy','','%.0f',help='set energy threshold for pilatus (eV)\nReturns set value rather than true readback')

from scannable.pilatus import PilatusThreshold, PilatusGain
pil100kthresh = PilatusThreshold('pil100kthresh', pilatus1_hardware_triggered.getCollectionStrategy().getAdDriverPilatus())
pil100kgain = PilatusGain('pil100kgain', pilatus1_hardware_triggered.getCollectionStrategy().getAdDriverPilatus())

_pilatus3_counter_monitor = Finder.getInstance().find("pilatus3_plugins").get('pilatus3_counter_monitor')
#pil3_100k = SwitchableHardwareTriggerableProcessingDetectorWrapper('pil3_100k',
pil3_100k = NxProcessingDetectorWrapper('pil3_100k',
		pilatus3,
		pilatus3_hardware_triggered,
		pilatus3_for_snaps,
		[],
		panel_name='Pilatus3_100k',
		panel_name_rcp='Plot 1',
		toreplace=None,
		replacement=None,
		iFileLoader=PilatusTiffLoader,
		fileLoadTimout=60,
		returnPathAsImageNumberOnly=True,
		array_monitor_for_hardware_triggering = _pilatus3_counter_monitor)
pil3_100k.processors=[DetectorDataProcessorWithRoi('max', pil3_100k, [SumMaxPositionAndValue()], False)]
pil3_100k.printNfsTimes = False
pil3_100ks = DetectorWithShutter(pil3_100k, x1)
pil3 = pil3_100k
pil3s = pil3_100ks

pil3_100kthresh = PilatusThreshold('pil3_100kthresh', pilatus3_hardware_triggered.getCollectionStrategy().getAdDriverPilatus())


### cam2 ###
cor = SwitchableHardwareTriggerableProcessingDetectorWrapper('cor',
							cam2,
							None,
							cam2_for_snaps,
							[],
							panel_name='Firecam',
							panel_name_rcp='Plot 1', 
							fileLoadTimout=60,
							printNfsTimes=False,
							returnPathAsImageNumberOnly=True)

cor.display_image = True
corpeak2d = DetectorDataProcessorWithRoi('corpeak2d', cor, [TwodGaussianPeak()])
cormax2d = DetectorDataProcessorWithRoi('cormax2d', cor, [SumMaxPositionAndValue()])

#create a version of cor, corpeak2d, cormax2d that performs auto exposure
#To record actual exposure time also add corExpTime
from autoRangeDetector import AutoRangeDetector
corAuto = AutoRangeDetector('corAuto',
							cam2,
							None,
							cam2_for_snaps,
							"BL16I-DI-COR-01:",
							[],
							panel_name='Firecam',
							panel_name_rcp='Plot 1', 
							fileLoadTimout=60,
							printNfsTimes=False,
							returnPathAsImageNumberOnly=True)

corAuto.display_image = True
corAutopeak2d = DetectorDataProcessorWithRoi('corAutopeak2d', corAuto, [TwodGaussianPeak()])
corAutomax2d = DetectorDataProcessorWithRoi('corAutomax2d', corAuto, [SumMaxPositionAndValue()])

#create pseudo-device 
#there is a copy of this in epics git epics_script folder.
from pv_scannable_utils import createPVScannable
createPVScannable( "corExpTime", "BL16I-DI-COR-01:CAM:AcquireTime_RBV", hasUnits=False)
corExpTime.level=10

cor2 = SwitchableHardwareTriggerableProcessingDetectorWrapper('cor2',
							c10,
							None,
							c10_for_snaps,
							[],
							panel_name='Firecam',
							panel_name_rcp='Plot 2', 
							fileLoadTimout=60,
							printNfsTimes=False,
							returnPathAsImageNumberOnly=True)

cor2peak2d = DetectorDataProcessorWithRoi('cor2peak2d', cor, [TwodGaussianPeak()])
cor2max2d = DetectorDataProcessorWithRoi('cor2max2d', cor, [SumMaxPositionAndValue()])

cor2Auto = AutoRangeDetector('cor2Auto',
							c10,
							None,
							c10_for_snaps,
							"BL16I-DI-DCAM-10:",
							[],
							panel_name='Firecam',
							panel_name_rcp='Plot 2', 
							fileLoadTimout=60,
							printNfsTimes=False,
							returnPathAsImageNumberOnly=True)
cor2Auto.display_image = True
cor2Autopeak2d = DetectorDataProcessorWithRoi('cor2Autopeak2d', corAuto, [TwodGaussianPeak()])
cor2Automax2d = DetectorDataProcessorWithRoi('cor2Automax2d', corAuto, [SumMaxPositionAndValue()])

createPVScannable( "cor2ExpTime", "BL16I-DI-DCAM-10:CAM:AcquireTime_RBV", hasUnits=False)
cor2ExpTime.level=10

xeye = SwitchableHardwareTriggerableProcessingDetectorWrapper('xeye',
                                                              _xeye,
                                                              None,
                                                              _xeye_for_snaps,
                                                              [],
                                                              panel_name='Firecam',
                                                              panel_name_rcp='Plot 2',
                                                              fileLoadTimout=60,
                                                              printNfsTimes=False,
                                                              returnPathAsImageNumberOnly=True)

xeye.display_image = True
xeyemax2d = DetectorDataProcessorWithRoi('xeyemax2d', xeye, [SumMaxPositionAndValue()])
xeyepeak2d = DetectorDataProcessorWithRoi('xeyepeak2d', xeye, [TwodGaussianPeak()])

xeye.processors=[DetectorDataProcessorWithRoi('peak', xeye, [SumMaxPositionAndValue(), TwodGaussianPeakWithCalibration()], False)]
xeye.processors[0].processors[1].setScalingFactors(0.0014, 0.0014)


#scan kphi -90 270 1. corAuto corAutopeak2d corExpTime

zylar = SwitchableHardwareTriggerableProcessingDetectorWrapper('zylar',
                                                               _zylar,
                                                               None,
                                                               _zylar_for_snaps,
                                                               [],
                                                               panel_name='Firecam', #no idea?
                                                               panel_name_rcp='Plot 2',
                                                               fileLoadTimout=60,
                                                               printNfsTimes=False,
                                                               returnPathAsImageNumberOnly=True)

zylar.display_image = True
zylarmax2d = DetectorDataProcessorWithRoi('zylarmax2d', zylar, [SumMaxPositionAndValue()])
zylarpeak2d = DetectorDataProcessorWithRoi('zylarpeak2d', zylar, [TwodGaussianPeak()])

zylar.processors=[DetectorDataProcessorWithRoi('peak', zylar, [SumMaxPositionAndValue(), TwodGaussianPeakWithCalibration()], False)]
#zylar needs scaling factors?
zylar.processors[0].processors[1].setScalingFactors(1, 1)

### cam1 ###
bpm = SwitchableHardwareTriggerableProcessingDetectorWrapper('bpm',
							_cam1,
							None,
							_cam1_for_snaps,
							[],
							panel_name='Firecam',
							panel_name_rcp='Plot 1', 
							fileLoadTimout=60,
							printNfsTimes=False,
							returnPathAsImageNumberOnly=True)

bpm.display_image = True
bpm.processors=[DetectorDataProcessorWithRoi('peak', bpm, [SumMaxPositionAndValue(), TwodGaussianPeakWithCalibration()], False)]
bpm.processors[0].processors[1].setScalingFactors(0.0027, 0.00375)
bpmpeak2d = DetectorDataProcessorWithRoi('bpmpeak2d', bpm, [TwodGaussianPeak()])
bpmmax2d = DetectorDataProcessorWithRoi('bpmmax2d', bpm, [SumMaxPositionAndValue()])
#bpm.processors[0].processors[1].calibrate()

###############################################################################
###                              Configure andor                            ###
###############################################################################
from uk.ac.diamond.scisoft.analysis.io import TIFFImageLoader
# the andor has no hardware triggered mode configured. This class is used to hijak its DetectorSnapper implementation.
andor = SwitchableHardwareTriggerableProcessingDetectorWrapper('andor',
								andor1,
								None,
								andor1_for_snaps,
								[],
								panel_name='Andor CCD',
								panel_name_rcp='Plot 1', 
								toreplace=None,
								replacement=None,
								iFileLoader=TIFFImageLoader,
								fileLoadTimout=15,
								returnPathAsImageNumberOnly=True)

from scannable.adbase import ADTemperature
andortemp = ADTemperature('andortemp', andor1.getCollectionStrategy().getAdBase())
from scannable.andor import andor_trigger_output_enable, andor_trigger_output_disable
alias('andor_trigger_output_disable')
alias('andor_trigger_output_enable')
try:
	andor_trigger_output_enable()
except:
	print "Error configuring andor"
	print "Is IOC running?"


print "-------------------------------MEDIPIX INIT---------------------------------------"
try:
	
	#visit_setter.addDetectorAdapter(FileWritingDetectorAdapter(_medipix_det, create_folder=True, subfolder='medipix'))
	'''
	medipix = SwitchableHardwareTriggerableProcessingDetectorWrapper('medipix',
																	_medipix,
																	None,
																	_medipix_for_snaps,
																	[],
																	panel_name='Medipix',
																	panel_name_rcp='Plot 1',
																	iFileLoader=PilatusTiffLoader,
																	fileLoadTimout=60,
																	printNfsTimes=False,
																	returnPathAsImageNumberOnly=True)
	medipix.disable_operation_outside_scans = False # True
	# medipix_threshold0_kev = SetPvAndWaitForCallbackWithSeparateReadback('medipix_threshold_kev', 'BL16I-EA-DET-02:Merlin:ThresholdEnergy0', 'BL16B-EA-DET-02:Merlin:ThresholdEnergy0_RBV', 10)
	#pil100kdet = EpicsPilatus('pil100kdet', 'BL16I-EA-PILAT-01:','/dls/b16/detectors/im/','test','%s%s%d.tif')
	#pil100k = ProcessingDetectorWrapper('pil100k', pil100kdet, [], panel_name='Pilatus100k', toreplace=None, replacement=None, iFileLoader=PilatusTiffLoader, fileLoadTimout=15, returnPathAsImageNumberOnly=True)
	#pil100k.processors=[DetectorDataProcessorWithRoi('max', pil100k, [SumMaxPositionAndValue()], False)]
	#pil100k.printNfsTimes = True
	
	
	medipix.processors=[DetectorDataProcessorWithRoi('max', medipix, [SumMaxPositionAndValue()], False)]
	'''
	pass
except gda.factory.FactoryException:
	print " *** Could not connect to pilatus (FactoryException)"
except 	java.lang.IllegalStateException:
	print " *** Could not connect to pilatus (IllegalStateException)"
print "-------------------------------MEDIPIX INIT COMPLETE---------------------------------------"


print "-------------------------------MERLIN INIT---------------------------------------"
try:
	
	merlin = SwitchableHardwareTriggerableProcessingDetectorWrapper('merlin',
																	_merlin,
																	None,
																	_merlin_for_snaps,
																	[],
																	panel_name='Merlin',
																	panel_name_rcp='Plot 1',
																	iFileLoader=PilatusTiffLoader,
																	fileLoadTimout=60,
																	printNfsTimes=False,
																	returnPathAsImageNumberOnly=True)
	merlin.disable_operation_outside_scans = False
	merlin.processors=[DetectorDataProcessorWithRoi('max', merlin, [SumMaxPositionAndValue()], False)]

except gda.factory.FactoryException:
	print " *** Could not connect to merlin (FactoryException)"
except 	java.lang.IllegalStateException:
	print " *** Could not connect to merlin (IllegalStateException)"
print "-------------------------------MERLIN INIT COMPLETE---------------------------------------"
###############################################################################
###                              Configure Xmap                            ###
###############################################################################
from scannable.detector.dxp import DxpSingleChannelRoiOnly
if USE_XMAP:
	pass#Sxmap = DxpSingleChannelRoiOnly('xmap', 'BL16I-EA-XMAP-01:')
###############################################################################
###                             Configure firecam                           ###
###############################################################################

###############################################################################
###                           Theta with offset eta                         ###
###############################################################################

print "Creating scannarcbles with offsets(th is eta with offset eta_offset"
run("pd_offsetAxis") #--> OffsetAxisClass
# e.g. th is eta with eta_off as offset
th=OffsetAxisClass('th',eta,eta_offset,help='eta device with offset given by eta_offset. Use pos eta_offset to change offset')
thv=OffsetAxisClass('thv',mu,mu_offset,help='mu device with offset given by mu_offset. Use pos mu_offset to change offset')


#############################################################################
###                           P/A detector angles                           ###
###############################################################################
if installation.isLive():
	#tthp.apd = 1.75 #16/1/15 - changed from 1.75
	#tthp.apd = 3.25 #30/9/15
	#tthp.apd = 0.5 #17/5/16
	#tthp.apd = 0.9 #13/2/17
	tthp.apd = -0.35 #24/04/18
	#tthp.diode=56.4#2/10/11 - changed from 55.6
	#tthp.diode=55#01/07/16 - changed from 56.4
	#tthp.diode=53.713#01/07/16 - changed from 56.4
	#tthp.diode=53.65#01/07/16 - changed from 53.713
	#tthp.diode=54.3	#13/02/17
	tthp.diode=0	#24/04/18
	tthp.camera=34.4 #14/10/12 -changed from 33.4
	tthp.vortex=-14.75 #31/1/10
	#tthp.ccd=70
	tthp.ccd=40 #24/04/18


###############################################################################
###                                Metadata                                 ###
###############################################################################
print "Configuring metadata capture"

run('Sample_perpMotion')

if installation.isLive():
	if not USE_DIFFCALC:
		d=diffractometer_sample=ReadPDGroupClass('diffractometer_sample',[delta, eta, chi, phi, gam, mu, hkl, psi, en, kphi, azihkl, beta, delta_axis_offset])
		xtal_info=ReadPDGroupClass('xtal_info',[xtalinfo])
	else:
		d=diffractometer_sample=ReadPDGroupClass('diffractometer_sample',[delta, eta, chi, phi, gam, mu, hkl, en, kphi, delta_axis_offset])
	source=ReadPDGroupClass('source',[rc, idgap, uharmonic])
	beamline_slits=ReadPDGroupClass('beamline_slits',[s1xcentre,s1xgap,s1ycentre, s1ygap,s2xcentre,s2xgap,s2ycentre, s2ygap,s3xcentre,s3xgap,s3ycentre, s3ygap,s4xcentre,s4xgap,s4ycentre, s4ygap, shtr3x,shtr3y])
	jjslits=ReadPDGroupClass('jjslits',[s5xgap, s5xtrans, s5ygap, s5ytrans, s6xgap, s6xtrans, s6ygap, s6ytrans])
	mirror1=ReadPDGroupClass('mirror1',[m1pitch, m1x, m1y, m1roll, m1yaw, m1piezo])
	mirror2=ReadPDGroupClass('mirror2',[m2pitch, m2x, m2y, m2roll, m2yaw,m2bender])
	mirror3=ReadPDGroupClass('minimirrors',[m3x, m4x, m3pitch, m4pitch])
	mirrors=ReadPDGroupClass('mirrors',[mirror1, mirror2,mirror3])
	###temporarilily remove cryolevel due to controls problem - go back to original when working
	#mono=ReadPDGroupClass('Mono',[en,bragg,dcmpitch, dcmfinepitch, perp, dcmlat,dcmroll1, dcmroll2,T1dcm, T2dcm,cryolevel])
	mono=ReadPDGroupClass('mono',[en,bragg,dcmpitch, dcmfinepitch, perp, dcmlat,dcmroll1, dcmroll2,T1dcm, T2dcm])
	###
	pa=ReadPDGroupClass('pa',[stoke, tthp, thp, zp])
	pp=ReadPDGroupClass('pp',[ppth, ppx, ppy, ppchi])
	#positions=ReadPDGroupClass('positions',[sx,sy,sz,base_y,base_z,ytable, ztable])
	positions=ReadPDGroupClass('positions',[sx,sy,sz,sperp, spara, base_y,base_z,ytable, ztable])# sperp spara added SPC 3/2/12
	xps2=ReadPDGroupClass('xps2',[gam,delta,mu,kth,kap,kphi])
	dummypd=ReadPDGroupClass('dummypd',[x,y,z])
	kbm_offsets=ReadPDGroupClass('kbm_offsets',[vmtrans_offset, hmtrans_offset, vmpitch_offset, hmpitch_offset, kbmx_offset, kbmroll_offset])
	try:
		xps3=ReadPDGroupClass('xps3',[xps3m1, xps3m2, xps3m3, xps3m4, xps3m5, xps3m6])
	except NameError, e:
		pass # XPS3 is often not present
	frontend=ReadPDGroupClass('frontend',[frontendx, frontendy])
	gains_atten=ReadPDGroupClass('gains_atten',[atten, diode.gain, ic1monitor.gain, ic2.gain])
	try:
		lakeshore=ReadPDGroupClass('lakeshore',[tset,Ta,Tb,Tc,Td])
	except NameError:
		lakeshore=ReadPDGroupClass('lakeshore',[]) # LS340 is often not present
	#minimirrors=ReadPDGroupClass('minimirrors',[m3x, m4x, m3pitch, m4pitch]) #added to metadata as mirror3
	"""
	offsets=ReadPDGroupClass('offsets',[m1y_offset, m2y_offset, base_z_offset, ztable_offset, m2_coating_offset, idgap_offset, kbm_offsets])
	"""
	offsets=ReadPDGroupClass('offsets',[m1y_offset, m2y_offset, base_z_offset, ztable_offset, m2_coating_offset, idgap_offset])
	#mt6138=ReadPDGroupClass('6138', [xps3m1, xps3m2])
	#adctab=ReadPDGroupClass('adctab',[adch,adcv])
	#add_default(adctab)
	#fzp=ReadPDGroupClass('FZP_motors',[zp1x, zp1y, zp1z, zp2x, zp2y, zp2z, xps3m1, xps3m2, micosx, micosy])
try:
	if not USE_DIFFCALC:
		toadd = [dummypd, mrwolf, diffractometer_sample, sixckappa, xtalinfo,source, jjslits, pa, pp, positions, gains_atten, mirrors, beamline_slits, mono, frontend, lakeshore,offsets,p2]
	else:
		toadd = [dummypd, mrwolf, diffractometer_sample, sixckappa, source, jjslits, pa, pp, positions, gains_atten, mirrors, beamline_slits, mono, frontend, lakeshore,offsets,p2]

	addedInSpring = [sixckappa] + [delta_axis_offset]
	toadd = [ _x for _x in toadd if _x != None and not _x in addedInSpring ]

	from gdascripts.scannable.metadata import _is_scannable

	if USE_NEXUS_METADATA_COMMANDS:
		try:
			meta_clear_alldynamical()
		except:
			pass
		for item in toadd:
			print "Adding metadata:", item.name
			print item
			if _is_scannable(item):
				meta_add(item)
			else:
				print "%s was not scannable and could not be entered as metadata" % item.name
	else:
		meta.add(*toadd)
	
	meta.prepend_keys_with_scannable_names = False
	mds=meta
	print "Removing frontend from metadata collection"
	if USE_NEXUS_METADATA_COMMANDS:
		meta_rm(frontend)
	else:
		meta.rm(frontend)
	try:
		if USE_NEXUS_METADATA_COMMANDS:
			meta_add(kbm1)
			meta_add(kbmbase)
		else:
			addmeta(kbm1)
			addmeta(kbmbase)
	except NameError:
		print "Not adding kbm1 or kbm1base metadata as these are unavailable"

	
except NameError, e:
	# diffractometer_sample,xtalinfo are not yet available with diffcalc
	print "!*"*40
	print "!*"*40
	print "Error trying to setup the metadata, metadata will not be properly written to files. Namespace error was: ",str(e)
	print "!*"*40
	print "!*"*40

###Default Scannables###
default_scannable_list = [kphi, kap, kth, kmu, kdelta, kgam, delta_axis_offset]
if USE_CRYO_GEOMETRY:
	default_scannable_list.append(cryophi)
for _x in default_scannable_list:
	add_default(_x)


###############################################################################
###                          Recent developments                            ###
###############################################################################
beamline = finder.find("Beamline")

#run('Sample_perpMotion') #move to before metadata

run('Struck_with_fastshutter')

#ADC optics table XMAP
run('pd_adc_table')

run('enable_xps_gda.py')

from edgeDetectRobust import edgeDetectRobust as edge
from edgeDetectEnergy import eEdge as eedge
#run('edgeDetectRobust')

run('rePlot')

run('whynobeam')

print "New minimirrors function - type help minimirrors"
run('minimirrors')

run("startup_trajscan")

if USE_DIFFCALC == False:
	print "run possiblehkl_new"
	run('possiblehkl_new')
	print "run Space Group Interpreter"
	run('SGinterpreter')




#### temp fix for valves closing due to img03#######################
gv1= Epics_Shutter('gv1','BL16I-VA-VALVE-01:CON')
gv2= Epics_Shutter('gv2','BL16I-VA-VALVE-02:CON')
d2open=Epics_Shutter('d2_actuator','BL16I-DI-PHDGN-02:CON')
def open_valves():
	print "Sending commands to open valves in case they have closed..."
	#don't try to read state of valves as they are not reliable
	print gv1(1); sleep(2)
	print gv2(1); sleep(2)
	print d2open(1); sleep(2)
#checkbeam.command_string='open_valves()'	#uncomment to attempt to open valves if closed
#### end of temp fix for valves closing due to img03###################


###############################################################################
###                          Detector Region-Of-Interest                    ###
###############################################################################

	
#(top right, bottom left)
#pixel values for centred spot and max/min pixel indices for detector (min is zero)
#(imin, jmin, imax, jmax)
#rois are at least two pixels wide;centre is half-integar value of pixels adjacent to peak
#ci=257.5; cj=99.5
#ci=256.5; cj=100.5	#27/1/11
#ci=250.5; cj=104.5	#23/4/11
#ci=246.5; cj=106.5	#02/10/11
#ci=256.0; cj=105.0	#29/11/11
#ci=226.0; cj=104.0	#31/01/12
#ci=226.0; cj=104.0	#17/04/12
#ci=228.0; cj=101.0	#31/10/12
#ci=234.0; cj=107.0	#/01/13
#ci=242.0; cj=104.0	#/03/13
#ci=237.0; cj=121.0	#17/03/13
#ci=236.0; cj=106.0	#16/04/13
#ci=240.0; cj=106.0	#26/04/13
#ci=240.0; cj=105.0	#18/06/13
#ci=237.0; cj=105.0	#24/06/13 gb (crash mt8772)
#ci=234.0; cj=106.0	#24/06/13 gb (pilatus returned after repair)
#ci=248.0; cj=106.0	#12/9/13 new value as previous is now bad pixel
#ci=247.0; cj=109.0	#12/9/13 new value as previous is now bad pixel
#ci=249.0; cj=108.0	#26/11/13
#ci=241.0; cj=107.0	#14/01/14
#ci=236.0; cj=107.0	#11/03/14
#ci=240.0; cj=108.0	#11/03/14
#ci=243.0; cj=106.0	#09/04/14
#ci=257.0; cj=109.0	#24/06/14
#ci=247.0; cj=106.0	#01/12/14
#ci=245.0; cj=107.0	#10/12/14
#ci=244.0; cj=110.0	#13/01/15
#ci=242.0; cj=108.0	#23/06/15
#ci=240.0; cj=118.0	#23/06/15 #wrong gam offset
#ci=242.0; cj=110.0	#23/06/15
#ci=239.;cj=112. #02/03/16 after pilatus exchange
#ci=240.;cj=109. #04/03/16 after pilatus reexchange
#ci=238.;cj=111. #06/04/16 after pilatus reexchange
#ci=204.; cj=107; #02/05/17ci=242.;cj=105. #13/07/16 loan detector
#ci=244.; cj=103.; #10/08/16 loan detector
#ci=205.; cj=105; #19/02/17
#ci=205.; cj=104; #23/06/17
ci=206.; cj=107; #20/10/17


maxi=486; maxj=194 #08/10/15
'''
#small centred
roi1 = scroi=HardwareTriggerableDetectorDataProcessor('roi1', pil, [SumMaxPositionAndValue()])
iw=13; jw=15; roi1.setRoi(int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))

########
# PLEASE PUT EXPERIMENT-SPECIFIC ROI'S IN USER SCRIPTS
########

#roib1=HardwareTriggerableDetectorDataProcessor('roib1', pil, [SumMaxPositionAndValue()]);
#iwm=39; iwM=13;  jw=15; roib1.setRoi(int(ci-iwm/2.),int(cj-jw/2.),int(ci-iwM/2.),int(cj+jw/2.))

#roib2=HardwareTriggerableDetectorDataProcessor('roib2', pil, [SumMaxPositionAndValue()]);
#iwm=39; iwM=13;  jw=15; roib2.setRoi(int(ci+iwM/2.),int(cj-jw/2.),int(ci+iwm/2.),int(cj+jw/2.))

#roib3=HardwareTriggerableDetectorDataProcessor('roib3', pil, [SumMaxPositionAndValue()])
#iw=13;  jwm=15; jwM=45;roib3.setRoi(int(ci-iw/2.),int(cj+jwM/2.),int(ci+iw/2.),int(cj+jwm/2.))

#roib4=HardwareTriggerableDetectorDataProcessor('roib4', pil, [SumMaxPositionAndValue()])
#iw=13;  jwm=15; jwM=45;roib4.setRoi(int(ci-iw/2.),int(cj-jw/2.-15),int(ci+iw/2.),int(cj+jw/2.-15)) 

#roib5=HardwareTriggerableDetectorDataProcessor('roib5', pil, [SumMaxPositionAndValue()])
#iw=13;  jwm=15; jwM=45;roib5.setRoi(int(ci-iwm/2.),int(cj+jwM/2.),int(ci+iwM/2.),int(cj+jwm/2.))

#roib6=HardwareTriggerableDetectorDataProcessor('roib6', pil, [SumMaxPositionAndValue()]);
#iw=13;  jwm=15; jwM=45;roib6.setRoi(int(ci-iwM/2.),int(cj+jwM/2.),int(ci+iwm/2.),int(cj+jwm/2.))

#roib7=HardwareTriggerableDetectorDataProcessor('roib7', pil, [SumMaxPositionAndValue()]);
#iw=13;  jw=15; jwm=15; jwM=45;roib7.setRoi(int(ci-iw/2.-13),int(cj-jw/2.-15),int(ci+iw/2.-13),int(cj+jw/2.-15)) 

#roib8=HardwareTriggerableDetectorDataProcessor('roib8', pil, [SumMaxPositionAndValue()]);
#iw=13;  jw=15; jwm=15; jwM=45;roib8.setRoi(int(ci-iw/2.+13),int(cj-jw/2.-15),int(ci+iw/2.+13),int(cj+jw/2.-15)) 

#chishort=HardwareTriggerableDetectorDataProcessor('chishort', pil, [SumMaxPositionAndValue()]);
#iw=20; jw=1; chishort.setRoi(int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))

#large centred
roi2 = lcroi=HardwareTriggerableDetectorDataProcessor('roi2', pil, [SumMaxPositionAndValue()])
#roi2.setRoi(263-40,95-30,250+40,110+30)
iw=67; jw=75; roi2.setRoi(int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))
#horizonal line for delta scan (vertical on display)
roi3 = delroi=HardwareTriggerableDetectorDataProcessor('roi3', pil, [SumMaxPositionAndValue()])
#roi3.setRoi(256,0,257,194)
roi3.setRoi(int(ci-1/2.),0,int(ci+1/2.),maxj)

#thick horizonal line for searching with known two-theta (vertical on display)
roi7 = HardwareTriggerableDetectorDataProcessor('roi7', pil, [SumMaxPositionAndValue()])
#roi7.setRoi(256-25,0,257+25,194)
iw=67; jw=75; roi7.setRoi(int(ci-iw/2.),0,int(ci+iw/2.),maxj)

#vertical line for chi scan (horizontal on display)
roi4 = chiroi=HardwareTriggerableDetectorDataProcessor('roi4', pil, [SumMaxPositionAndValue()])
#roi4.setRoi(0,102,486,103)
roi4.setRoi(0,int(cj-1/2.),maxi,int(cj+1/2.))


#vertical line for background subtraction (horizontal on display) (15px wide, 13 * roi5 covers full detector)
roi5 = HardwareTriggerableDetectorDataProcessor('roi5', pil, [SumMaxPositionAndValue()])
roi5.setRoi(0,0,486,14)

#very small centred
roi6 = HardwareTriggerableDetectorDataProcessor('roi6', pil, [SumMaxPositionAndValue()])
iw=7; jw=7; roi6.setRoi(int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))

#for searching for reflections at known delta
#wideroi = HardwareTriggerableDetectorDataProcessor('roi3', pil, [SumMaxPositionAndValue()])
#wid=20; wideroi.setRoi(int(ci-wid/2.),0,int(ci+wid/2.),maxj)
'''

## pilatus3 rois changed 14 April 2018
ci, cj = 243, 96
roi1 = scroi=HardwareTriggerableDetectorDataProcessor('roi1', pil3, [SumMaxPositionAndValue()])
iw=13; jw=15; roi1.setRoi(int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))

roi2 = lcroi=HardwareTriggerableDetectorDataProcessor('roi2', pil3, [SumMaxPositionAndValue()])
iw=50; jw=50; roi2.setRoi(int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))

roi3 = delroi=HardwareTriggerableDetectorDataProcessor('roi3', pil3, [SumMaxPositionAndValue()])
roi3.setRoi(int(ci-1/2.),0,int(ci+1/2.),maxj)

roi4 = chiroi=HardwareTriggerableDetectorDataProcessor('roi4', pil3, [SumMaxPositionAndValue()])
roi4.setRoi(0,int(cj-1/2.),maxi,int(cj+1/2.))




#roi6.setRoi(258-3,99+3,258+3,10.693599-3)

#roi1 = DetectorDataProcessorWithRoi('roi1', pil, [SumMaxPositionAndValue()])
#roi1.setRoi(219,75,275,115)

#roi2 = DetectorDataProcessorWithRoi('roi2', pil, [SumMaxPositionAndValue()])
#roi2.setRoi(262,100,253,110)
#roi2.setRoi(263,95,250,110)

# Refl beam ROI
#roiR = DetectorDataProcessorWithRoi('roiR', pil, [SumMaxPositionAndValue()])
#roiR.setRoi(1342, 1425, 1354, 1434)

# Dir beam ROI
#roiD = DetectorDataProcessorWithRoi('roiD', pil, [SumMaxPositionAndValue()])
#roiD.setRoi(1342, 1430, 1354, 1438)


#roi2m1= DetectorDataProcessorWithRoi('roi2m1', pil2m, [SumMaxPositionAndValue()])
#roi2m1.setRoi(1300,1438,1318,1444)

#roi3 = DetectorDataProcessorWithRoi('roi3', pil, [SumMaxPositionAndValue()])
#roi3.setRoi(229,60,300,140)

# This depends on lcroi
run('FlipperClass')




###############################################################################
###                             Complete Localstation                       ###
###############################################################################

# Restore data directory
setDatadirPropertyFromPersistanceDatabase()
showlm()
print "======================================================================"
import gda.data.PathConstructor
print "Current data directory: ", gda.data.PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")
print "======================================================================"
if USE_DUMMY_IDGAP_MOTOR or type(idgap.getMotor())==gda.device.motor.DummyMotor:
	print "!"*80
	print "Warning: Using a dummy idgap motor"
	print "!"*80
if type(bragg.getMotor())==gda.device.motor.DummyMotor:
	print "!"*80
	print "WARNING: Using a dummy bragg motor"

if USE_DIFFCALC:
	print "WARNING: Using Diffcalc instead of Allesandro's code"
	
	
print "======================================================================"

	
	
run('diffractometer/pid.py')
###############################################################################
###                           Diff - xpsgather                              ###
###############################################################################
from scannable.xpsdatagathering import ScannableXPSDataGatherer
xpsgather = ScannableXPSDataGatherer('xpsgather', pvroot='BL16I-CS-IOC-15:XPSG:')

###############################################################################
###                           Defaults - keep at end                        ###
###############################################################################
if installation.isLive():
	add_default meta
	add_default atime
	add_default ic1monitor 
	add_default rc
	add_default waitforinjection
	waitforinjection.due=5	#wait for injection if due in this period of time (sec)

###############################################################################
###                Optionally switch pilatus to CBF writing                 ###
###############################################################################
from scannable.detector import pilatuscbfswitcher
# NOTE: state will be stored across calls to reset_namespace
#pilatuscbfswitcher.set(pil2m, 'cbf')


###############################################################################
###                           Run beamline scripts                          ###
###############################################################################


run('bpm')
run('align1')
run('select_and_move_detector')
run('showdiff')
run('showdiff_new')
bpmroi1 = HardwareTriggerableDetectorDataProcessor('bpmroi1', bpm, [SumMaxPositionAndValue()])
#bpmroi1.setRoi(int(972-30),int(426-5),int(972+30),int(426+5))
bpmroi1.setRoi(int(1010-30),int(394-5),int(1010+30),int(394+5)) # set 04/10/2017 at 8 keV shtr3x 11.93 shtr3y 4.40
#run('pd_searchref2') #put at the end as it gave some errors
run('pd_read_list')	#to make PD's that can scan a list
run('pd_function')	#to make PD's that return a variable
#run('PDFromFunctionClass')#to make PD's that return the value of a function  - already run!

print "==========================="
print "Setting up continuous scans"
run("setup_cvscan")
print "Continuous scans setup"
print "==========================="

run("startup_pie725")

if USE_NEXUS:
	run("datawriting/i16_nexus")
	pass
else:
	#clear extenders possible configured already
	writerMap = Finder.getInstance().getFindablesOfType(gda.data.scan.datawriter.DefaultDataWriterFactory)
	ddwf = writerMap.get("DefaultDataWriterFactory")
	for dwe in ddwf.getDataWriterExtenders():
		ddwf.removeDataWriterExtender(dwe)
	pass
'''
from mtscripts.scannable.ContinouslyRockingScannable import ContinuouslyRockingScannable
kphirock = ContinuouslyRockingScannable('kphirock', scannable = kphi)
kphirock.verbose = False

chirock = ContinuouslyRockingScannable('chirock', scannable = chi)
chirock.verbose = False

etarock = ContinuouslyRockingScannable('etarock', scannable = eta)
etarock.verbose = False
'''

run("sz_cryo")
cryodevices={'800K':[4.47796541e-14, -7.01502180e-11, 4.23265147e-08, -1.24509237e-05, 8.48412284e-04, 1.00618264e+01],'4K':[-1.43421764e-13, 1.05344999e-10, -1.68819096e-08, -5.63109884e-06, 3.38834427e-04, 9.90716891]}
szc=szCryoCompensation("szc", sz, cryodevices, help="Sample height with temperature compensation.\nEnter, for example szc.calibrate('4K','Ta') \nto calibrate using the 4K cryo and channel Ta or\nszc.calibrate('800K','Tc') for the cryofurnace.")



SMARGON = False

if SMARGON: 
	sgphi=SingleEpicsPositionerClass('phi','BL16I-MO-SGON-01:PHI.VAL','BL16I-MO-SGON-01:PHI.RBV','BL16I-MO-SGON-01:PHI.DMOV','BL16I-MO-SGON-01:PHI.STOP','deg','%.4f')
	sgomega=SingleEpicsPositionerClass('omega','BL16I-MO-SGON-01:OMEGA.VAL','BL16I-MO-SGON-01:OMEGA.RBV','BL16I-MO-SGON-01:OMEGA.DMOV','BL16I-MO-SGON-01:OMEGA.STOP','deg','%.4f')
	sgchi=SingleEpicsPositionerClass('chi','BL16I-MO-SGON-01:CHI.VAL','BL16I-MO-SGON-01:CHI.RBV','BL16I-MO-SGON-01:CHI.DMOV','BL16I-MO-SGON-01:CHI.STOP','deg','%.4f')
	exec("del hkl")
	exec("del euler")
	run("SmargonTopClass")	
	from diffractometer.scannable import HklSmargon,EulerSmargonPseudoDevice 
	reload(HklSmargon) 
	reload(EulerSmargonPseudoDevice)
	exec('phi =sgphi')
	exec('eta =sgomega')
	exec('chi =sgchi')
	BLobjects.my_smarchi =chi
	BLobjects.my_smaromega = eta 
	BLobjects.my_smarphi =phi
	euler= EulerSmargonPseudoDevice.EulerianPseudoDevice("euler",san,kmu,kdelta,kgam)   
	hkl = HklSmargon.HklSmargon("hkl",euler,rs,CA,EDi,az) 
	
 	print """ Smargon script was successful"""




######### temp 24/04/2018 ############# 

do.pil = 8.8

def diodein():
    pos tthp 0
    pos dettrans 0
def apdin():
    pos tthp -0.35
    pos dettrans -27.71
def vortexin():
    pos tthp 85.4-96.5
    pos dettrans 25

def pilin():
    pos do do.pil
    pos s6ygap 2
    pos s6ytrans 10.433
    pos s6ygap 9
def pilout():
    pos do 0
    pos s6ygap 2.8
    pos s6ytrans 0
meta.add(dettrans) # should go in a better place







print "======================================================================"
print "Local Station Script completed"
print "======================================================================"
