import sys	
import os
import time
from gdascripts.messages import handle_messages
from gda.jython import InterfaceProvider
from gda.device.scannable import ScannableBase
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
		if new_position == self.rawGetPosition():
			return
		if new_position == "Open":
			self.delegate.asynchronousMoveTo(1)
		else:
			self.delegate.asynchronousMoveTo(0)
		time.sleep(.25) #sleep to allow shutter to 
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
		
try:
	from gda.device import Scannable
	from gda.jython.commands.GeneralCommands import ls_names, vararg_alias
	
	def ls_scannables():
		ls_names(Scannable)


	from pv_scannable_utils import createPVScannable, caput, caget
	alias("createPVScannable")
	alias("caput")
	alias("caget")
	


	from gda.factory import Finder
	from gda.configuration.properties import LocalProperties


#	from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
	import i13i
	
	from gda.util import VisitPath
	
	finder = Finder.getInstance() 
	beamline = finder.find("Beamline")
	ring= finder.find("Ring")
	commandServer = InterfaceProvider.getJythonNamespace()
#	import tests.testRunner
#	tests.testRunner.run_tests()
	
	from gda.scan.RepeatScan import create_repscan, repscan
	vararg_alias("repscan")

	from gdascripts.metadata.metadata_commands import setTitle
	alias("setTitle")

	
	from gdascripts.pd.time_pds import waittimeClass2, showtimeClass, showincrementaltimeClass, actualTimeClass
	waittime=waittimeClass2('waittime')
	showtime=showtimeClass('showtime')
	inctime=showincrementaltimeClass('inctime')
	actualTime=actualTimeClass("actualTime")
	
	from flyscan_script import flyscan, flyscannable, WaitForScannableAtLineEnd
	vararg_alias("flyscan")
#	waitForQcm_bragg1 = WaitForScannableAtLineEnd('waitForQcm_bragg1', qcm_bragg1)
	
	try:
		if not LocalProperties.check("gda.dummy.mode"):
			createPVScannable( "d1_total", "BL13I-DI-PHDGN-01:STAT:Total_RBV")
			createPVScannable( "expt_fastshutter_raw", "BL13I-EA-FSHTR-01:CONTROL", hasUnits=False)
			expt_fastshutter = ExperimentShutterEnumPositioner("expt_fastshutter", expt_fastshutter_raw)
			
			#if you change these you need to change the values in cameraScaleProviders
			lensX2="X2 7mm x 5mm"
			lensX4="X4 4mm x 3mm"
			lensX4Pink="X4 CWD 200"
			lensX10="X10 2mm x 1mm"
			
			caput("BL13I-EA-TURR-01:DEMAND.ZRST",lensX2 )
			caput("BL13I-EA-TURR-01:CURRENTPOS.ZRST", lensX2)
		
			caput("BL13I-EA-TURR-01:DEMAND.ONST", "2")
			caput("BL13I-EA-TURR-01:CURRENTPOS.ONST", "2")
			caput("BL13I-EA-TURR-01:DEMAND.TWST", "3")
			caput("BL13I-EA-TURR-01:CURRENTPOS.TWST", "3")
			caput("BL13I-EA-TURR-01:DEMAND.THST", "4")
			caput("BL13I-EA-TURR-01:CURRENTPOS.THST", "4")
			caput("BL13I-EA-TURR-01:DEMAND.FRST", "5")
			caput("BL13I-EA-TURR-01:CURRENTPOS.FRST", "5")
		
		
			caput("BL13I-EA-TURR-01:DEMAND.FVST", lensX4)
			caput("BL13I-EA-TURR-01:CURRENTPOS.FVST", lensX4)
			caput("BL13I-EA-TURR-01:DEMAND.SXST", lensX10)
			caput("BL13I-EA-TURR-01:CURRENTPOS.SXST", lensX10)
			#make the lens re-read its list of positions following setting them in EPICS above
			lens.initializationCompleted()

	except :
		exceptionType, exception, traceback = sys.exc_info()
		handle_messages.log(None, "Error creating pvScannables", exceptionType, exception, traceback, False)
			
	#make scannablegroup for driving sample stage
#	from gda.device.scannable.scannablegroup import ScannableGroup
#	t1_xy = ScannableGroup()
#	t1_xy.addGroupMember(t1_sx)
#	t1_xy.addGroupMember(t1_sy)
#	t1_xy.addGroupMember(ix)
#	t1_xy.setName("t1_xy")
#	t1_xy.configure()
	
	#make ScanPointProvider
	import sample_stage_position_provider
	two_motor_positions = sample_stage_position_provider.ScanPositionProviderFromFile()
#	two_motor_positions.load("/dls_sw/i13/software/gda_versions/gda_trunk/i13i-config/scripts/tests/sample_stage_position_provider_test.dat",(0.,0.))

	imageFitter = finder.find("imageFitter")
	imageStats = finder.find("imageStats")
	imagePlotter = finder.find("imagePlotter")
	imageROI = finder.find("imageROI")


	#create objects in namespace
#	mpx_controller = mpx.getMaxiPix2MultiFrameDetector()
#	mpx_threshold = mpx_controller.energyThreshold
#	mpx_limaCCD = mpx_controller.getLimaCCD()
#	mpx_maxipix = mpx_controller.getMaxiPix2()
#	mpx_reset_configure()
	
	import file_converter
	
#	import integrate_mpx_scan
#	try:
#		mpx_set_folder("test","mpx")
#	except :
#		exceptionType, exception, traceback = sys.exc_info()
#		handle_messages.log(None, "Problem setting mpx folder and prefix",exceptionType, exception, traceback,False)
	#from tests.testRunner import run_tests

	try:
		if not LocalProperties.check("gda.dummy.mode"):
			import autocollimator_script
			autocollimator_script.setup()
			import alignmentGui
			tomodet = alignmentGui.TomoDet()
			#setup trigger for pink beam
			pco1_hw_tif.collectionStrategy.shutterDarkScannable = eh_shtr_dummy
			pco1_hw_hdf.collectionStrategy.shutterDarkScannable = eh_shtr_dummy
	except :
		exceptionType, exception, traceback = sys.exc_info()
		handle_messages.log(None, "Error connecting to autocollimator", exceptionType, exception, traceback, False)
	
	import tomographyScan
	
#	run("i13diffcalc")
	import raster_scan
	

except :
	exceptionType, exception, traceback = sys.exc_info()
	handle_messages.log(None, "Error in localStation", exceptionType, exception, traceback, False)

