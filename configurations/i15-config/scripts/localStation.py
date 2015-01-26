import sys;
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog # @UnusedImport

import cendac # @UnusedImport
import integrationTests # @UnusedImport
import CrysalisDataCollection # @UnusedImport
import pd_epicsdevice # @UnusedImport
#import ruby_scripts
import gdascripts.pd.epics_pds # @UnusedImport
from gdascripts.pd.epics_pds import DisplayEpicsPVClass
import gdascripts.pd.time_pds
import gdascripts.utils # @UnusedImport
import pd_ratio
import pd_baseTable
import dataDir
import shutterCommands # @UnusedImport
import marAuxiliary # @UnusedImport
#from marAuxiliary import closeMarShield as closeDetectorShield
#from marAuxiliary import openMarShield as openDetectorShield
import ccdAuxiliary # @UnusedImport
import ccdScanMechanics
from ccdScanMechanics import setMaxVelocity # @UnusedImport
import ccdFloodCorrections
import ccdScripts # @UnusedImport
import pilatus_scripts # @UnusedImport
import operationalControl

from operationalControl import * # @UnusedWildImport
from dummy_scan_objects import SimpleDummyDetector
from gda.configuration.properties import LocalProperties
from gdascripts.parameters import beamline_parameters
from gda.device.epicsdevice import ReturnType
from gda.util import VisitPath
from constants import * # @UnusedWildImport
from dataPlot import dp # @UnusedImport
from meterCounterSetup import * # @UnusedWildImport
#from scan_commands import scan
from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()

#global zebraContinuousMoveController
import scannables.detectors.fastShutterZebraDetector
zebraFastShutter=scannables.detectors.fastShutterZebraDetector.FastShutterZebraDetector('zebraFastShutter', 'BL15I-EA-ZEBRA-01:', beamline_parameters.JythonNameSpaceMapping().zebraContinuousMoveController)

from gdascripts.scannable.epics.PvManager import PvManager
import scannables.detectorShield
ds=scannables.detectorShield.DetectorShield('ds', PvManager(pvroot='BL15I-RS-ABSB-06:'))

import scannables.MerlinColourModeThresholdsScannable
mcts=scannables.MerlinColourModeThresholdsScannable.MerlinColourModeThresholdsScannable('mcts',
    PvManager(pvroot='BL15I-EA-DET-18:Merlin1:'))

from detector_scan_commands import * # @UnusedWildImport
from centreProxy import * # @UnusedWildImport
#from scanPeak import *
from diodeTime import * # @UnusedWildImport
from setGain import * # @UnusedWildImport
#from marAuxiliary import marErase, resetMarScanNumber
#from ccdAuxiliary import resetCCDScanNumber
#from pilatus_scripts import resetPilatusScanNumber

from dataDir import setDir, setFullUserDir # @UnusedImport
from ccdFloodCorrections import exportMultiDark # @UnusedImport
from gda.epics import CAClient

