###############################################################################
# This script is the main i16 localStation script, it will be used whenever   #
# the `reset_namespace` command is run on the Jython terminal console in GDA, #
# or the gda servers are restarted.                                           #
###############################################################################

from localstation_functions import localStation_print, localStation_exception,\
	localStation_warning, localStation_warnings, localStation_exceptions
from localStationScripts.startup_epics_positioners import X1_DELAY

print("=============================================================")
print("Running I16 specific initialisation code from localStation.py")
print("=============================================================")

localStation_print("Import configuration booleans from user scripts localStationConfiguration.py")
try:
	from localStationConfiguration import USE_DIFFCALC, USE_DIFFCALC_WITHOUT_LASTUB, USE_DUMMY_IDGAP_MOTOR # @UnresolvedImport
	from localStationConfiguration import USE_NEXUS, USE_NEXUS_METADATA_COMMANDS, USE_XMAP # @UnresolvedImport
	from localStationConfiguration import USE_SMARGON, USE_PIL1, USE_PIL2, USE_PIL3, USE_ROCKING_SCANNABLES # @UnresolvedImport
except:
	USE_DIFFCALC = True
	USE_DIFFCALC_WITHOUT_LASTUB = False
	USE_DUMMY_IDGAP_MOTOR = False
	USE_NEXUS = True
	USE_NEXUS_METADATA_COMMANDS = True
	USE_XMAP= False
	USE_SMARGON = False
	USE_PIL1 = True
	USE_PIL2 = True
	USE_PIL3 = True
	USE_ROCKING_SCANNABLES = False
	localStation_exception("importing configuration booleans from user scripts localStationConfiguration.py, using default values:\n"+
		"        USE_DIFFCALC=%r, USE_DIFFCALC_WITHOUT_LASTUB=%r, USE_DUMMY_IDGAP_MOTOR=%r,\n" %
				(USE_DIFFCALC,    USE_DIFFCALC_WITHOUT_LASTUB,    USE_DUMMY_IDGAP_MOTOR) +
		"        USE_NEXUS=%r, USE_NEXUS_METADATA_COMMANDS=%r, USE_XMAP=%r,\n" %
				(USE_NEXUS,    USE_NEXUS_METADATA_COMMANDS,    USE_XMAP) +
		"        USE_SMARGON=%r, USE_PIL1=%r, USE_PIL2=%r, USE_PIL3=%r, USE_ROCKING_SCANNABLES=%r" %
				(USE_SMARGON,    USE_PIL1,    USE_PIL2,    USE_PIL3,    USE_ROCKING_SCANNABLES)
		)

if USE_NEXUS_METADATA_COMMANDS and not USE_NEXUS:
	localStation_exception("trying to use USE_NEXUS_METADATA_COMMANDS when USE_NEXUS = False, setting USE_NEXUS_METADATA_COMMANDS = False", None)
	USE_NEXUS_METADATA_COMMANDS = False

if USE_DIFFCALC and USE_SMARGON:
	localStation_exception("trying to both USE_DIFFCALC and USE_SMARGON, setting USE_DIFFCALC = False", None)
	USE_DIFFCALC = False

from gda.configuration.properties import LocalProperties
LocalProperties.set('gda.scan.clearInterruptAtScanEnd', "False")

global Finder, pos, add_default, meta
global idgap
global bragg, perp

global sixckappa, sixckappa_fly
global delta_axis_offset
global azir, psi, psic, hkl
global setDatadirPropertyFromPersistanceDatabase, pitchupClass
global stokes,zp,thp_offset,thp_offset_sigma,thp_offset_pi,tthp_offset_sigma,tthp_detoffset,cry_offset,ref_offset,tthp_offset_pi,detector_lateral_offset_zero,detector_lateral_offset_ninety
global ic1monitor
global x2000, x2003
global delta
global energy, simple_energy, gam
global x1
global _bpm1, _bpm1_for_snaps, _bpm1_no_screen, _bpm1_no_screen_for_snaps
global _cam1, _cam1_for_snaps
global _camd3, _camd3_for_snaps
global _camd4, _camd4_for_snaps
global _camd5, _camd5_for_snaps
global corExpTime, cor2ExpTime
global _xeye, _xeye_for_snaps
global _zylar, _zylar_for_snaps
global _merlin, _merlin_for_snaps
global xtalinfo
global mu, en
global uharmonic
global shtr3x,shtr3y
global m1piezo
global m3x, m4x, m3pitch, m4pitch
global eta_offset, mu_offset
global beta
global T1dcm, T2dcm
global ppx, ppy, ppchi
global ppyaw,ppth1,ppz1,ppth2,ppz2,ppyaw,pppitch
global sperp, spara, ytable, ztable
global xps3m1, xps3m2, xps3m3, xps3m4, xps3m5, xps3m6
global frontendx, frontendy
global diode, ic2
global m1y_offset, m2y_offset, base_z_offset, ztable_offset, m2_coating_offset, idgap_offset, ppy_offset
global san
global rs,CA,EDi,az

try:
	from gdascripts.parameters import beamline_parameters
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
except:
	localStation_exception("creating jythonNameMap")

if Finder.find("kbmbase"):
	global kbmbase

localStation_print("Importing installation")
import installation

if installation.isDummy():
	print "*"*80
	localStation_print("DUMMY Mode!")
	print "*"*80
	
	from lab84.installVarDataFromBeamlineIfNotPresent import install_cache_data
	install_cache_data()
	
	USE_DIFFCALC = True
	USE_DIFFCALC_WITHOUT_LASTUB = False
	USE_DUMMY_IDGAP_MOTOR = True
	USE_SMARGON = False
	USE_PIL1 = False
	USE_PIL2 = False
	localStation_print("Override some localStationConfiguration options in order to run in dummy mode:\n"+
		"        USE_DIFFCALC=%r, USE_DIFFCALC_WITHOUT_LASTUB=%r, USE_DUMMY_IDGAP_MOTOR=%r,\n" %
				(USE_DIFFCALC,    USE_DIFFCALC_WITHOUT_LASTUB,    USE_DUMMY_IDGAP_MOTOR) +
		"        USE_NEXUS=%r, USE_NEXUS_METADATA_COMMANDS=%r, USE_XMAP=%r,\n" %
				(USE_NEXUS,    USE_NEXUS_METADATA_COMMANDS,    USE_XMAP) +
		"        USE_SMARGON=%r, USE_PIL1=%r, USE_PIL2=%r, USE_PIL3=%r, USE_ROCKING_SCANNABLES=%r" %
				(USE_SMARGON,    USE_PIL1,    USE_PIL2,    USE_PIL3,    USE_ROCKING_SCANNABLES)
		)
# Java
import java
from Jama import Matrix

# Python
from time import sleep
from math import * #@UnusedWildImport
from javashell import * #@UnusedWildImport

# Gda
localStation_print("Importing various gda classes")
from gda.analysis.io import  PilatusTiffLoader
from gda.device.epicsdevice import ReturnType #@UnusedImport
from gda.device.scannable import ScannableBase
from gda.device.scannable import ScannableMotionBase as PseudoDevice
from gda.epics import CAClient #@UnusedImport
from gda.jython.commands.GeneralCommands import alias, run #@UnusedImport

localStation_print("Importing LocalJythonShelfManager")
from uk.ac.diamond.daq.persistence.jythonshelf import LocalJythonShelfManager

localStation_print("Importing datasetprocessors")
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeakWithCalibration import TwodGaussianPeakWithCalibration
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.analysis.datasetprocessor.oned.scan_stitching import Lcen, Rcen
from gdascripts.analysis.datasetprocessor.oned.GaussianEdge import GaussianEdge #@UnusedImport

localStation_print("Importing concurrentScanWrapper")
import gdascripts.scan.concurrentScanWrapper #@UnusedImport

localStation_print("Importing jobs")
from gdascripts.utils import jobs #@UnusedImport

localStation_print("Importing gdascans")
from gdascripts.scan import gdascans #@UnusedImport

localStation_print("Importing installStandardScannableMetadataCollection")
from gdascripts.scannable.installStandardScannableMetadataCollection import * #@UnusedWildImport

localStation_print("Importing EpicsPilatus")
from gdascripts.scannable.detector.epics.EpicsPilatus import EpicsPilatus #@UnusedImport

localStation_print("Importing ProcessingDetectorWrapper...")
from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper, HardwareTriggerableProcessingDetectorWrapper, SwitchableHardwareTriggerableProcessingDetectorWrapper #@UnusedImport

localStation_print("Importing DetectorDataProcessor...")
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessor, DetectorDataProcessorWithRoi, HardwareTriggerableDetectorDataProcessor #@UnusedImport

localStation_print("Importing MultiInputExtraFieldsDummy, SingleInputDummy")
from gdascripts.scannable.dummy import MultiInputExtraFieldsDummy, SingleInputDummy #@UnusedImport

#localStation_print("Importing EpicsFirewireCamera")
#from gdascripts.scannable.detector.epics.EpicsFirewireCamera import EpicsFirewireCamera #@UnusedImport

localStation_print("Importing NxProcessingDetectorWrapper")
from epics.detector.NxProcessingDetectorWrapper import NxProcessingDetectorWrapper #@UnusedImport

# I16
localStation_print("Importing ShelveIO")
import ShelveIO
localStation_print("Importing BLobjects")
import beamline_objects as BLobjects

