import sys	
import os
import time
from gdascripts.messages import handle_messages
from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableBase
from gda.jython.commands import GeneralCommands
from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names, vararg_alias
from gda.data import PathConstructor

import tomographyXGIScan
from tomographyXGIScan import tomoXGIScan
import tomographyXGIScan2d
from tomographyXGIScan2d import tomoXGIScan2d

from i13i_utilities import isLive, interruptable
from i13i_utilities import pco_edge_agg, pco_4000_agg, filter_sticks, filter_stick_1, filter_stick_2, filter_stick_3, filter_stick_4, filter_stick_5, beamline_xray_mode
from i13i_utilities import ionc_A_over_V_gain, ionc_gainmode, ionc_acdc

section_sep = "-"*128
class ExperimentShutterEnumPositioner(ScannableBase):
	"""
	Class to handle experimental hutch shutter
	"""
	def __init__(self, name, delegate):
		self.name = name
		self.inputNames = [name]
		self.delegate = delegate
	def isBusy(self):
		return self.delegate.isBusy()
	def rawAsynchronousMoveTo(self,new_position):
		if new_position == self.rawGetPosition():
			return
		if new_position == "Open":
			self.delegate.asynchronousMoveTo(1)
		else:
			self.delegate.asynchronousMoveTo(0)
		time.sleep(.25) #sleep to allow shutter to get into position
	def rawGetPosition(self):
		position = self.delegate.getPosition()
		if int(position) == 1:
			return "Open" 
		return "Closed"

def eh_shtr_control():
	if eh_shtr()=="Open":
		pos eh_shtr "Close"
	else:
		pos eh_shtr "Reset"
		time.sleep(3)
		pos eh_shtr "Open"

def fs_control():
	if fs()=="Open":
		pos fs "Closed"
	else:
		pos fs "Open"


def ls_scannables():
	ls_names(Scannable)

print(section_sep)

def meta_add_i13i():
	fname = meta_add_i13i.__name__
	print "\n Adding scan meta-data items (to be recorded in every Nexus scan file as part of the before_scan group)..."
	
	# add meta-data scannables
	meta_scannables = []
	meta_scannables.append(filter_aperture)
	meta_scannables.append(filter1)
	meta_scannables.append(filter2)
	meta_scannables.append(filter3)
	meta_scannables.append(filter4)
	meta_scannables.append(filter5)
	meta_scannables.append(id_gap)
	meta_scannables.append(s1)
	meta_scannables.append(s2)
	meta_scannables.append(s3)
	meta_scannables.append(s4)
	
	
	# add meta-data texts
	meta_texts_cam = {}
	meta_texts_cam.update({"pco_cam_model": "BL13I-EA-DET-01:CAM:Model_RBV"})
	try:
		cam_pv = meta_texts_cam["pco_cam_model"]
		pco_cam_model_rbv = caget(cam_pv)
		if "edge" in pco_cam_model_rbv.lower():
			pass
		elif "4000" in pco_cam_model_rbv.lower():
			pass
		elif "dimax" in pco_cam_model_rbv.lower():
			pass
		else:
			if pco_cam_model_rbv is not None:
				print "Unsupported camera %s detected in %s!" %(pco_cam_model_rbv,fname)
	except:
		rbv = "caget failed"
		rbv_ = rbv + " on %s!" %(cam_pv)
		msg = "Error in %s: " %(fname)
		exceptionType, exception, traceback = sys.exc_info()
		handle_messages.log(None, msg + rbv_, exceptionType, exception, traceback, False)
	
	meta_texts = {}
	
	for k, v in meta_texts.iteritems():
		try:
			rbv = caget(v)
		except:
			rbv = "caget failed"
			rbv_ = rbv + " on %s!" %(v)
			msg = "Error in %s: " %(fname)
			exceptionType, exception, traceback = sys.exc_info()
			handle_messages.log(None, msg + rbv_, exceptionType, exception, traceback, False)
		meta_add(k, rbv)
	
	for s in meta_scannables:
		meta_add(s)
		
	meta_add("filter_stick_1", filter_stick_1())
	meta_add("filter_stick_2", filter_stick_2())
	meta_add("filter_stick_3", filter_stick_3())
	meta_add("filter_stick_4", filter_stick_4())
	meta_add("filter_stick_5", filter_stick_5())
	meta_add("beamline_xray_mode", beamline_xray_mode())
	meta_add("ionc_A_over_V_gain", ionc_A_over_V_gain())
	meta_add("ionc_gainmode", ionc_gainmode())
	meta_add("ionc_acdc", ionc_acdc())
	
	print "\n Finished adding meta-data items!"

print(section_sep)

