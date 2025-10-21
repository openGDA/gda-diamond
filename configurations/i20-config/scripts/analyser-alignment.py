
from gda.device.detector import MoveableImageDetector, RoiExtractor
from __builtin__ import True, None
from  gda.data.scan.datawriter import DefaultDataWriterFactory
from gda.scan import ConcurrentScan, CentroidScan

# Parameters to control the range and step size of the pitch, yaw
pitch_scan_range = 0.2
pitch_scan_step_size = 0.025

yaw_scan_range = 0.3
yaw_scan_step_size = 0.025

energy_scan_range = 5.0
energy_scan_step_size = 0.3

moveableImageDet = MoveableImageDetector()
moveableImageDet.setName("moveableImageDet")
# set x and y scannables to be pitch and yaw
#moveableImageDet.setxScannable(pitchScannable)
#moveableImageDet.setyScannable(yawScannable)


moveableImageDet.setLowerPositionLimit([-0.1, -0.2])
moveableImageDet.setUpperPositionLimit([0.1, 0.2])
moveableImageDet.setImageSize([1000,500])
moveableImageDet.configure()
  

# imageDetector = medipix
nexusFilenameTemplate = "alignment/%d.nxs"
asciiFilenameTemplate = "alignment/%d.dat"

# medipix1 for upper, medipix2 for lower
imageDetector = medipix2_addetector
detectorMap = {XESEnergyLower:medipix2_addetector , XESEnergyUpper:medipix1_addetector}
#imageDetector = playbackDet

imageSize=[256, 1033] #'height', 'width'
roiCentre=[128, 517]
roiSize=[50,50]

#imageDetector = moveableImageDet
#imageSize = [1000, 500]
#roiCentre = [500, 250] # ROI centre pixel position
#roiSize = [20, 20] # ROI half size in x and y

# ROIs to take lineout at roiCentre location on detector in horiz and vert. direction
hvRois = RoiExtractor()
hvRois.setName("hvRois")
hvRois.setDetector(imageDetector)

from uk.ac.gda.beamline.i20.scannable import CurveFitting
curveFitting = CurveFitting()
curveFitting.setFitToPeakPointsOnly(True)
curveFitting.setPeakPointRange(4)

def setupProcessingRois(roiWidth, roiHeight) :
# ROI in horizontal direction (along x axis, at y ROI centre position)
    print("Setting up ROIs on RoiExtractor : width = %d, height = %d"%(roiWidth, roiHeight))
    roiHalfSize = [ int(roiHeight/2), int(roiWidth/2) ]
    hvRois.clearRois()
    hvRois.addRoi("verticalRoi", 0, roiCentre[1]-roiHalfSize[1], imageSize[0], roiCentre[1]+roiHalfSize[1]) # name, xmin, ymin, xmax, ymax
    hvRois.addRoi("horizontalRoi", roiCentre[0]-roiHalfSize[0], 0, roiCentre[0]+roiHalfSize[0], imageSize[1])
    hvRois.addRoi("centreRoi", roiCentre[0]-roiHalfSize[0], roiCentre[1]-roiHalfSize[1], roiCentre[0]+roiHalfSize[0], roiCentre[1]+roiHalfSize[1])

def showProcessingRois() :
    print("ROIs on RoiExtractor : ")
    for roi in hvRois.getRois() :
        xroi = roi.getXRoi()
        yroi = roi.getYRoi()
        print("%15s : \tx (start, end) = %d, %d, \ty (start, end) = %d, %d"%(roi.getRoiName(), xroi.getRoiStart(), xroi.getRoiEnd(), yroi.getRoiStart(), yroi.getRoiEnd()))

setupProcessingRois(100, 100)



def getYawScannable(analyserCrystal) :
    return analyserCrystal.getRotMotor()

def getPitchScannable(analyserCrystal) :
    return analyserCrystal.getPitchMotor()

def doPitchScan(pitchScannable, centralPitch) :
    return runScanAndFindPeak(pitchScannable, centralPitch, pitch_scan_range, pitch_scan_step_size, "horizontalRoi")

def doYawScan(yawScannable, centralYaw) :
    return runScanAndFindPeak(yawScannable, centralYaw, yaw_scan_range, yaw_scan_step_size, "verticalRoi")

def doEnergyScan(energyScannable, expectedEnergy) :
    return runScanAndFindPeak(energyScannable, expectedEnergy, energy_scan_range, energy_scan_step_size, "centreRoi")

def doEnergyScanLoop(energyScannable, pitchScannable, expectedEnergy, offsets) :
    # Do energy scan, but disable all the analysers stages except the one being optimised
    energyScanResults=[]
    for offset in offsets :
        print("Moving %s offset to %.4g"%(pitchScannable.getName(), offset))
        pitchScannable.setOffset(offset) 
        result = doEnergyScan(energyScannable, expectedEnergy)
        energyScanResults.append(result)
        
    return energyScanResults

