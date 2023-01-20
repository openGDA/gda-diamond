
from gda.device.detector import MoveableImageDetector, RoiExtractor
from __builtin__ import True, None
from  gda.data.scan.datawriter import DefaultDataWriterFactory
from gda.scan import ConcurrentScan, CentroidScan


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

imageDetector = moveableImageDet

imageSize = [1000, 500]

roiCentre = [500, 250] # ROI centre pixel position
roiSize = [20, 20] # ROI half size in x and y

# ROIs to take lineout at roiCentre location on detector in horiz and vert. direction
hvRois = RoiExtractor()
hvRois.setName("hvRois")
hvRois.setDetector(imageDetector)
# ROI in horizontal direction (along x axis, at y ROI centre position)
# name, xmin, ymin, xmax, ymax
hvRois.addRoi("horizontalRoi", 0, roiCentre[1]-roiSize[1], imageSize[0], roiCentre[1]+roiSize[1])
hvRois.addRoi("verticalRoi", roiCentre[0]-roiSize[0], 0, roiCentre[0]+roiSize[0], imageSize[1])
hvRois.addRoi("centreRoi", roiCentre[0]-roiSize[0], roiCentre[1]-roiSize[1], roiCentre[0]+roiSize[0], roiCentre[1]+roiSize[1])
hvRois.configure()

from uk.ac.gda.beamline.i20.scannable import CurveFitting
curveFitting = CurveFitting()
curveFitting.setFitToPeakPointsOnly(True)
curveFitting.setPeakPointRange(4)

def getYawScannable(analyserCrystal) :
    return analyserCrystal.getRotMotor()

def getPitchScannable(analyserCrystal) :
    return analyserCrystal.getPitchMotor()

def doPitchScan(pitchScannable, centralPitch) :
    return runScanAndFindPeak(pitchScannable, centralPitch, 0.1, 0.01, "verticalRoi")

def doYawScan(yawScannable, centralYaw) :
    return runScanAndFindPeak(yawScannable, centralYaw, 0.2, 0.02, "horizontalRoi")

def doEnergyScan(energyScannable, expectedEnergy) :
    return runScanAndFindPeak(energyScannable, expectedEnergy, 5.0, 0.3, "centreRoi")

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

def moveAllXStages(xesBraggScn, position = 1.2):
    print("Moving all X stages for %s to %.4g"%(xesBraggScn.getName(), position))
    for cryst in xesBraggScn.getCrystalsList() :
        cryst.getxMotor().asynchronousMoveTo(position)
    xesBraggScn.waitWhileBusy()
    print("Finished")
    
def printInfo(info):
    marker = "----------"
    print("\n%s %s %s"%(marker,info, marker))
    
# First move all analyser stages out of the way
def optimisePitchYaw(xesEnergyScn, crystalIndex, expectedEnergy) :
    """
        Parameters 
            XES energy scannable object
            crystalIndex - index of the analyser crystal to be optimised (-3, -2, 1, 1, 2, 3)
            expectedEnergy - energy value to use when calculating positions of the analyser motors.
            
        Method : 
        1) Disable all analysers apart from the one being optimised. This means they are not moved when changing energy.
        2) Move the analyser to the expectedEnergy using the XESEnergy scannable.
        3) Scan the pitch and yaw about the centre values at the expected energy; find the pitch and yaw positions that best overlap
        the diffracted image with the detector horizontal and vertical detector ROIs.
        4) Set the pitch and yaw offsets (in Epics motor record) so that actual motor positions correspond to the best fit positions
        from step 3) when they are moved to values for the expectedEnergy.
        5) Do several scans of XESEnergy using several different pitch offsets. For each energy scan, find the energy where the peak
        emission occurs. Use linear regression on the set of [peak emission energy, pitch offset] values to find the offset that puts
        the peak emission at the expectedEnergy.
        
    """
    
    printInfo("Preparing to optimise analyser %d on %s. Expected energy = %.4g"%(crystalIndex, xesEnergyScn.getName(), expectedEnergy))

    xesBraggScn = xesEnergyScn.getXes()
    
    # Get the analyser crystal object corresponding to the index
    analyserCrystal = None
    for cryst in xesBraggScn.getCrystalsList() :
        if cryst.getHorizontalIndex() == crystalIndex :
            analyserCrystal = cryst
    
    if analyserCrystal is None : 
        raise Exception("No analyser crystal with index = "+str(crystalIndex)+" was found in "+xesBraggScn.getName())
    
    # Disable all the analysers except the one being optimised    
    disableAnalysers(xesBraggScn, analyserCrystal.getHorizontalIndex())   
    
    # Move analyser motors to the expected energy
    print("Moving %s to expected energy %.4g"%(xesEnergyScn.getName(), expectedEnergy))
    xesEnergyScn.moveTo(expectedEnergy)
    
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
    printInfo("Running yaw scan using "+yawScannable.getName())
    yawScanResults = doYawScan(yawScannable, centreYaw)
    
    # Set the pitch and yaw values to to peak intensity position found during the scan
    pitchPeak = pitchScanResults[1].getPosition()
    printInfo("Setting motor offsets using scan results")
    setupOffsets(pitchScannable, pitchPeak, centrePitch)    
    yawPeak = yawScanResults[1].getPosition()
    setupOffsets(yawScannable, yawPeak, centreYaw)

    # Do XES energy scan near expected energy; repeat several times for different pitch offset values
    pitchOffsets = [-0.4, -0.2, 0, 0.2, 0.4]
    printInfo("Running energy scans using "+pitchScannable.getName()+" offset values : "+str(pitchOffsets))
    energyScanResults = doEnergyScanLoop(xesEnergyScn, pitchScannable, expectedEnergy, pitchOffsets)
    
    
    printInfo("Fitting motor offset - peak Xes energy values to find best offset for %s"%pitchScannable.getName())

    fitResults = fitOffsetPitchCurve(energyScanResults, pitchOffsets)
    
    # y = ax + b (y = energy, x = offset).
    # Find offset to give expected energy 
    a=fitResults[0]
    b=fitResults[1]
    offset = (expectedEnergy-b)/a
    print("Offset to give peak at expected energy (%.4g) : %.4g"%(expectedEnergy, offset))
    return fitResults

