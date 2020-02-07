import sys;
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog # @UnusedImport

from localStationScripts.pd_epicsdevice import Simple_PD_EpicsDevice
import gdascripts.pd.epics_pds # @UnusedImport
from gdascripts.pd.epics_pds import DisplayEpicsPVClass
from gdascripts.pd.time_pds import waittime
import gdascripts.utils # @UnusedImport
from localStationScripts.pd_ratio import Simple_PD_Ratio
from localStationScripts.baseTable import BaseTable
from localStationScripts.shutterCommands import configure as shutterCommands_configure
from localStationScripts.ccdScanMechanics import configure as ccdScanMechanics_configure
from localStationScripts.ccdScanMechanics import setMaxVelocity # @UnusedImport
from localStationScripts.operationalControl import configure as operationalControl_configure
from localStationScripts.operationalControl import * # @UnusedWildImport
from gda.configuration.properties import LocalProperties
from gdascripts.parameters import beamline_parameters
from gda.device.epicsdevice import ReturnType
from gda.util import VisitPath
from localStationScripts.constants import * # @UnusedWildImport
from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()

#global zebraContinuousMoveController
from scannables.detectors.fastShutterZebraDetector import FastShutterZebraDetector
zebraFastShutter=FastShutterZebraDetector(          'zebraFastShutter', 'BL15I-EA-ZEBRA-01:', beamline_parameters.JythonNameSpaceMapping().zebraContinuousMoveController)
from scannables.detectors.checkZebraScannable import ZebraPositionScannable #, ZebraCheckScannable
zebraPositionScannable=ZebraPositionScannable('zebraPositionScannable', 'BL15I-EA-ZEBRA-01:', beamline_parameters.JythonNameSpaceMapping().dkphi)
#zebraCheckScannable=ZebraCheckScannable(         'zebraCheckScannable', 'BL15I-EA-ZEBRA-01:', beamline_parameters.JythonNameSpaceMapping().dkphi)

from gdascripts.scannable.epics.PvManager import PvManager
import scannables.detectorShield
ds=scannables.detectorShield.DetectorShield('ds', PvManager(pvroot='BL15I-RS-ABSB-06:'))

import scannables.MerlinColourModeThresholdsScannable
mcts=scannables.MerlinColourModeThresholdsScannable.MerlinColourModeThresholdsScannable('mcts', PvManager(pvroot='BL15I-EA-DET-18:Merlin1:'))

from localStationScripts.detector_scan_commands import * # @UnusedWildImport
from localStationScripts.user_commands import * # @UnusedWildImport
from localStationScripts.centreProxy import * # @UnusedWildImport
from mapping_scan_commands import *

from gda.epics import CAClient

from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue #@UnusedImport
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak

global finder, run, etl, prop, add_default, vararg_alias, \
	s1xpos, s1xgap, s1ypos, s1ygap,\
	s1xplus, s1xminus, s1yplus, s1yminus,\
	dcmbragg1, dcmbragg2, dcmxtl1y, dcmxtl2y,\
	dcmxtl1roll, dcmxtl1z, dcmenergy,\
	qbpm1_x, qbpm1_y, qbpm1A, qbpm1B, qbpm1C, qbpm1D, qbpm1total,\
	s6ypos, s6ygap, s6yup, s6ydown,\
	vfm_x, vfm_y, vfm_pitch, vfm_curve, vfm_ellipticity, vfm_gravsag,\
	hfm_x, hfm_y, hfm_pitch, hfm_curve, hfm_ellipticity, hfm_yaw, hfm_roll,\
	s2ygap, s2ypos,\
	qbpm2_x, qbpm2_y, qbpm2A, qbpm2B, qbpm2C, qbpm2D, qbpm2total,\
	f2x,\
	s4xpos, s4xgap, s4ypos, s4ygap, s4yaw, s4pitch,\
	fsx, fsy,\
	pinx, piny, pinz, pinpitch, pinyaw,\
	dx, dy, dz, dmu, dkphi, dkappa, dktheta,\
	djack1, djack2, djack3, dtransx, drotation, det1z, ddelta,\
	shdx, shdy, shdz,\
	bsx, bsy,\
	tab2jack1, tab2jack2, tab2jack3, tab2transx, tab2rotation,\
	s7xpos, s7ypos, s7xgap, s7ygap,\
	d6x,\
	fs2x, fs2y,\
	skbjack1, skbjack2, skbjack3, skby, skbpitch, skbroll,\
	svfmcurve, svfmellip, svfmy, svfmpitch, \
	shfmcurve, shfmellip, shfmx, shfmpitch, \
	pin3x, pin3y,\
	sx, sy, sz, spitch, syaw, sroll,\
	spivotx, spivoty, spivotz, sphi, ssx, ssz,\
	d7x, d7y,\
	bs2x, bs2y, bs3x, bs3y, bs3z, \
	\
	d1, d2, d3, d4, d5, d6, d7, d8, d9\
#	,cryox, cryoy, cryoz, cryorot\

#	det2z,

def peakFinder():
	"""
	This function runs the Epics Peak Finder proc for DCM-01
	
	It returns when the state is no longer searching.
	"""
	caclient = CAClient()
	caclient.caput( "BL15I-OP-DCM-01:PEAK:GO.PROC", 1)
	
	peakFindStatus = "1"
	
	while peakFindStatus=="1":
		simpleLog("Searching for peak")
		peakFindStatus = caclient.caget("BL15I-OP-DCM-01:PEAK:STATE")
		sleep(5)
		
	if peakFindStatus=="3":
		simpleLog("Couldn't find peak")
	elif peakFindStatus=="2":
		simpleLog("qbpm1total="+str(qbpm1total))