def runScanAndFindPeak(scnToMove, scanCentre, scanRange=0.1, scanStepSize=0.01, roiName="horizontalRoi", collectionTime=1.0):
    print("Scanning %s : centre = %.4g, range = %.4g, stepsize = %.4g"%(scnToMove.getName(), scanCentre, scanRange, scanStepSize))
    print("ROI = %s"%(roiName))
    
    imageDetector.stop()
    
    # Generate points for centroid scan (ConcurrentScan needs the points as a tuple) 
    scanPoints = dnp.arange(scanCentre-scanRange, scanCentre+scanRange+0.5*scanStepSize, scanStepSize)
    scanObj = ConcurrentScan([scnToMove, tuple(scanPoints.tolist()), imageDetector, collectionTime, hvRois])

    # Create XasAsciiNexusDatawriter with nexus and ascii output paths
    dw=DefaultDataWriterFactory.createDataWriterFromFactory()
    dw.setNexusFileNameTemplate(nexusFilenameTemplate)
    dw.setAsciiFileNameTemplate(asciiFilenameTemplate)

    scanObj.setDataWriter(dw) # CentroidScan does not use this datawriter. Need to set on CentroidScan#concurrentScan object...
    scanObj.runScan()
    
    scanDataFilename = getLastScanFileName()
    return scanDataFilename, fitDataFromFile(scanDataFilename, hvRois.getName(), roiName, scnToMove.getName())

def setEnableAllAnalysers(xesBraggScn, state):
    print("Setting %s all crystals allowed to move = %s"%(xesBraggScn.getName(), state))
    vals=[]
    for cryst in xesBraggScn.getCrystalsList() :
        vals.append(state)
    print("Crystals allowed to move = %s"%(vals))
    xesBraggScn.getCrystalsAllowedToMove().moveTo(vals)

def disableAnalysers(xesBraggScn, index):
    print("Enabling analyser %d on %s (disabling all others)"%(index, xesBraggScn.getName()))
    vals=[]
    for cryst in xesBraggScn.getCrystalsList() :
        if cryst.getHorizontalIndex() == index :
            vals.append("true")
        else :
            vals.append("false")
    print("Crystals allowed to move = %s"%(vals))
    xesBraggScn.getCrystalsAllowedToMove().moveTo(vals)

def moveAllPitchStages(xesBraggScn, amount):
    print("Moving all pitch stages for %s by %.4g degrees"%(xesBraggScn.getName(), amount))
    for cryst in xesBraggScn.getCrystalsList() :
        pitchMotor = cryst.getPitchMotor()
        currentPos = pitchMotor.getPosition()
        newPos = currentPos + amount
        print("Moving %s from %.4g to %.4g"%(pitchMotor.getName(), currentPos, newPos))
        pitchMotor.asynchronousMoveTo(newPos)

    xesBraggScn.waitWhileBusy()
    print("Finished")

def moveAllXStages(xesBraggScn, position = 1.2):
    print("Moving all X stages for %s to %.4g"%(xesBraggScn.getName(), position))
    for cryst in xesBraggScn.getCrystalsList() :
        cryst.getxMotor().asynchronousMoveTo(position)
    xesBraggScn.waitWhileBusy()
    print("Finished")
    
def printInfo(info):
    marker = "----------"
    print("\n%s %s %s"%(marker,info, marker))
    
def getAnalyserCrystal(xesEnergyScn, crystalIndex) :
    xesBraggScn = xesEnergyScn.getXes()
    analyserCrystal = None
    for cryst in xesBraggScn.getCrystalsList() :
        if cryst.getHorizontalIndex() == crystalIndex :
            analyserCrystal = cryst
    
    if analyserCrystal is None : 
        raise Exception("No analyser crystal with index = "+str(crystalIndex)+" was found in "+xesBraggScn.getName())
    
    return analyserCrystal
    
def setupDetectorToUse(xesEnergyScn) :
    detectorForScan = detectorMap.get(xesEnergyScn)
    if detectorForScan == None : 
        raise Exception("No detector found to use for %s"%(xesEnergyScn.getName()))

    global imageDetector
    imageDetector = detectorForScan
    
    # Set the detector to be use on the ROIExtractor 
    hvRois.setDetector(imageDetector)
    
    print("Using detector %s for %s scans"%(imageDetector.getName(), xesEnergyScn.getName()))
    
