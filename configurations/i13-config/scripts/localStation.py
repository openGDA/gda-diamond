import sys	
import os
import time
from gdascripts.messages import handle_messages
from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableBase
from gda.jython.commands import GeneralCommands
from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names, vararg_alias

import tomographyXGIScan
from tomographyXGIScan import tomoXGIScan
import tomographyXGIScan2d
from tomographyXGIScan2d import tomoXGIScan2d

from i13i_utilities import pco_edge_agg, pco_4000_agg, filter_sticks, xray_mode, isLive

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

def interruptable():
	"""
	Fn to facilitate making for-loops interruptable in GDA: need to call this fn in the 1st or the last line of a for-loop
	"""
	GeneralCommands.pause()

def ls_scannables():
	ls_names(Scannable)

#--------------------------------------------------------------------------------------------------------------

def meta_add_i13i():
	fname = meta_add_i13i.__name__
	print "\n Adding scan meta-data items (to be recorded in every Nexus scan file as part of the before_scan group)..."
	
	# add meta-data scannables
	meta_scannables = []
	meta_scannables.append(filters)
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
			#meta_texts_cam.update({"focus_pco_edge_label": "BL13I-MO-STAGE-02:FOCUS2:MP:RBV:CURPOS"})
			#meta_texts_cam.update({"focus_pco_edge": "BL13I-MO-STAGE-02:FOCUS2.RBV"})
			meta_scannables.append(pco_edge_agg)
		elif "4000" in pco_cam_model_rbv.lower():
			#meta_texts_cam.update({"focus_pco_4000_label": "BL13I-MO-STAGE-02:FOCUS:MP:RBV:CURPOS"})
			#meta_texts_cam.update({"focus_pco_4000": "BL13I-MO-STAGE-02:FOCUS.RBV"})
			meta_scannables.append(pco_4000_agg)
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
	#meta_texts.update(meta_texts_cam)
	#meta_texts.update({"filter_stick_1": "BL13I-OP-ATTN-01:STICK1:MP:RBV:CURPOS"})
	#meta_texts.update({"filter_stick_2": "BL13I-OP-ATTN-01:STICK2:MP:RBV:CURPOS"})
	#meta_texts.update({"filter_stick_3": "BL13I-OP-ATTN-01:STICK3:MP:RBV:CURPOS"})
	#meta_texts.update({"filter_stick_4": "BL13I-OP-ATTN-01:STICK4:MP:RBV:CURPOS"})
	#meta_texts.update({"filter_stick_5": "BL13I-OP-ATTN-01:STICK5:MP:RBV:CURPOS"})
	
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
	
	meta_scannables.append(filter_sticks)
	meta_scannables.append(xray_mode)
	for s in meta_scannables:
		meta_add(s)
	print "\n Finished adding scan meta-data items!"

#--------------------------------------------------------------------------------------------------------------

try:
	from epics_scripts.pv_scannable_utils import createPVScannable, caput, caget, caputStringAsWaveform, ls_pv_scannables
	alias("ls_pv_scannables")

	from gda.factory import Finder
	from gda.configuration.properties import LocalProperties

	from i13i_utilities import wd, cfn, nfn, pwd, nwd, send_email
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
#	import tests.testRunner
#	tests.testRunner.run_tests()
	
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
#	waitForQcm_bragg1 = WaitForScannableAtLineEnd('waitForQcm_bragg1', qcm_bragg1)

	expt_fastshutter = ExperimentShutterEnumPositioner("expt_fastshutter", fastshutter)
	
	if isLive():
		try:
			#if you change these you need to change the values in cameraScaleProviders
			#edited by J. Vila-Comamala to match new objective lens configuration 25.04.2014
			position1="Empty"
			position2="Empty"
			position3="Empty"
			position4="Empty"
			position5="10x Pink"
			position6="4x Pink"
			position7="2x Pink"

			caput("BL13I-EA-TURR-01:DEMAND.ZRST",position1)
			caput("BL13I-EA-TURR-01:CURRENTPOS.ZRST", position1)
			caput("BL13I-EA-TURR-01:DEMAND.ONST", position2)
			caput("BL13I-EA-TURR-01:CURRENTPOS.ONST", position2)
			caput("BL13I-EA-TURR-01:DEMAND.TWST", position3)
			caput("BL13I-EA-TURR-01:CURRENTPOS.TWST", position3)
			caput("BL13I-EA-TURR-01:DEMAND.THST", position4)
			caput("BL13I-EA-TURR-01:CURRENTPOS.THST", position4)
			caput("BL13I-EA-TURR-01:DEMAND.FRST", position5)
			caput("BL13I-EA-TURR-01:CURRENTPOS.FRST", position5)
			caput("BL13I-EA-TURR-01:DEMAND.FVST", position6)
			caput("BL13I-EA-TURR-01:CURRENTPOS.FVST", position6)
			caput("BL13I-EA-TURR-01:DEMAND.SXST", position7)
			caput("BL13I-EA-TURR-01:CURRENTPOS.SXST", position7)


			#make the lens re-read its list of positions following setting them in EPICS above
			lens.initializationCompleted()

		except:
			exceptionType, exception, traceback = sys.exc_info()
			handle_messages.log(None, "Error setting initial positions for lens", exceptionType, exception, traceback, False)


		from dcm_energy_mode import DcmEnergyMode
		energy_mode = DcmEnergyMode()
			
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

	#for fast flyscans
	if isLive():
		flyScanDetector.pluginList[1].ndFileHDF5.file.filePathConverter.windowsSubString="d:\\i13\\data"
	else:
		flyScanDetector.readOutTime=.03 #Manta_G-125B camera	
#		flyScanDetector.pluginList[1].ndFileHDF5.file.filePathConverter.windowsSubString="c:\\data"	

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

		run("localStationUser.py")

		from deben import *
		deben_configure()

		# add meta-data for all scans on this beamline
		meta_add_i13i()
		caput("BL13I-MO-HEX-01:SAMPLEROT.VMAX", 100.0)
	
except:
	exceptionType, exception, traceback = sys.exc_info()
	handle_messages.log(None, "Error in localStation", exceptionType, exception, traceback, False)

