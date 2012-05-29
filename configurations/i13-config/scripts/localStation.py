import sys	
import os
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
		if new_position == "Open":
			self.delegate.asynchronousMoveTo(5.)
		else:
			self.delegate.asynchronousMoveTo(0.)
	def rawGetPosition(self):
		position = self.delegate.getPosition()
		if int(position) == 5:
			return "Open" 
		return "Closed"

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
	
	from gdascripts.pd.time_pds import waittimeClass2, showtimeClass, showincrementaltimeClass, actualTimeClass
	waittime=waittimeClass2('waittime')
	showtime=showtimeClass('showtime')
	inctime=showincrementaltimeClass('inctime')
	actualTime=actualTimeClass("actualTime")
	
	from flyscan_script import flyscan, flyscannable, WaitForScannableAtLineEnd
	vararg_alias("flyscan")
#	waitForQcm_bragg1 = WaitForScannableAtLineEnd('waitForQcm_bragg1', qcm_bragg1)
	
	if not LocalProperties.check("gda.dummy.mode"):
		createPVScannable( "d1_total", "BL13I-DI-PHDGN-01:STAT:Total_RBV")
		createPVScannable( "expt_fastshutter_raw", "BL13I-EA-FSHTR-01:RAWCONTROL", hasUnits=False)
		expt_fastshutter = ExperimentShutterEnumPositioner("expt_fastshutter", expt_fastshutter_raw)
	
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

	import autocollimator_script
	if not LocalProperties.check("gda.dummy.mode"):
		autocollimator_script.setup()
	
	import tomographyScan
	import beam_optimizers
	beam_optimizer = beam_optimizers.beam_optimizer("beam_optimizer", dummy=True)
	beam_optimizer_dummy = beam_optimizers.beam_optimizer("beam_optimizer_dummy", dummy=True)
#	run("i13diffcalc")


except :
	exceptionType, exception, traceback = sys.exc_info()
	handle_messages.log(None, "Error in localStation", exceptionType, exception, traceback, False)

