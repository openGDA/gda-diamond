import sys;
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog

import cendac
import integrationTests
import CrysalisDataCollection
import pd_epicsdevice
import ruby_scripts
import gdascripts.pd.epics_pds
import gdascripts.pd.time_pds
import gdascripts.utils
import pd_ratio
import pd_baseTable
import dataDir
import shutterCommands
import marAuxiliary
import ccdAuxiliary
import ccdScanMechanics
import ccdFloodCorrections
import ccdScripts
import mar_scripts
import pilatus_scripts
import operationalControl

from operationalControl import *
from dummy_scan_objects import SimpleDummyDetector
from gda.configuration.properties import LocalProperties	
from gdascripts.parameters import beamline_parameters
from gda.device.epicsdevice import ReturnType
from gda.util import VisitPath
from constants import *
from dataPlot import dp
from meterCounterSetup import *
#from scan_commands import scan
from gdascripts.scan.installStandardScansWithProcessing import *
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()

from detector_scan_commands import *
from centreProxy import *
from scanPeak import *
from diodeTime import *
from setGain import *
from marAuxiliary import marErase, resetMarScanNumber
from ccdAuxiliary import resetCCDScanNumber
from pilatus_scripts import resetPilatusScanNumber

from dataDir import getDir, setDir, setFullUserDir
from time import sleep
from ccdFloodCorrections import exportMultiDark
from gda.epics import CAClient

def peakFinder():
	
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

