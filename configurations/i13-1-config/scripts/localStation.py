import sys
import os
from gdascripts.messages import handle_messages
import gda.factory.FactoryException
import time

from gda.device import Scannable
from gda.jython import Jython
from gda.jython.commands.GeneralCommands import ls_names, alias, vararg_alias
from gda.jython.commands.ScannableCommands import add_default, pos
from gda.device.scannable import ScannableBase
from gda.device.scannable.scannablegroup import ScannableGroup
from i13j_utilities import createScannableFromPV, clear_defaults, isLive
from gda.jython import InterfaceProvider
from gdaserver import ionc_gain, ionc_gainmode, ionc_coupling, f1_crly_mp, m1_strip, optics_zp, eh_shtr, fs
from gdaserver import d4_i, expt_fastshutter_raw, qcm_bragg1, fes1, id_gap, ionc_i, ionc_photonflux, ix, iy, iz
from gdaserver import qcm_energy, s1, s2, s4, s5, s6, s7, sample_lab_x, scope1_turret, t1, t1_pitch, t2

section_sep = "-"*128

class ExperimentShutterEnumPositioner(ScannableBase):
	"""
	Class to handle
	"""
	def __init__(self, name, delegate):
		self.name = name
		self.inputNames = [name]
		self.delegate = delegate
	def isBusy(self):
		return self.delegate.isBusy()
	def rawAsynchronousMoveTo(self,new_position):
		if new_position == "Open":
			self.delegate.asynchronousMoveTo(5.)
		else:
			self.delegate.asynchronousMoveTo(0.)
	def rawGetPosition(self):
		position = self.delegate.getPosition()
		if int(position) == 5:
			return "Open"
		return "Closed"


def ls_scannables():
	ls_names(Scannable)

scansReturnToOriginalPositions=1

from epics_scripts.pv_scannable_utils import createPVScannable, caput, caget, caputStringAsWaveform, ls_pv_scannables
alias("ls_pv_scannables")
alias("caput")
alias("caget")

from gda.factory import Finder
from gda.configuration.properties import LocalProperties
#	from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
import i13j

#import for help
from robots import calcRobotMotors, calcRobotMotorsInverse
from gda.device.lima import LimaCCD
from gda.util import VisitPath

beamline = Finder.find("Beamline")
ring= Finder.find("Ring")
commandServer = InterfaceProvider.getJythonNamespace()
#	import tests.testRunner
#	tests.testRunner.run_tests()

from gda.scan.RepeatScan import create_repscan, repscan
vararg_alias("repscan")

from gdascripts.pd.time_pds import waittimeClass2, showtimeClass, showincrementaltimeClass, actualTimeClass
waittime=waittimeClass2('waittime')
showtime=showtimeClass('showtime')
inctime=showincrementaltimeClass('inctime')
actualTime=actualTimeClass("actualTime")

from i13j_utilities import cfn, csn, nfn, nsn, pwd, nwd
alias("cfn")
alias("csn")
alias("nfn")
alias("nsn")
alias("pwd")
alias("nwd")

from gdascripts.metadata.metadata_commands import setTitle, meta_add, meta_ll, meta_ls, meta_rm
alias("setTitle")
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")
from gda.data.scan.datawriter import NexusDataWriter
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop")

from gdascripts.watchdogs.watchdogs import enableWatchdogs, disableWatchdogs, listWatchdogs
alias("enableWatchdogs")
alias("disableWatchdogs")
alias("listWatchdogs")

import help_cmds
if not LocalProperties.check("gda.dummy.mode"):
	try:
		import filter_array
		xia_filter=filter_array.filter_array("xia_filter", prefix="BL13J-OP-ATTN-02:", elements=["Cr", "Fe", "Cu", "Nb"])
	except gda.factory.FactoryException, e:
		print "!!!!!!!!!!!!!!!!!!!!!!! problem configuring xia_filter"
		print e
		print "Continuing anyway..."

from flyscan_script import flyscan, flyscannable, WaitForScannableAtLineEnd
vararg_alias("flyscan")
try:
	waitForQcm_bragg1 = WaitForScannableAtLineEnd('waitForQcm_bragg1', qcm_bragg1)
except NameError:
	print "!!!!!!!!!!!!!!!!!!!!!!! qcm_bragg1 not found so could not create waitForQcm_bragg1 "
	print "Continuing anyway..."

try:
	expt_fastshutter = ExperimentShutterEnumPositioner("expt_fastshutter", expt_fastshutter_raw)
