import time
import re
import sys

from com.google.common.base import Optional # @UnresolvedImport
from org.slf4j import LoggerFactory

from gda.commandqueue import JythonScriptProgressProvider
from gda.configuration.properties import LocalProperties
from gda.configuration.properties.LocalProperties import isDummyModeEnabled
from gda.px import MxProperties
from gda.px.detector import IAreaDetectorPilatus, IPilatusDetector, PilatusConstants, PilatusGain

from framework.thread_utils import ScriptThread

logger = LoggerFactory.getLogger(__name__)

def checkPilatusFilenumberUpdate(detector, update, imageNumber, filenumberUpdateTimeout=10):
	''' At the end of a Pilatus data collection, EPICS increments the filenumber by 1.
		This is our signal that we can continue to the next image(s).
	'''
	update("checking file number, which is "+str(detector.getFilenumber()) + " should be "+str(imageNumber+1))
	startTimeoutCheck = time.time()
	while detector.getFilenumber() < imageNumber + 1:
		interval = time.time() - startTimeoutCheck
		update("Waiting for EPICS to update filenumber to "+str(imageNumber+1) + ". interval since check started: "+ str(interval))
		if time.time() - startTimeoutCheck > filenumberUpdateTimeout:
			raise RuntimeError("Waited too long for Pilatus filenumber update. Check detector log file to see if trigger was received")
		time.sleep(0.5)


def clearPilatusLastImage(detector, update, visit_path):
	update("Clearing last image")
	# now collect a 1-image dataset to clear out what is in the detector's memory
	time.sleep(1)
	detector.waitForReady() # make sure everything is done
	detector.setNumberOfExposures(1)
	detector.setNumberOfImages(1)
	detector.setFileprefix("ClearBuffer")
	detector.setFilenumber(1)
	detector.setMode("Internal")
	filepath = getDetectorWriteFilepath(visit_path)
	detector.setFilepath(filepath)
	detector.start("name",0)
	time.sleep(0.5) # make sure detector has started
	update("Image cleared from detector. If you do not get a message after this, check detector IOC/camserver ")
	detector.waitForReady() # should now be done


def getBestPilatusThreshold(incomingEnergy):
	''' See table in PilatusCheckGain for the values recommended by Dectris. '''
	if incomingEnergy > 36000:
		if incomingEnergy > 40000:
			raise Exception("This detector is not designed for energies higher than 40 KeV")
		return 18000
	elif incomingEnergy >= 8000:
		return incomingEnergy/2
	else:
		if incomingEnergy < 5000:
			raise Exception("This detector is not designed for energies lower than 5 KeV")
		return 4000


def getDetectorWriteFilepath(filepath):
	''' For beamlines where the detector needs to be told where to put the data
		if this is different than the standard /dls/ixx/data
		Necessary for the Pilatus detectors with PPU, where we must write to /ramdisk
	'''
	pilatus_ramdisk = LocalProperties.check("gda.px.pilatus.useramdisk")
	
	if pilatus_ramdisk:
		filepath = re.sub("/dls/.*?/data", "/ramdisk", filepath, count=1) #I03-60
	
	return filepath


def isAreaDetectorPilatus(detector):
	return isinstance(detector, IAreaDetectorPilatus)


def isPilatus(detector):
	return isinstance(detector, IPilatusDetector)


