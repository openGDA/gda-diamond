import sys	
import os
from gdascripts.messages import handle_messages
from gda.jython import InterfaceProvider


from gda.device.scannable import EpicsScannable

def createPVScannable( name, pv, addToNameSpace=True):
	sc = EpicsScannable()
	sc.setName(name)
	sc.setPvName(pv)
	sc.setUseNameAsInputName(True)
	sc.afterPropertiesSet()
	sc.configure()
	if addToNameSpace:
		commandServer.placeInJythonNamespace(name,sc)
	return sc
	

try:
	from gda.device import Scannable
	from gda.jython.commands.GeneralCommands import ls_names, vararg_alias

	def ls_scannables():
		ls_names(Scannable)

	
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
	
	from gdascripts.pd.time_pds import waittimeClass2
	waittime=waittimeClass2('waittime')
	
	from flyscan_script import flyscan, flyscannable
	vararg_alias("flyscan")
	
	createPVScannable( "d1_total", "BL13J-DI-PHDGN-01:STAT:Total_RBV")
	
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
	two_motor_positions.load("/dls_sw/i13-1/software/gda_versions/gda_trunk/i13j-config/scripts/tests/sample_stage_position_provider_test.dat",(0.,0.))

	imageFitter = finder.find("imageFitter")
	imageStats = finder.find("imageStats")
	imagePlotter = finder.find("imagePlotter")

# TIFF saver does not work. We will get the data in NexusData
#	d1_det.setFileTemplate("%s%s%d.tif")
#	d1_det.setFilePath("/dls_sw/i3-1/software/gdavar/d1")
#	d1_det.setFileNumber(1)

#	from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
#	from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue #@UnusedImport
#	from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak

#	d1_det = ProcessingDetectorWrapper('d1_det', d1_cam, panel_name=None, panel_name_rcp='Detector Image',nexusDataKeys=["d1_cam","data"])
#	d1_det.display_image = True
#	d1_peak2d = DetectorDataProcessorWithRoi('d1_peak2d', d1_det, [TwodGaussianPeak()])
#	d1_max2d = DetectorDataProcessorWithRoi('d1_max2d', d1_det, [SumMaxPositionAndValue()])

#	d2_det = ProcessingDetectorWrapper('d2_det', d2_cam, panel_name=None, panel_name_rcp='Detector Image',nexusDataKeys=["d2_cam","data"])
#	d2_det.display_image = True
#	d2_peak2d = DetectorDataProcessorWithRoi('d2_peak2d', d2_det, [TwodGaussianPeak()])
#	d2_max2d = DetectorDataProcessorWithRoi('d2_max2d', d2_det, [SumMaxPositionAndValue()])

#	d3_det = ProcessingDetectorWrapper('d3_det', d3_cam, panel_name=None, panel_name_rcp='Detector Image',nexusDataKeys=["d3_cam","data"])
#	d3_det.display_image = True
#	d3_peak2d = DetectorDataProcessorWithRoi('d3_peak2d', d3_det, [TwodGaussianPeak()])
#	d3_max2d = DetectorDataProcessorWithRoi('d3_max2d', d3_det, [SumMaxPositionAndValue()])

#	d4_det = ProcessingDetectorWrapper('d4_det', d4_cam, panel_name=None, panel_name_rcp='Detector Image',nexusDataKeys=["d4_cam","data"])
#	d4_det.display_image = True
#	d4_peak2d = DetectorDataProcessorWithRoi('d4_peak2d', d4_det, [TwodGaussianPeak()])
#	d4_max2d = DetectorDataProcessorWithRoi('d4_max2d', d4_det, [SumMaxPositionAndValue()])

#	oh4_shtr_det = ProcessingDetectorWrapper('oh4_shtr_cam_det', oh4_shtr_cam, panel_name=None, panel_name_rcp='Detector Image',nexusDataKeys=["oh4_shtr_cam","data"])
#	oh4_shtr_det.display_image = True
#	oh4_shtr_peak2d = DetectorDataProcessorWithRoi('oh4_shtr_peak2d', oh4_shtr_det, [TwodGaussianPeak()])
#	oh4_shtr_max2d = DetectorDataProcessorWithRoi('oh4_shtr_max2d', oh4_shtr_det, [SumMaxPositionAndValue()])
	
#	import gda.device.detector.NexusDetectorWrapper
#	mpx_wrap = gda.device.detector.NexusDetectorWrapper(mpx)
#	from uk.ac.diamond.scisoft.analysis.io import PilatusEdfLoader
	
#	mpx_plot = ProcessingDetectorWrapper('mpx_det', mpx, panel_name=None, panel_name_rcp='Detector Image',nexusDataKeys=["mpx","image_data"], 
#									nexusDataFileNames=True, iFileLoader=PilatusEdfLoader, returnPathAsImageNumberOnly=True)
#	mpx_plot.display_image = True
#	mpx_peak2d = DetectorDataProcessorWithRoi('mpx_peak2d', mpx_plot, [TwodGaussianPeak()])
#	mpx_max2d = DetectorDataProcessorWithRoi('mpx_max2d', mpx_plot, [SumMaxPositionAndValue()])

	#create objects in namespace
	mpx_controller = mpx.getMaxiPix2MultiFrameDetector()
	mpx_threshold = mpx_controller.energyThreshold
	mpx_limaCCD = mpx_controller.getLimaCCD()
	mpx_maxipix = mpx_controller.getMaxiPix2()
	mpx_reset_configure()
	
	import file_converter
	
	import integrate_mpx_scan
#	try:
#		mpx_set_folder("test","mpx")
#	except :
#		exceptionType, exception, traceback = sys.exc_info()
#		handle_messages.log(None, "Problem setting mpx folder and prefix",exceptionType, exception, traceback,False)
	
	
	#scan eh 0. 10. 1. mpx 0.1
	
	#to take multiple images from d1_ad_det and use d1_det to plot then always set collectiontime for d1_det as its internal cache is only
	#cleared when asynchronousMoveTo
	# e.g. repscan 5 d1_det .5 
	#to get d1_ad_det Nexusdata into the file add on d1_ad_det
	# e.g. repscan 5 d1_det .5 d1_ad_det
	# to get max2d add to the end
	# e.g. repscan 5 d1_det .5 d1_ad_det d1_max2d
	#but only the data from d1_ad_det goes into thefile!
	
	#repscan 5 mpx .1 - take 5 images 0.1 exposure
	#repscan 5 mpx 0.1 mpx_plot - same but plot after each
	#we need to have a proper detector wrapper
	#handle scannables that return a string in NexusDataWriter
	
	#from tests.testRunner import run_tests

	run("i13diffcalc")


except :
	exceptionType, exception, traceback = sys.exc_info()
	handle_messages.log(None, "Error in localStation", exceptionType, exception, traceback, False)

