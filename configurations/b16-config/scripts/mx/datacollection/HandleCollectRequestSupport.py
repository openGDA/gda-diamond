import datetime
import re
import sys

from os import path
from os import makedirs
from os import mkdir

from java.io import File

from dna.xml import Collect_response
from dna.xml import Dbstatus
from dna.xml import Status
from dna.xml.types import Status_code

from gda.configuration.properties import LocalProperties
from gda.px import BeamProfile
from gda.px import MxProperties
from gda.px.model import ExtendedCollectRequest
from gda.px.model import ExtendedCollectRequests
from gda.px.model import ExtendedCollectRequestIO
from gdascripts.messages import handle_messages

from datacollection.DatasetMetadata import DatasetMetadata
from datacollection.RunMetadata import RunMetadata

from framework.script_utilities import ScriptBaseInterruption
from framework.script_utilities import UserRequestedHaltException

from javax.vecmath import Point3d

from org.slf4j import LoggerFactory
logger = LoggerFactory.getLogger(__name__)


################################################################################

def create_collect_responses(ecrs):
	collect_responses =  [None for _ in range(len(ecrs.getExtendedCollectRequests()))]
	return collect_responses


def create_standard_ecr(visit_path, directory, prefix, run_number):
	ecr = (ExtendedCollectRequest.ECRBuilder.builder() #@UndefinedVariable
		.setDataCollectionId(0)
		.setRunStatus("")
		.setRunNumber(run_number) #@UndefinedVariable
		.setSampleDetectorDistanceInMM(105.) #@UndefinedVariable
		.setTotalNumberOfImages(100L)
		.setVisitPath(visit_path) #@UndefinedVariable
		.setComment("comment") #@UndefinedVariable
		.setTransmissionInPerCent(100) #@UndefinedVariable
		.setXtalSnapShots([""])
		.setSynchrotronMode("")
		.setDetectorBinningMode("")
		.setUndulatorGap(0.0)
		.setSampleName("test")
		.setKappa(0.0)
		.setChi(0.0)
		.setPhi(0.0)
		.setTwoTheta(0.0)
		.setAxisChoice("Omega")
		.setOtherAxis(0.0)
		.setOmegaDelta(0.0)
		.setActualBarcode("")
		.setSamplePosition(Point3d(0.0, 0.0 ,0.0))
  # .setBeamProfile()
  # 	.setBeamSizeX(0.0)
  # 	.setBeamSizeY(0.0)
  # 	.setFocalSpotSizeX(0.0)
  # 	.setFocalSpotSizeY(0.0)
  # 	.setSlitGapSizeX(0.0)
  # 	.setSlitGapSizeY(0.0)
  # 	.setAperturePosition("")
  # 	.end()
		.setCollectRequest() #@UndefinedVariable
			.setFileInfo() #@UndefinedVariable
				.setPrefix(prefix) #@UndefinedVariable
				.setDirectory(directory) #@UndefinedVariable
				.end() #@UndefinedVariable
			.setOscillationSequence() #@UndefinedVariable
				.setNumberOfImages(100) #@UndefinedVariable
				.setStart(0) #@UndefinedVariable
				.setOverlap(0) #@UndefinedVariable
				.setRange(0.1) #@UndefinedVariable
				.setExposureTime(0.04) #@UndefinedVariable
				.setStartImageNumber(1) #@UndefinedVariable
				.setNumberOfPasses(1) #@UndefinedVariable
				.end() #@UndefinedVariable
			.setResolution()
				.end()
			.setSampleReference()
				.end()
			.end() #@UndefinedVariable
		.build()) #@UndefinedVariable
		# build sets default run number, experiment type, DCG id, beamstop position
		# build sets default fileNameTemplate, dnsFilePrefix, dnaFileDir, dnaFileNameTemplate
		# build evaluates total number images
	
	return ecr


def create_standard_ecrs(visit_path, directory, prefix, run_number):
	ecr = create_standard_ecr(visit_path, directory, prefix, run_number)
	ecrs = ExtendedCollectRequests()
	ecrs.addExtendedCollectRequest(ecr)
	return ecrs


def datetime_now():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]


def ensureDataDirectoryExists(extendedRequest):
	targetDir = File(extendedRequest.requestDir)
	try:
		if not targetDir.exists():
			targetDir.mkdirs()
		
		# TODO: check each directory level on the way down to targetDir
		if targetDir.isFile():
			raise Exception, "Error while trying to create data directory: " + `targetDir` + " - already exists as a file"
	
	except:
		type_, exception, _ = sys.exc_info()
		raise Exception, "Error while trying to create data directory:"  + `targetDir` + " " + `type_` + ":" + `exception`