def fitOffsetPitchCurve(energyLoopResult, pitchOffsets) :
    energyPeakValues = []
    for res in energyLoopResult :
        energyPeakValues.append(res[1].getPosition())
    print("Offset values (x) : %s"%(pitchOffsets))
    print("Energy peak positions (y) : %s"%(energyPeakValues))
    
    fitResults = linearFit(pitchOffsets,energyPeakValues)
    fitParams = fitResults.parameters
    print("Linear regression results using y = ax + b : a = %.4g, b = %.4g"%(fitParams[0], fitParams[1]))
    fitResults.plot()
    return fitResults
    
import scisoftpy as dnp
 
# Move motor to given peakPosition (peakPos); Call setPosition with calculatedPos - this adjusts
# the motor offsets so that next time it moves to calculatedPos, the real position is peakPos.
def setupOffsets(scannableMotor, peakPos, calculatedPos):
    print("Moving %s to peak found during scan : %.4g"%(scannableMotor.getName(), peakPos))
    scannableMotor.moveTo(peakPos)
    print("Setting offset on %s to give peak value at %.4g"%(scannableMotor.getName(), calculatedPos))
    scannableMotor.setPosition(calculatedPos)

def linearFit(xvals, yvals) :
    """
        xvals - array of x values
        yvals - array of y values
        
        See : https://alfred.diamond.ac.uk/documentation/manuals/Diamond_SciSoft_Python_Guide/trunk/fitting.html
    """
    initialParams=[0, 1]
    results = dnp.fit.fit(dnp.fit.function.linear, dnp.array(xvals), dnp.array(yvals), initialParams, bounds=[], args=None, ptol=1e-4, optimizer='local')
    # Use 'results.plot()' to plot data and the fitted line :-)
    # results.parameterValues to get array of the fitted parameters (for straight line : 0 = gradient, 1=intercept)
    return results

def getLastScanFileName() :
    return lastScanDataPoint().getCurrentFilename()

def testRoiProcessing(filename) :
    return processRois(filename, "rois", "verticalRoi", moveableImageDet.getxScannable().getName(), moveableImageDet.getyScannable().getName(), 5)

# Fit x y data from file to Gaussian profile
def fitDataFromFile(nexusFileName, groupName, roiName, axisName) :
    data = dnp.io.load(nexusFileName)
    dataGroup = data['entry1'][groupName];
    return curveFitting.findPeakOutput(dataGroup[axisName][...], dataGroup[roiName][...])
                                
    
def processRois(nexusFileName, groupName, roiName, xAxisName, yAxisName, numBestValues=10) :
    
    # load the x, y value datasets and the roi values
    data = dnp.io.load(nexusFileName)
    dataGroup = data['entry1'][groupName]
    xValues = dataGroup[xAxisName][...]
    yValues = dataGroup[yAxisName][...]
    roiValues= dataGroup[roiName][...]
    
    numYVals = len(vals)
    numXVals = len(vals[0])
    
    # Make list of tuples (roiValue, xPosition, yPosition)
    combined = []
    for i in range(numYVals) :
        for j in range(numXVals) :
            combined.append( (roiValues[i][j], xValues[i][j], yValues[i][j]) )
    
    # Sort into order of descending ROI count
    sortedRois = sorted(vals, key=lambda s : s[0], reverse=True)
    
    return sortedRois
    return combined

def getAverage(intensityPosition) :
    return [sum(x) for x in zip(*intensityPosition)]

    # find the best N values
    # find bounding box in x-y containing the best values