def runFile(name):
	simpleLog("Running file " + name + "...")
	run(name)
	simpleLog("..." + name + " complete")

def plot(detector):
	if not isinstance(detector, ProcessingDetectorWrapper):
		simpleLog("Detector %r not supported." % detector)
		simpleLog("Supported detectors include: pil, pe1, cam1, cam2, cam3, cam4")
		return
	detector.clearLastAcquisitionState();
	detector.display()

localStation_exceptions = []

def localStation_exception(exc_info, msg):
	typ, exception, traceback = exc_info
	simpleLog("! Failure %s !" % msg)
	localStation_exceptions.append("    %s" % msg)
	handle_messages.log(None, "Error %s -  " % msg , typ, exception, traceback, False)

try:
	simpleLog("================ INITIALISING I15 GDA ================")

	from localStationConfiguration import disableZebra2
	if disableZebra2:
		simpleLog("Disabling zebra 2 by setting the move controller to have no triggered controllers.")
		beamline_parameters.JythonNameSpaceMapping().zebraContinuousMoveController.setTriggeredControllers([])
		# Remove the zebra2 reference from triggered detectors, while it's broken. This should also cause
		# user_commands._rockScanParams() to remove all relevant scannables and controllers from rock scans.

	scansReturnToOriginalPositions = 1;
	
	beamlineName = "i15"
	commissioningProposal = "ee0"
	beamline = finder.find("Beamline")

	try:
		simpleLog("Creating devices")
		w = waittime
		baseTab = BaseTable("baseTab", beamline, "-MO-DIFF-01:BASE:", djack1, djack2, djack3, 2.5)
		baseTab2 = BaseTable("baseTab2", beamline, "-MO-TABLE-03:BASE:", tab2jack1, tab2jack2, tab2jack3, 2.5)
		qbpm1total = Simple_PD_EpicsDevice("qbpm1total", beamline, "-DI-QBPM-01:INTEN")
		from localStationConfiguration import useQbpm2eth
		if not useQbpm2eth:
			qbpm2total = Simple_PD_EpicsDevice("qbpm2total", beamline, "-DI-QBPM-02:INTEN") # Original QBPM
		else:
			qbpm2total = Simple_PD_EpicsDevice("qbpm2total", beamline, "-EA-QBPM-02:INTEN") # New ethercat based QBPM
		#s4pitch = Simple_PD_EpicsDevice("s4pitch", beamline, "-AL-SLITS-04:PITCH.VAL")
		#s4yaw = Simple_PD_EpicsDevice("s4yaw", beamline, "-AL-SLITS-04:YAW.VAL")
		#pin2x = Simple_PD_EpicsDevice("pin2x", beamline, "-AL-APTR-02:X")
		#pin2y = Simple_PD_EpicsDevice("pin2y", beamline, "-AL-APTR-02:Y")
		#pin2pitch = Simple_PD_EpicsDevice("pin2pitch", beamline, "-AL-APTR-02:PITCH")
		#pin2yaw = Simple_PD_EpicsDevice("pin2yaw", beamline, "-AL-APTR-02:YAW")
		ionc1 = Simple_PD_EpicsDevice("ionc1", beamline, "-DI-IONC-01:I")

		#prop = Simple_PD_EpicsDevice("prop", beamline, "-DI-PROP-01:I")
		#dcmpiezo = Simple_PD_EpicsDevice("dcmpiezo", beamline, "-OP-DCM-01:PIEZO:OUT")
		#s2ygap = Simple_PD_EpicsDevice("s2ygap", beamline, "-AL-SLITS-02:Y:GAP.VAL")
		#s2ycen = Simple_PD_EpicsDevice("s2ycen", beamline, "-AL-SLITS-02:Y:CENTRE.VAL")
		#qbpX = Simple_PD_EpicsDevice("qbpX", beamline, "-DI-QBPMD-01:X.VAL")
		#qbpY = Simple_PD_EpicsDevice("qbpY", beamline, "-DI-QBPMD-01:Y.VAL")
		#qbpm2acurrent = Simple_PD_EpicsDevice("qbpm2acurrent", beamline, "-DI-IAMP-02:CHA:PEAK")
		#qbpm2bcurrent = Simple_PD_EpicsDevice("qbpm2bcurrent", beamline, "-DI-IAMP-02:CHB:PEAK")
		#qbpm2ccurrent = Simple_PD_EpicsDevice("qbpm2ccurrent", beamline, "-DI-IAMP-02:CHC:PEAK")
		#qbpm2dcurrent = Simple_PD_EpicsDevice("qbpm2dcurrent", beamline, "-DI-IAMP-02:CHD:PEAK")
	
		qbpm1A = Simple_PD_EpicsDevice("qbpm1A", beamline, "-DI-QBPM-01:A")
		qbpm1B = Simple_PD_EpicsDevice("qbpm1B", beamline, "-DI-QBPM-01:B")
		qbpm1C = Simple_PD_EpicsDevice("qbpm1C", beamline, "-DI-QBPM-01:C")
		qbpm1D = Simple_PD_EpicsDevice("qbpm1D", beamline, "-DI-QBPM-01:D")

		if not useQbpm2eth:
			qbpm2A = Simple_PD_EpicsDevice("qbpm2A", beamline, "-DI-QBPM-02:A")
			qbpm2B = Simple_PD_EpicsDevice("qbpm2B", beamline, "-DI-QBPM-02:B")
			qbpm2C = Simple_PD_EpicsDevice("qbpm2C", beamline, "-DI-QBPM-02:C")
			qbpm2D = Simple_PD_EpicsDevice("qbpm2D", beamline, "-DI-QBPM-02:D")
		else:
			qbpm2A = Simple_PD_EpicsDevice("qbpm2A", beamline, "-EA-QBPM-02:A")
			qbpm2B = Simple_PD_EpicsDevice("qbpm2B", beamline, "-EA-QBPM-02:B")
			qbpm2C = Simple_PD_EpicsDevice("qbpm2C", beamline, "-EA-QBPM-02:C")
			qbpm2D = Simple_PD_EpicsDevice("qbpm2D", beamline, "-EA-QBPM-02:D")

		vfm_gravsag = Simple_PD_EpicsDevice("vfm_gravsag", beamline, "-OP-VFM-01:SAG.VAL")

		spivotx = Simple_PD_EpicsDevice("spivotx", beamline, "-MO-SFAB-01:PIVOT:X")
		spivoty = Simple_PD_EpicsDevice("spivoty", beamline, "-MO-SFAB-01:PIVOT:Y")
		spivotz = Simple_PD_EpicsDevice("spivotz", beamline, "-MO-SFAB-01:PIVOT:Z")

		patch12x7 = Simple_PD_EpicsDevice("patch12x7", beamline, "-EA-PATCH-12:X7")
		patch12x8 = Simple_PD_EpicsDevice("patch12x8", beamline, "-EA-PATCH-12:X8")
		patch14x5 = Simple_PD_EpicsDevice("patch14x5", beamline, "-EA-PATCH-14:X5")
		patch14x6 = Simple_PD_EpicsDevice("patch14x6", beamline, "-EA-PATCH-14:X6")
		patch14x7 = Simple_PD_EpicsDevice("patch14x7", beamline, "-EA-PATCH-14:X7")

		patch12x13 = Simple_PD_EpicsDevice("patch12x13", beamline, "-EA-PATCH-12:X13")
		patch12x14 = Simple_PD_EpicsDevice("patch12x14", beamline, "-EA-PATCH-12:X14")

		#ring= finder.find("Ring")
		ringCurrent = DisplayEpicsPVClass("ringCurrent", "SR-DI-DCCT-01:SIGNAL", "mA", "%f")
		wigglerField = DisplayEpicsPVClass("wigglerField", "SR15I-ID-SCMPW-01:B_REAL", "Tesla", "%f")
		#detz = DisplayEpicsPVClass("detz", "BL15I-MO-DIFF-01:ARM:DETECTOR:Z.VAL", "mm", "%f")
		
		patch12x6 = Simple_PD_EpicsDevice("patch12x6", beamline, "-EA-PATCH-12:X6")
		
		thermo1 = DisplayEpicsPVClass("thermo1", "BL15I-EA-PATCH-50:TEMP1", "deg C", "%f")
		thermo2 = DisplayEpicsPVClass("thermo2", "BL15I-EA-PATCH-50:TEMP2", "deg C", "%f")
		thermo3 = DisplayEpicsPVClass("thermo3", "BL15I-EA-PATCH-50:TEMP3", "deg C", "%f")
		pt100_1 = DisplayEpicsPVClass("pt100_1", "BL15I-EA-PATCH-51:TEMP1", "deg C", "%f")
		pt100_2 = DisplayEpicsPVClass("pt100_2", "BL15I-EA-PATCH-51:TEMP2", "deg C", "%f")
		pt100_3 = DisplayEpicsPVClass("pt100_3", "BL15I-EA-PATCH-51:TEMP3", "deg C", "%f")

		#patch12x13 = DisplayEpicsPVClass("patch12x13", "BL15I-EA-PATCH-12:X13", "", "%f")
		#patch12x14 = DisplayEpicsPVClass("patch12x14", "BL15I-EA-PATCH-12:X14", "", "%f")
		
		#
		#add_default(thermo1) - Moved to /dls/i15/scripts/localStationUser.py
		#add_default(pt100_1) - Moved to /dls/i15/scripts/localStationUser.py
	except:
		localStation_exception(sys.exc_info(), "creating devices")

	#dummyDetector = SimpleDummyDetector()

	try:
		from dls_scripts.scannable.CryojetScannable import CryojetScannable
		cryojet = CryojetScannable('cryojet', 'BL15I-CG-CJET-01:', 
									temp_tolerance=1, stable_time_sec=60)
	except:
		localStation_exception(sys.exc_info(), "creating cryojet scannable")

	try:
		global pe
		pe1 = ProcessingDetectorWrapper('pe1', pe, [], panel_name_rcp='Plot 1')
		pe1.processors=[DetectorDataProcessorWithRoi(
						'max', pe1, [SumMaxPositionAndValue()], False)]
		
		pe1peak2d = DetectorDataProcessorWithRoi(
			'pe1peak2d', pe1, [TwodGaussianPeak()])
		pe1max2d = DetectorDataProcessorWithRoi(
			'pe1max2d', pe1, [SumMaxPositionAndValue()])
	except:
		localStation_exception(sys.exc_info(), "creating pe1...")

	def gigeFactory(camdet_name, cam_name, peak2d_name, max2d_name, cam_pv):
		from gdascripts.scannable.detector.epics.EpicsGigECamera import EpicsGigECamera
		try:
			print "Creating %s, %s, %s and %s" % \
				(camdet_name, cam_name, peak2d_name, max2d_name)
			camdet = EpicsGigECamera(camdet_name, cam_pv,
				filepath=VisitPath.getVisitPath() + '/', stdNotArr=False, reconnect=False)
			cam = ProcessingDetectorWrapper(cam_name, camdet, [], panel_name_rcp='Plot 1')
			peak2d = DetectorDataProcessorWithRoi(peak2d_name, cam, [TwodGaussianPeak()])
			max2d = DetectorDataProcessorWithRoi(max2d_name, cam, [SumMaxPositionAndValue()])
			return camdet, cam, peak2d, max2d
		except:
			localStation_exception(sys.exc_info(), "creating %s" % cam_name)

	cam1det, cam1, peak2d, max2d = gigeFactory(
		'cam1det', 'cam1', 'peak2d', 'max2d', 'BL15I-DI-GIGE-01:')
	cam2det, cam2, peak2d2, max2d2 = gigeFactory(
		'cam2det', 'cam2', 'peak2d2', 'max2d2', 'BL15I-DI-GIGE-02:')
	cam3det, cam3, peak2d3, max2d3 = gigeFactory(
		'cam3det', 'cam3', 'peak2d3', 'max2d3', 'BL15I-DI-GIGE-03:')
	cam4det, cam4, peak2d4, max2d4 = gigeFactory(
		'cam4det', 'cam4', 'peak2d4', 'max2d4', 'BL15I-DI-GIGE-04:')
	cam5det, cam5, peak2d5, max2d5 = gigeFactory(
		'cam5det', 'cam5', 'peak2d5', 'max2d5', 'BL15I-DI-GIGE-05:')

	try:
		simpleLog("Create diodes")

		def diodeFactory(channel_name, finder_name):
			simplePv = finder.find(finder_name)
			simplePv.configure()
			diode = simplePv.createEpicsChannel(channel_name, ReturnType.DBR_NATIVE, "", "")
			diode.setLevel(6)
			diode.setValue(".SCAN", 9)
			return diode

		simpleLog("Create diodes 1-5")
		d1=diodeFactory("d1", "PHDGN1")
		d2=diodeFactory("d2", "PHDGN2")
		d3=diodeFactory("d3", "PHDGN3")
		d4=diodeFactory("d4", "PHDGN4")
		d5=diodeFactory("d5", "PHDGN5")

		simpleLog("Create diode ratios")
		d2_d1 = Simple_PD_Ratio('d2_d1', d2, d1)
		d3_d2 = Simple_PD_Ratio('d3_d2', d3, d2)
		d4_d2 = Simple_PD_Ratio('d4_d2', d4, d2)
		d5_d1 = Simple_PD_Ratio('d5_d1', d5, d1)

		simpleLog("Create diode sums")
		d1sum = DisplayEpicsPVClass("d1sum", "BL15I-DI-PHDGN-01:DIODESUM", "", "%f")
		d2sum = DisplayEpicsPVClass("d2sum", "BL15I-DI-PHDGN-02:DIODESUM", "", "%f")
		d3sum = DisplayEpicsPVClass("d3sum", "BL15I-DI-PHDGN-03:DIODESUM", "", "%f")
		d4sum = DisplayEpicsPVClass("d4sum", "BL15I-DI-PHDGN-04:DIODESUM", "", "%f")
		d5sum = DisplayEpicsPVClass("d5sum", "BL15I-DI-PHDGN-05:DIODESUM", "", "%f")
		#add_default(d1sum) - Moved to /dls/i15/scripts/localStationUser.py

		simpleLog("Create diodes 6+")
		d6=diodeFactory("d6", "PHDGN6")
		d8=diodeFactory("d8", "PHDGN8")
		d9=diodeFactory("d9", "PHDGN9")
	except:
		localStation_exception(sys.exc_info(), "creating diodes")

	try:
		simpleLog("Setup aliases")
		vararg_alias("scan")
		alias("dp")
		alias("shopen")
		alias("oehs")
		alias("shclose")
		alias("cehs")
		alias("shopenall")
		alias("hcloseall")
		alias("cfs")
		alias("ofs")
		alias("d1in")
		alias("d2in")
		alias("d3in")
		alias("d4in")
		alias("d1out")
		alias("d2out")
		alias("d3out")
		alias("d4out")
		alias("d4cryoIn")
		alias("d4cryoOut")
		alias("align")
		alias("ready")
		alias("homeToMinus")
		alias("minusToHome")
		alias("homeToMinus57")
		alias("minus57ToMinus122")
		exposeAliases(alias) # expose*
	except:
		localStation_exception(sys.exc_info(), "setting up aliases")

	try:
		from localStationScripts.etl_detector import * #@UnusedWildImport
		etl.setLevel(7)
	except:
		localStation_exception(sys.exc_info(), "creating etl detector")

	try:
		simpleLog("Create checkbeam objects: checkbeam")
		from gdascripts.pd.pd_waitWhileScannableBelowThreshold import WaitWhileScannableBelowThreshold
		checkbeam = WaitWhileScannableBelowThreshold('checkbeam', scannableToMonitor=prop, minimumThreshold=5, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=30)
		checkbeam.setLevel(6)
		#from checkbeam_pds import * #@UnusedWildImport
		print "checkbeam level: %d" % checkbeam.getLevel()
	except:
		localStation_exception(sys.exc_info(), "creating checkbeam objects")

	from future.toggleBinaryPvAndWait import ToggleBinaryPvAndWait
	from future.binaryPvDetector import BinaryPvDetector
	from future.timeOverThresholdDetector import TimeOverThresholdDetector
	from localStationConfiguration import enableXps7out1trig
	if enableXps7out1trig:
		try:
			xps7out1trig = ToggleBinaryPvAndWait('xps7out1trig', 'BL15I-MO-XPS-07:GPIO:OUT1', normalLevel='1', triggerLevel='0')
		except:
			localStation_exception(sys.exc_info(), "creating xps7out1trig object")
	else:
		simpleLog("* Not creating xps7out1trig object *")
	
	from localStationConfiguration import enablePatchX7triggers
	if enablePatchX7triggers:
		try:
			patch12x7trig = ToggleBinaryPvAndWait('patch12x7trig', 'BL15I-EA-PATCH-12:X7', normalLevel='Logic 0', triggerLevel='Logic 1')
			patch14x7trig = ToggleBinaryPvAndWait('patch14x7trig', 'BL15I-EA-PATCH-14:X7', normalLevel='Logic 0', triggerLevel='Logic 1')

			patch12x7trigLow = ToggleBinaryPvAndWait('patch12x7trigLow', 'BL15I-EA-PATCH-12:X7', normalLevel='Logic 1', triggerLevel='Logic 0')
			patch14x7trigLow = ToggleBinaryPvAndWait('patch14x7trigLow', 'BL15I-EA-PATCH-14:X7', normalLevel='Logic 1', triggerLevel='Logic 0')

			patch12x7trig2 = BinaryPvDetector('patch12x7trig2', 'BL15I-EA-PATCH-12:X7', normalLevel='Logic 0', triggerLevel='Logic 1')
			patch14x7trig2 = BinaryPvDetector('patch14x7trig2', 'BL15I-EA-PATCH-14:X7', normalLevel='Logic 0', triggerLevel='Logic 1')

			patch12x7trig2low = BinaryPvDetector('patch12x7trig2low', 'BL15I-EA-PATCH-12:X7', normalLevel='Logic 1', triggerLevel='Logic 0')
			patch14x7trig2low = BinaryPvDetector('patch14x7trig2low', 'BL15I-EA-PATCH-14:X7', normalLevel='Logic 1', triggerLevel='Logic 0')
			
			totatboxtrig = TimeOverThresholdDetector('totatboxtrig',
				'BL15I-EA-PATCH-12:X7', normalLevel='Logic 1', triggerLevel='Logic 0',
				edgeDetectorPvString="BL15I-EA-PATCH-12:X6:EDGE:WAIT")

			totatboxtrig14 = TimeOverThresholdDetector('totatboxtrig',
				'BL15I-EA-PATCH-14:X7', normalLevel='Logic 1', triggerLevel='Logic 0',
				edgeDetectorPvString="BL15I-EA-PATCH-14:X6:EDGE:WAIT")
		except:
			localStation_exception(sys.exc_info(), "creating patch x7trig object")
	else:
		simpleLog("* Not creating patch x7trig objects *")

	try:
		pe.hdfwriter.getNdFileHDF5().reset()
		caput("BL15I-EA-DET-01:PROC4:DataTypeOut",		"Int32")
		caput("BL15I-EA-DET-01:PROC4:EnableCallbacks",	"Enable")
		caput("BL15I-EA-DET-01:PROC3:NDArrayPort",		"pe1.proc.proc2")
		caput("BL15I-EA-DET-01:PROC3:EnableCallbacks",	"Enable")
		caput("BL15I-EA-DET-01:PROC:NDArrayPort",		"pe1.proc.proc4")
		caput("BL15I-EA-DET-01:ARR:NDArrayPort",		"pe1.proc.proc3")
		caput("BL15I-EA-DET-01:ARR:EnableCallbacks",	"Enable")
		caput("BL15I-EA-DET-01:MJPG:NDArrayPort",		"pe1.proc") # Greyed out!
		caput("BL15I-EA-DET-01:MJPG:EnableCallbacks",	"Enable") # Greyed out when enabled!
	except:
		localStation_exception(sys.exc_info(), "configuring pe compression & correcting pe area detector pipeline")

	global mar, pil3, mpx, psl

	try:
		mar.hdfwriter.getNdFileHDF5().reset()
		caput("BL15I-EA-MAR-01:ARR:EnableCallbacks",	"Enable")
		caput("BL15I-EA-MAR-01:PROC:EnableCallbacks",	"Enable")
		caput("BL15I-EA-MAR-01:MJPG:EnableCallbacks",	"Enable")
		caput("BL15I-EA-MAR-01:CAM:EraseMode",			"None")
		caput("BL15I-EA-MAR-01:ROI:EnableX",			"Disable")
		caput("BL15I-EA-MAR-01:ROI:EnableY",			"Disable")
	except:
		localStation_exception(sys.exc_info(), "configuring mar area detector plugins")

	try:
		pil3.hdfwriter.getNdFileHDF5().reset()
	except:
		localStation_exception(sys.exc_info(), "configuring pil3 compression")

	try:
		mpx.hdfwriter.getNdFileHDF5().reset()
		caput("BL15I-EA-DET-18:ARR:EnableCallbacks",	"Enable")
	except:
		localStation_exception(sys.exc_info(), "configuring mpx compression")

	try:
		psl.hdfwriter.getNdFileHDF5().reset()
		caput("BL15I-EA-PSL-01:ARR:EnableCallbacks",	"Enable")
		caput("BL15I-EA-PSL-01:PROC:EnableCallbacks",	"Enable")
		caput("BL15I-EA-PSL-01:MJPG:EnableCallbacks",	"Enable")
	except:
		localStation_exception(sys.exc_info(), "configuring psl compression & callbacks")

	try:
		from scannables.safeScannable import SafeScannable
		rot_dkphi = SafeScannable('rot_dkphi', control_scannable=dkphi,
			check_scannable=shdx, threshold=200, failIfGreaterNotLessThan=False)
		alias('rot_dkphi')
	except:
		localStation_exception(sys.exc_info(), "creating rot_dkphi object")

	try:
		from scannables.EpicsRockingScannable import EpicsRockingScannable
		dkphi_rockscan = EpicsRockingScannable('dkphi_rockscan', scannable=dkphi)
		alias('dkphi_rockscan')
	except:
		localStation_exception(sys.exc_info(), "creating dkphi_rockscan object")

	"""
	try:
		global srot
		from dls_scripts.scannable.ContinuouslyRockingScannable import ContinuouslyRockingScannable
		srot_rocker = ContinuouslyRockingScannable('srot_rocker', scannable=srot)
	except:
		localStation_exception(sys.exc_info(), "creating srot_rocker object")
	"""

	try:
		dx.setOutputFormat(["%.6g"])
		dy.setOutputFormat(["%.6g"])
		dz.setOutputFormat(["%.6g"])
		sx.setOutputFormat(["%.6g"])
		sy.setOutputFormat(["%.6g"])
		sz.setOutputFormat(["%.6g"])
		dkappa.setOutputFormat(["%.6g"])
	except:
		localStation_exception(sys.exc_info(), "setting output formats")

	try:
		run('utilities/centreBeam')
	except:
		localStation_exception(sys.exc_info(), "running centreBeam")

	try:
		from scannables.chiPseudoDevice import ChiPseudoDevice
		chi=ChiPseudoDevice('chi', dktheta, dkappa, dkphi,
									thoffset=2.2, phioffset=2.2)
	except:
		localStation_exception(sys.exc_info(), "creating chi object")

	from localStationConfiguration import enableAttoPiezos
	if enableAttoPiezos:
		try:
			print "Installing atto devices from epics BL15I-EA-ATTO..."
			
			from future.anc150axis import createAnc150Axis
			
			atto1 = createAnc150Axis("atto1", "BL15I-EA-ATTO-03:PIEZO1:", 0.25)
			atto2 = createAnc150Axis("atto2", "BL15I-EA-ATTO-03:PIEZO2:", 0.25)
			atto3 = createAnc150Axis("atto3", "BL15I-EA-ATTO-03:PIEZO3:", 0.25)
			atto4 = createAnc150Axis("atto4", "BL15I-EA-ATTO-04:PIEZO1:", 0.25)
			atto5 = createAnc150Axis("atto5", "BL15I-EA-ATTO-04:PIEZO2:", 0.25)
			atto6 = createAnc150Axis("atto6", "BL15I-EA-ATTO-04:PIEZO3:", 0.25)
			
			atto1.setFrequency(900)
			atto2.setFrequency(900)
			atto3.setFrequency(900)
			atto4.setFrequency(900)
			atto5.setFrequency(900)
			atto6.setFrequency(900)
		except:
			localStation_exception(sys.exc_info(), "creating atto devices")
	else:
		print "* Not installing atto devices *"

	from localStationConfiguration import enableWirescanner
	if enableWirescanner:
		print "Installing example wirescanner..."
		try:
			from gdascripts.scan.process.ScannableScan import ScannableScan
			from gdascripts.scan.gdascans import Rscan
			#from gdascripts.scan.gdascans import Scan
			from future.TwoGaussianEdges import TwoGaussianEdges
	
			wirescanner = ScannableScan('wirescanner', TwoGaussianEdges(), Rscan, sx, -2, 3, 0.1, w, 0.5, d7)
			wirescanner.__doc__ = """
		This is an example wirescanner, created with the command
		
			wirescanner = ScannableScan('wirescanner', TwoGaussianEdges(), Rscan, sx, -2, 3, 0.1, w, 0.5, d7)
				
		This performs a wirescan of sx from its starting position -2 to +3 in steps
		of 0.1, at each point waiting for 0.5s and taking the value of d7.
	
			>>>pos wirescanner
			Writing data to file:/dls/i15/data/2012/cm5709-3/45678.dat
			     sx	Time	      d7	    d1sum
			-7.1970	0.00	0.041284	16.850816
			...
			-3.1970	0.00	0.040710	16.850816
			Scan complete.
			wirescanner : scan: 45010 upos: -5.897000 ufwhm: 0.250358 dpos: -3.197000 dfwhm: 0.107779 area: 0.008844 fwhm: 0.179069
	
		To scan between absolute positions, use "Scan" instead of "Rscan", e.g.
		
			wirescansx = ScannableScan('wirescansx', TwoGaussianEdges(), Scan, sx, -5.235, -5.236, 0.0005, w, 0.2, d7)
	
		This performs a wirescan of sx from -5.235 to -5.236 in steps of half a
		micron, at each point waiting for 0.2s and taking the value of d7.
		
		It is probably best to create new wirescanners each time, but if you you
		want to re-use an existing name, you will need to del the old one.
		
		For example, if you want to change the position on wirescansx:
		
			>>>wirescansx = ScannableScan('wirescansx', TwoGaussianEdges(), Scan, sx, -5.255, -5.256, 0.0005, w, 0.2, d7)
			Traceback (most recent call last):
			  File "<input>", line 1, in <module>
			Exception: Trying to overwrite a Scannable: wirescansx
			>>>del wirescansx
			>>>wirescansx = ScannableScan('wirescansx', TwoGaussianEdges(), Scan, sx, -5.255, -5.256, 0.0005, w, 0.2, d7)
			
		Note: If you delete and recreate this wirescanner, you will lose this help. 
	"""
			simpleLog("For help on wirescanner run `help wirescanner`")
		except:
			localStation_exception(sys.exc_info(), "creating example wirescan")
	else:
		print "* Not installing example wirescanner *"

	from localStationConfiguration import enablePerpendicularSampleMotionScannables
	if enablePerpendicularSampleMotionScannables:
		""" TODO: Verify functionality before enabling.

		Note that these were developed during a time when there was a fault with the orientation of one of the axes.
		This fault is expected to be fixed during 2017 Shutdown 2, at which point, the calculations in this class
		will no longer be valid.

		Before enabling these scannables, you will need to verify that they still work if the axis modifications
		haven't happened, or update the calculations if they have.
		"""
		from scannables.PerpendicularSampleMotion import PerpendicularSampleMotion, ParallelSampleMotion, HeightSampleMotion
	
		try:
			simpleLog("Creating dperp, dpara & dheight")
			dperp=PerpendicularSampleMotion("dperp", dx, dy, dz, dmu, dkphi, dkappa, dktheta, True, 0, 58,
											help_text="To move sample stage horizontal to the beam.")
			dpara=ParallelSampleMotion     ("dpara", dx, dy, dz, dmu, dkphi, dkappa, dktheta, True, 0, 58,
											help_text="To move sample stage parallel to the beam.")
			dheight=HeightSampleMotion     ("dpara", dx, dy, dz, dmu, dkphi, dkappa, dktheta, True, 0, 58,
											help_text="To move sample stage vertical to the beam.")
		except:
			localStation_exception(sys.exc_info(), "creating dperp & dpara")
	else:
		simpleLog("* Not creating dperp, dpara & dheight *")

	try:
		jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		beamlineParameters = beamline_parameters.Parameters()
	except:
		localStation_exception(sys.exc_info(), "creating jythonNameMap & beamlineParameters")
	
	try:
		shutterCommands_configure(jythonNameMap, beamlineParameters)
		operationalControl_configure(jythonNameMap, beamlineParameters)
		ccdScanMechanics_configure(jythonNameMap, beamlineParameters)
	except:
		localStation_exception(sys.exc_info(), "configuring scripts")
	
	# meta should be created last to ensure we have all required scannables
	try:
		from gdascripts.scannable.installStandardScannableMetadataCollection import * #@UnusedWildImport
		meta.rootNamespaceDict=globals()
		note.rootNamespaceDict=globals()

		# See http://confluence.diamond.ac.uk/x/UQKY
		#from gdascripts.metadata.metadata_commands import setTitle, getTitle, meta_add, meta_ll, meta_ls, meta_rm, meta_clear_alldynamical
		from gdascripts.metadata.metadata_commands import * #@UnusedWildImport
		alias("setTitle")
		alias("getTitle")
		alias("meta_add") # addmeta
		alias("meta_ll")  # 
		alias("meta_ls")  # lsmeta
		alias("meta_rm")  # rmmeta
		# meta_clear_alldynamical
		#				  # setmeta # Errors if used with metashop
		#				  # note
		meta.readFromNexus = True

		metashop=Finder.getInstance().find("metashop")
		LocalProperties.set( NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME, "metashop" ) # gda.nexus.metadata.provider.name
		# As well as metashop needing to be define, GDAMetadata also needs to be defined.
		# metashop is defined in i15-config/servers/main/common/required_at_start.py

		simpleLog("Metadata scannables, from configuration: " + " ".join(str(x.name) for x in metashop.getMetaScannables()))

		# New metadata system doesn't allow metadata scannables to be set
		def stdmeta():
			""" This function resets the metadata scannables to the standard list in localststion"""

			logger = LoggerFactory.getLogger("stdmeta")

			stdmetadatascannables = ('ringCurrent', 'wigglerField',
				's1xpos', 's1xgap', 's1ypos', 's1ygap',
				's1xplus', 's1xminus', 's1yplus', 's1yminus',
				'dcmbragg1', 'dcmbragg2', 'dcmxtl1y', 'dcmxtl2y',
				'dcmxtl1roll', 'dcmxtl1z', 'dcmenergy',
				'qbpm1_x', 'qbpm1_y', 'qbpm1A', 'qbpm1B', 'qbpm1C', 'qbpm1D', 'qbpm1total',
				's6ypos', 's6ygap', 's6yup', 's6ydown',
				'vfm_x', 'vfm_y', 'vfm_pitch', 'vfm_curve', 'vfm_ellipticity', 'vfm_gravsag',
				'hfm_x', 'hfm_y', 'hfm_pitch', 'hfm_curve', 'hfm_ellipticity', 'hfm_yaw', 'hfm_roll',
				's2ygap', 's2ypos',
				'qbpm2_x', 'qbpm2_y', 'qbpm2A', 'qbpm2B', 'qbpm2C', 'qbpm2D', 'qbpm2total',
				'f2x',
				's4xpos', 's4xgap', 's4ypos', 's4ygap', 's4yaw', 's4pitch',
				'fsx', 'fsy',
				'pinx', 'piny', 'pinz', 'pinpitch', 'pinyaw',
				'thermo1', 'thermo2', 'thermo3', 'pt100_1',
				'dx', 'dy', 'dz', 'dkphi', 'dkappa', 'dktheta',
				'djack1', 'djack2', 'djack3', 'dtransx', 'drotation', 'det1z', 'ddelta',
				'shdx', 'shdy', 'shdz',
				'bsx', 'bsy',
				'tab2jack1', 'tab2jack2', 'tab2jack3', 'tab2transx', 'tab2rotation',
				's7xpos', 's7ypos', 's7xgap', 's7ygap',
				'd6x',
				'fs2x', 'fs2y',
				'skbjack1', 'skbjack2', 'skbjack3', 'skby', 'skbpitch', 'skbroll',
				'svfmcurve', 'svfmellip', 'svfmy', 'svfmpitch',
				'shfmcurve', 'shfmellip', 'shfmx', 'shfmpitch',
				'pin3x', 'pin3y',
				'sx', 'sy', 'sz', 'spitch', 'syaw', 'sroll',
				'spivotx', 'spivoty', 'spivotz', 'sphi', 'ssx', 'ssz',
				'd7x', 'd7y',
				'bs2x', 'bs2y', 'bs3x', 'bs3y', 'bs3z',
				'det2z',
				'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd8', 'd9',
				'd1sum', 'd2sum', 'd3sum', 'd4sum', 'd5sum',
				'cryox', 'cryoy', 'cryoz', 'cryorot',
				)
			
			before=set(metashop.getMetaScannables())
			cant_find=[]
			errors=[]
			for scn_name in stdmetadatascannables:
				scn=jythonNameMap[scn_name]
				if not scn:
					logger.debug("Unable to find {} in jythonNameMap, trying finder", scn_name)
					scn=finder.find(scn_name)
				if scn:
					try:
						if scn.isConfigured():
							scn.getPosition()
						else:
							logger.debug("Ignoring {} as it's not configured!")
						meta_add(scn)
					except:
						logger.error("Unable to add {}", scn_name, sys.exc_info()[1])
						errors.append(scn_name)
				else:
					logger.error("Unable to find {}", scn_name)
					cant_find.append(scn_name)
			after=set(metashop.getMetaScannables())
			if (before-after):
				simpleLog("Metadata scannables,            removed: " + " ".join(str(x.name) for x in before-after))
			if (after-before):
				simpleLog("                                  added: " + " ".join(str(x.name) for x in after-before))
			if (cant_find):
				simpleLog("                             can't find: " + " ".join(x for x in cant_find))
				localStation_exceptions.append("  finding scannables for metadata: " + " ".join(x for x in cant_find))
			if (errors):
				simpleLog("                               erroring: " + " ".join(x for x in errors))
				localStation_exceptions.append("    adding scannables to metadata: " + " ".join(x for x in errors))
				localStation_exceptions.append("     Try running `stdmeta` again now that localstation has finished")
			if (after):
				simpleLog("                                current: " + " ".join(str(x.name) for x in after))

		stdmeta()
		simpleLog("Use 'stdmeta' to reset to standard scannables")
		alias('stdmeta')
		add_default(meta)
		meta.quiet = True

	except:
		localStation_exception(sys.exc_info(), "creating metadata objects")

	from localStationConfiguration import enableSolsticeExamples
	if enableSolsticeExamples:
		try:
			from solsticeScanning.jythonAreaDetectorRunnableDeviceDelegate import JythonAreaDetectorRunnableDeviceDelegate

			pe1AreaDetectorRunnableDeviceProxyFinder = finder.find("pe1AreaDetectorRunnableDeviceProxyFinder")
			pe1AreaDetectorRunnableDeviceProxy = pe1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

			pe1JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(pe1AreaDetectorRunnableDeviceProxy)
			pe1AreaDetectorRunnableDeviceProxy.setDelegate(pe1JythonAreaDetectorRunnableDeviceDelegate)
			pe1AreaDetectorRunnableDeviceProxy.register()

			print "Configured pe1AD detector"

		except:
			localStation_exception(sys.exc_info(), "creating example solstice scanning devices")
	else:
		print "* Not installing example solstice scanning devices *"

	from gda.util.converters import JEPConverterHolder
	from gda.device.scannable import ConvertorScannable

	def createConvertorScannable(name, theScannable, theConvertor):
		scannable = ConvertorScannable()
		scannable.setName(name);
		scannable.setInputNames([ name ])
		scannable.setScannable(theScannable)

		# set up the units component for this object based on the underlying scannable
		scannable.setConvertor(theConvertor)
		scannable.setScannableName(theScannable.getName())

		scannable.configure()
		return scannable

	try:
		energy_calibration = JEPConverterHolder("energy_calibration", "calibrated_energy.xml")
		calibrated_energy = createConvertorScannable("ConvertorScannable", dcmenergy, energy_calibration)
	except:
		localStation_exception(sys.exc_info(), "creating calibrated_energy scannable")

	try:
		if abs(zebraPositionScannable.getPosition()[2]) > 0.01:
			zebraPositionScannable.moveTo(1)
			if abs(zebraPositionScannable.getPosition()[2]) > 0.01:
				localStation_exceptions.append("    Mismatch between dkphi motor position and zebra encoder - Rocking of dkphi will probably fail!\n    * To fix, run 'zebraPositionScannable.copyMotorPosToZebra()' when motor is static (it must not be moving at all).\n    * Then run 'pos zebraPositionScannable 1' and check that the reported diff is now small.\n    * See 'http://confluence.diamond.ac.uk/x/9AVBAg' for more details.")
	except:
		localStation_exception(sys.exc_info(), "checking zebra encoder position")
except:
	localStation_exception(sys.exc_info(), "in localStation")

print "*"*80
print "Attempting to run localStationStaff.py from user scripts directory"
try:
	run("localStationStaff")
	print "localStationStaff.py completed."
except java.io.FileNotFoundException, e:
	print "No localStationStaff.py found in user scripts directory"
except:
	localStation_exception(sys.exc_info(), "running localStationStaff user script")

print "*"*80
print "Attempting to run localStationUser.py from user scripts directory"
try:
	run("localStationUser")
	print "localStationUser.py completed."
except java.io.FileNotFoundException, e:
	print "No localStationUser.py found in user scripts directory"
except:
	localStation_exception(sys.exc_info(), "running localStationUser user script")

if len(localStation_exceptions) > 0:
	simpleLog("=============== %r ERRORS DURING STARTUP ================" % len(localStation_exceptions))

for localStationException in localStation_exceptions:
	simpleLog(localStationException)

simpleLog("===================== GDA ONLINE =====================")