### Configure shelveIO path
localStation_print("Configuring ShelveIO system")
installation.setLoadOldShelf(0)
localStation_print("LoadOldShelf="+("True" if installation.loadOldShelf() else "False"))
shelveIoDir = LocalProperties.get("gda.var")
shelveIoDir  = shelveIoDir + "/oldStyleShelveIO/"
ShelveIO.ShelvePath = shelveIoDir
localStation_print("  ShelveIO path = %r" % shelveIoDir)

from constants import * #@UnusedWildImport
from element_library import * #@UnusedWildImport
from scannable.toggleBinaryPvAndWaitScannable import ToggleBinaryPvAndWait
from misc_functions import list_scannables, listprint, frange, attributes, caput, caget, cagetArray, add, mult #@UnusedImport
import pd_offset
from analysis.FindScanPeak import FindScanPeak #@UnusedImport
from analysis.FindScanCentroid import findCentroidPoint, FindScanCentroid, readSRSDataFile #@UnusedImport
from device_serial import SerialDevice #@UnusedImport
from device_serial_ace import ace
from device_tca import TCA
from pd_epics import SingleEpicsPositionerSetAndGetOnlyClass #@UnusedImport
from pd_readSingleValueFromVectorScannable import ReadSingleValueFromVectorPDClass
from pd_time import tictoc, showtimeClass, mrwolfClass, showincrementaltimeClass, waittimeClass, TimeScannable, absoluteTimeClass, absoluteTimeClassTwo #@UnusedImport
from pd_dummy import dummyClass
from pd_foilinserter import Foilinserter
from pd_attenuator import Atten
from pd_epics import DisplayEpicsPVClass, SingleEpicsPositionerClass, SingleEpicsPositionerNoStatusClass, SingleEpicsPositionerSetAndGetOnlyClass, SingleEpicsPositionerNoStatusClass2, Epics_Shutter #@UnusedImport #@UnusedImport
from pd_ionpump import AllPumpsOnPD, EpicsIonpClass #@UnusedImport
from pd_struck import Struck
from pd_struck2 import Struck2
from pd_MoveScalarPDsToPresetValues import MoveScalarPDsToPresetValuesClass
from pd_qbpm import EPICSODQBPMClass, EPICSODQBPMClass2 #@UnusedImport
from pd_tca import tcasca
from pd_mcachannel import McaChannel #@UnusedImport
from pd_mca import Mca
from pd_LS340readback import DisplayEpicsPVClassLS, DisplayEpicsPVClassLS2 #@UnusedImport
from pd_LS340control import EpicsLScontrol
from pd_LS340setpoint import EpicsLSsetpoint
from pd_LakeshorePID import EpicsLakeshorePID
from pd_WaitForBeam import WaitForBeamPDClass, TimeToMachineInjectionClass, WaitForInjectionPDClass, wait_for_injection_scan_start, wait_for_beam_scan_start #@UnusedImport
from pd_metadata_group import ReadPDGroupClass
from pd_diffractometerbase import DiffoBaseClass
from pd_x2000 import x2000scaClass
from pd_acescaler import acesca1
from device_serial_x2000 import x2000class
from pd_azihklClass import AzihklClass
from spechelp import * #@UnusedWildImport # aliases man objects
from scannable.MoveThroughOrigin import MoveThroughOriginScannable #@UnusedImport
from gda.device.scannable.scannablegroup import DeferredScannableGroup

alias("jobs")

if not USE_NEXUS:
	LocalProperties.set("gda.data.scan.datawriter.dataFormat", "SrsDataFile")

# USE_NEXUS & USE_NEXUS_METADATA_COMMANDS are now defined in the
# localStationConfiguration.py user script

if USE_NEXUS and USE_NEXUS_METADATA_COMMANDS:

	from gdascripts.metadata.metadata_commands import setTitle, getTitle, meta_add, meta_ll, meta_ls, meta_rm, meta_clear_alldynamical #@UnusedImport
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
localStation_print("Replacing ScannableMotors kphi, kap. kth, kmu, kdelta and kgam with wrappers supporting coordinated movement")

sixc = sixckappa #@UndefinedVariable  NOTE: sixc is overwritten by diffcalc later
kap, kth, kmu, kdelta, kgam, kphi = sixc.kap, sixc.kth, sixc.kmu, sixc.kdelta, sixc.kgam, sixc.kphi
kphi_fly, kap_fly, kth_fly, kmu_fly, kdelta_fly, kgam_fly = sixckappa_fly.kphi_fly, sixckappa_fly.kap_fly, sixckappa_fly.kth_fly, sixckappa_fly.kmu_fly, sixckappa_fly.kdelta_fly, sixckappa_fly.kgam_fly

SIXC_MOTOR_NAMES = ['sixcKphiMotor', 'sixcKappaMotor', 'sixcKthMotor', 'sixcMuMotor', 'sixcDeltaMotor','sixcGammaMotor']
SIXC_SCANNABLEMOTOR_NAMES = ['kphi', 'kap', 'kth', 'kmu', 'kdelta', 'kgam']

localStation_print("Creating post_xps_restart")
def post_xps_restart():
	for mot in [Finder.find(n) for n in SIXC_MOTOR_NAMES]:
		mot.forceCallback()

localStation_print("Creating set_assert_sixc_home_before_moving(True|False)")
def set_assert_sixc_homed_before_moving(b):
	for mot in [Finder.find(n) for n in SIXC_MOTOR_NAMES]:
		mot.setAssertHomedBeforeMoving(b)

localStation_print("Creating set_sixc_returns_demand_position(True|False)")
def set_sixc_returns_demand_position(b):
	for scnmot in [Finder.find(n) for n in SIXC_SCANNABLEMOTOR_NAMES]:
		scnmot.setReturnDemandPosition(b)

###############################################################################
###                            Generic Scannables                             #
###############################################################################

### Dummy IDGAP
if USE_DUMMY_IDGAP_MOTOR:
	with overwriting:  # @UndefinedVariable
		exec("idgap=dummyClass('idgap')")

# TODO: This shouldn't be necessary, try removing it.
#       Look for "Overwriting scannable 'c1'" etc. in logs
#       Look for uses in scans, try to replicate at desk
from gda.device.monitor import EpicsMonitor
from scannable.MonitorWrapper import MonitorWrapper #@UnusedImport
toPrint = ''
localStation_print("Wrapping Monitors...")
for objname in dir():
	if isinstance(eval(objname),EpicsMonitor):
		toPrint+= objname + " "
		with overwriting:  # @UndefinedVariable
			exec(objname + " = MonitorWrapper(" + objname + ")")
localStation_print("Wrapped the monitors: " + toPrint)

### Create dummy Scannables
localStation_print("Creating dummy scannables")
dummy = dummyClass('Dummy')
x=dummyClass('x')
y=dummyClass('y')
z=dummyClass('z')
q=dummyClass('q')
qq=dummyClass('qq')
progress=dummyClass('progress')
mie = MultiInputExtraFieldsDummy('mie', ['i1', 'i2'], ['e1'])


### Create time Scannables
localStation_print("Creating time scannables")
tim = TimeScannable('Time')
showtime=showtimeClass('Showtime')
inctime=showincrementaltimeClass('inctime')
waittime=waittimeClass('Waittime')
atime=absoluteTimeClass('atime')
atimetwo=absoluteTimeClassTwo('atimetwo')
w=waittime	#abreviated name
mrwolf=mrwolfClass('mrwolf')

### Create offset devices
localStation_print("Running localStationScripts/startup_offsets.py: Starting database system...")
run("localStationScripts/startup_offsets")
localStation_print("...Database system started")
offsetshelf=LocalJythonShelfManager.open('offsets')
localStation_print("  use 'offsetshelf' to see summary of offsets")
#delta_axis_offset.pil=9.5
#delta_axis_offset.pil=9.0 #new offset 31/01/12 (179)
#delta_axis_offset.pil=9.2#new offset 12/09/13
delta_axis_offset.pil=8.6#new offset 19/02/17
do=delta_axis_offset

if installation.isDummy():
	from lab84.initialise_offsets import setup_scannables_offsets
	setup_scannables_offsets()
	
###############################################################################
###                            Generic Functions                            ###
###############################################################################

### Create datadir functions
localStation_print("Running localStationScripts/startup_dataDirFunctions.py")
localStation_print("  use 'datadir' to read the current directory or 'datadir name' to change it")
run("localStationScripts/startup_dataDirFunctions") # depends on globals pil2mdet and pil100kdet
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

localStation_print("Importing analysis commands (peak, centroid & peak optimisation)")
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
localStation_print("Creating diffractometer base scannable base_z")
#base_z= DiffoBaseClass(basez1, basez2, basez3, [1.52,-0.37,0.]) #measured 28/11/07
base_z= DiffoBaseClass(basez1, basez2, basez3, [0.,0.,0.]) #jacks recal to zero in epics 8 keV direct beam 20/10/15 @UndefinedVariable

run("localStationScripts/startup_diffractometer_euler")

if not USE_DIFFCALC:
	localStation_warning("setting up diffractometer, using Allesandro's code instead of diffcalc")
	run("localStationScripts/startup_diffractometer_hkl")
	azihkl=AzihklClass('aziref')
	azihkl.azir_function = azir
	psi.setInputNames(['psi'])
	psic.setInputNames(['psic'])