except gda.factory.FactoryException, e:
	print "!!!!!!!!!!!!!!!!!!!!!!! problem configuring fast shutter "
	print e
	print "Continuing anyway..."

# Aliases for ion chamber objects
ic1 = ionc_i
ic1_rate = ionc_photonflux

# Define lens as identical to scope1_turret so we can use the same scripts as on Imaging
lens = scope1_turret

import gdascripts.scannable.beamokay
beamok = gdascripts.scannable.beamokay.WaitWhileScannableBelowThresholdMonitorOnly("beamok",ic1,0.1)

from i13j_utilities import WaitWhileScannableBelowThresholdMonitorOnlyWithEmailFeedback
ebeamok = WaitWhileScannableBelowThresholdMonitorOnlyWithEmailFeedback("ebeamok",ic1,0.1,emails=['kaz.wanelik@diamond.ac.uk', 'silvia.cipiccia@diamond.ac.uk', 'darren.batey@diamond.ac.uk'])

from i13j_utilities import ShutterDirector, CAShutterDirector, StepScanMinder, pcotif_minder
#shutter_director = ShutterDirector('shutter_director', fs, delay_after_open_sec=0, delay_after_close_sec=0)

#make ScanPointProvider
import sample_stage_position_provider
two_motor_positions = sample_stage_position_provider.ScanPositionProviderFromFile()
#two_motor_positions.load("/dls_sw/i13-1/software/gda_versions/gda_trunk2/i13-1-config/scripts/tests/sample_stage_position_provider_test.dat",(0.,0.))

imageFitter = Finder.find("imageFitter")
imageStats = Finder.find("imageStats")
imagePlotter = Finder.find("imagePlotter")
imageROI = Finder.find("imageROI")
imageFitter2 = Finder.find("imageFitter2")
imageStats2 = Finder.find("imageStats2")
imagePlotter2 = Finder.find("imagePlotter2")
imageROI2 = Finder.find("imageROI2")
imageFitter3 = Finder.find("imageFitter3")
imageStats3 = Finder.find("imageStats3")
imagePlotter3 = Finder.find("imagePlotter3")
imageROI3 = Finder.find("imageROI3")

import file_converter
#from tests.testRunner import run_tests

#comment out when not connected
#from autocollimator_script import  * #@UnusedWildImport

#run("startup_diffcalc")

#except :
#	exceptionType, exception, traceback = sys.exc_info()
#	handle_messages.log(None, "Error in localStation", exceptionType, exception, traceback, False)

from gdascripts.scannable.beamokay import WaitWhileScannableBelowThresholdMonitorOnly
#comment out when not connected -
#beammonitor=WaitWhileScannableBelowThresholdMonitorOnly("beammonitor", d4_i, 1,1,1)
#beamok=WaitWhileScannableBelowThresholdMonitorOnly("beamok",ic1,0.1)


ix.setInputNames(["ix"])
iy.setInputNames(["iy"])
iz.setInputNames(["iz"])

#stuff for Vortex editor
def vortex(vortexParameterName, outputfile):
	from uk.ac.gda.beans.vortex import VortexParameters
	VortexParameters.writeToXML(XspressParametersToLoad, mll_xmap.getConfigFileName());
	mll_xmap.loadConfigurationFromFile()

alias("vortex")

import scan_aborter
beam_check=scan_aborter.scan_aborter("beam_check",3, 300000., "Too high")
#imageROI.enable = True
#imageStats.enable = True
#imageROI.setROI(370, 390, 370, 390)#    ( y_start, y_end, x_start, x_end)


import average
d4_i_avg = average.Average(d4_i,numPoints=10, timeBetweenReadings=0.1)

def eh_shtr_control():
	if eh_shtr()=="Open":
		pos(eh_shtr, "Close")
	else:
		pos(eh_shtr, "Reset")
		time.sleep(3)
		pos(eh_shtr, "Open")


def fs_control():
	if fs()=="Open":
		pos(fs, "Closed")
	else:
		pos(fs, "Open")

#mtscripts have been commented out of JythonServerFacade as this is used temprarily for moveable equipment
#import mtscripts.moveable.me07m
#from mtscripts.moveable.me07m import mepiezo1x, mepiezo1y, eembimorph, dummy_bimorph

#import dataset_provider

#from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
#from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
#from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
#from gdascripts.analysis.datasetprocessor.twod.PixelIntensity import PixelIntensity

#detDSProvider = dataset_provider.NXDetectorDataWithFilepathForSrsDatasetProvider(pcoEdge,fileLoadTimout=5.)