def generate_response(OK, msg="", type_=None, exception=None, traceback=None, dataCollectionId=-1):
	response = Collect_response()
	status = Status()
	
	if isinstance(exception, ScriptBaseInterruption):
		msg += " abort called during data collection."
	elif isinstance(exception, UserRequestedHaltException):
		msg += " " + exception.reason
	else:
		status.setMessage(handle_messages.constructMessage(msg, type_, exception))
	
	status.setCode(Status_code.OK if OK else Status_code.ERROR) #@UndefinedVariable: PyDev has trouble seeing some values
	
	if dataCollectionId != -1:
		dbstatus = Dbstatus()
		dbstatus.setDataCollectionId(dataCollectionId)
		#set the dbstatus code (required) to be the same as the experiment status
		dbstatus.setCode(status.getCode())
		response.setDbstatus(dbstatus)
	
	response.setStatus(status)
	return response


def get_detector_write_filepath(extended_request):
	directory = extended_request.request.getFileinfo().getDirectory()
	prefix = extended_request.request.getFileinfo().getPrefix()
	
	''' For beamlines where the detector needs to be told where to put the data
	if this is different than the standard /dls/ixx/data
	Necessary for the Pilatus detectors with PPU, where we must write to /ramdisk
	
	prefix used to name each data file
	directory goes to data file header
	filepath goes to detector parameters
	'''
	if LocalProperties.check("gda.px.pilatus.useramdisk"):
		filepath = re.sub("/dls/.*?/data", "/ramdisk", directory)
	else:
		filepath = directory

	return directory, prefix, filepath


def isAutoIncrementRunFolder():
	return True


def extract_metadata(run_data):
	return prepare_metadata(run_data.ecr)


def prepare_metadata(extended_request):
	metadata = DatasetMetadata()
	directory, output_filename, ppu_directory = get_detector_write_filepath(extended_request)
	metadata.setDirectory(directory)
	metadata.setDetectorWritePath(ppu_directory)
	metadata.setPrefix(output_filename)
	metadata.setStartRunNumber(extended_request.getRunNumber())
	return metadata


def prepare_run_data(extended_request, index=0):
	run_data = RunMetadata()
	run_data.setExtendedCollectRequest(extended_request, index)
	return run_data


def update_folders(extended_requests, filepath):
	auto_increment_run_folder = isAutoIncrementRunFolder()
	
	logger.debug("autoIncrementRunFolder set to = %s. If True the folders in the ECR will be updated to include the next incremental number " % auto_increment_run_folder)
	
	if auto_increment_run_folder:
		
		format_str = MxProperties.FOLDER_NUMBER_FORMAT
		
		for request in extended_requests.getExtendedCollectRequests():
			folder_name = str(request.getRequest().getFileinfo().getDirectory())
			logger.debug("autoIncrementRunFolder current folder name = %s" % folder_name)
			
			auto_increment_folder_name = folder_name + "_auto_inc"
			
			if not path.exists(auto_increment_folder_name):
				makedirs(auto_increment_folder_name)
				
			with open(auto_increment_folder_name + "/auto_inc.txt", "w+") as auto_increment_file:
				counter = auto_increment_file.readline()
				
				if counter == "":
					counter = 0
				else:
					counter = int(counter)
				
				found_correct_folder = False
				
				# loop through the folders until you find one that hasn't been created
				while not found_correct_folder:
					counter += 1
					
					folder_to_test = "%s_%s" % (folder_name, format_str.format(counter))
	
					logger.debug("autoIncrementRunFolder testing for folder = %s" % folder_to_test)
					
					folder_exist = path.exists(folder_to_test)
					
					if not folder_exist:
						logger.debug("autoIncrementRunFolder folder %s doesn't exist so will use")
						# This will make the folder on disk so that it is taken into account on the next iteration round this loop 
						mkdir(folder_to_test)
						
						# Update the ECR
						request.getRequest().getFileinfo().setDirectory(folder_to_test)
						request.setDnaFileDir(folder_to_test)
						
						filename_template = request.getFileNameTemplate()
						request.setFileNameTemplate(folder_to_test + filename_template[len(folder_name):])
						
						auto_increment_file.write(str(counter))
						
						found_correct_folder = True
		
		# once you have looped through all of the ecrs in the file re-save it to disk
		ExtendedCollectRequestIO.saveExtendedCollectRequestsToFile(extended_requests, filepath)
	
	return extended_requests