else:
	del sixc
	robot_startup_script = "diffractometer/scannable/RobotArmBeamline"
	run(robot_startup_script)
	from startup.i16 import *

	if USE_DIFFCALC_WITHOUT_LASTUB:
		localStation_warning("loading lastub(), this has been suppressed by Starting Diffcalc by USE_DIFFCALC_WITHOUT_LASTUB %r" % USE_DIFFCALC_WITHOUT_LASTUB)
	else:
		try:
			lastub()  # Load the last ub calculation used
		except:
			localStation_exception("trying to run lastub()")
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

if Finder.find("kbmbase") and installation.isLive():
	try:
		from scannable.tripod import TripodToolBase

		kbm1 = TripodToolBase("kbm1", kbmbase, c=[152, 42.5, 63], **copy.deepcopy(_kbm_common_geom))
	
		kbm2 = TripodToolBase("kbm2", kbmbase, c=[42, 42.5, 63], **copy.deepcopy(_kbm_common_geom))
	
		from pd_single_element_of_vector_pd import * #@UnusedWildImport
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
	
	except:
		localStation_exception("creating kbm1 and kbm2.")
else:
	localStation_warning("creating kbm1 and kbm2. Please restart the GDA servers with the 'kbm' transient device enabled, if you need them.")

###############################################################################
###############################################################################
###############################################################################
###############################################################################
#
#                             END OF DUMMYSTARTUP
#
# if installation.isDummy():
# 	localStation_print("Running localStation.test_only.py ...")
# 	run("localStationScripts/localStation.test_only")
# 	localStation_print("... completed localStation.test_only.py")
# 	print
# 	setDatadirPropertyFromPersistanceDatabase()
# 	raise Exception("Manually INTERRUPTING localStation.py run as this is a test installation")

###############################################################################
###############################################################################
###############################################################################
###############################################################################


###############################################################################
###                          Tune finepitch using QBPM                      ###
###############################################################################
localStation_print("Tuning finepitch using QBPM *Use with care*")
run("localStationScripts/pitchup") # GLOBALS: qbpm6inserter, finepitch, ic1, atten, , vpos
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
#mca=Finder.find(vortexName)
#if (mca != None):
#	ctmca=mca_utils.ctmcaClass('ctmca',mca)
#	rdmca=mca_utils.rdmcaClass('rdmca',mca)
#	mcaROI1=mca_utils.rdROIClass('rdROI1',mca,910,917)
#	mcaROI2=mca_utils.rdROIClass('rdROI2',mca,913,914)
#	mcaSca1 = mca_utils.rdScaClass('mcaSca1',mca,910,917)
#	mcaSca2 = mca_utils.rdScaClass('mcaSca2',mca,913,914)

try:
	### Various ###
	localStation_print("   running localStationScripts/startup_epics_monitors.py")
	from localStationScripts.startup_epics_monitors import *
	global ppchitemp, ppth1temp, ppz1temp, ppth2temp, ppz2temp
except:
	localStation_exception("running localStationScripts/startup_epics_monitors.py")

if installation.isLive():
	localStation_print("   running localStationScripts/startup_epics_positioners.py")
	run("localStationScripts/startup_epics_positioners")
else:
	from gda.device.scannable import DummyScannable
	frontendx = DummyScannable('frontendx', 0)
	frontendy = DummyScannable('frontendy', 0)
	m1piezo = DummyScannable("m1piezo", 0)
	m3pitch = DummyScannable("m3pitch", -3.399999999997849e-05)
	m3x = DummyScannable("m3x", -3.999865)
	m4pitch = DummyScannable("m4pitch", 1.6799999999983495e-05)
	m4x = DummyScannable("m4x", 4.000532499999999)
	p2mj1 = DummyScannable("p2mj1", 0)
	p2mj2 = DummyScannable("p2mj2", 0)
	p2mj3 = DummyScannable("p2mj3", 0)
	p2mx1 = DummyScannable("p2mx1", 0)
	p2mx2 = DummyScannable("p2mx2", 0)
	shtr3x = DummyScannable("shtr3x", 11.53)
	shtr3y = DummyScannable("shtr3y", 4.305)
	x1=x1_ttl=DummyScannable("x1_ttl", 0)
	ytable = DummyScannable("ytable", 0)
	ztable = DummyScannable("ztable", 0)
	zp = DummyScannable('zp', -22.314700000000002)

	T1dcm = DummyScannable('T1dcmSi111', 108.24045790941138) # From scan 971324
	T2dcm = DummyScannable('T2dcmSi111', 11.705548057664442)

try:
	localStation_print("   running localStationScripts/startup_cryocooler.py")          #[NOTE: Also creates commands]
	run("localStationScripts/startup_cryocooler")
except:
	localStation_exception("running localStationScripts/startup_cryocooler.py")

try:
	localStation_print("   running pd_femto_adc_current2.py")
	run("localStationScripts/pd_femto_adc_current2.py")
except:
	localStation_exception("running localStationScripts/pd_femto_adc_current2.py")

try:
	localStation_print("   running pd_xyslit.py")
	from pd_xyslit import pd_xyslit
	ds=pd_xyslit('Detector slits (s7)','%.3f',s7xgap,s7ygap,s7xtrans,s7ytrans,help='Detector slit gaps\npos ds [1 2] to get 1 mm (h) x 2 mm(v) slit\npos ds.x .5 to translate x centre to 0.5 mm')  # @UndefinedVariable
	ss=pd_xyslit('Sample slits (s5)',  '%.3f',s5xgap,s5ygap,s5xtrans,s5ytrans,help=  'Sample slit gaps\npos ss [1 2] to get 1 mm (h) x 2 mm(v) slit\npos ss.x .5 to translate x centre to 0.5 mm')  # @UndefinedVariable
except:
	localStation_exception("configuring epics ds & ss scannables")

localStation_print( "   creating attocube devices")
try:
	from scannable.ecc100axis import attoltilt, attoutilt, attorot, attox, attoy, attoz
except:
	localStation_exception("creating attocube devices")

try:
	localStation_print("   creating ion pump scannables")
	run("localStationScripts/startup_ionpumps")
except:
	localStation_exception("running localStationScripts/startup_ionpumps.py")

try:
	localStation_print("   creating shutter scannable")
	shutter= Epics_Shutter('shutter','BL16I-PS-SHTR-01:CON')

	### Struck ###
	localStation_print("   Creating struck counter/timer scannables: ct1-ct11")
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
	localStation_print("   creating QBPM scannables")
	qbpm1=EPICSODQBPMClass('QBPM1','BL16I-DI-IAMP-01',help='Current amp in optics hutch\nc1: White beam diode\nc2: broken\nc3: d3d diode\nc4: d4d diode')
	qbpm7=EPICSODQBPMClass('QBPM7','BL16I-DI-IAMP-07',help='Current amp1 in experimental hutch\nc1: S5 diagnostic diode\nc2-4: not used')
	qbpm6=EPICSODQBPMClass('QBPM6','BL16I-DI-IAMP-06',help='Current amp for QBPM in experimental hutch')
	#pmon=qbpm8=EPICSODQBPMClass2('QBPM8','BL16I-DI-IAMP-08',help='Current amp for polarimeter QBPM in experimental hutch')
	#vpos=ReadSingleValueFromVectorPDClass(qbpm6,6,'vpos','%.4f',help='qbpm vertical position (Y)')
	#hpos=ReadSingleValueFromVectorPDClass(qbpm6,5,'hpos','%.4f',help='qbpm horizontal position (X)')
except:
	localStation_exception("configuring epics shutter struck and qbpm scannables")

if installation.isLive():
	### Foil inserters ###
	localStation_print("   creating foil inserter scannables")
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
else:
	atten = Atten('Attenuator',[])
	atten.setOutputFormat(['%.0f', '%.4g'])

try:
	### Polarization analyser ###
	from pd_polarizationAnalyser import pa_crystal, pa_detector, pol, stokes_pars, pa_jones

	### TCA  ###
	localStation_print("   creating TCA scanables")
	tca=TCA('BL16I-EA-DET-01:tca1')
	tcasca1=tcasca('TCAsca1',"%4.3f",tca,"%",'1')
	tcasca2=tcasca('TCAsca2',"%4.3f",tca,"%",'2')
	tcasca3=tcasca('TCAsca3',"%4.3f",tca,"%",'3')

	### MCA ###
	if installation.isLive():
		localStation_print("Creating MCA scannables: mca1")
		mca1=Mca('MCA1','BL16I-EA-DET-01:aim_adc1')
except:
	localStation_exception("configuring epics pol, tca and mca scannables")