#peak2d = DetectorDataProcessorWithRoi('peak2d', detDSProvider, [TwodGaussianPeak()])
#max2d = DetectorDataProcessorWithRoi('max2d', detDSProvider, [SumMaxPositionAndValue()])
#intensity2d = DetectorDataProcessorWithRoi('intensity2d', detDSProvider, [PixelIntensity()])

###############################################################################
###                   Configure scan data processing                        ###
###############################################################################
#from analysis_FindScanPeak import FindScanPeak
#from analysis_FindScanCentroid import findCentroidPoint, FindScanCentroid, readSRSDataFile
#print "Importing analysis commands (peak, centroid & peak optimisation)"
#peak=FindScanPeak #@UndefinedVariable
#cen=FindScanCentroid #@UndefinedVariable

#from gdascripts.scan import gdascans
#from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
#import gdascripts
#gdascripts.scan.concurrentScanWrapper.PRINTTIME = True
#gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()
#scancn=gdascans.Scancn([scan_processor])
#alias('scancn');print scancn.__doc__.split('\n')[2]
#lup = dscan # line up apparently!
#alias('lup')

#scan_processor.rootNamespaceDict=globals()
#scan_processor.duplicate_names = {'maxval':'maxpos', 'minval':'minpos'}
#scan_processor.processors.append(Lcen())
#scan_processor.processors.append(Rcen())
#scan_processor.processors.append(GaussianEdge(name='spedge')) # edge already maps to a function edgeDetectRobust


#dacscan is used by excalibur
from dac_scan import dacscan
vararg_alias("dacscan")

import excalibur_config
#from gdascripts.bimorph import bimorph

#from gdascripts.pd.dummy_pds import DummyPD
#from gdascripts.scannable.detector.dummy.focused_beam_dataset import CreateImageReadingDummyDetector
#from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
#from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
#from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
#from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
#from gdascripts.analysis.datasetprocessor.twod.PixelIntensity import PixelIntensity
#x = DummyPD("x")
#x.asynchronousMoveTo(430)
#cam1det = CreateImageReadingDummyDetector.create(x)
#cam1 = ProcessingDetectorWrapper('cam1', cam1det, [], panel_name_rcp='Plot 1')
#cam1 = ProcessingDetectorWrapper('cam1', pcoEdge_tif, [], panel_name_rcp='Plot 1')
#peak2d = DetectorDataProcessorWithRoi('peak2d', cam1, [TwodGaussianPeak()])
#max2d = DetectorDataProcessorWithRoi('max2d', cam1, [SumMaxPositionAndValue()])
#intensity2d = DetectorDataProcessorWithRoi('intensity2d', cam1, [PixelIntensity()])
#cam1.returnPathAsImageNumberOnly=True

#from gdascripts.bimorph.bimorph_mirror_optimising import SlitScanner, ScanAborter, TopupCountdown
#scanAborter=ScanAborter("scanAborter",ic, -10)
#slitscanner = SlitScanner()
#slitscanner.setScanAborter(scanAborter)
#from gdascripts.bimorph.bimorph_mirror_optimising import TopupCountdown
#bm_topup = TopupCountdown("bm_topup")

#	caput ("BL13I-EA-DET-01:CAM:ReverseX", 1)
#if( caget("BL13J-EA-DET-01:CAM:Model_RBV") == "PCO.Camera 4000"):
#	caput("BL13J-EA-DET-01:CAM:PIX_RATE", "32000000 Hz")
#if( caget("BL13J-EA-DET-01:CAM:Model_RBV") == "PCO.Camera Edge"):
#	caput("BL13J-EA-DET-01:CAM:PIX_RATE", "286000000 Hz")

if not LocalProperties.check("gda.dummy.mode"):
	try:
		if( caget("BL13J-EA-DET-01:CAM:Model_RBV") == "PCO.Camera 4000"):
			caput("BL13J-EA-DET-01:CAM:PIX_RATE", "32000000 Hz")
		if( caget("BL13J-EA-DET-01:CAM:Model_RBV") == "PCO.Camera Edge"):
			caput("BL13J-EA-DET-01:CAM:PIX_RATE", "286000000 Hz")
	except:
		print "Unable to connect to PCO IOC - please check if it's running!"


# pos afg_chan1_ampl 2.
# pos afg_chan1_state "On"

import alignmentGui
try:
	tomodet = alignmentGui.TomoDet()
except:
	print "Unable to connect to PCO IOC - please check if it's running!"

import tomographyScan
from tomographyScan import reportTomo, showNormalisedImage
alias("reportTomo")
alias("showNormalisedImage")
tomography_additional_scannables=[]