def PilatusCheckGain(update, detector, currentEnergy, currentGain, do_sleep=True):
	''' Stefan at Dectris has recommendations about what incoming energies should be used
	the table below is in his priority order, with incoming and threshold values shown clearly
	incoming (keV)	threshold (keV)	gain
	==============	===============	====
	14-40			  7-18			lowG
	10-14			  5-7			midG
	5-10			  4-5			highG
	
	Note that currentEnergy is incoming energy.
	'''
	lowGainString = PilatusGain.LOW.epicsLabel
	midGainString = PilatusGain.MEDIUM.epicsLabel
	highGainString = PilatusGain.HIGH.epicsLabel
	
	# MXGDA-37
	# round energy to nearest integer before working out which gain to use
	# eliminates ~0.001eV fluctuations seen in the current energy
	currentEnergy = int(round(currentEnergy))
	
	# user-friendly names for each gain for reporting
	gains = {
		lowGainString:  "low",
		midGainString:  "mid",
		highGainString: "high",
	}
	
	if currentEnergy >= 14000 and currentEnergy < 40000:
		requiredGain = lowGainString
	elif currentEnergy >= 10000 and currentEnergy < 14000:
		requiredGain = midGainString
	elif currentEnergy >= 5000 and currentEnergy < 10000:
		requiredGain = highGainString
	
	# ultraG is shown on EPICS but not used by Dectris
	
	else: # only energies below 5 keV are omitted
		if update:
			update("INVALID ENERGY FOR SETTING GAIN")
		return
	
	if currentGain == requiredGain:
		if update:
			update("keeping %s gain" % gains[currentGain])
	else:
		if update:
			update("changing to %s gain" % gains[requiredGain])
		detector.setGain(requiredGain)
		if do_sleep:
			thresholdSleep(update, detector)
	
	#reset to default gain at end.
	if detector.getGain()!=PilatusConstants.DEFAULT_GAIN_STRING:
		detector.setGain(PilatusConstants.DEFAULT_GAIN_STRING)
	
	return (currentGain != requiredGain)


def PilatusCheckThreshold(detector, currentEnergy, update):
	''' Expects a value in eV for currentEnergy '''
	if isPilatus(detector):
		#first part, check gain
		if detector.getGain()!=PilatusConstants.DEFAULT_GAIN_STRING:
			update("Pilatus not in default mode, gain and threshold will not be changed")
			return
		update("PilatusCheckThreshold: Current energy: " + str(currentEnergy) + " threshold * 2: "+str(detector.getThresholdEnergy()*2))
		currentGain = detector.getActualGain()
		
		if not isAreaDetectorPilatus(detector):
			PilatusCheckGain(update, detector, currentEnergy, currentGain, do_sleep=True)
			PilatusCheckThresholdOnly(update, detector, currentEnergy, do_sleep=True)
		
		else:
			
			detector.setAutoApplyThresholdGain(False)
			
			logger.info("setting demand energy {}eV on AreaDetector", currentEnergy)
			detector.setEnergyDemand(currentEnergy)
			
			gain_changed = PilatusCheckGain(update, detector, currentEnergy, currentGain, do_sleep=False)
			th_changed = PilatusCheckThresholdOnly(update, detector, currentEnergy, do_sleep=False)
			
			if gain_changed or th_changed:
				logger.debug("calling apply threshold on AreaDetector")
				detector.applyThreshold()
				thresholdSleep(update, detector)
	
	else:
		update("Not a Pilatus detector, not checking threshold")


def PilatusCheckThresholdOnly(update, detector, currentEnergy, do_sleep=True):
	# assume that we will not change the threshold
	threshold_changed = False
	
	if isPilatus(detector):
		# second part, set threshold energy
		if True : # threshold should be 1/2 of incoming energy
			defaultThresholdEnergy = getBestPilatusThreshold(currentEnergy)
			if (currentEnergy < 8000.1 and detector.getThresholdEnergy() < 4000.1):
				update("Energy below 8000eV and threshold already at 4000eV, not changing threshold energy")
			elif (abs(currentEnergy - detector.getThresholdEnergy()*2)>100): # is difference greater than 50 eV in threshold energy?
				update("Changing threshold energy to "+str(defaultThresholdEnergy))
				detector.setThresholdEnergy(defaultThresholdEnergy) # threshold energy must be in eV
				threshold_changed = True
				if do_sleep:
					thresholdSleep(update, detector)
			else:
				update("Not changing threshold energy")
	else:
		update("Not a Pilatus detector, not checking threshold")
	
	return threshold_changed