if installation.isLive():
	### LS340 ###
	localStation_print("Creating LS340 scannables")
	try:
		from pd_sample_temperature import TemperatureController
		tcontrol_id = pd_offset.Offset('tcontrol_id')
		tcontrol = TemperatureController('tcontrol', tcontrol_id)
		tset = tcontrol.tset_device('tset')
		Ta = tcontrol.Ta_device('Ta')
		Tb = tcontrol.Tb_device('Tb')
		Tc = tcontrol.Tc_device('Tc')
		Td = tcontrol.Td_device('Td')
		Tsample = tcontrol.Tsample_device('Tsample')
		Theater = tcontrol.Theater_device('Theater')
		twait = tcontrol.twait_device('twait', tset, Tsample)
		Tchannel = tcontrol.Tchannel_device('Tchannel')
	except:
		localStation_exception("connecting to epics PVs for BL16I-EA-LS340-01 - failed to create Scannables: Treg, Tsam, tset, T1, T2, Ta, Tb, Tc, Td, Tas, Tbs, Tcs & Tds")

	LSP=SingleEpicsPositionerSetAndGetOnlyClass('LS_P','BL16I-EA-LS340-01:P_S','BL16I-EA-LS340-01:P','P','%4f')
	LSI=SingleEpicsPositionerSetAndGetOnlyClass('LS_I','BL16I-EA-LS340-01:I_S','BL16I-EA-LS340-01:I','I','%4f')
	LSD=SingleEpicsPositionerSetAndGetOnlyClass('LS_D','BL16I-EA-LS340-01:D_S','BL16I-EA-LS340-01:D','D','%4f')
	#LSPID=ReadPDGroupClass('LS_PID',[LSP,LSI,LSD])
	pid1=EpicsLakeshorePID('PID_1','PID? 1','PID 1','','%4f')
	pid2=EpicsLakeshorePID('PID_2','PID? 2','PID 2','','%4f')
else:
	localStation_print("Creating limited dummy LS340 scannables") # Based on scan 971324
	from gda.device.scannable import DummyUnitsScannable
	# DummyUnitsScannable(String name, double initialPosition, String hardwareUnits, String userUnits) throws
	tset=DummyUnitsScannable('tset', 300.0,  'K','K')
	Ta=DummyUnitsScannable(  'Ta',   300.033,'K','K')
	Tb=DummyUnitsScannable(  'Tb',   297.84, 'K','K')
	Tc=DummyUnitsScannable(  'Tc',   3.15,   'K','K')
	Td=DummyUnitsScannable(  'Td',   3.15,   'K','K')


try:
	### Struck ###
	localStation_print("   creating new Stuck counter-timer object, t    Type help t")
	t=Struck2('t',"BL16I-EA-DET-01:SCALER",[3])
	t.setname(3,'APD'); t.setname(4,'Scintillator1'); t.setname(5,'APD2'); t.setname(9,'SCA1'); t.setname(10,'SCA2'); t.setname(11,'SCA3'); t.setname(15,'IC2');

	### Wait for beam ###
	localStation_print("   creating checkbeam scannables")
	checkbeamcurrent=WaitForBeamPDClass('BeamOK',rc,10)  # @UndefinedVariable
#	checkbeam=WaitForBeamPDClass('BeamOK',ic1monitor,1); checkbeam.command_string='fill_if_needed()'	#fill cryocooler vessel while waiting for beam
	checkbeam=WaitForBeamPDClass('BeamOK',ic1monitor,1); checkbeam.command_string='None'
	timetoinjection=TimeToMachineInjectionClass('TimeToInjection','SR-CS-FILL-01:COUNTDOWN', 'sec', '%.1f')
	waitforinjection=WaitForInjectionPDClass('waitforinjection',timetoinjection, 5, 5)

	### x1trig and x2trig ###
	localStation_print("Creating x1trig and x2trig")
	x1trig = ToggleBinaryPvAndWait('x1trig', 'BL16I-EA-USER-01:BO1')
	x1trig.triggerLength=0.1
	x2trig = ToggleBinaryPvAndWait('x2trig', 'BL16I-EA-USER-01:BO2')
	x2trig.triggerLength=0.2
	#ppa* & ppb* scannables moved to localStationStaff.py

except:
	localStation_exception("creating strick, checkbeam and x trig scannables")


### Homebrew positioners
localStation_print('Creating positioners with preset values: mono_screens, mono_diode')
mono_screens=MoveScalarPDsToPresetValuesClass('mono_screens',[d3a,d3d,d4a,d4d,d5a,d5d],[[90,33,20,33,20,35],[60,0,20,0,20,0]],help='0=all out; 1=fluo foils and d3a Al in, rest out')  # @UndefinedVariable
mono_diode=MoveScalarPDsToPresetValuesClass('mono_diodes',[d3a,d3d,d4a,d4d,d5a,d5d],[[90,33,20,33,20,35],[90,76.3,20,33,20,35],[90,33,20,75.5,20,35],[90,33,20,33,20,76.5]],help='0=all out; 1=d3d diode in, 2=d4d diode in; 3=d5diode in')  # @UndefinedVariable

### Homebrew groups
localStation_print("Creating OD current amplifier monitors")
run("localStationScripts/startup_currents")
run("localStationScripts/startup_currents2")
sleep(1)


###  Serial devices: Ace, X2000
if installation.isLive():
	localStation_print("   Creating raw serial devices for x2000 and Ace cards")
	try:
		acedict = {'reset':"RESET",'ver':"VER",'help':"HELP",'tlvl':"TLVL",'sout':"SOUT",'sca':"SCA",'alcur':"ALCURR",'alarm':"ALARM",'hcurr':"HCURR",'scaps':"OUT",'hvolt':"HVOLT",'hvmon':"HVMON",'info':"INFO",'ht':"HTEMP"}
		ace1=ace("BL16I-EA-DET-04:asyn",acedict)
		ace2=ace("BL16I-EA-SPARE-05:asyn",acedict)

		if False: # Has not been used for years
			localStation_print("Creating x2000sca & x2003 scannables")
			x2000dict={'gain' : ":INP0:GAIN",'reset':"*RST0",'scaupp' : ":SENS0:SCA:UPP", 'scalow' : ":SENS0:SCA:LOW",'pkt' : ":SENS0:PKT",'volt' : ":SOUR0:VOLT",'sat' : ":SENS0:SAT",'fail' : ":SENS0:HVFAIL"}
			x2000sca=x2000scaClass('X2000 sca1',"%4.3f",x2000,"cts")
			x2003sca=x2000scaClass('X2003 sca1',"%4.3f",x2003,"cts")
			x2003=x2000class("BL16I-EA-DET-03:asyn","\\006",x2000dict)
			x2000=x2000class("BL16I-EA-DET-05:asyn","\\006",x2000dict)

		localStation_print("Creating Ace scannable: acesca")
		acesca=acesca1('APDsca',"%4.3f",ace1,"V")
		acesca2=acesca1('APDsca2',"%4.3f",ace2,"V")

	except:
		localStation_exception("connecting to Epics for x2000 and Ace cards")


###############################################################################
###                      Monitor kth, delta, kappa                          ###
###############################################################################
localStation_print("Creating more scannables to monitor kth, delta and kap.")
kthshow=ReadPDGroupClass('kthshow',[kth]); kthshow.setLevel(8); #kthshow.setExtraNames(['kthshow']);kthshow.setOutputFormat(['%.6f']) @UndefinedVariable
delshow=ReadPDGroupClass('delshow',[delta]); delshow.setLevel(8); #delshow.setExtraNames(['delshow']);delshow.setOutputFormat(['%.6f'])
kapshow=ReadPDGroupClass('kapshow',[kap]); kapshow.setLevel(8); #kapshow.setExtraNames(['kapshow']);kapshow.setOutputFormat(['%.6f']) @UndefinedVariable

if installation.isLive():
	localStation_print("Creating kth_read and delta_read")
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
import beamline_info as BLi #@UnusedImport - contains energy and wavelength
run("localStationScripts/startup_energy_related")
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
	run("localStationScripts/OptimizePeak") #--> ptimizePeak, OP2, OP3 commands



###############################################################################
###                              Set user limits                            ###
###############################################################################
import limits
reload(limits)
from limits import * #@UnusedWildImport
limits.ROOT_NAMESPACE = globals()
localStation_print("Setting user limits (running ConfigureLimits.py)")
try:
	run("localStationScripts/ConfigureLimits")
except:
	localStation_exception("configuring limits")



###############################################################################
###                             Configure Pilatus                           ###
###############################################################################
from scannable.detector.DetectorWithShutter import DetectorWithShutter
from scannable.pilatus import PilatusThreshold, PilatusGain



### 2m ###
if USE_PIL2:
	localStation_print("Configuring pilatus 2 (2m)")
	global pilatus2, pilatus2_hardware_triggered, pilatus2_for_snaps
	try:
		#pil2mdet = EpicsPilatus('pil2mdet', 'BL16I-EA-PILAT-02:','/dls/i16/detectors/im/','test','%s%s%d.tif')
		pil2mdet = pilatus2
		_pilatus2_counter_monitor = Finder.find("pilatus2_plugins").get('pilatus2_counter_monitor')

		#pil2m = SwitchableHardwareTriggerableProcessingDetectorWrapper('pil2m',
		pil2m = NxProcessingDetectorWrapper('pil2m',
			pilatus2,
			pilatus2_hardware_triggered,
			pilatus2_for_snaps,
			[],
			panel_name_rcp='Pilatus',
			toreplace=None,
			replacement=None,
			iFileLoader=PilatusTiffLoader,
			fileLoadTimout=60,
			returnPathAsImageNumberOnly=True,
			array_monitor_for_hardware_triggering = _pilatus2_counter_monitor)
		pil2m.processors=[DetectorDataProcessorWithRoi('max', pil2m, [SumMaxPositionAndValue()], False)]
		pil2m.printNfsTimes = True
		pil2m.display_image = True
		pil2ms = DetectorWithShutter(pil2m, x1, X1_DELAY)
	except:
		localStation_exception("configuring pilatus 2 (2m)")
else:
	localStation_print("Not configuring pilatus 2 (2m)")

