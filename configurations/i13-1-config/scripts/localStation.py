import sys	
import os
from gdascripts.messages import handle_messages
from gda.jython import InterfaceProvider
import gda.factory.FactoryException

	
#try:
from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names, vararg_alias
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


def ls_scannables():
	ls_names(Scannable)


from epics_scripts.pv_scannable_utils import createPVScannable, caput, caget
alias("createPVScannable")
alias("caput")
alias("caget")

from gda.factory import Finder
from gda.configuration.properties import LocalProperties
#	from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
import i13j

#import for help
from maxipix import mpx_set_folder, mpx_reset_configure, mpx_config_file_monitor
from robots import calcRobotMotors, calcRobotMotorsInverse
from gda.device.lima import LimaCCD
from gda.device.maxipix2 import MaxiPix2
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

from gdascripts.metadata.metadata_commands import setTitle
alias("setTitle")

import filter_array
xia_filter=filter_array.filter_array("xia_filter", prefix="BL13J-OP-ATTN-02:", elements=["Cr", "Fe", "Cu", "Nb"])

from flyscan_script import flyscan, flyscannable, WaitForScannableAtLineEnd
vararg_alias("flyscan")
try:
	waitForQcm_bragg1 = WaitForScannableAtLineEnd('waitForQcm_bragg1', qcm_bragg1)
except NameError:
	print "!!!!!!!!!!!!!!!!!!!!!!! qcm_bragg1 not found so could not create waitForQcm_bragg1 "
	print "Continuing anyway..."
#createPVScannable( "d1_total", "BL13J-DI-PHDGN-01:STAT:Total_RBV")

if not LocalProperties.check("gda.dummy.mode"):
	createPVScannable( "expt_fastshutter_raw", "BL13J-EA-FSHTR-01:RAWCONTROL", hasUnits=False)
	expt_fastshutter = ExperimentShutterEnumPositioner("expt_fastshutter", expt_fastshutter_raw)
	createPVScannable( "ic", "BL13J-DI-IONC-01:I", hasUnits=True)

#make scannablegroup for driving sample stage
from gda.device.scannable.scannablegroup import ScannableGroup
t1_xy = ScannableGroup()
t1_xy.addGroupMember(t1_sx)
t1_xy.addGroupMember(t1_sy)
t1_xy.addGroupMember(ix)
t1_xy.setName("t1_xy")
t1_xy.configure()

#make ScanPointProvider
import sample_stage_position_provider
two_motor_positions = sample_stage_position_provider.ScanPositionProviderFromFile()
#two_motor_positions.load("/dls_sw/i13-1/software/gda_versions/gda_trunk2/i13j-config/scripts/tests/sample_stage_position_provider_test.dat",(0.,0.))

imageFitter = finder.find("imageFitter")
imageStats = finder.find("imageStats")
imagePlotter = finder.find("imagePlotter")
imageROI = finder.find("imageROI")


#create objects in namespace
try:
	mpx_controller = mpx.getMaxiPix2MultiFrameDetector()
	mpx_threshold = mpx_controller.energyThreshold
	mpx_limaCCD = mpx_controller.getLimaCCD()
	mpx_maxipix = mpx_controller.getMaxiPix2()
	mpx_reset_configure()
except gda.factory.FactoryException, e:
	print "!!!!!!!!!!!!!!!!!!!!!!! problem configuring mpx detector"
	print e
	print "Continuing anyway..."
import file_converter

import mpx_external_scan_monitor
import mll
import integrate_mpx_scan
#	try:
#		mpx_set_folder("test","mpx")
#	except :
#		exceptionType, exception, traceback = sys.exc_info()
#		handle_messages.log(None, "Problem setting mpx folder and prefix",exceptionType, exception, traceback,False)
#from tests.testRunner import run_tests

#comment out when not connected
#from autocollimator_script import  * #@UnusedWildImport

#run("i13diffcalc")
del diff, delta, gamma, eta, chi, phi
#execfile("/dls_sw/i13-1/software/diffcalc/example/startup/sixcircle_dummy.py")
#execfile("/dls_sw/i13-1/software/diffcalc/example/startup/sixcircle.py")

#except :
#	exceptionType, exception, traceback = sys.exc_info()
#	handle_messages.log(None, "Error in localStation", exceptionType, exception, traceback, False)

from gdascripts.scannable.beamokay import WaitWhileScannableBelowThresholdMonitorOnly
#comment out when not connected - 
#beammonitor=WaitWhileScannableBelowThresholdMonitorOnly("beammonitor", d4_i, 1,1,1)

ix.setInputNames(["ix"])
iy.setInputNames(["iy"])

#stuff for Vortex editor
def vortex(vortexParameterName, outputfile):
	from uk.ac.gda.beans.vortex import VortexParameters	
	VortexParameters.writeToXML(XspressParametersToLoad, mll_xmap.getConfigFileName());
	mll_xmap.loadConfigurationFromFile()

alias("vortex")

import scan_aborter
beam_check=scan_aborter.scan_aborter("beam_check",3, 300000., "Too high")
imageROI.enable = True
imageStats.enable = True
imageROI.setROI(370, 390, 370, 390)#    ( y_start, y_end, x_start, x_end)