def setDetectorCollectionParameters(detector, detCollPar, exposeTime, wavelength, distance, start, angleRange, xBeam, yBeam, actualTransmission, flux, filepath, update):
	''' flux should be Optional<Double> as returned by flux_utils.get_current_flux() '''
	if not isinstance(flux, Optional):
		flux = Optional.fromNullable(flux) # if value, wrap as Optional
	
	detCollPar.setExposureTime(exposeTime)
	detCollPar.setWavelength(wavelength)
	detCollPar.setSampleDetectorDistance(distance)
	detCollPar.detectorVOffset = 0
	detCollPar.setStartAngle(start)
	detCollPar.setOscillationSize(angleRange)
	detCollPar.setPolarization(0.99)
	detCollPar.setBeamX(xBeam)
	detCollPar.setBeamY(yBeam)
	detCollPar.setTransmission(actualTransmission)
	detCollPar.setFlux(flux)
	
	detCollPar.phiIncrement = 0
	detCollPar.chi = 0
	detCollPar.chiIncrement = 0
	detCollPar.omega = start
	detCollPar.omegaIncrement = angleRange
	
	detector.setFilepath(filepath)
	update("Sent out file path to detector")
	detector.setGapFill(-1)
	update("Set gap fill to -1")


def setInitialCollectionParameters(detector, camera, numImages, startImageNumber, angleOverlap, dnaFilePrefix, update, multipleTriggers=False, delayTime=-1):
	detector.setFileprefix(dnaFilePrefix)
	detector.setNumberOfExposures(1)
	detector.setNumberOfImages(1) # necessary if not special collection
	detector.setFileformat("%s%s" + MxProperties.IMAGE_NUMBER_FORMAT + "." + detector.getSuffix())
	detector.setFilenumber(startImageNumber)
	detector.setAutoIncrement("Yes")
	
	if delayTime == -1:
		delayTime = camera.getShutterOpenTime()
	detector.setDelayTime(delayTime)
	
	detector.setMode("Mult. Trigger" if multipleTriggers else "Ext. Trigger")
	detector.setImageMode("Continuous")
	
	#Robin's email:Mon 22/02/2010 13:55. assume special mode if omega delta ==0. stop using comment field!
	if angleOverlap==0 and (detector.getAttribute("PILATUSSPECIALMODE")==None or detector.getAttribute("PILATUSSPECIALMODE")==True):
		update("PILATUS SPECIAL COLLECTION MODE")
		return True
	else:
		return False


def setSpecialCollectionModeCameraParameters(detector, camera, detCollPar, exposeTime, angleRange, numImages, passes, startAngle=None):
	detCollPar.setExposureTime(exposeTime)
	# change parameters so that camera thinks it's a single image experiment
	# angleOverlap will be ignored!!!
	camera.setImageAngularSize(angleRange * numImages)
	camera.setNumberPasses(passes)
	camera.setImageTime(exposeTime * numImages)
	
	if startAngle:
		camera.setImageStartAngle(startAngle)
	
	detector.setNumberOfExposures(1)
	detector.setNumberOfImages(numImages)


def thresholdSleep(update, detector):
	try:
		thresholdSleep = detector.getThresholdTime()
	except:
		if update:
			update("Unknown Pilatus detector! Not sleeping for threshold time or gain")
		return
	
	if update:
		update("Will sleep for "+str(thresholdSleep)+"sec while gain or threshold is changed...")
	
	if not isDummyModeEnabled():
		startTime=time.time()
		while time.time()-startTime < thresholdSleep:      # Let's make it clearer what's happening and how long's left - Mark 22/10/12
			if update:
				timeToGo=`int(thresholdSleep-(time.time()-startTime)+0.5)`
				update("Still changing Pilatus settings ("+timeToGo+"s remaining), do not restart GDA.")
				updateProgress(int(100*(time.time()-startTime)/thresholdSleep),"Changing Pilatus settings ("+timeToGo+"s remaining)")
			time.sleep(10)
	else:
		update("GDA is running in dummy mode, not sleeping")


def updateProgress(percent, msg):
	JythonScriptProgressProvider.sendProgress(percent, msg)


class PilatusThresholdAndGainThread(ScriptThread):

	def __init__(self, detector, new_energy, log):
		ScriptThread.__init__(self)
		self.detector = detector
		self.new_energy = new_energy
		self.log = log


	def run(self):
		try:
			if isPilatus(self.detector):
				self.log("changing detector gain/threshold (if necessary)")
				PilatusCheckThreshold(self.detector, self.new_energy, self.log)
				self.log("detector gain/threshold should now be correct")
		except:
			self.exception = sys.exc_info()[1]