def optimisePitchYaw(xesEnergyScn, crystalIndex, expectedEnergy) :
    """
        Parameters 
            XES energy scannable object
            crystalIndex - index of the analyser crystal to be optimised (-3, -2, 1, 1, 2, 3)
            expectedEnergy - energy value to use when calculating positions of the analyser motors.
            
        Method : 
        1) Enable all analysers
        2) Move to the expected energy
        3) Move the pitch stages by a small amount so that the image from the analysers is not the detector
        4) Disable all analysers apart from the one being optimised. This means they are not moved when changing energy.
        5) Move the analyser to the expectedEnergy using the XESEnergy scannable.
        6) Scan the pitch and yaw about the centre values at the expected energy; find the pitch and yaw positions that best overlap
        the diffracted image with the detector horizontal and vertical detector ROIs.
        7) Set the pitch and yaw offsets (in Epics motor record) so that actual motor positions correspond to the best fit positions
        from step 3) when they are moved to values for the expectedEnergy)
    """
    
    printInfo("Preparing to optimise analyser %d on %s. Expected energy = %.2f"%(crystalIndex, xesEnergyScn.getName(), expectedEnergy))

    # Get the detector to use for the scan
    setupDetectorToUse(xesEnergyScn)

    xesBraggScn = xesEnergyScn.getXes()
    
    prepareAnalyserPositions(xesEnergyScn, crystalIndex, expectedEnergy)
    
    # Move the analyser being aligned to the 'expected energy'.
    print("Moving %s to expected energy %.4g"%(xesEnergyScn.getName(), expectedEnergy))
    xesEnergyScn.moveTo(expectedEnergy)

    # Get the analyser crystal object corresponding to the index
    analyserCrystal = getAnalyserCrystal(xesEnergyScn, crystalIndex)
    
    # Get pitch and yaw scannables, record the initial positions (set by moving xesEnergy)
    pitchScannable = getPitchScannable(analyserCrystal)
    yawScannable = getYawScannable(analyserCrystal)
    
    centrePitch = pitchScannable.getPosition()
    centreYaw = yawScannable.getPosition()

    #Setup the detector in dummy mode so image is produced during scan.
    if LocalProperties.isDummyModeEnabled() :
        # Apply slight offset, so that pitch needs to be away from calculated value to get image in the centre
        pitchScannable.setOffset(0.05)
        yawScannable.setOffset(0.05)
        # Set the x, y scannables and the detector position ranges
        moveableImageDet.setxScannable(pitchScannable)
        moveableImageDet.setyScannable(yawScannable)
        moveableImageDet.setLowerPositionLimit([centrePitch-0.2, centreYaw-0.4])
        moveableImageDet.setUpperPositionLimit([centrePitch+0.2, centreYaw+0.4])

    #Do pitch and yaw scans, find the pitch and yaw producing the peak ROI counts
    printInfo("Running pitch scan using "+pitchScannable.getName())
    pitchScanResults = doPitchScan(pitchScannable, centrePitch)
    pitchPeak = pitchScanResults[1].getPosition()
    print("Peak pitch position : %.4f\n"%(pitchPeak))
    print("Moving pitch to peak position")
    pitchScannable.moveTo(pitchPeak)
    
    printInfo("Running yaw scan using "+yawScannable.getName())
    yawScanResults = doYawScan(yawScannable, centreYaw)
    yawPeak = yawScanResults[1].getPosition()
    print("Peak yaw position : %.4f"%(yawPeak))

    # Set the pitch and yaw values to to peak intensity position found during the scan
    #pitchPeak = pitchScanResults[1].getPosition()
    printInfo("Setting motor offsets using scan results")
    setupOffsets(pitchScannable, centrePitch, pitchPeak, )    
    setupOffsets(yawScannable, centreYaw, yawPeak)


def prepareAnalyserPositions(xesEnergyScn, crystalIndex, expectedEnergy) :
    """
        Prepare analyser stages for alignment scans :
        0) Enable all analysers
        1) Move XESEnergy to the 'expected energy' value
        2) Adjust pitch of all motors by a small amount (2 deg), to place image away from detector.
        3) Disanle all the analysers apart from the one with specified index
        4) Move XESEnergy again to the 'expected energy' value
        
    """
    
    printInfo("Preparing analyser motors on %s (analyser index = %d)---"%(xesEnergyScn.getName(), crystalIndex))
    
    xesBraggScn = xesEnergyScn.getXes()

    #Enable all analysers
    print("Enabling all analysers for %s"%(xesBraggScn.getName()))
    setEnableAllAnalysers(xesBraggScn, "true")
    
        # Move analyser motors to the expected energy
    print("Moving %s to expected energy : %.4g"%(xesEnergyScn.getName(), expectedEnergy))
    xesEnergyScn.moveTo(expectedEnergy)
    
    # Change the pitch of all the stages by a small amount, so the image from each
    # analyser is moved off the detector
    pitchMoveAmount=2.0
    print("Moving pitch by %.2f"%(pitchMoveAmount))
    moveAllPitchStages(xesBraggScn, pitchMoveAmount)
        
    # Disable all the analysers when changing energy apart from the one being optimised
    print("Disabling all analysers except for : %d"%(crystalIndex))
    disableAnalysers(xesBraggScn, crystalIndex)
    
     # Move the analyser being aligned to the 'expected energy'.
    print("Moving %s to expected energy %.4g"%(xesEnergyScn.getName(), expectedEnergy))
    xesEnergyScn.moveTo(expectedEnergy)
    
    print("Finished preparing analyser motors")
    
