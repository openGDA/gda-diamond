'''
The central data collection manager module for I19-X
 - prepares beam line for data collection
 - prepares oscillation parameters 
 - delegates to detectorControl for triggering detector and formatting data files
 - tracks images complete and sends notifications
'''

import sys
import time
from time import sleep

from java.lang import String
from java.util import Date
from java.util import Optional

# from com.google.common.base import Optional  # @UnresolvedImport: PyDev has trouble seeing some values
from com.google.common.base import Preconditions  # @UnresolvedImport: PyDev has trouble seeing some values

from gda.device import DeviceException

from uk.ac.gda.beamline.i19.server.api import BeamlineKey # @UnresolvedImport
from uk.ac.gda.beamline.i19.server.common.collection import CollectionTracking # @UnresolvedImport

from component import hutch_utilities
from component import synchrotron
from component.DetectorController import detectorController

from datacollection import ecr_dump
from datacollection import HandleCollectRequestSupport as hcr_support
from datacollection.config import ACTION_ALL, ACTION_EXPOSE, ACTION_PREPARE # @UnusedImport
from datacollection.CollectionMode import COLLECT_MODE, CollectionMode
from datacollection.RunMetadata import RunMetadata

from framework import script_utilities
from framework.script_utilities import UserRequestedHaltException

from gda.configuration.properties import LocalProperties
from gda.configuration.properties.LocalProperties import isDummyModeEnabled # @UnusedImport
from gda.factory import Finder
from gda.px import BeamstopPosition
from gda.px import MxProperties
from gda.px.bcm import BCMFinder
from gda.px.model import ExtendedCollectRequestIO
from gda.px.util import ExtendedCollectRequestProcessor, MxBeamline
from gda.px.model import ExtendedCollectRequests

from org.slf4j import LoggerFactory

from gdascripts.parameters import beamline_parameters