global finder, run, etl, prop, add_default, vararg_regex, \
	s1xpos, s1xgap, s1ypos, s1ygap,\
	s1xplus, s1xminus, s1yplus, s1yminus,\
	dcmbragg1, dcmbragg2, dcmxtl1y, dcmxtl2y,\
	dcmxtl1roll, dcmxtl1z, dcmenergy,\
	qbpm1_x, qbpm1_y, qbpm1A, qbpm1B, qbpm1C, qbpm1D, qbpm1total,\
	s6ypos, s6ygap, s6yup, s6ydown,\
	vfm_x, vfm_y, vfm_pitch, vfm_curve, vfm_ellipticity, vfm_gravsag,\
	hfm_x, hfm_y, hfm_pitch, hfm_curve, hfm_ellipticity, hfm_yaw, hfm_roll,\
	qbpm2_x, qbpm2_y, qbpm2A, qbpm2B, qbpm2C, qbpm2D, qbpm2total,\
	s4xpos, s4xgap, s4ypos, s4ygap, s4yaw, s4pitch,\
	fsx, fsy,\
	pinx, piny, pinz, pinpitch, pinyaw,\
	dx, dy, dz, dmu, dkphi, dkappa, dktheta,\
	djack1, djack2, djack3, dtransx, drotation, detz, ddelta,\
	shdx, shdy, shdz,\
	bsx, bsy,\
	tab2jack1, tab2jack2, tab2jack3, tab2transx, tab2rotation,\
	s7xpos, s7ypos, s7xgap, s7xgap,\
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
	
	scansReturnToOriginalPositions = 1;
	
	beamlineName = "i15"
	commissioningProposal = "ee0"
	beamline = finder.find("Beamline")

	try:
		simpleLog("Creating devices")
		w = gdascripts.pd.time_pds.waittime
		baseTab = pd_baseTable.BaseTable("baseTab", beamline, "-MO-DIFF-01:BASE:", djack1, djack2, djack3, 2.5)
		baseTab2 = pd_baseTable.BaseTable("baseTab2", beamline, "-MO-TABLE-03:BASE:", tab2jack1, tab2jack2, tab2jack3, 2.5)
		qbpm1total = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm1total", beamline, "-DI-QBPM-01:INTEN")
		qbpm2total = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2total", beamline, "-DI-QBPM-02:INTEN")
		#s4pitch = pd_epicsdevice.Simple_PD_EpicsDevice("s4pitch", beamline, "-AL-SLITS-04:PITCH.VAL")
		#s4yaw = pd_epicsdevice.Simple_PD_EpicsDevice("s4yaw", beamline, "-AL-SLITS-04:YAW.VAL")
		#pin2x = pd_epicsdevice.Simple_PD_EpicsDevice("pin2x", beamline, "-AL-APTR-02:X")
		#pin2y = pd_epicsdevice.Simple_PD_EpicsDevice("pin2y", beamline, "-AL-APTR-02:Y")
		#pin2pitch = pd_epicsdevice.Simple_PD_EpicsDevice("pin2pitch", beamline, "-AL-APTR-02:PITCH")
		#pin2yaw = pd_epicsdevice.Simple_PD_EpicsDevice("pin2yaw", beamline, "-AL-APTR-02:YAW")
		ionc1 = pd_epicsdevice.Simple_PD_EpicsDevice("ionc1", beamline, "-DI-IONC-01:I")

		#prop = pd_epicsdevice.Simple_PD_EpicsDevice("prop", beamline, "-DI-PROP-01:I")
		#dcmpiezo = pd_epicsdevice.Simple_PD_EpicsDevice("dcmpiezo", beamline, "-OP-DCM-01:PIEZO:OUT")
		#s2ygap = pd_epicsdevice.Simple_PD_EpicsDevice("s2ygap", beamline, "-AL-SLITS-02:Y:GAP.VAL")
		#s2ycen = pd_epicsdevice.Simple_PD_EpicsDevice("s2ycen", beamline, "-AL-SLITS-02:Y:CENTRE.VAL")
		#qbpX = pd_epicsdevice.Simple_PD_EpicsDevice("qbpX", beamline, "-DI-QBPMD-01:X.VAL")
		#qbpY = pd_epicsdevice.Simple_PD_EpicsDevice("qbpY", beamline, "-DI-QBPMD-01:Y.VAL")
		#qbpm2acurrent = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2acurrent", beamline, "-DI-IAMP-02:CHA:PEAK")
		#qbpm2bcurrent = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2bcurrent", beamline, "-DI-IAMP-02:CHB:PEAK")
		#qbpm2ccurrent = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2ccurrent", beamline, "-DI-IAMP-02:CHC:PEAK")
		#qbpm2dcurrent = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2dcurrent", beamline, "-DI-IAMP-02:CHD:PEAK")
	
		qbpm1A = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm1A", beamline, "-DI-QBPM-01:A")
		qbpm1B = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm1B", beamline, "-DI-QBPM-01:B")
		qbpm1C = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm1C", beamline, "-DI-QBPM-01:C")
		qbpm1D = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm1D", beamline, "-DI-QBPM-01:D")

		qbpm2A = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2A", beamline, "-DI-QBPM-02:A")
		qbpm2B = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2B", beamline, "-DI-QBPM-02:B")
		qbpm2C = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2C", beamline, "-DI-QBPM-02:C")
		qbpm2D = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2D", beamline, "-DI-QBPM-02:D")

		vfm_gravsag = pd_epicsdevice.Simple_PD_EpicsDevice("vfm_gravsag", beamline, "-OP-VFM-01:SAG.VAL")

		spivotx = pd_epicsdevice.Simple_PD_EpicsDevice("spivotx", beamline, "-MO-SFAB-01:PIVOT:X")
		spivoty = pd_epicsdevice.Simple_PD_EpicsDevice("spivoty", beamline, "-MO-SFAB-01:PIVOT:Y")
		spivotz = pd_epicsdevice.Simple_PD_EpicsDevice("spivotz", beamline, "-MO-SFAB-01:PIVOT:Z")

		patch12x7 = pd_epicsdevice.Simple_PD_EpicsDevice("patch12x7", beamline, "-EA-PATCH-12:X7")
		patch12x8 = pd_epicsdevice.Simple_PD_EpicsDevice("patch12x8", beamline, "-EA-PATCH-12:X8")
		patch14x5 = pd_epicsdevice.Simple_PD_EpicsDevice("patch14x5", beamline, "-EA-PATCH-14:X5")
		patch14x6 = pd_epicsdevice.Simple_PD_EpicsDevice("patch14x6", beamline, "-EA-PATCH-14:X6")
		patch14x7 = pd_epicsdevice.Simple_PD_EpicsDevice("patch14x7", beamline, "-EA-PATCH-14:X7")

		patch12x13 = pd_epicsdevice.Simple_PD_EpicsDevice("patch12x13", beamline, "-EA-PATCH-12:X13")
		patch12x14 = pd_epicsdevice.Simple_PD_EpicsDevice("patch12x14", beamline, "-EA-PATCH-12:X14")

		#ring= finder.find("Ring")
		ringCurrent = DisplayEpicsPVClass("ringCurrent", "SR-DI-DCCT-01:SIGNAL", "mA", "%f")
		wigglerField = DisplayEpicsPVClass("wigglerField", "SR15I-ID-SCMPW-01:B_REAL", "Tesla", "%f")
		detz = DisplayEpicsPVClass("detz", "BL15I-MO-DIFF-01:ARM:DETECTOR:Z.VAL", "mm", "%f")
		
		patch12x6 = pd_epicsdevice.Simple_PD_EpicsDevice("patch12x6", beamline, "-EA-PATCH-12:X6")
		
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

	dummyDetector = SimpleDummyDetector()

	try:
		from scannable.CryojetScannable import CryojetScannable
		cryojet = CryojetScannable('cryojet', 'BL15I-CG-CJET-01:', 
									temp_tolerance=1, stable_time_sec=60)
	except:
		localStation_exception(sys.exc_info(), "creating cryojet scannable")

	try:
		import pd_pilatus
		pilatus = pd_pilatus.Pilatus("pilatus", "BL15I-EA-PILAT-02:", "/dls/i15/data/currentdir/", "pil")
	except:
		localStation_exception(sys.exc_info(), "creating pilatus")

	try:
		from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
		from gda.analysis.io import PilatusTiffLoader #, SRSLoader
		from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
		from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue #@UnusedImport
		from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak

		pildet = pd_pilatus.EpicsPilatus('pildet', 'BL15I-EA-PILAT-02:',"/dls/i15/data/currentdir/",'p','%s%s%d.tif')
		#pil = ProcessingDetectorWrapper('pil', pildet, [], panel_name='Pilatus Plot', toreplace=None, replacement=None, iFileLoader=PilatusTiffLoader, fileLoadTimout=15, returnPathAsImageNumberOnly=True)
		pil = ProcessingDetectorWrapper('pil', pildet, [], panel_name='Pilatus Plot', panel_name_rcp='Plot 1', toreplace=None, replacement=None, iFileLoader=PilatusTiffLoader, fileLoadTimout=15, returnPathAsImageNumberOnly=True)
		pil.processors=[DetectorDataProcessorWithRoi('max', pil, [SumMaxPositionAndValue()], False)]
		
		pil.printNfsTimes = True
		pil.display_image = True
		pilpeak2d = DetectorDataProcessorWithRoi('pilpeak2d', pil, [TwodGaussianPeak()])
		pilmax2d = DetectorDataProcessorWithRoi('pilmax2d', pil, [SumMaxPositionAndValue()])
	except:
		localStation_exception(sys.exc_info(), "creating new pilatus (pil...)")

	""" Remove ODCCD/Ruby/Atlas objects
	try:
		ccd = finder.find("ODCCD")
	except:
		localStation_exception(sys.exc_info(), "creating ccd")

	try:
		ruby = ruby_scripts.Ruby(ccd)
	except:
		localStation_exception(sys.exc_info(), "creating ruby")

	try:
		ruby.connectIfNeeded()
	except:
		localStation_exception(sys.exc_info(), "connecting ruby")

	try:
		atlas = ruby_scripts.Atlas(ccd)
	except:
		localStation_exception(sys.exc_info(), "creating atlas")
	
	try:
		atlas.connectIfNeeded()
	except:
		localStation_exception(sys.exc_info(), "connecting ruby")
	"""

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
			cam = ProcessingDetectorWrapper(cam_name, camdet, [], panel_name='GigE Camera', panel_name_rcp='Plot 1')
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

	try:
		simpleLog("Create diodes")
		finder.find("PHDGN1").configure()
		finder.find("PHDGN2").configure()
		finder.find("PHDGN3").configure()
		finder.find("PHDGN4").configure()
		finder.find("PHDGN5").configure()
		finder.find("PHDGN6").configure()
		finder.find("PHDGN7").configure()
		finder.find("PHDGN8").configure()
		finder.find("PHDGN9").configure()
		d1 = finder.find("PHDGN1").createEpicsChannel("d1", ReturnType.DBR_NATIVE, "", "")
		d1.setLevel(6)
		d2 = finder.find("PHDGN2").createEpicsChannel("d2", ReturnType.DBR_NATIVE, "", "")
		d2.setLevel(6)
		d3 = finder.find("PHDGN3").createEpicsChannel("d3", ReturnType.DBR_NATIVE, "", "")
		d3.setLevel(6)
		d4 = finder.find("PHDGN4").createEpicsChannel("d4", ReturnType.DBR_NATIVE, "", "")
		d4.setLevel(6)
		d5 = finder.find("PHDGN5").createEpicsChannel("d5", ReturnType.DBR_NATIVE, "", "")
		d5.setLevel(6)
		d6 = finder.find("PHDGN6").createEpicsChannel("d6", ReturnType.DBR_NATIVE, "", "")
		d6.setLevel(6)
		d7 = finder.find("PHDGN7").createEpicsChannel("d7", ReturnType.DBR_NATIVE, "", "")
		d7.setLevel(6)
		d8 = finder.find("PHDGN8").createEpicsChannel("d8", ReturnType.DBR_NATIVE, "", "")
		d8.setLevel(6)
		d9 = finder.find("PHDGN9").createEpicsChannel("d9", ReturnType.DBR_NATIVE, "", "")
		d9.setLevel(6)
		d1.setValue(".SCAN", 9)
		d2.setValue(".SCAN", 9)
		d3.setValue(".SCAN", 9)
		d4.setValue(".SCAN", 9)
		d5.setValue(".SCAN", 9)
		d6.setValue(".SCAN", 9)
		d7.setValue(".SCAN", 9)
		d8.setValue(".SCAN", 9)
		d9.setValue(".SCAN", 9)
		simpleLog("Create diode ratios")
		d2_d1 = pd_ratio.Simple_PD_Ratio('d2_d1', d2, d1)
		d3_d2 = pd_ratio.Simple_PD_Ratio('d3_d2', d3, d2)
		d4_d2 = pd_ratio.Simple_PD_Ratio('d4_d2', d4, d2)
		d5_d1 = pd_ratio.Simple_PD_Ratio('d5_d1', d5, d1)
		
		d1sum = DisplayEpicsPVClass("d1sum", "BL15I-DI-PHDGN-01:DIODESUM", "", "%f")
		d2sum = DisplayEpicsPVClass("d2sum", "BL15I-DI-PHDGN-02:DIODESUM", "", "%f")
		d3sum = DisplayEpicsPVClass("d3sum", "BL15I-DI-PHDGN-03:DIODESUM", "", "%f")
		d4sum = DisplayEpicsPVClass("d4sum", "BL15I-DI-PHDGN-04:DIODESUM", "", "%f")
		d5sum = DisplayEpicsPVClass("d5sum", "BL15I-DI-PHDGN-05:DIODESUM", "", "%f")
		#add_default(d1sum) - Moved to /dls/i15/scripts/localStationUser.py
	except:
		localStation_exception(sys.exc_info(), "creating diodes")

	try:
		simpleLog("Create mca's")
		d1_mca = finder.find("D1_MCA")
		d2_mca = finder.find("D2_MCA")
		d3_mca = finder.find("D3_MCA")
		d4_mca = finder.find("D4_MCA")
	except:
		localStation_exception(sys.exc_info(), "creating mca's")

	try:
		simpleLog("Setup aliases")
		vararg_regex("scan")
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
		alias("expose")
		alias("darkExpose")
		alias("rockScan")
		alias("rockScanUnsync")
		#alias("resetCCDScanNumber")
		#alias("incrementMarScanNumber")
		#alias("resetMarScanNumber")
		#alias("resetPilatusScanNumber")
	except:
		localStation_exception(sys.exc_info(), "setting up aliases")

	try:
		#simpleLog("Create ETL detector objects, names: etl_lowlim, etl_uplim, etl_gain")
		from detector_control_pds import * #@UnusedWildImport
		
		#print "ETL detector control values are: "
		#print "\tName  \t\tTarget   \tPosition"
		#pd_initialValues = [(pd.getName(), pd.getTargetPosition(), pd.Units[0], pd.getPosition(), pd.Units[0]) for pd in pds]
		#for pd_initialValue in pd_initialValues:
		#	print "\t%s:\t%7.1f%s\t%7.1f%s" % pd_initialValue
		#print

		etl.setLevel(7)
		#print "ETL detector level: %d" % etl.getLevel()
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
	if False:
		try:
			xps7out1trig = ToggleBinaryPvAndWait('xps7out1trig', 'BL15I-MO-XPS-07:GPIO:OUT1', normalLevel='1', triggerLevel='0')
		except:
			localStation_exception(sys.exc_info(), "creating xps7out1trig object")
	else:
		simpleLog("* Not creating xps7out1trig object *")
	
	if True:
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
	
	"""
	if False:
		try:
			from scannables.detectors.fastShutterDetector import FastShutterDetector
			fsdet = FastShutterDetector('fsdet', atlas)
		except:
			localStation_exception(sys.exc_info(), "creating fsdet object")
	else:
		simpleLog("* Not creating fsdet object *")
	"""
	
	try:
		from scannables.safeScannable import SafeScannable
		rot_dkphi = SafeScannable('rot_dkphi', control_scannable=dkphi,
			check_scannable=shdx, threshold=200, failIfGreaterNotLessThan=False)
		alias('rot_dkphi')
	except:
		localStation_exception(sys.exc_info(), "creating rot_dkphi object")

	try:
		from scannables.ContinuouslyRockingScannable import ContinuouslyRockingScannable
		dkphi_rocker = ContinuouslyRockingScannable('dkphi_rocker', scannable=dkphi)
		alias('dkphi_rocker')
	except:
		localStation_exception(sys.exc_info(), "creating dkphi_rocker object")

	try:
		from scannables.EpicsRockingScannable import EpicsRockingScannable
		dkphi_rockscan = EpicsRockingScannable('dkphi_rockscan', scannable=dkphi)
		alias('dkphi_rockscan')
	except:
		localStation_exception(sys.exc_info(), "creating dkphi_rockscan object")

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

	if False:
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

	if False:
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

	if True:
		from scannables.PerpendicularSampleMotion import PerpendicularSampleMotion, ParallelSampleMotion
	
		try:
			simpleLog("Creating dperp & dpara")
			dperp=PerpendicularSampleMotion("dperp", dx, dy, dmu, dkphi, True, 0, 58)
			dpara=ParallelSampleMotion     ("dpara", dx, dy, dmu, dkphi, True, 0, 58)
		except:
			localStation_exception(sys.exc_info(), "creating dperp & dpara")
	else:
		simpleLog("* Not creating dperp & dpara *")

	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	beamlineParameters = beamline_parameters.Parameters()
	
	dataDir.configure(jythonNameMap, beamlineParameters)
	shutterCommands.configure(jythonNameMap, beamlineParameters)
	#marAuxiliary.configure(jythonNameMap, beamlineParameters)
	operationalControl.configure(jythonNameMap, beamlineParameters)
	#ccdAuxiliary.configure(jythonNameMap, beamlineParameters)
	ccdScanMechanics.configure(jythonNameMap, beamlineParameters)
	ccdFloodCorrections.configure(jythonNameMap, beamlineParameters)