try:
	from epics_scripts.pv_scannable_utils import createPVScannable, caput, caget, caputStringAsWaveform, ls_pv_scannables
	alias("ls_pv_scannables")

	from gda.factory import Finder
	from gda.configuration.properties import LocalProperties

	from i13i_utilities import wd, cfn, nfn, pwd, nwd, send_email, use_storage, report_storage
	alias("wd")
	alias("cfn")
	alias("nfn")
	alias("pwd")
	alias("nwd")
	
	import i13i

	from gda.util import VisitPath
	
	finder = Finder.getInstance() 
	beamline = finder.find("Beamline")
	ring = finder.find("Ring")
	commandServer = InterfaceProvider.getJythonNamespace()
	
	from gda.scan.RepeatScan import create_repscan, repscan
	vararg_alias("repscan")

	from gdascripts.metadata.metadata_commands import setTitle, getTitle, meta_add, meta_ll, meta_ls, meta_rm
	alias("setTitle")
	alias("meta_add")
	alias("meta_ll")
	alias("meta_ls")
	alias("meta_rm")

	from gda.data.scan.datawriter import NexusDataWriter
	LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop")
	
	from gdascripts.pd.time_pds import waittimeClass2, showtimeClass, showincrementaltimeClass, actualTimeClass
	waittime=waittimeClass2('waittime')
	showtime=showtimeClass('showtime')
	inctime=showincrementaltimeClass('inctime')
	actualTime=actualTimeClass("actualTime")
	
	from flyscan_script import flyscan, flyscannable, WaitForScannableAtLineEnd
	vararg_alias("flyscan")

	expt_fastshutter = ExperimentShutterEnumPositioner("expt_fastshutter", fastshutter)
	
	if isLive():
		try:
			#if you change these you need to change the values in cameraScaleProviders
			#edited by J. Vila-Comamala to match new camera 1 objective lens configuration 25.04.2014
			position1="Empty"
			position2="Empty"
			position3="Empty"
			position4="Empty"
			position5="10x Pink"
			position6="4x Pink"
			position7="2x Pink"

			turret_prefix = "BL13I-MO-CAM-01:TURRET"
			caput(turret_prefix + ":DEMAND.ZRST",position1)
			caput(turret_prefix + ":CURRENTPOS.ZRST", position1)
			caput(turret_prefix + ":DEMAND.ONST", position2)
			caput(turret_prefix + ":CURRENTPOS.ONST", position2)
			caput(turret_prefix + ":DEMAND.TWST", position3)
			caput(turret_prefix + ":CURRENTPOS.TWST", position3)
			caput(turret_prefix + ":DEMAND.THST", position4)
			caput(turret_prefix + ":CURRENTPOS.THST", position4)
			caput(turret_prefix + ":DEMAND.FRST", position5)
			caput(turret_prefix + ":CURRENTPOS.FRST", position5)
			caput(turret_prefix + ":DEMAND.FVST", position6)
			caput(turret_prefix + ":CURRENTPOS.FVST", position6)
			caput(turret_prefix + ":DEMAND.SXST", position7)
			caput(turret_prefix + ":CURRENTPOS.SXST", position7)


			#make the lens re-read its list of positions following setting them in EPICS above
			cam01_objective.initializationCompleted()

		except:
			exceptionType, exception, traceback = sys.exc_info()
			handle_messages.log(None, "Error setting initial positions for cam01_objective", exceptionType, exception, traceback, False)


		from dcm_energy_mode import DcmEnergyMode
		energy_mode = DcmEnergyMode()

	from dcm_yz import DcmFreezeYZ
	dcm_freeze_yz = DcmFreezeYZ(isLive(), 'BL13I-OP-DCM-01:LOCKYZ')

	from gda.device.scannable.scannablegroup import ScannableGroup
	
	#make ScanPointProvider
	import sample_stage_position_provider
	two_motor_positions = sample_stage_position_provider.ScanPositionProviderFromFile()