# -----------------------------------------------------------------------------
class CollectRequestHandler:

	def __init__(self, controller, request, responses, action=None):
		
		self.controller = controller # script controller
		self.request = request
		self.ecrs = request.get_ecrs() # ecrs
		self.responses = responses
		self.action = action
		self.logger = LoggerFactory.getLogger(__name__)
		
		self.tracker = CollectionTracking()
		self.tracker.stopAfterNextImage = False
		
		self.currentRequestIndex = 0
		self.currentOscIndex = 0
		self.currentImage = 0
		self.flux = Optional.empty()


	def atEndOfDataCollection(self):
		pass


	def configure(self):
		self.beamline_map = beamline_parameters.Parameters()
		self.hcr_support = hcr_support
		
		self.detector = Finder.find("PXDetector")
		self.detz = Finder.find("GONIODET")
		self.setDetectorController(detectorController)
		Preconditions.checkNotNull(self.detectorControl, "detectorControl is not defined")
		
		self.startDate = Date()
		self.totalNumberOfImages = self.ecrs.getTotalNumberOfImages()
		self.averageTimePerSampleChange = 0.
		self.averageTimePerRequestChange = 0.
		self.averageImageOverhead = 0.
		
		self.totalImagesComplete=0
		self.currentRequestOverheadDone = False
		self.currentSampleChangeDone = False
		self.currentImageDone = False
		self.queueFilePath = LocalProperties.getVarDir() + "/" + BeamlineKey.EXPT_QUEUE_DAT

		self.skipFileExistenceCheck = False # MxProperties.skipFileExistenceCheck()
		self.isInverseBeamDataCollection = False # self.isInverseBeamDataCollection(self.ecrs)
		self.isWedgedMAD = False # self.isWedgedMAD(self.ecrs)
		self.storeInIspyb = False
		
		cameraDefAccelerationTime = self.beamline_map.getValueOrNone("cameraDefAccelerationTime")
		if not cameraDefAccelerationTime:
			cameraDefAccelerationTime = 0.1
		self.cameraDefAccelerationTime = float(cameraDefAccelerationTime)
		
		self.useZebra = True
		self.sampleProvider = Finder.find("sampleProvider")


	def update_ecr(self, ecr):
		# Add the data collection to ISPyB and retrieve the data collection ID for use later
		# when adding images or informing ISPyB that the collection has ended.
		ispybDataCollectionId = 0
		self.update("Not storing data collection in ISPyB")
		
		try:
			# store undulator gap & synchrotron mode
			ecr.setUndulatorGap(hutch_utilities.get_undulator_gap())
			ecr.setSynchrotronMode(synchrotron.get_beam_mode_name())
			
			#ISpyB is expecting it to be in mm not micron!
			realBeamSizeX = 0.0 # beamSizeXObject.getPosition()
			realBeamSizeY = 0.0 # beamSizeYObject.getPosition()
			
			slitGapSizeX = 0.0 # beamSizeXObject.getSlitGap()
			slitGapSizeY = 0.0 # beamSizeYObject.getSlitGap()
			
			focalSpotSizeX = 0.0 # beamSizeXObject.getFocalSpotSize()
			focalSpotSizeY = 0.0 # beamSizeYObject.getFocalSpotSize()
			
			ecr.getBeamProfile().setBeamSizeX(realBeamSizeX/1000.)
			ecr.getBeamProfile().setBeamSizeY(realBeamSizeY/1000.)
			
			ecr.getBeamProfile().setSlitGapSizeX(slitGapSizeX/1000.)
			ecr.getBeamProfile().setSlitGapSizeY(slitGapSizeY/1000.)
			
			ecr.getBeamProfile().setFocalSpotSizeX(focalSpotSizeX)
			ecr.getBeamProfile().setFocalSpotSizeY(focalSpotSizeY)
			
			ecr.getBeamProfile().setHasBeamSize(True)
			
		except:
			type_, exception, traceback = sys.exc_info()
			self.update("exception seen while setting fields of ecr.", type_, exception, traceback, False)
		
		try:
			# distance = ecr.getSampleDetectorDistanceInMM()
			# two_theta = 0
			request = ecr.request
			resolution = request.getResolution()
			# wavelength = request.getWavelength()
			# calculator = Finder.find("detDistResolutionConverter")
			# res_val = calculator.getResInAngstroms(wavelength, distance, two_theta)
			res_val = 0.0 # CHECK: do we need this ?
			resolution.setUpper(res_val)
		
		except:
			type_, exception, traceback = sys.exc_info()
			self.update("exception seen while setting maximum resolution in ecr.", type_, exception, traceback, False)
		
		return ispybDataCollectionId


	def createSnapshots(self, extendedRequest, prefixEnding="", storeFilenamesInExtendedRequest=True, beamSizeXY=None, isPrimaryRow=False):
		# TODO:
		pass

	def doAutomatedAlign(self, alignFull=False):
		return False


	def doExpose(self):
		return True
		# return (self.action == ACTION_ALL) or (self.action == ACTION_EXPOSE)


	def doOscillation(self, oscIndex, extendedRequest, ispybDataCollectionId, run_data=None):
		''' Perform an oscillation sequence
		
		oscIndex is the index of the oscillation sequence we are using here
		detector_distance is the distance between the sample and the front of the detector
		
		This method collects data for a single sample at a single wavelength
		over a range of rotation axis angles.
		'''

		self.logger.debug("doOscillation - entry")

		# Check if a pause is required in a data collection - throw an exception if so
		self.pauseIfRequired()
		self.doOscStartTime = time.clock()
		self.update("Oscillation called")
		
		if not run_data:
			return
		
		if 0 == run_data.numPasses():
			run_data.setNumPasses(1)
		
		startImageNumber = run_data.startImageNumber()
		exposureTimePerImage = run_data.exposure()
		self.originalNumImages = run_data.numImages()
		
		try:
			self.detectorControl.closeFastShutter()
			self.detectorControl.waitWhileMoving()
			
			# Prepare detector controller and trigger the scan asynchronously
			self.update("CRH Call detcon.doOscillation")
			statusOK = self.detectorControl.doOscillation(run_data)
			