try:
	simpleLog("================INITIALISING I15 GDA================")	
	
	scansReturnToOriginalPositions = 1;
	
	beamlineName = "i15"
	symbolicDataLink = "/dls/i15/data/currentdir"
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
		dcmpiezo = pd_epicsdevice.Simple_PD_EpicsDevice("dcmpiezo", beamline, "-OP-DCM-01:PIEZO:OUT")
		#s2ygap = pd_epicsdevice.Simple_PD_EpicsDevice("s2ygap", beamline, "-AL-SLITS-02:Y:GAP.VAL")
		#s2ycen = pd_epicsdevice.Simple_PD_EpicsDevice("s2ycen", beamline, "-AL-SLITS-02:Y:CENTRE.VAL")	
		#qbpX = pd_epicsdevice.Simple_PD_EpicsDevice("qbpX", beamline, "-DI-QBPMD-01:X.VAL")
		#qbpY = pd_epicsdevice.Simple_PD_EpicsDevice("qbpY", beamline, "-DI-QBPMD-01:Y.VAL")
		#qbpm2acurrent = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2acurrent", beamline, "-DI-IAMP-02:CHA:PEAK")
		#qbpm2bcurrent = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2bcurrent", beamline, "-DI-IAMP-02:CHB:PEAK")
		#qbpm2ccurrent = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2ccurrent", beamline, "-DI-IAMP-02:CHC:PEAK")
		#qbpm2dcurrent = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm2dcurrent", beamline, "-DI-IAMP-02:CHD:PEAK")	
	
		qbpm0A = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm0A", beamline, "-DI-QBPM-00:A")
		qbpm0B = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm0B", beamline, "-DI-QBPM-00:B")
		qbpm0C = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm0C", beamline, "-DI-QBPM-00:C")
		qbpm0D = pd_epicsdevice.Simple_PD_EpicsDevice("qbpm0D", beamline, "-DI-QBPM-00:D")

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

		#ring= finder.find("Ring")
		from gdascripts.pd.epics_pds import DisplayEpicsPVClass
		ringCurrent = DisplayEpicsPVClass("ringCurrent", "SR-DI-DCCT-01:SIGNAL", "mA", "%f")
		wigglerField = DisplayEpicsPVClass("wigglerField", "SR15I-ID-SCMPW-01:B_REAL", "Tesla", "%f")

		cryox = pd_epicsdevice.Simple_PD_EpicsDevice("cryox", beamline, "-MO-VCOLD-01:X.VAL")
		cryoy = pd_epicsdevice.Simple_PD_EpicsDevice("cryoy", beamline, "-MO-VCOLD-01:Y.VAL")
		cryoz = pd_epicsdevice.Simple_PD_EpicsDevice("cryoz", beamline, "-MO-VCOLD-01:Z.VAL")
		cryorot = pd_epicsdevice.Simple_PD_EpicsDevice("cryorot", beamline, "-MO-VCOLD-01:THETA.VAL")
		cryobsx = pd_epicsdevice.Simple_PD_EpicsDevice("cryobsx", beamline, "-MO-VCOLD-01:BS:X.VAL")
		cryobsy = pd_epicsdevice.Simple_PD_EpicsDevice("cryobsy", beamline, "-MO-VCOLD-01:BS:Y.VAL")
		
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None, "Error creating devices -  " , type, exception, traceback, False)

	dummyDetector = SimpleDummyDetector()
	
	try:
		import pd_pilatus
		pilatus = pd_pilatus.Pilatus("pilatus", "BL15I-EA-PILAT-02:", "/dls/i15/data/currentdir/", "pil")
	except:
		simpleLog("Pilatus did not connect")

	try:
		from gdascripts.scannable.detector.epics.EpicsPilatus import EpicsPilatus
		from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
		from gda.analysis.io import PilatusTiffLoader #, SRSLoader
		from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
		from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue #@UnusedImport
		from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak

		pildet = EpicsPilatus('pildet', 'BL15I-EA-PILAT-02:',"/dls/i15/data/currentdir/",'p','%s%s%d.tif')
		#pil = ProcessingDetectorWrapper('pil', pildet, [], panel_name='Pilatus Plot', toreplace=None, replacement=None, iFileLoader=PilatusTiffLoader, fileLoadTimout=15, returnPathAsImageNumberOnly=True)
		pil = ProcessingDetectorWrapper('pil', pildet, [], panel_name='Pilatus Plot', panel_name_rcp='Plot 1', toreplace=None, replacement=None, iFileLoader=PilatusTiffLoader, fileLoadTimout=15, returnPathAsImageNumberOnly=True)
		pil.processors=[DetectorDataProcessorWithRoi('max', pil, [SumMaxPositionAndValue()], False)]
		
		pil.printNfsTimes = True
		pil.display_image = True
		pilpeak2d = DetectorDataProcessorWithRoi('pilpeak2d', pil, [TwodGaussianPeak()])
		pilmax2d = DetectorDataProcessorWithRoi('pilmax2d', pil, [SumMaxPositionAndValue()])
	except:
		type, exception, traceback = sys.exc_info()
		simpleLog("New Pilatus (pil) did not connect")
		handle_messages.log(None, "Error -  " , type, exception, traceback, False)
		
	try:
		mar = finder.find("Mar345Detector")
	except:
		simpleLog("MAR did not connect")
		
	try:
		ccd = finder.find("ODCCD")
	except:
		simpleLog("ccd did not connect")
		
	try:
		ruby = ruby_scripts.Ruby(ccd)
	except:
		simpleLog("Ruby did not connect")
	
	try:
		ruby.connectIfNeeded()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None, "ruby error -  " , type, exception, traceback, False)
	
	try:
		atlas = ruby_scripts.Atlas(ccd)
	except:
		simpleLog("Atlas did not connect")
	
	try:
		atlas.connectIfNeeded()
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None, "atlas error -  " , type, exception, traceback, False)

	try:
		import scannables.detectors.perkinElmer as sdpe
		peid = sdpe.PerkinElmerInterface()
		pe = sdpe.PerkinElmer('pe', peid,
			"X:", "/dls/i15/data", "2011/cm2062-3", "tmp", "deletemeMBB")
		resetPEScanNumber = sdpe.resetPEScanNumberFactory(peid)
		alias("resetPEScanNumber")
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None, "pe error -  " , type, exception, traceback, False)

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
			type, exception, traceback = sys.exc_info()
			handle_messages.log(None, "%s error -  " % cam_name, type, exception, traceback, False)
	
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
	except:
		simpleLog("Could not create diodes")

	try:
		simpleLog("Create mca's")
		d1_mca = finder.find("D1_MCA")
		d2_mca = finder.find("D2_MCA")
		d3_mca = finder.find("D3_MCA")
		d4_mca = finder.find("D4_MCA")
	except:
		simpleLog("Could not create mca's")
		
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
		alias("d1out")
		alias("d2out")
		alias("d3out")
		alias("d4out")
		alias("align")
		alias("ready")
		alias("homeToMinus")
		alias("minusToHome")
		alias("homeToMinus57")
		alias("minus57ToMinus122")
		alias("expose")
		alias("resetCCDScanNumber")
		alias("incrementMarScanNumber")
		alias("resetMarScanNumber")
		alias("resetPilatusScanNumber")
	except:
		simpleLog("Could not setup aliases")
	
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
		simpleLog("Could not create ETL detector objects")
	
	try:
		simpleLog("Create checkbeam objects: checkbeam")
		from gdascripts.pd.pd_waitWhileScannableBelowThreshold import WaitWhileScannableBelowThreshold
		checkbeam = WaitWhileScannableBelowThreshold('checkbeam', scannableToMonitor=prop, minimumThreshold=5, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=30)
		checkbeam.setLevel(6)
		#from checkbeam_pds import * #@UnusedWildImport
		print "checkbeam level: %d" % checkbeam.getLevel()
	except:
		simpleLog("Could not create checkbeam objects")
	
	if True:
		try:
			from future.toggleBinaryPvAndWait import ToggleBinaryPvAndWait
			xps7out1trig = ToggleBinaryPvAndWait('xps7out1trig', 'BL15I-MO-XPS-07:GPIO:OUT1', normalLevel='1', triggerLevel='0')
		except:
			simpleLog("Could not create trigger_xps1 object")
	
	try:
		from scannables.safeScannable import SafeScannable
		rot_dkphi = SafeScannable('rot_dkphi', control_scannable=dkphi,
			check_scannable=shdx, threshold=200, failIfGreaterNotLessThan=False)
		alias('rot_dkphi')
	except:
		type, exception, traceback = sys.exc_info()
		handle_messages.log(None, "localStation error -  " , type, exception, traceback, False)
		simpleLog("Could not create rot_dkphi object")

	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	beamlineParameters = beamline_parameters.Parameters()
	
	dataDir.configure(jythonNameMap, beamlineParameters)	
	shutterCommands.configure(jythonNameMap, beamlineParameters)	
	marAuxiliary.configure(jythonNameMap, beamlineParameters)	
	operationalControl.configure(jythonNameMap, beamlineParameters)	
	ccdAuxiliary.configure(jythonNameMap, beamlineParameters)	
	ccdScanMechanics.configure(jythonNameMap, beamlineParameters)	
	ccdFloodCorrections.configure(jythonNameMap, beamlineParameters)	