#	two_motor_positions.load("/dls_sw/i13/software/gda_versions/gda_trunk/i13i-config/scripts/tests/sample_stage_position_provider_test.dat",(0.,0.))

	imageFitter = finder.find("imageFitter")
	imageStats = finder.find("imageStats")
	imagePlotter = finder.find("imagePlotter")
	imageROI = finder.find("imageROI")

	import file_converter
	
	if isLive():
		try:
			import autocollimator_script
			autocollimator_script.setup()

			#setup trigger for pink beam
			pco1_hw_tif.collectionStrategy.shutterDarkScannable = eh_shtr_dummy
			pco1_hw_hdf.collectionStrategy.shutterDarkScannable = eh_shtr_dummy

		except :
			exceptionType, exception, traceback = sys.exc_info()
			handle_messages.log(None, "Error connecting to autocollimator", exceptionType, exception, traceback, False)

	import alignmentGui
	tomodet = alignmentGui.TomoDet()

	
	import tomographyScan
	from tomographyScan import reportJythonNamespaceMapping, reportTomo
	alias("reportJythonNamespaceMapping")
	alias("reportTomo")
	tomography_additional_scannables=[] #=[p2r_force, p2r_y]
	from p2r_utilities import p2r_telnet

	#for fast flyscans
	if isLive():
		flyScanDetector.pluginList[1].ndFileHDF5.file.filePathConverter.windowsSubString="d:\\i13\\data"
	else:
		flyScanDetector.readOutTime=.03 #Manta_G-125B camera	

	import raster_scan

	if isLive():
		data_dir = "/dls/$instrument$/data/$year$/$visit$/raw"
	else:
		data_dir = LocalProperties.get("gda.config") + "/../../../gda_data_non_live/cs-scratch/i13i-dummy"

	LocalProperties.set("gda.data.scan.datawriter.datadir", data_dir)
	LocalProperties.set("gda.data", data_dir)

	import beamlineEnergy
	bl = beamlineEnergy.beamLineEnergy()
	bl.setName("bl")

	if isLive():
		pco1_hw_tif.pluginList[1].waitForFileArrival=False
		pco1_tif.pluginList[1].waitForFileArrival=False
	
		#reverse the camera image so that the image is as looking upstream
		caput ("BL13I-EA-DET-01:CAM:ReverseX", 1)
		if( caget("BL13I-EA-DET-01:CAM:Model_RBV") == "PCO.Camera 4000"):
			caput("BL13I-EA-DET-01:CAM:PIX_RATE", "32000000 Hz")
			pco4000_readout=0.21
			flyScanDetector.readOutTime=pco4000_readout
			flyScanDetectorNoChunking.readOutTime=pco4000_readout
			p2r_flyScanDetector.getCollectionStrategy().setReadoutTime(pco4000_readout)
			p2r_flyScanDetector.readOutTime=pco4000_readout		
		if( caget("BL13I-EA-DET-01:CAM:Model_RBV") == "PCO.Camera Edge"):
			caput("BL13I-EA-DET-01:CAM:PIX_RATE", "286000000 Hz")
			pcoEdge_readout=0.011
			flyScanDetector.readOutTime=pcoEdge_readout
			flyScanDetectorNoChunking.readOutTime=pcoEdge_readout
			p2r_flyScanDetector.getCollectionStrategy().setReadoutTime(pcoEdge_readout)
			p2r_flyScanDetector.readOutTime=pcoEdge_readout
	
		# Ensure rot speed is set in case GDA has crashed during fly scan.
		ss1_rot.motor.speed=45
		# set up tiff plug-in for saving images to NetApp 
		caput("BL13I-EA-DET-01:TIFF:CreateDirectory", 1)
		caput("BL13I-EA-DET-01:TIFF:TempSuffix", ".tmp")

		# Set ports of file-writing plugins 
		caput("BL13I-EA-DET-01:TIFF:NDArrayPort", caget("BL13I-EA-DET-01:CAM:PortName_RBV"))
		caput("BL13I-EA-DET-01:HDF5:NDArrayPort", caget("BL13I-EA-DET-01:CAM:PortName_RBV"))

		run("localStationUser.py")

		from deben import *
		deben_configure()
		deben_after_ioc_restart()

		print("\n Adding beamline meta scannables...")
		meta_add_i13i()
		caput("BL13I-MO-HEX-01:SAMPLEROT.VMAX", 100.0)
		createPVScannable('xgi_sample_rot','BL13I-MO-SMAR-02:RY.VAL')
		createPVScannable('xgi_sample_x','BL13I-MO-SMAR-02:X.VAL')
		createPVScannable('xgi_sample_y','BL13I-MO-SMAR-02:Y.VAL')
		createPVScannable('xgi_sample_z','BL13I-MO-SMAR-02:Z.VAL')
		
		createPVScannable('xgi_grat_x','BL13I-MO-SMAR-01:X2.VAL')
		createPVScannable('xgi_grat_y','BL13I-MO-SMAR-01:Y2.VAL')
		createPVScannable('xgi_grat_z','BL13I-MO-SMAR-01:Z2.VAL')
		
		_stressTesting = False
		if _stressTesting:
			from i13i_utilities import stressTest
			LocalProperties.set("gda.data.scan.datawriter.datadir", "/dls/$instrument$/data/$year$/$visit$/tmp")

except:
	exceptionType, exception, traceback = sys.exc_info()
	handle_messages.log(None, "Error in localStation", exceptionType, exception, traceback, False)