#	ccdScripts.configure(jythonNameMap, beamlineParameters)
#	pilatus_scripts.configure(jythonNameMap, beamlineParameters)
	
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
		# metashop is defined in mt-config/servers/main/common/required_at_start.py

		simpleLog("Metadata scannables, from configuration: " + " ".join(str(x.name) for x in metashop.getMetaScannables()))

		# New metadata system doesn't allow metadata scannables to be set
		def stdmeta():
			""" This function resets the metadata scannables to the standard list in localststion"""
			stdmetadatascannables = ('ringCurrent', 'wigglerField',
				's1xpos', 's1xgap', 's1ypos', 's1ygap',
				's1xplus', 's1xminus', 's1yplus', 's1yminus',
				'dcmbragg1', 'dcmbragg2', 'dcmxtl1y', 'dcmxtl2y',
				'dcmxtl1roll', 'dcmxtl1z', 'dcmenergy',
				'qbpm1_x', 'qbpm1_y', 'qbpm1A', 'qbpm1B', 'qbpm1C', 'qbpm1D', 'qbpm1total',
				's6ypos', 's6ygap', 's6yup', 's6ydown',
				'vfm_x', 'vfm_y', 'vfm_pitch', 'vfm_curve', 'vfm_ellipticity', 'vfm_gravsag',
				'hfm_x', 'hfm_y', 'hfm_pitch', 'hfm_curve', 'hfm_ellipticity', 'hfm_yaw', 'hfm_roll',
				'qbpm2_x', 'qbpm2_y', 'qbpm2A', 'qbpm2B', 'qbpm2C', 'qbpm2D', 'qbpm2total',
				's4xpos', 's4xgap', 's4ypos', 's4ygap', 's4yaw', 's4pitch',
				'fsx', 'fsy',
				'pinx', 'piny', 'pinz', 'pinpitch', 'pinyaw',
				'thermo1', 'thermo2', 'thermo3', 'pt100_1',
				'dx', 'dy', 'dz', 'dkphi', 'dkappa', 'dktheta',
				'djack1', 'djack2', 'djack3', 'dtransx', 'drotation', 'detz', 'ddelta',
				'shdx', 'shdy', 'shdz',
				'bsx', 'bsy',
				'tab2jack1', 'tab2jack2', 'tab2jack3', 'tab2transx', 'tab2rotation',
				's7xpos', 's7ypos', 's7xgap', 's7xgap',
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
				'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8', 'd9',
				'd1sum', 'd2sum', 'd3sum', 'd4sum', 'd5sum',
				'cryox', 'cryoy', 'cryoz', 'cryorot'
				)
			
			before=set(metashop.getMetaScannables())
			errors=[]
			for scn_name in stdmetadatascannables:
				try:
					scn=finder.find(scn_name)
					meta_add(scn)
				except:
					errors.append(scn_name)
			after=set(metashop.getMetaScannables())
			if (before-after):
				simpleLog("Metadata scannables, removed:            " + " ".join(str(x.name) for x in before-after))
			if (after-before):
				simpleLog("                     added:              " + " ".join(str(x.name) for x in after-before))
			if (after):
				simpleLog("                     current:            " + " ".join(str(x.name) for x in after))
			if (errors):
				simpleLog("                     erroring:           " + " ".join(x for x in errors))
			#return ''

		stdmeta()
		simpleLog("Use 'stdmeta' to reset to standard scannables")
		alias('stdmeta')
		add_default(meta)
		meta.quiet = True
		
	except:
		localStation_exception(sys.exc_info(), "creating metadata objects")

except:
	localStation_exception(sys.exc_info(), "in localStation")

print "*"*80
print "Attempting to run localStationUser.py from users script directory"
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