### 100k ###
if USE_PIL1:
	localStation_print("Configuring pilatus 1 (100k)")
	global pilatus1, zebrapil1, pilatus1_for_snaps, pilatus1_hardware_triggered
	try:
		pil100kdet = pilatus1
		_pilatus1_counter_monitor = Finder.find("pilatus1_plugins").get('pilatus1_counter_monitor')

		#pil100k = SwitchableHardwareTriggerableProcessingDetectorWrapper('pil100k',
		pil100k = NxProcessingDetectorWrapper('pil100k',
			pilatus1,
			zebrapil1,
			pilatus1_for_snaps,
			[],
			panel_name_rcp='Pilatus',
			toreplace=None,
			replacement=None,
			iFileLoader=PilatusTiffLoader,
			fileLoadTimout=60,
			returnPathAsImageNumberOnly=True,
			array_monitor_for_hardware_triggering = _pilatus1_counter_monitor)
		pil100k.processors=[DetectorDataProcessorWithRoi('max', pil100k, [SumMaxPositionAndValue()], False)]
		pil100k.printNfsTimes = False
		pil100ks = DetectorWithShutter(pil100k, x1, X1_DELAY)
		pil_tmp = pil100k
		pils_tmp = pil100ks
		#pil100kvrf=SingleEpicsPositionerSetAndGetOnlyClass('P100k_VRF','BL16I-EA-PILAT-01:VRF','BL16I-EA-PILAT-01:VRF','V','%.3f',help='set VRF (gain) for pilatus\nReturns set value rather than true readback\n-0.05=very high\n-0.15=high\n-0.2=med\n-0.3=low')
		#pil100kvcmp=SingleEpicsPositionerSetAndGetOnlyClass('P100k_VCMP','BL16I-EA-PILAT-01:VCMP','BL16I-EA-PILAT-01:VCMP','V','%.3f',help='set VCMP (threshold) for pilatus\nReturns set value rather than true readback\n0-1 V')
		#pil100kgain=SingleEpicsPositionerSetAndGetOnlyClass('P100k_gain','BL16I-EA-PILAT-01:Gain','BL16I-EA-PILAT-01:Gain','','%.3f',help='set gain for pilatus\nReturns set value rather than true readback\n3=very high\n2=high\n1=med\n0=low')
		#pil100kthresh=SingleEpicsPositionerSetAndGetOnlyClass('P100k_threshold','BL16I-EA-PILAT-01:ThresholdEnergy','BL16I-EA-PILAT-01:ThresholdEnergy','','%.0f',help='set energy threshold for pilatus (eV)\nReturns set value rather than true readback')

		pil100kthresh = PilatusThreshold('pil100kthresh', pilatus1_hardware_triggered.getCollectionStrategy().getAdDriverPilatus())
		pil100kgain = PilatusGain('pil100kgain', pilatus1_hardware_triggered.getCollectionStrategy().getAdDriverPilatus())
	except:
		localStation_exception("configuring pilatus 1 (100k)")
else:
	localStation_print("Not configuring pilatus 1 (100k)")

if USE_PIL3:
	if LocalProperties.get("gda.data.scan.datawriter.dataFormat") == u'NexusScanDataWriter':
		global pil3_100k
		with overwriting:  # @UndefinedVariable
			pil3 = pil3_100k  # @UnusedVariable
		localStation_warning("pil3 = NXDetector")
	else:
		from detector_wrappers.pilatus_instances import pil, pil3,pil3_100k, pil3_100kgain, pil3_100ks, pil3_100kthresh, pil3s, pils  # @UnusedImport
		localStation_warning("pil3 = NXProcessingDetectorWrapper")
else:
	localStation_print("Not configuring pilatus 3 (100k)")

from autoRangeDetector import AutoRangeDetector
from pv_scannable_utils import createPVScannable

### cam2 ###
localStation_print("Configuring cor (cam2)")
try:
	global cam2, cam2_for_snaps
	cor = SwitchableHardwareTriggerableProcessingDetectorWrapper('cor',
		cam2,
		None,
		cam2_for_snaps,
		[],
		panel_name_rcp='Plot 1',
		fileLoadTimout=60,
		printNfsTimes=False,
		returnPathAsImageNumberOnly=True)

	cor.display_image = True
	corpeak2d = DetectorDataProcessorWithRoi('corpeak2d', cor, [TwodGaussianPeak()])
	cormax2d = DetectorDataProcessorWithRoi('cormax2d', cor, [SumMaxPositionAndValue()])

	#create a version of cor, corpeak2d, cormax2d that performs auto exposure
	# Example: scan kphi -90 270 1. corAuto corAutopeak2d corExpTime
	#To record actual exposure time also add corExpTime
	corAuto = AutoRangeDetector('corAuto',
		cam2,
		None,
		cam2_for_snaps,
		"BL16I-DI-COR-01:",
		[],
		panel_name_rcp='Plot 1',
		fileLoadTimout=60,
		printNfsTimes=False,
		returnPathAsImageNumberOnly=True)

	corAuto.display_image = True
	corAutopeak2d = DetectorDataProcessorWithRoi('corAutopeak2d', corAuto, [TwodGaussianPeak()])
	corAutomax2d = DetectorDataProcessorWithRoi('corAutomax2d', corAuto, [SumMaxPositionAndValue()])

	#create pseudo-device
	#there is a copy of this in epics git epics_script folder.
	createPVScannable( "corExpTime", "BL16I-DI-COR-01:CAM:AcquireTime_RBV", hasUnits=False)
	corExpTime.level=10
except:
	localStation_exception("configuring cor (cam2)")

localStation_print("Configuring cor2")
try:
	global c10, c10_for_snaps
	cor2 = SwitchableHardwareTriggerableProcessingDetectorWrapper('cor2',
		c10,
		None,
		c10_for_snaps,
		[],
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
		panel_name_rcp='Plot 2',
		fileLoadTimout=60,
		printNfsTimes=False,
		returnPathAsImageNumberOnly=True)
	cor2Auto.display_image = True
	cor2Autopeak2d = DetectorDataProcessorWithRoi('cor2Autopeak2d', cor2Auto, [TwodGaussianPeak()])
	cor2Automax2d = DetectorDataProcessorWithRoi('cor2Automax2d', cor2Auto, [SumMaxPositionAndValue()])
	createPVScannable( "cor2ExpTime", "BL16I-DI-DCAM-10:CAM:AcquireTime_RBV", hasUnits=False)
	cor2ExpTime.level=10
except:
	localStation_exception("configuring cor2")

localStation_print("Configuring xeye")
try:
	xeye = SwitchableHardwareTriggerableProcessingDetectorWrapper('xeye',
		_xeye,
		None,
		_xeye_for_snaps,
		[],
		panel_name_rcp='Plot 2',
		fileLoadTimout=60,
		printNfsTimes=False,
		returnPathAsImageNumberOnly=True)

	xeye.display_image = True
	xeyemax2d = DetectorDataProcessorWithRoi('xeyemax2d', xeye, [SumMaxPositionAndValue()])
	xeyepeak2d = DetectorDataProcessorWithRoi('xeyepeak2d', xeye, [TwodGaussianPeak()])

	xeye.processors=[DetectorDataProcessorWithRoi('peak', xeye, [SumMaxPositionAndValue(), TwodGaussianPeakWithCalibration()], False)]
	xeye.processors[0].processors[1].setScalingFactors(0.0014, 0.0014)
except:
	localStation_exception("configuring xeye")