# 			if statusOK:
# 				try:
# 					beam_posn = self.getBeamPosition(run_data.ecr)
# 					self.detectorControl.writeMetadata(run_data, self.parameters, beam_posn)
# 				except:
# 					_type, _exception, _traceback = sys.exc_info()
# 					raise DeviceException, "METADATA WRITE FAILED: " + _exception.message, _traceback
			
			# Scanning started asynchronously. Allow all motions to start
			sleep(3)
				
			# TODO: do updates or monitoring here via asynchronous calls
			self.updateMultipleImages(exposureTimePerImage, startImageNumber, extendedRequest, ispybDataCollectionId)
			
		except:
			statusOK = False
			didStopDetector, didCloseShutter = self.detectorControl.abortCollection()
			type_, exception, traceback = sys.exc_info()
			self.update("FAILURE in data collection", type_, exception, traceback, True, True)
			if didStopDetector:
				self.update("STOPPED detector")
			if didCloseShutter:
				self.update("CLOSED fast shutter")
			
		finally:
			self.detectorControl.waitWhileScanning()
			self.detectorControl.waitWhileMoving()
			self.detectorControl.closeFastShutter()
			
			#7. Ensure shutter is closed - should have been done automatically
			#6. Wait for the ready signal from the detector, reset defaults speeds on omega
			self.detectorControl.stop()
			self.detectorControl.resetSpeeds()
			self.waitUntilDetectorReady()
			
			self.update("Pilatus detector state after exposure is (isBusy) = " + str(self.detectorControl.isDetectorBusy()) + ". should be 1 so that we're getting full exposure")
			currentShutterState = self.detectorControl.getShutterState()
			self.update("Shutter state after exposure is %r" % currentShutterState)
			self.detectorControl.resetScanController() # default 'normal' collection mode, zebra
		
		
		#8. Check that EPICS File number is updated
		# filenumberUpdateTimeout = 30
		# if not isDummyModeEnabled():
		# detectorControl.checkFileNumberUpdate(1, filenumberUpdateTimeout, self.update)
		
		#9. Check for any errors on the detector
		self.handleDetectorErrorStatus()
		
		#10. See if user has requested to terminate the experiment
		if self.isStopAfterNextImage():
			self.update("User requested stop of experiment after run: " + str(extendedRequest.getRunNumber()))
			self.waitUntilDetectorReady()
			self.pauseIfRequired()
			
			raise UserRequestedHaltException("User requested stop of experiment after image: " + str(self.currentImage))
		
		# self.pauseIfRequired(checkBacklight=True)
		
		# Do something more useful with the execution state
		self.logger.debug("doOscillation - exit")

		self.update("Handle Collect Request success state is %s" % statusOK)
		return statusOK


	def doWriteMetadata(self, run_data):
		pass


	def doPrepare(self):
		return (self.action == ACTION_ALL) or (self.action == ACTION_PREPARE)


	def doSample(self):
		self.logger.debug("doSample - entry")
		extendedRequest = self.request.get_ecr()
# 		self.highestExistingFileMonitor.configureHighestExistingFileMonitor(
# 			extendedRequest.requestDir,
# 			extendedRequest.dnaFilePrefix + MxProperties.IMAGE_NUMBER_FORMAT + "." + self.detector.getSuffix(),
# 			extendedRequest.request.getOscillation_sequence()[0].getStart_image_number())
		
		self.currentOscIndex = 0
		startTime = time.clock()
		
		# self.update_ecr(extendedRequest)
		self.ispybDataCollectioId = 0
		
		# collect the oscillations for this sample
		try:
			self.currentRequestOverheadDone = True
			self.averageTimePerRequestChange = time.clock() - startTime
			
			#loop over all oscillation sequences in this collect_request
			statusOK = True
			num_oscillation_sequences = len(extendedRequest.request.getOscillation_sequence())
			self.update("Looping over %d oscillation sequence(s)..." % num_oscillation_sequences)
			for self.currentOscIndex in range(0, num_oscillation_sequences):
				self.currentImage = 0
				if not statusOK:
					self.update("Skipping further oscillations")
					break
				else:
					statusOK = self.doOscillation(self.currentOscIndex, extendedRequest, 0, self.request.get_run_data())
			
			return self.hcr_support.generate_response(statusOK, dataCollectionId=0)
		
		except: # catches DeviceException(TimeoutException) from self.makeCameraSafe
			type_, exception, traceback = sys.exc_info()
			self.update("doSample exception seen", type_, exception, traceback, True)
		
		finally:
			self.logger.debug("doSample - exit")



	def dump(self):
		ecr_dump.dumpCollectRequestArray(script_utilities.update, None, self.ecrs)
		self.update("cameraDefAccelerationTime = " + `self.cameraDefAccelerationTime`)