def optimiseEnergy(xesEnergyScannable, crystalIndex, expectedEnergy, numRepetitions = 3) :
    """
        Perform XESEnergy scans to find the yaw and pitch offsets that put the peak emission at the 'expected' energy
        
        Parameters 
            XES energy scannable object
            crystalIndex - index of the analyser crystal to be optimised (-3, -2, 1, 1, 2, 3)
            expectedEnergy - energy value to use when calculating positions of the analyser motors.
            numRepetition - the number of times the energy scan should be repeated (optional, default = 3)
            
        Method :
        1) Do scan of XESEnergy using XESEnergy. 
        2) Find the energy of the peak of the emission profile. Move the XESEnergy scannable to the peak energy to set the pitch
        and yaw scannables at peak position.
        3) Set the pitch and yaw offsets to give the expected pitch and yaw values (i.e. pitch and yaw for expected energy)
        
        4) Repeat steps 1-3 until peak XESEnergy scan is close enough to expectedEnergy value
        
    """
    printInfo("Running energy scans using %s, analyser %d"%(xesEnergyScannable.getName(), crystalIndex))

    setupDetectorToUse(xesEnergyScannable)
    
    prepareAnalyserPositions(xesEnergyScannable, crystalIndex, expectedEnergy)

    analyserCrystal = getAnalyserCrystal(xesEnergyScannable, crystalIndex)
    pitchScannable = getPitchScannable(analyserCrystal)
    yawScannable = getYawScannable(analyserCrystal)
    
    xesEnergyScannable.moveTo(expectedEnergy)
    expectedPitch = pitchScannable.getPosition()
    expectedYaw = yawScannable.getPosition();

    for i in range(numRepetitions) :  
        printInfo("Scan %d of %d"%(i+1, numRepetitions))
        fitResult = doEnergyScan(xesEnergyScannable, expectedEnergy)
        peakEnergy = fitResult[1].getPosition()
        print("Energy peak position : %.4f"%(peakEnergy))
        print("Moving %s to %.4f"%(xesEnergyScannable.getName(), peakEnergy))
        xesEnergyScannable.moveTo(peakEnergy)
        
        printInfo("Setting motor offsets using scan results")
        setupOffsets(pitchScannable, expectedPitch)    
        setupOffsets(yawScannable, expectedYaw)  
    
def optimiseAnalyser(xesEnergyScannable, crystalIndex, expectedEnergy) :
    optimisePitchYaw(xesEnergyScannable, crystalIndex, expectedEnergy)
    optimiseEnergy(xesEnergyScannable, crystalIndex, expectedEnergy)
 
# Move motor to given peakPosition (peakPos); Call setPosition with calculatedPos - this adjusts
# the motor offsets so that next time it moves to calculatedPos, the real position is peakPos.
def setupOffsets(scannableMotor, calculatedPos, peakPos=None):
    if peakPos != None : 
        print("Moving %s to peak found during scan : %.4f"%(scannableMotor.getName(), peakPos))
        scannableMotor.moveTo(peakPos)
    print("Current %s offset : %.6f"%(scannableMotor.getName(), scannableMotor.getUserOffset()))
    print("Setting offset on %s to give peak value at %.4f"%(scannableMotor.getName(), calculatedPos))
    scannableMotor.setPosition(calculatedPos)
    print("---> New %s offset : %.6f\n"%(scannableMotor.getName(), scannableMotor.getUserOffset()))

def getLastScanFileName() :
    return lastScanDataPoint().getCurrentFilename()

# Fit x y data from file to Gaussian profile
def fitDataFromFile(nexusFileName, groupName, roiName, axisName) :
    data = dnp.io.load(nexusFileName)
    dataGroup = data['entry1'][groupName];
    return curveFitting.findPeakOutput(dataGroup[axisName][...], dataGroup[roiName][...])

from gda.device.scannable import ScannableMotor
def showOffsets(xesEnergyScannable) :
    for scn in xesEnergyScannable.getXes().getScannables() :
        if isinstance(scn, ScannableMotor) :
            mot = scn.getMotor()
            print("%s : %.4f"%(scn.getName(), mot.getUserOffset()))