#	ccdScripts.configure(jythonNameMap, beamlineParameters)	
	mar_scripts.configure(jythonNameMap, beamlineParameters)	
	pilatus_scripts.configure(jythonNameMap, beamlineParameters)	
	
	# meta should be created last to ensure we have all required scannables
	try:
		from gdascripts.scannable.installStandardScannableMetadataCollection import *
		meta.rootNamespaceDict=globals()
		note.rootNamespaceDict=globals()

		def stdmeta():
			stdmetadatascannables = (s1xpos, s1xgap, s1ypos, s1ygap,
				s1xplus, s1xminus, s1yplus, s1yminus, ringCurrent, wigglerField,
				dcmbragg1, dcmbragg2, 
				dcmxtl1y, dcmxtl2y, dcmxtl1roll, dcmxtl1z, dcmpiezo, dcmenergy,
				s6ypos, s6ygap, s6yup, s6ydown,
				hfm_x, hfm_y, hfm_pitch, hfm_curve, hfm_ellipticity, hfm_yaw, hfm_roll,
				vfm_x, vfm_y, vfm_pitch, vfm_curve, vfm_ellipticity, vfm_gravsag,
				qbpm2_x, qbpm2_y,
				s4xpos, s4xgap, s4ypos, s4ygap, s4yaw, s4pitch,
				pinx, piny, pinz, pinpitch, pinyaw,
				dx, dy, dz, dkphi, dkappa, dktheta,
				djack1, djack2, djack3, dtransx, drotation,
				bsx, bsy)
			setmeta_ret=setmeta(*stdmetadatascannables)
			simpleLog("Standard metadata scannables: " + setmeta_ret)
			#return ''

		stdmeta()
		simpleLog("Use 'stdmeta()' to reset to standard scannables")
		#alias('stdmeta')
		add_default(meta)
		meta.quiet = True
		
	except:
		simpleLog("Could not create metadata objects")

except:
	type, exception, traceback = sys.exc_info()
	handle_messages.log(None, "localStation error -  " , type, exception, traceback, False)
	simpleLog("localStation error")
	
simpleLog("===================== GDA ONLINE =====================")