# 	# Only returns if sample current is OK
# 	# True if it was always OK
# 	def ensureSampleCurrentOK(self):
# 		
# 		sampleCurrentCheck = self.sampleCurrentCheck()
# 		
# 		if sampleCurrentCheck == None or (not self.hutch.isFastShutterOpen()):
# 			return True
# 		
# 		while sampleCurrentCheck != None:
# 			self. waitForResume(sampleCurrentCheck)
# 			sampleCurrentCheck = self.sampleCurrentCheck()
# 		
# 		return False


# 	def ensureSampleCurrentOKAndRestartAutomatically(self):
# 		
# 		# if shutter is closed, we don't bother checking anything else, since there's no beam
# 		if not self.hutch.isFastShutterOpen():
# 			return True
# 		
# 		# is the current OK?
# 		sampleCurrentCheck = self.sampleCurrentCheck()
# 		if not sampleCurrentCheck:
# 			return True
# 		
# 		# Got a "less than minimum" warning. Log it
# 		self.update(sampleCurrentCheck)
# 		self.update("Data collection will automatically resume when beam returns and stabilises")
# 		
# 		# wait while the current is below the minimum
# 		while sampleCurrentCheck != None:
# 			sleep(10)
# 			sampleCurrentCheck = self.sampleCurrentCheck()
# 		self.update("Sample current detected.")
# 		
# 		# then wait a further 5 minutes, for the beam to stabilise
# 		minutesToWait = 5
# 		while minutesToWait > 0:
# 			self.update("Beam stabilising, data collection will resume in "+str(minutesToWait)+" minute(s)...")
# 			sleep(60)
# 			minutesToWait = minutesToWait-1
# 		
# 		return False


	def getBeamPosition(self, extendedRequest):
		detector_distance = extendedRequest.getSampleDetectorDistanceInMM()
		x_beam_mm = BCMFinder.getBeamXYConverter().getBeamXUsingMM(detector_distance)
		y_beam_mm = BCMFinder.getBeamXYConverter().getBeamYUsingMM(detector_distance)
		
		detector_x_pixels = self.detectorControl.getDetectorPixelsX()
		detector_y_pixels = self.detectorControl.getDetectorPixelsY()
		detector_dimensions_mm = self.detectorControl.getDetectorDimensionInMm()
		x_beam_pixels = BCMFinder.getBeamXYConverter().getBeamXUsingPixels(detector_distance, detector_x_pixels, detector_dimensions_mm.getWidth())
		y_beam_pixels = BCMFinder.getBeamXYConverter().getBeamYUsingPixels(detector_distance, detector_y_pixels, detector_dimensions_mm.getHeight())
		
		return (x_beam_pixels, y_beam_pixels, x_beam_mm, y_beam_mm)


	def handleDetectorErrorStatus(self):
		# first test to check that the detector is not in an error status
		if self.detectorControl.isDetectorInError():
			msg = "Detector in an error status.\n"
			self.detectorControl.stop()
			raise Exception, msg


	def handleImageDone(self, filename, showImageUpdate = False):
		self.totalImagesComplete += 1
		self.updateConsole("File %d of %d : filename %s" % (self.totalImagesComplete, self.totalNumberOfImages, filename))


	def handleTransmission(self, extendedRequest):
		pass


	def handleWaveLength(self, extendedRequest, doCheckGain=False):
		pass


	def initialiseProgress(self):
		pass


	def is_spectrum_required(self, sample_ref):
		return False


	def isInverseBeamDataCollection(self, requests):
		return False


	def isStopAfterNextImage(self):
		return self.tracker.stopAfterNextImage


	def isWedgedMAD(self, requests):
		return False


	def makeDetectorSafe(self, error=False):
		# close the shutter
		# abort the detector trigger/gate, disable
		# stop scanning axes
		# reset default speeds
		if error:
			self.update("Something has gone wrong so the detector is being made safe.")
			self.detectorControl.abortCollection() # ensure detector in known state
			
		else:
			self.detectorControl.stop() # ensure detector in known state


	def pauseIfRequired(self, checkBacklight=False):
		pass


	def run(self):
		self.updateQueue(self.ecrs.getExtendedCollectRequests(), 0)
		self.handleDetectorErrorStatus()
		self.setStopAfterNextImage(False)

		try:
			self.ispybDataCollectionGroupId = 0
			first_ecr = self.ecrs.getExtendedCollectRequests()[0]
			experiment_type = first_ecr.getExperimentType()
			# self.update("Experiment type is '%s'" % experiment_type)
			# self.update("Visit path: " + repr(first_ecr.getVisitPath()))
		except:
			_type, _exception, _traceback = sys.exc_info()
			msg = "FAIL to set fetch ECR or set DC Group ID"
			self.update(msg, _type, _exception, _traceback, True)
		
		self.update("Data Collection Group ID NOT set")
		self.update("Looping over array of collect_requests:")
		
		for self.currentRequestIndex in range(0, len(self.ecrs.getExtendedCollectRequests())):
			
			# We look up these settings here to allow them to be changed while data collections are running
			self.doProcessing = False
			self.TakePNGs = False # mxUserOptionsScript.isTakePNGs() # FIXME: Implement for I19-2
			
			extendedRequest = self.ecrs.getExtendedCollectRequests()[self.currentRequestIndex]
			extendedRequest.setDataCollectionGroupId(0)

			# Every data collection is a 'primary row', except in an inverse beam data collection, or a wedged MAD,
			# where only the first row is a 'primary row'
			self.isPrimaryRow = True # (not self.isInverseBeamDataCollection and not self.isWedgedMAD) or ((self.isInverseBeamDataCollection or self.isWedgedMAD) and (self.currentRequestIndex == 0))
			
			self.updateQueue(self.ecrs.getExtendedCollectRequests(), self.currentRequestIndex)
			
			self.sampleRef = extendedRequest.request.getSample_reference()
			
			# self.handleWaveLength(extendedRequest, doCheckGain=True)
			
			self.currentOscIndex = 0
			self.currentImage = 0
			self.currentRequestOverheadDone = False
			self.currentSampleChangeDone = False
			self.currentImageDone = False
			self.sampleRequested = False
			self.pauseForCentring = False
			
			self.hcr_support.ensureDataDirectoryExists(extendedRequest)
			# self.update("Write run list to visit data folder")
			# self.hcr_support.writeRunList(extendedRequest)
			
			runNumber = self.request.get_ecr().runNumber
			self.update("Run Number from Request is "+str(runNumber))
			self.currentSampleChangeDone = True
			
			#collect this collect_request
			try:
				self.setupDetectorParameters()
				self.tracker.setCollecting(True)
				
				# ******
				# configure and move to start
				self.detectorControl.configureScanPosition(self.request.get_run_data())
				self.detectorControl.setupScanPosition(self.request.get_run_data())
				# ******
				
				# collect the data!
				# self.ensureSampleCurrentOKAndRestartAutomatically()
				try:
					# ******
					self.responses[self.currentRequestIndex-1] = self.doSample()
					# ******
				except:
					raise
				
				self.tracker.setCollecting(False)
			
			except UserRequestedHaltException, e:
				type_, exception, traceback = sys.exc_info()
				self.responses[self.currentRequestIndex-1] = hcr_support.generate_response(False, "user requested halt: " + e.reason, type_, exception)
				raise Exception, e.reason
			
			except:
				type_, exception, traceback = sys.exc_info()
				
				self.detectorControl.stop() # clearPilatusLastImage can throw DeviceException(TimeoutException) from AreaDetectorPilatus.start via PilatusScripts.clearPilatusLastImage
				self.tracker.setCollecting(False) # which means this is not set
				
				msg = "CollectRequestHandler: Error processing request " + `self.currentRequestIndex` + ". Stopping data collection."
				
				self.responses[self.currentRequestIndex-1] = hcr_support.generate_response(False, msg, type_, exception)
				self.update(msg, type_, exception, traceback, Raise=True)
		
		timeInms = float(Date().getTime() - self.startDate.getTime())
		self.update(String.format("Completed at %s. Time taken : %.1fs", [Date(), timeInms/1000.]))
		self.atEndOfDataCollection()
		self.updateQueue(self.ecrs.getExtendedCollectRequests(), len(self.ecrs.getExtendedCollectRequests()))


	def sampleCurrentCheck(self):
		"""Returns warning if current is below the minimum, or None if OK"""
		return None


	def sendProgress(self, percent, message):
		# For Command Queue observers
		pass


	def setDetectorController(self, controller):
		self.detectorControl = controller


	#sets the flag whether the scripts should stop after the next image has been taken
	def setStopAfterNextImage(self, doStop):
		self.tracker.stopAfterNextImage = doStop


	def setupDetectorParameters(self):
		''' Prepare detector for data collection
			Interact with detectorControl, based on ECR
			Set up DatasetMetadata, RunMetadata to prepare:
			- template
			- detector settings
			- scan settings
		'''

		# prefix used to name each data file
		# directory goes to data file header
		# write_path goes to detector parameters
		metadata = self.request.get_metadata() # self.hcr_support.prepare_metadata(extended_request)
		run_data = self.request.get_run_data() # self.hcr_support.prepare_run_data(extended_request)
		
		self.detectorControl.setupDetectorParameters(metadata, run_data)
		
		return metadata


	def update(self, msg, exceptionType=None, exception=None, traceback=None, Raise=False, popup=False):
		#def update(controller, msg, exceptionType=None, exception=None, traceback=None, Raise=False, logger_ref=logger):
		script_utilities.update(self.controller, "> "+msg, exceptionType, exception, traceback, Raise, self.logger)


	def updateConsole(self, msg):
		image = String.format("# Row: %d Osc :%d Image: %d - ",[self.currentRequestIndex+1, self.currentOscIndex+1, self.currentImage+1])
		print image + msg


	def updateMultipleImages(self, exposureTimePerImage, startImageNumber, extendedRequest, ispybDataCollectionId):
		# Only run console updates in 'normal' collection mode
		if not COLLECT_MODE[0] == CollectionMode().getMode():
			return
		
		self.update("Note: the image number and time remaining are approximate")
		checkTime = 5 # check for first file will happen after 2*checkTime
		checkInterval = max(int(checkTime/exposureTimePerImage), 1)
		
		startUpdateTime = time.time()
		fallenBehindNumImages = 0
		
		self.update("Updater looping over original number images %d" % self.originalNumImages)
		
		for image_loop_index in range(0, self.originalNumImages): # loop index counts from zero
			image_counter = 1 + image_loop_index # useful for human friendly counting from 1
			
			image_file_number = startImageNumber + image_loop_index
			filename = self.image_filename_of(extendedRequest.fileNameTemplate, image_file_number )
			
			# compare current time with expected time. wait until the expected time,
			# or don't wait if we're behind (GUI slow/network problems/etc.)
			startNextImageTime = startUpdateTime + exposureTimePerImage * image_loop_index - time.time()
			
			if startNextImageTime > 0: # wait until expected, or mark overdue
				time.sleep(startNextImageTime)
			else:
				fallenBehindNumImages += 1
				if fallenBehindNumImages/50==1:
					self.update("Falling behind 50 times, current image fall behind time: "+str(startNextImageTime))
			
			# On last image or multiple of interval, do autoload
			doAutoload = False
					
			self.handleImageDone(filename, doAutoload)
			
			self.currentImage += 1 #the first one may need to be changed if we are getting too many counted
			self.currentImageDone = True
			self.averageImageOverhead = 0
			
			if self.isStopAfterNextImage(): # GDA-4445, stop after next image
				toReturn = "User requested stop of experiment after (approximately) image: " + str(self.currentImage)
				self.update(toReturn)
				raise UserRequestedHaltException(toReturn)


	# Convenience method for building file names from template and detector suffix
	def image_filename_of(self, template, image_file_number):
		file_suffix = self.detector.getSuffix()
		return String.format(template,image_file_number,file_suffix)


	# Write current list of requests to file
	def updateQueue(self, requests, currentRequestIndex):
		queue = ExtendedCollectRequests()
		for index in range(currentRequestIndex, len(requests)):
			queue.addExtendedCollectRequest(requests[index])
		
		# CHECK: ExtendedCollectRequestIO.writeExtendedCollectRequests(queue, self.queueFilePath)
		
		#do not use self.update as that prefixes the string
		# update(self.controller,ExtendedCollectRequestProcessor.QUEUE_EVENT_MARKER_VALUE)


	def waitUntilDetectorReady(self):
		self.update("If we do not get past here, check detector IOC/camserver")
		self.update("Checking detector controller...")
		if self.detectorControl.isScanning():
			self.update("Wait on detector control...")
			self.detectorControl.waitUntilDetectorReady()
		self.update("Detector control OK. Continuing.")