localStation_print("Configuring zylar")
try:
	zylar = SwitchableHardwareTriggerableProcessingDetectorWrapper('zylar',
		_zylar,
		None,
		_zylar_for_snaps,
		[],
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
except:
	localStation_exception("configuring zylar")

def wrappedDetector(name, cam_for_scans, cam_for_snaps, display_image=True, sum_last=True, panel_name_rcp='Plot 1'):
	localStation_print("Configuring %s" % name)
	try:
		cam = SwitchableHardwareTriggerableProcessingDetectorWrapper(name,
			cam_for_scans,
			None,
			cam_for_snaps,
			[],
			panel_name_rcp=panel_name_rcp,
			fileLoadTimout=60,
			printNfsTimes=False,
			returnPathAsImageNumberOnly=True)

		cam.display_image = display_image
		if sum_last:
			cam.processors=[DetectorDataProcessorWithRoi('peak', cam, [TwodGaussianPeakWithCalibration(), SumMaxPositionAndValue()], False)]
			cam.processors[0].processors[0].setScalingFactors(0.0027, 0.00375)
		else:
			cam.processors=[DetectorDataProcessorWithRoi('peak', cam, [SumMaxPositionAndValue(), TwodGaussianPeakWithCalibration()], False)]
			cam.processors[0].processors[1].setScalingFactors(0.0027, 0.00375)
		peak2d = DetectorDataProcessorWithRoi(name+'_peak2d', cam, [TwodGaussianPeak()])
		max2d = DetectorDataProcessorWithRoi(name+'_max2d', cam, [SumMaxPositionAndValue()])
		#cam.processors[0].processors[1].calibrate()

		return cam, peak2d, max2d
	except:
		localStation_exception("configuring %s" % name)

try:
	bpm, bpmpeak2d, bpmmax2d = wrappedDetector("bpm", _bpm1, _bpm1_for_snaps, panel_name_rcp='BPM')
	bpm_no_screen, bpm_no_screen_peak2d, bpm_no_screen_max2d = wrappedDetector("bpm", _bpm1_no_screen, _bpm1_no_screen_for_snaps, panel_name_rcp='BPM')
	cam1, cam1_peak2d, cam1_max2d = wrappedDetector("cam1", _cam1, _cam1_for_snaps, panel_name_rcp='CAM1')
	camd3, camd3_peak2d, camd3_max2d = wrappedDetector("camd3", _camd3, _camd3_for_snaps)
	camd4, camd4_peak2d, camd4_max2d = wrappedDetector("camd4", _camd4, _camd4_for_snaps)
	camd5, camd5_peak2d, camd5_max2d = wrappedDetector("camd5", _camd5, _camd5_for_snaps)
except:
	localStation_exception("configuring cam1, bpm, camd3, camd4 and camd5 cameras")

def wrappedAutoDetector(name, cam_for_scans, cam_for_snaps, auto_range_base_PV, display_image=True, sum_last=True, panel_name_rcp='Plot 2'):
	try:
		cam, cam_peak2d, cam_max2d = wrappedDetector(name, cam_for_scans, cam_for_snaps, display_image, sum_last, panel_name_rcp)
		camAuto = AutoRangeDetector(name+'Auto',
			cam_for_scans,
			None,
			cam_for_snaps,
			auto_range_base_PV,
			[],
			panel_name_rcp=panel_name_rcp,
			fileLoadTimout=60,
			printNfsTimes=False,
			returnPathAsImageNumberOnly=True,
			useOldExposureAutoPVs=False)
		camAuto.display_image = True
		camAutopeak2d = DetectorDataProcessorWithRoi(name+'Autopeak2d', camAuto, [TwodGaussianPeak()])
		camAutomax2d = DetectorDataProcessorWithRoi(name+'Automax2d', camAuto, [SumMaxPositionAndValue()])
		createPVScannable(name+"ExpTime", auto_range_base_PV+"CAM:AcquireTime_RBV", hasUnits=False)

		return cam, cam_peak2d, cam_max2d, camAuto, camAutopeak2d, camAutomax2d
	except:
		localStation_exception("configuring %s" % name+"Auto")

global camlab84_for_scans, camlab84_for_snaps, camlab84ExpTime, camlab84b_for_scans, camlab84b_for_snaps, camlab84bExpTime

with overwriting:  # @UndefinedVariable

	try:
		camlab84, camlab84_peak2d, camlab84_max2d, camlab84Auto, camlab84Autopeak2d, camlab84Automax2d = wrappedAutoDetector(
			"camlab84", camlab84_for_scans, camlab84_for_snaps, "LA84R-DI-DCAM-01:", panel_name_rcp='Plot 1')
	except:
		localStation_exception("configuring wrapped auto detectors - camlab84")
	
	try:
		camlab84b, camlab84b_peak2d, camlab84b_max2d, camlab84bAuto, camlab84bAutopeak2d, camlab84bAutomax2d = wrappedAutoDetector(
			"camlab84", camlab84b_for_scans, camlab84b_for_snaps, "LA84R-DI-DCAM-03:", panel_name_rcp='Plot 2')
	except:
		localStation_exception("configuring wrapped auto detectors - camlab84b")
	
###############################################################################
###                              Configure andor                            ###
###############################################################################
if Finder.find("andor1"):
	localStation_print("Configuring andor")
	from uk.ac.diamond.scisoft.analysis.io import TIFFImageLoader
	# the andor has no hardware triggered mode configured. This class is used to hijak its DetectorSnapper implementation.
	try:
		global andor1, andor1_for_snaps
		andor = SwitchableHardwareTriggerableProcessingDetectorWrapper('andor',
									andor1,
									None,
									andor1_for_snaps,
									[],
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
		andor_trigger_output_enable()
	except:
		localStation_exception("configuring andor. Is IOC running?")
else:
	localStation_warning("finding andor detector. Please restart the GDA servers with the andor transient device enabled, if you need it.")

localStation_print("-------------------------------MEDIPIX INIT---------------------------------------")
try:

	#visit_setter.addDetectorAdapter(FileWritingDetectorAdapter(_medipix_det, create_folder=True, subfolder='medipix'))
	'''
	medipix = SwitchableHardwareTriggerableProcessingDetectorWrapper('medipix',
																	_medipix,
																	None,
																	_medipix_for_snaps,
																	[],
																	panel_name_rcp='Plot 1',
																	iFileLoader=PilatusTiffLoader,
																	fileLoadTimout=60,
																	printNfsTimes=False,
																	returnPathAsImageNumberOnly=True)
	medipix.disable_operation_outside_scans = False # True
	# medipix_threshold0_kev = SetPvAndWaitForCallbackWithSeparateReadback('medipix_threshold_kev', 'BL16I-EA-DET-02:Merlin:ThresholdEnergy0', 'BL16B-EA-DET-02:Merlin:ThresholdEnergy0_RBV', 10)
	#pil100kdet = EpicsPilatus('pil100kdet', 'BL16I-EA-PILAT-01:','/dls/b16/detectors/im/','test','%s%s%d.tif')
	#pil100k = ProcessingDetectorWrapper('pil100k', pil100kdet, [], toreplace=None, replacement=None, iFileLoader=PilatusTiffLoader, fileLoadTimout=15, returnPathAsImageNumberOnly=True)
	#pil100k.processors=[DetectorDataProcessorWithRoi('max', pil100k, [SumMaxPositionAndValue()], False)]
	#pil100k.printNfsTimes = True

	medipix.processors=[DetectorDataProcessorWithRoi('max', medipix, [SumMaxPositionAndValue()], False)]
	'''
	pass
except gda.factory.FactoryException as e:
	localStation_exception("connecting to medipix (FactoryException)", e)
except java.lang.IllegalStateException as e:
	localStation_exception("connecting to medipix (IllegalStateException)", e)
except:
	localStation_exception("connecting to medipix (Other)")
localStation_print("-------------------------------MEDIPIX INIT COMPLETE---------------------------------------")


localStation_print("-------------------------------MERLIN INIT---------------------------------------")
from detector_wrappers.merlin_instances import merlin, merlins  # @UnusedImport
localStation_print("-------------------------------MERLIN INIT COMPLETE---------------------------------------")
###############################################################################
###                              Configure Xmap                            ###
###############################################################################
if USE_XMAP:
	from scannable.detector.dxp import DxpSingleChannelRoiOnly
	Sxmap = DxpSingleChannelRoiOnly('xmap', 'BL16I-EA-XMAP-01:')
###############################################################################
###                             Configure firecam                           ###
###############################################################################

###############################################################################
###                           Theta with offset eta                         ###
###############################################################################

localStation_print("Creating scannables with offsets(th is eta with offset eta_offset")
from pd_offsetAxis import OffsetAxisClass
# e.g. th is eta with eta_off as offset
th=OffsetAxisClass('th',eta,eta_offset,help='eta device with offset given by eta_offset. Use pos eta_offset to change offset')
thv=OffsetAxisClass('thv',mu,mu_offset,help='mu device with offset given by mu_offset. Use pos mu_offset to change offset')

###############################################################################
###                                Metadata                                 ###
###############################################################################
localStation_print("Configuring metadata capture")

run('localStationScripts/Sample_perpMotion')

try:
	diffractometer_sample_scannables = [delta, eta, chi, phi, gam, mu, hkl]
	if not USE_DIFFCALC:
		xtal_info=ReadPDGroupClass('xtal_info',[xtalinfo])

	diffractometer_sample_scannables += [hklverbose.psi, hklverbose.alpha, hklverbose.beta, hklverbose.betain, hklverbose.betaout]
	diffractometer_sample_scannables += [en]
	diffractometer_sample_scannables += [kphi]  # @UndefinedVariable

	diffractometer_sample_scannables += [azihkl]
	diffractometer_sample_scannables += [delta_axis_offset]

	d=diffractometer_sample=ReadPDGroupClass('diffractometer_sample', diffractometer_sample_scannables)

	source=ReadPDGroupClass('source',[rc, idgap, uharmonic])  # @UndefinedVariable
	beamline_slits=ReadPDGroupClass('beamline_slits',[s1xcentre,s1xgap,s1ycentre, s1ygap,s2xcentre,s2xgap,s2ycentre, s2ygap,s3xcentre,s3xgap,s3ycentre, s3ygap,s4xcentre,s4xgap,s4ycentre, s4ygap, shtr3x,shtr3y])  # @UndefinedVariable
	jjslits=ReadPDGroupClass('jjslits',[s5xgap, s5xtrans, s5ygap, s5ytrans, s6xgap, s6xtrans, s6ygap, s6ytrans, s7xgap, s7xtrans, s7ygap, s7ytrans])  # @UndefinedVariable
	mirror1=ReadPDGroupClass('mirror1',[m1pitch, m1x, m1y, m1roll, m1yaw, m1piezo])  # @UndefinedVariable
	mirror2=ReadPDGroupClass('mirror2',[m2pitch, m2x, m2y, m2roll, m2yaw,m2bender])  # @UndefinedVariable
	mirror3=ReadPDGroupClass('minimirrors',[m3x, m4x, m3pitch, m4pitch])
	mirrors=ReadPDGroupClass('mirrors',[mirror1, mirror2,mirror3])
	###temporarilily remove cryolevel due to controls problem - go back to original when working
	#mono=ReadPDGroupClass('Mono',[en,bragg,dcmpitch, dcmfinepitch, perp, dcmlat,dcmroll1, dcmroll2,T1dcm, T2dcm,cryolevel])
	mono=ReadPDGroupClass('mono',[en,bragg,dcmpitch, dcmfinepitch, perp, dcmlat,dcmroll1, dcmroll2,T1dcm, T2dcm])  # @UndefinedVariable
	###
	pa=ReadPDGroupClass('pa',[stokes, tthp, thp, zp, dettrans, mtthp])  # @UndefinedVariable
	#pp=ReadPDGroupClass('pp',[ppth, ppx, ppy, ppchi])
	#positions=ReadPDGroupClass('positions',[sx,sy,sz,base_y,base_z,ytable, ztable])
	positions=ReadPDGroupClass('positions',[sx,sy,sz,sperp, spara, base_y,base_z,ytable, ztable])# sperp spara added SPC 3/2/12 @UndefinedVariable
	#xps2=ReadPDGroupClass('xps2',[gam,delta,mu,kth,kap,kphi])
	dummypd=ReadPDGroupClass('dummypd',[x,y,z])
	kbm_offsets=ReadPDGroupClass('kbm_offsets',[vmtrans_offset, hmtrans_offset, vmpitch_offset, hmpitch_offset, kbmx_offset, kbmroll_offset])
	try:
		xps3=ReadPDGroupClass('xps3',[xps3m1, xps3m2, xps3m3, xps3m4, xps3m5, xps3m6])
	except NameError, e:
		pass # XPS3 is often not present
	frontend=ReadPDGroupClass('frontend',[frontendx, frontendy])
	gains_atten=ReadPDGroupClass('gains_atten',[atten, diode.gain, ic1monitor.gain, ic2.gain])
	try:
		temperature_controller=ReadPDGroupClass('temperature_controller',[tset, Ta, Tb, Tc, Td, Tsample, Theater, Tchannel])
	except NameError:
		temperature_controller=ReadPDGroupClass('temperature_controller',[]) # LS340 is often not present
	#minimirrors=ReadPDGroupClass('minimirrors',[m3x, m4x, m3pitch, m4pitch]) #added to metadata as mirror3
	"""
	offsets=ReadPDGroupClass('offsets',[m1y_offset, m2y_offset, base_z_offset, ztable_offset, m2_coating_offset, idgap_offset, kbm_offsets])
	"""
	offsets=ReadPDGroupClass('offsets',[m1y_offset, m2y_offset, base_z_offset, ztable_offset, m2_coating_offset, idgap_offset, ppy_offset])
	#mt6138=ReadPDGroupClass('6138', [xps3m1, xps3m2])
	#adctab=ReadPDGroupClass('adctab',[adch,adcv])
	#add_default(adctab)
	#fzp=ReadPDGroupClass('FZP_motors',[zp1x, zp1y, zp1z, zp2x, zp2y, zp2z, xps3m1, xps3m2, micosx, micosy])
except:
	localStation_exception("configuring metadata capture")

def meta_std(full=True):
	try:
		meta_scannable_names = ['dummypd', 'mrwolf', 'diffractometer_sample', 'sixckappa',
							'source', 'pa', 'mirrors', 'beamline_slits', 'mono']
		if not USE_DIFFCALC:
			meta_scannable_names += ['xtalinfo']
		if full:
			meta_scannable_names += ['jjslits', 'PPR', 'positions', 'gains_atten', 'tcontrol', 'temperature_controller', 'offsets',
									'ppy', 'ppx', 'ppyaw', 'pppitch', 'ppchitemp', 'ppth1temp', 'ppz1temp', 'ppth2temp', 'ppz2temp',
                                    'p2', 'pa_crystal', 'pa_detector', 'pol', 'stokes_pars', 'pa_jones', 'Energy', 'ubMeta']

		addedInSpring = ['sixckappa', 'delta_axis_offset'] # See /i16-config/servers/main/_common/nxmetadata.xml

		meta_scannable_names = [ _x for _x in meta_scannable_names if _x != None and not _x in addedInSpring ]

		from gdascripts.scannable.metadata import _is_scannable

		if USE_NEXUS_METADATA_COMMANDS:
			try:
				meta_clear_alldynamical()
			except:
				pass
			localStation_print("Adding metadata:")
			for item in meta_scannable_names:
				if _is_scannable(jythonNameMap[item]):
					meta_add(jythonNameMap[item])
					localStation_print("  %s added" % item)
				else:
					localStation_print("  %s was not scannable and could not be entered as metadata" % item)
		else:
			meta.add(*[jythonNameMap[item] for item in meta_scannable_names])

		meta.prepend_keys_with_scannable_names = False
		mds=meta
	except NameError, e:
		# diffractometer_sample,xtalinfo are not yet available with diffcalc
		print "Error trying to setup the metadata, metadata will not be properly written to files. Namespace error was: ",str(e)
		localStation_exception("trying to set up metadata, metadata will not be properly written to files.", e)

def meta_minimal():
	meta_std(False)

alias("meta_std")
alias("meta_minimal")

# Define a function which turns any scannable into one which doesn't pause the
# scan if it's moving.
from gda.device.scannable import PassthroughScannableMotionUnitsDecorator

class AsyncMonitor(PassthroughScannableMotionUnitsDecorator):

	def waitWhileBusy(self):
		return

	def stop(self):
		return

def asyncMonitor(scannable):
	return AsyncMonitor(scannable)

alias(asyncMonitor)

class AsyncScannable(PassthroughScannableMotionUnitsDecorator):

	def __init__(self, scannable, targetPosition):
		super(AsyncScannable, self).__init__(scannable)
		self.targetPosition = targetPosition

	def atScanStart(self):
		self.asynchronousMoveTo(self.targetPosition)
		super(AsyncScannable, self).atScanStart()

	def atScanEnd(self):
		self.stop()
		super(AsyncScannable, self).atScanEnd()

	def atCommandFailure(self):
		self.stop()
		super(AsyncScannable, self).atCommandFailure()

	def waitWhileBusy(self):
		return

	def stop(self):
		return

def asyncScannable(scannable, targetPosition):
	return AsyncScannable(scannable, targetPosition)

alias(asyncScannable)
###Default Scannables###
try:
	for scannable_name in SIXC_SCANNABLEMOTOR_NAMES:
		add_default(asyncMonitor(jythonNameMap[scannable_name]))
	add_default(jythonNameMap["delta_axis_offset"])
except:
	localStation_exception("setting default scannables")

###############################################################################
###                          Recent developments                            ###
###############################################################################
beamline = Finder.find("Beamline")

#run('Sample_perpMotion') #move to before metadata

run('localStationScripts/Struck_with_fastshutter')

#ADC optics table XMAP
run('localStationScripts/pd_adc_table')

run('localStationScripts/enable_xps_gda.py')

from edgeDetectRobust import edgeDetectRobust as edge #@UnusedImport
from edgeDetectEnergy import eEdge as eedge #@UnusedImport

run('localStationScripts/rePlot')

run('localStationScripts/whynobeam')

localStation_print("New minimirrors function - type help minimirrors")
run('localStationScripts/minimirrors')

if USE_DIFFCALC == False:
	localStation_print("run possiblehkl_new")
	run('localStationScripts/possiblehkl_new')
	localStation_print("run Space Group Interpreter")
	run('localStationScripts/SGinterpreter')

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
# The Detector regions of interest are now defined in the localStationStaff.py user script
###############################################################################

# This depends on lcroi
run('localStationScripts/FlipperClass')

try:
	run('scannable/pd_rs_remap_autorun')
except:
	localStation_exception("running pd_rs_remap_autorun")

###############################################################################
###                             Complete Localstation                       ###
###############################################################################

# Restore data directory
setDatadirPropertyFromPersistanceDatabase()
showlm()
from gda.jython import InterfaceProvider
print "======================================================================"
localStation_print("Current data directory: %r" % InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir"))
print "======================================================================"
from gda.device.motor import DummyMotor
if USE_DUMMY_IDGAP_MOTOR or type(idgap.getMotor())==DummyMotor:
	print "!"*80
	localStation_warning("finding idgap motor, using dummy idgap")
	idgap.asynchronousMoveTo(6.1511) # Based on scan 971324
	print "!"*80

if type(bragg.getMotor())==DummyMotor:
	print "!"*80
	localStation_warning("finding bragg motor, using dummy bragg")
	bragg.asynchronousMoveTo(-16.189525) # Based on scan 971324

if type(perp.getMotor())==DummyMotor:
	print "!"*80
	localStation_warning("finding perp motor, using dummy perp")
	perp.asynchronousMoveTo(40.54095) # Based on scan 971324

print "======================================================================"

run('diffractometer/pid.py')
###############################################################################
###                           Diff - xpsgather                              ###
###############################################################################
try:
	from scannable.xpsdatagathering import ScannableXPSDataGatherer
	xpsgather = ScannableXPSDataGatherer('xpsgather', pvroot='BL16I-CS-IOC-15:XPSG:')
except:
	localStation_exception("creating xps data gathering scannable")

###############################################################################
###                           Defaults - keep at end                        ###
###############################################################################
add_default(meta)
add_default(atime)
add_default(atimetwo)
add_default(ic1monitor)
add_default(rc)  # @UndefinedVariable
add_default(pptTempMonitor)
if installation.isLive():
	add_default(waitforinjection)
	waitforinjection.due=5	#wait for injection if due in this period of time (sec)

###############################################################################
###                Optionally switch pilatus to CBF writing                 ###
###############################################################################
from scannable.detector import pilatuscbfswitcher #@UnusedImport
# NOTE: state will be stored across calls to reset_namespace
#pilatuscbfswitcher.set(pil2m, 'cbf')


###############################################################################
###                           Run beamline scripts                          ###
###############################################################################


run('localStationScripts/bpm')
run('localStationScripts/align1')
run('localStationScripts/select_and_move_detector')
run('localStationScripts/showdiff')
run('localStationScripts/showdiff_new')
# bpmroi1 is now defined in the localStationStaff.py user script
#run('pd_searchref2') #put at the end as it gave some errors
run('localStationScripts/pd_read_list')	#to make PD's that can scan a list
run('localStationScripts/pd_function')	#to make PD's that return a variable
#run('PDFromFunctionClass')#to make PD's that return the value of a function  - already run!

print "==========================="
localStation_print("Setting up continuous scans")
run("localStationScripts/setup_cvscan")
localStation_print("Continuous scans setup")
print "==========================="

if installation.isLive():
	try:
		run("localStationScripts/startup_pie725")
	except:
		localStation_exception("running localStationScripts/startup_pie725 script")

if USE_NEXUS:
	try:
		class TextsScannable (ScannableBase):
			def __init__(self, name, contents):
				self.name = name
				self.contents = contents
		
			def getPosition(self):
				return self.contents
		
			def rawAsynchronousMoveTo(self, contents):
				self.contents = contents
		
			def isBusy(self):
				return False
		
		_title = TextsScannable('title', 'Scan of sample with GDA')
		
		def title(title = None):
			if not title == None:
				_title.rawAsynchronousMoveTo(title)
			return _title.getPosition()
		
		alias(title)
		
		_sample= TextsScannable('sample', 'Default Sample')
		
		def sample(sampleName = None):
			if not sampleName == None:
				_title.rawAsynchronousMoveTo(title)
			return _title.getPosition()
		
		alias(sample)

		run("datawriting/i16_nexus")
	except:
		localStation_exception("running datawriting/i16_nexus script")
else:
	#clear extenders possible configured already
	writerMap = Finder.getFindablesOfType(gda.data.scan.datawriter.DefaultDataWriterFactory)
	ddwf = writerMap.get("DefaultDataWriterFactory")
	for dwe in ddwf.getDataWriterExtenders():
		ddwf.removeDataWriterExtender(dwe)

if USE_ROCKING_SCANNABLES:
	try:
		from dls_scripts.scannable.RockerScannable import RockerScannable  # @UnresolvedImport
		rocker = RockerScannable('rocker')
		localStation_print("Configured rocker scannable")

		from dls_scripts.scannable.ContinuouslyRockingScannable import ContinuouslyRockingScannable  # @UnresolvedImport
		kphirock = ContinuouslyRockingScannable('kphirock', scannable = kphi)  # @UndefinedVariable
		kphirock.verbose = False

		chirock = ContinuouslyRockingScannable('chirock', scannable = chi)
		chirock.verbose = False

		etarock = ContinuouslyRockingScannable('etarock', scannable = eta)
		etarock.verbose = False

		localStation_print("Configured kphirock, chirock and etarock")
		localStation_print("To start rocking eta around 58 plus and minus 1 degree use")
		localStation_print("  pos etarock [ 58 1 ]")
		localStation_print("To stop rocking eta use")
		localStation_print("  pos etarock [ 58 0 ]")
		print "e.g."

	except:
		localStation_exception("setting up kphirock, chirock or etarock")
else:
	localStation_print("Not configuring kphirock, chirock or etarock")

try:
	from sz_cryo import szCryoCompensation
	cryodevices={'800K':[4.47796541e-14, -7.01502180e-11, 4.23265147e-08, -1.24509237e-05, 8.48412284e-04, 1.00618264e+01]
				,'4K':[-1.43421764e-13, 1.05344999e-10, -1.68819096e-08, -5.63109884e-06, 3.38834427e-04, 9.90716891]
				,'4K22':[-4.946860907921413e-13, 4.204591199936939e-10, -1.215261111328385e-07, 9.803917323445766e-06, -0.0004902951460550646, 14.225861061835865]
				}
	szc=szCryoCompensation("szc", sz, cryodevices, help="Sample height with temperature compensation.\nEnter, for example "+  # @UndefinedVariable
		"szc.calibrate('4K22',Ta) \nto calibrate using the 2022 commissioned 4K cryo and channel Ta,\n"+
		"szc.calibrate('4K',Ta) \nto calibrate using the older 4K cryo and channel Ta or\n"+
		"szc.calibrate('800K',Tc) \nfor the cryofurnace.")
except:
	localStation_exception("setting up szc")

if USE_SMARGON and Finder.find("sgphi"):
	try:
		exec("del hkl")
		exec("del euler")
		run("localStationScripts/SmargonTopClass")
		from diffractometer.scannable import HklSmargon,EulerSmargonPseudoDevice
		reload(HklSmargon)
		reload(EulerSmargonPseudoDevice)
		exec('phi =sgphi')
		exec('eta =sgomega')
		exec('chi =sgchi')
		BLobjects.my_smarchi =chi
		BLobjects.my_smaromega = eta
		BLobjects.my_smarphi =phi
		euler= EulerSmargonPseudoDevice.EulerianPseudoDevice("euler",san,kmu,kdelta,kgam)  # @UndefinedVariable
		hkl = HklSmargon.HklSmargon("hkl",euler,rs,CA,EDi,az)

		localStation_print("Smargon script was successful")
	except:
		localStation_exception("setting up smargon")
elif USE_SMARGON:
	localStation_warning("checking that smargon devices are available. Please set USE_SMARGON=False or restart the GDA servers with the smargon transient device enabled")
elif Finder.find("sgphi"):
	localStation_warning("checking that smargon devices are unavailable. Please set USE_SMARGON=True or restart the GDA servers with the smargon transient device disabled")
else:
	localStation_print("Not configuring smargon")

localStation_print("Setting diffcalc ubmeta scannable")
try:
	from gda.device.scannable import ScannableBase
	from __builtin__ import False
	try:
		import json
	except ImportError:
		import simplejson as json

	from diffcalc.ub.calcstate import UBCalcStateEncoder

	class UBCalcMetadata (ScannableBase):
		def __init__(self, name):
			self.name = name

		def getPosition(self):
			if ubcalc is not None or ubcalc._state is not None:
				return json.dumps(ubcalc._state, cls=UBCalcStateEncoder)
			return None

		def rawAsynchronousMoveTo(self, position):
			pass

		def isBusy(self):
			return False

	ubMeta = UBCalcMetadata("ubMeta")
except:
	localStation_exception("setting diffcalc ubmeta scannable")

# Define offset between pilatus detector and analyser crystal
do.pil = 8.8

# Setting the standard metadata scannables & protecting all defined scannables should be last
meta_std()

def protect_all_scannables():
	def unprotected_scannables():
		return [i for i in InterfaceProvider.getJythonNamespace().getAllNamesForType(Scannable) if not overwriting.isProtected(i)]  # @UndefinedVariable

	scannables_to_protect = unprotected_scannables()
	[overwriting.protect(i) for i in scannables_to_protect]  # @UndefinedVariable

	if scannables_to_protect:
		print "Scannables now protected: %r" % scannables_to_protect

alias("protect_all_scannables")

if installation.isLive():
	print "*"*80
	localStation_print("Attempting to run localStationStaff.py from user scripts directory")
	print "*"*80
	try:
		run("localStationStaff")
		localStation_print("localStationStaff.py completed.")
	except java.io.FileNotFoundException, e:
		localStation_exception("running localStationStaff user script! See above for details.", e)
	except:
		localStation_exception("running localStationStaff user script! See above for details.")

	print "*"*80
	localStation_print("Attempting to run localStationUser.py from user scripts directory")
	print "*"*80
	try:
		run("localStationUser")
		localStation_print("localStationUser.py completed.")
	except java.io.FileNotFoundException, e:
		localStation_exception("running localStationUser user script! See above for details.", e)
	except:
		localStation_exception("running localStationUser user script! See above for details.")
else:
	print "*"*80
	try:
		run("dummy/localStationStaff")
		from lab84.initialise_offsets import setup_pil3_centre
		setup_pil3_centre()

	except:
		localStation_exception("running localStationStaff dummy script")

	print "*"*80
	try:
		run("dummy/localStationUser")
	except:
		localStation_exception("running localStationUser dummy script")

print("*"*80)
protect_all_scannables()

protected_commands=["pos","inc","peak","maxval","com","minval","rcen","lcen","range"]
for to_protect in protected_commands :
	overwriting.protect(to_protect)  # @UndefinedVariable

print("-"*100)

from gdascripts.scan.flyscans import flyscannable, FlyScanPositionsProvider, flyscan, setflyscandeadtime, getflyscandeadtime, flyscancn, fscan, fscancn, flyscan_should_wait_for_beam  # @UnusedImport
from scan.miscan import miscan  # @UnusedImport

if localStation_warnings:
	print("\n====================== %r WARNINGS DURING STARTUP WHILE ======================\n%s" % (
		len(localStation_warnings), "\n".join(localStation_warnings)))

if localStation_exceptions:
	print "\n====================== %r ERRORS DURING STARTUP WHILE ======================\n%s" % (
		len(localStation_exceptions), "\n".join(localStation_exceptions))

print("\n======================================================================")
localStation_print("Local Station Script completed")
print("======================================================================")