print "stxm_det - begin"
import stxm_det
from stxm_det import *
#stxm_merlin_sw_hdf = stxm_det(name="stxm_merlin_sw_hdf", det=merlin_sw_hdf)
print "stxm_det - end"

from trigger import trigz2

print(section_sep)
#if not LocalProperties.check("gda.dummy.mode"):
#	run("localStationUser.py")

import tomographyXGIScan
from tomographyXGIScan import tomoXGIScan
import tomographyXGIScan2d
from tomographyXGIScan2d import tomoXGIScan2d

print(section_sep)
print "\n Adding beamline default scannables..."
# append new items to the list below as required
_default_scannable_names = []
#_default_scannable_names.append("ring")
_default_scannable_names.append("actualTime")
_default_scannable_names.append("ionc_i")

from types import *
_default_scannables = []
for sname in _default_scannable_names:
	if type(Finder.find(sname)) is not NoneType:
		_default_scannables.append(Finder.find(sname))
	else:
		try:
			#print sname
			eval(sname)
			_default_scannables.append(eval(sname))
		except:
			msg = "\t Failed to find a default scannable named: " + sname
			print msg
try:
	for s in _default_scannables:
		add_default(s)
except:
	exceptionType, exception, traceback = sys.exc_info()
	msg = "Failed to complete the task of adding default scannables: "
	handle_messages.log(None, msg, exceptionType, exception, traceback, False)

print "\n Finished adding beamline default scannables."
srv = Finder.findSingleton(Jython)
_default_scannables_in_gda = srv.getDefaultScannables().toArray()
print "\n The following default scannables will be recorded at each scan point under /entry1/default or /entry1/instrument in every Nexus scan file:"
for s in _default_scannables_in_gda:
	print s.getName()
print(section_sep)

try:
	print "\n Adding beamline meta scannables..."
	meta_scannables = []

	# in alphabetical order
	meta_scannables.append(id_gap)
	meta_scannables.append(fes1)
	meta_scannables.append(qcm_energy)
	meta_scannables.append(s1)
	meta_scannables.append(s2)
	#meta_scannables.append(s3)
	meta_scannables.append(s4)
	meta_scannables.append(s5)
	meta_scannables.append(s6)
	meta_scannables.append(s7)
	meta_scannables.append(t2)
	meta_scannables.append(t1)

	# this fails coz it is trying to write string as float
	#meta_scannables.append(ionc_gain)
	#meta_scannables.append(ionc_gainmode)
	#meta_scannables.append(ionc_coupling)

	for s in meta_scannables:
		meta_add(s)
	# temp fix
	meta_add("ionc_A_over_V_gain", ionc_gain())
	meta_add("ionc_gainmode", ionc_gainmode())
	meta_add("ionc_acdc", ionc_coupling())
	meta_add("mirror_stripe", m1_strip())
	meta_add("crls_present", f1_crly_mp())

	print "\n Finished adding beamline meta scannables."
	print "\n The following meta scannables will be recorded once per scan under /entry1/before_scan in every Nexus scan file:"
	meta_scannables_in_gda = meta_ls()
	print meta_scannables_in_gda
except:
	exceptionType, exception, traceback = sys.exc_info()
	msg = "Failed to complete the task of adding meta scannables: "
	handle_messages.log(None, msg, exceptionType, exception, traceback, False)
print(section_sep)

# for vortex to set Preset Mode to 'Real time' (the default is 'No preset')
if isLive():
	try:
		caput("ME13C-EA-DET-01:PresetMode", 1)
	except:
		print("Failed to set Preset Mode on XMAP to 'Real time' - is XMAP present on the beamline and its IOC running?")

#8/4/2014 pie725 not present
#run("startup_pie725")

#shutter_director = ShutterDirector('shutter_director', delay_after_open_sec=0, delay_after_close_sec=0)

try:
	print "Adding sample_lab_x_t1_pitch..."
	sample_lab_x_t1_pitch = ScannableGroup()
	sample_lab_x_t1_pitch.addGroupMember(sample_lab_x)
	sample_lab_x_t1_pitch.addGroupMember(t1_pitch)
	sample_lab_x_t1_pitch.setName("sample_lab_x_t1_pitch")
	sample_lab_x_t1_pitch.configure()
except:
	print "Failed to create sample_lab_x_t1_pitch!"

if isLive():
	excalibur_config_normal_vds.getCollectionStrategy().scriptEnabled=True
	excalibur_config_normal_vds.getCollectionStrategy().scriptFileName="/dls_sw/prod/tools/RHEL6-x86_64/defaults/bin/dls-vds-gen.py"
	excalibur_config_normal_vds.getAdditionalPluginList()[0].fileTemplate="%s%s-%d.hdf"

	# for b16 Vishal BEGIN
	#try:
	#	print "Adding metadata system for DAT files (b16)..."
	#	from gdascripts.scannable.installStandardScannableMetadataCollection import *
	#	meta.rootNamespaceDict=globals()
	#	note.rootNamespaceDict=globals()
	#except:
	#	print "Failed to add metadata system for DAT files (b16)!"

	#try:
	#	print "Installing attocube axes from epics BL13J-EA-ECC..."
	#	from ecc100axis import createEcc100Axis
		#attol1 = createEcc100Axis("attol1", "BL13J-EA-ECC-01:ACT0:")
		#attol2 = createEcc100Axis("attol2", "BL13J-EA-ECC-01:ACT1:")
		#attol3 = createEcc100Axis("attol3", "BL13J-EA-ECC-01:ACT2:")

		#attor1 = createEcc100Axis("attor1", "BL13J-EA-ECC-02:ACT0:")
		#attor2 = createEcc100Axis("attor2", "BL13J-EA-ECC-02:ACT1:")
		#attor3 = createEcc100Axis("attor3", "BL13J-EA-ECC-02:ACT2:")
	#	attol1 = createEcc100Axis("attol1", "BL13J-EA-ECC-04:ACT0:")
	#	attol2 = createEcc100Axis("attol2", "BL13J-EA-ECC-04:ACT1:")
	#	attol3 = createEcc100Axis("attol3", "BL13J-EA-ECC-04:ACT2:")

	#	attoltilt1 = createEcc100Axis("attoltilt1", "BL13J-EA-ECC-02:ACT0:")
	#	attoutilt1 = createEcc100Axis("attoutilt1", "BL13J-EA-ECC-02:ACT1:")
	#	attorot1   = createEcc100Axis("attorot1",   "BL13J-EA-ECC-02:ACT2:")

	#	attoltilt2 = createEcc100Axis("attoltilt2", "BL13J-EA-ECC-01:ACT0:")
	#	attoutilt2 = createEcc100Axis("attoutilt2", "BL13J-EA-ECC-01:ACT1:")
	#	attorot2   = createEcc100Axis("attorot2",   "BL13J-EA-ECC-01:ACT2:")

	#	attol4 = createEcc100Axis("attol4", "BL13J-EA-ECC-03:ACT0:")
	#	attol5 = createEcc100Axis("attol5", "BL13J-EA-ECC-03:ACT1:")
	#	attol6   = createEcc100Axis("attol6",   "BL13J-EA-ECC-03:ACT2:")
	#except:
	#	print "Failed to create attocube axes!"
	# for b16 Vishal END

	excalibur_config_normal_vds.getCollectionStrategy().scriptFileName='/dls_sw/prod/common/python/RHEL6-x86_64/vds-gen/0-3-1/prefix/bin/versioned/dls-vds-gen-0.3.1.py'

print(section_sep)
try:
	print "Adding Pycho scripts..."
	run("/dls_sw/i13-1/scripts/Pycho/pycho/controls/beamlineAlignment.py")
	run("/dls_sw/i13-1/scripts/Pycho/pycho/controls/pycho_collect.py")
except:
	print "Failed to add Pycho scripts!"
print(section_sep)
# localStationUser.py should be run at the very end of this localStation.py
if not LocalProperties.check("gda.dummy.mode"):
	run("localStationUser.py")

meta_add(optics_zp)

if isLive():
	try:
		caput("BL13J-EA-DET-04:HDF5:NDArrayPort", "merlin1.cam")
	except:
		print("Error setting array port on Merlin detector")

import excalibur_odin
from excalibur_odin import excalibur_odin_xgraph

run("mapping_scan_commands.py")

def douglas(start, stop, stepasdf):
	mscan(step('t1_pi_lz', start, stop, stepasdf), det=[detector('BL13J-ML-SCAN-01', 0.01)])

from gdascripts.watchdogs.watchdogs import enableWatchdogs, disableWatchdogs, listWatchdogs
from gdascripts.watchdogs.watchdogs import enable_watchdogs, disable_watchdogs, list_watchdogs, set_watchdog_enabled, is_watchdog_enabled
alias("enableWatchdogs")
alias("disableWatchdogs")
alias("listWatchdogs")

print(section_sep)
print("\n Finished running localStation.py")
