from org.slf4j import LoggerFactory
from gda.epics import CAClient

class OverlapDetector(DetectorBase):
    """
Detector class for computing 'overlap' between reference and current spectrum on an EdeDetector.
'Overlap' is the sum over the element-by-element multiplication of the reference and current detector spectra.

This is intended to assist getting same turboslit energy before and after moving turboslit arm out and into beam
when making diffraction measurements :

1) Measure 'reference' spectrum at desired position of TurboSlit - use OverlapDet#recordReferenceSpectrum()
2) Move TurboSlit out of the beam by moving the arm.
3) Make required measurements using full beam
4) Move arm back, to replace turboslit in the beam
5) Scan the turboslit a small amount either side of the position of reference spectrum (from step 1)
including OverlapDetector scannable in the scan.
6) Peak value of OverlapDetector during the scan corresponds to turboslit real-space position matching original
position from step 1. Fitted peak position is printed to Jython console at the end of the scan, and available
from OverlapDet#getStats().getPosition()
    """

    def __init__(self, name):
        self.logger = LoggerFactory.getLogger("OverlapDetector")
        self.setName(name)
        self.setExtraNames([]);
        self.setInputNames([name]);
        self.setOutputFormat(["%.4f"])
        self.overlapCurve = []
        self.referenceSpectrum = []
        self.stats = []
        self.readoutWarningShown = False
        self.fittedCurve = None
        self.edeDetector = None
        # Fraction of the x axis range to use either side of the peak y value
        # when fitting the curve
        self.fitPeakRangeFrac = 0.2
        
    def setEdeDetector(self, edeDetector):
        self.edeDetector = edeDetector
        
    def setReferenceSpectrum(self, referenceSpectrum):
        self.referenceSpectrum = referenceSpectrum
    
    def getReferenceSpectrum(self):
        return self.referenceSpectrum
    
    def recordReferenceSpectrum(self):
        self.referenceSpectrum = self.getCurrentSpectrum()
        
    def collectData(self):
        pass

    def createsOwnFiles(self):
        return False
    
    def getStatus(self):
        return 0
    
    def isBusy(self):
        return False
    
    def showWarning(self, message):
        InterfaceProvider.getTerminalPrinter().print(message)
        self.logger.warn(message)
        
    # Extract an array containing the currently collected spectrum from the detector
    def getCurrentSpectrum(self):
        #Get the NXDetectorData object
        if self.edeDetector == None :
            self.showWarning("Cannot get current spectrum - no EdeDetector has been set")
            return []
        
        dat=self.edeDetector.readout()
        if dat == None :
            self.showWarning("No data available from %s"%(self.edeDetector.getName()))
            return []
        
        # Extract the channel counts from the tree
        dset = dat.getData(self.edeDetector.getName(), 'data', 'SDS').toDataset()
        # Convert to an array
        return dset.getData()

    def atScanStart(self):
        self.overlapCurve = []
        self.readoutWarningShown = False
        
    def readout(self):
        """
        Compute the 'overlap' between the 'reference' and the current spectrum.
        i.e. the sum over the element-by-element multiplication of the two arrays.
        """
        currentData = self.getCurrentSpectrum()

        if len(currentData) != len(self.referenceSpectrum):
            if self.readoutWarningShown == False :
                self.showWarning("Cannot compute data from %s - "
                    "current spectrum length (%d), does not match reference spectrum length (%d)"%(self.getName(), len(currentData), len(self.referenceSpectrum)))
            self.readoutWarningShown = True
            return 0.0
        
        overlap = 0.0
        for i in range(len(currentData)) :
            overlap += currentData[i]*self.referenceSpectrum[i]
            
        self.overlapCurve.append(overlap)
        return overlap

    def atScanEnd(self):
        if len(self.overlapCurve) == 0 :
            sdp = self.getLastScanDataPoint()
            if sdp == None :
                print "Could not load data from Nexus file - unable to get name of last scan"
                return 
            self.overlapCurve = self.getDataFromFile(sdp.getCurrentFilename(), "data")

        if len(self.overlapCurve) == 0 :
            self.showWarning(self.getName()+" cannot compute statistics at end of scan - reference spectrum has not been set or no data has been collected")
            return
        
        axisData = self.getAxisDataFromFile()
        axisRange = max(axisData)-min(axisData)
        maxFwhm = axisRange
        maxArea = axisRange*10

        print "X axis range = %.4e, using %.2f of range about peak when fitting"%(axisRange, self.fitPeakRangeFrac)
        self.fittedCurve = fitGaussian(axisData, self.overlapCurve, axisRange*self.fitPeakRangeFrac, maxFwhm, maxArea)

        message= "Results from %s : fitted curve peak position = %.4e"%(self.getName(), self.fittedCurve.getPosition())
        print message
        
    # Read the x values produced during the scan from the nexus file
    def getAxisDataFromFile(self):
        sdp = self.getLastScanDataPoint()
        filename = sdp.getCurrentFilename();
        
        # Assume the first scannable is the one being moved during the scan
        axisScannableName = sdp.getScannableNames()[0]
        return self.getDataFromFile(filename, axisScannableName)

    def getLastScanDataPoint(self):
        sdpp = InterfaceProvider.getScanDataPointProvider()
        return sdpp.getLastScanDataPoint()

    # Return statistic computed at the end of the scan :
    def getStats(self):
        return self.fittedCurve

    def getDataFromFile(self, filename, dataname) :
        import scisoftpy as dnp
        dataFile = dnp.io.load(filename)
        return dataFile['entry1'][self.getName()][dataname][...].data

from uk.ac.diamond.scisoft.analysis.fitting.functions import Gaussian 
from uk.ac.diamond.scisoft.analysis.fitting import Fitter
import math, random

def fitGaussian(xdata, ydata, fitPeakRange=20, fitMaxFwhm=100, fitMaxArea=100) :
    """
    Attempt to fit a Gaussian function to the supplied curve
    Y values are normalised to 1 before performing the fit.
    xdata, ydata - arrays defining x and y values for the curve.
    fitPeakRange - x axis range to use when finding peak (centred on peak Y value).
    Returns Gaussian object containing fit parameters (FWHM, centre position, area etc)
    """
    
    if len(xdata) != len(ydata) :
        print "Could not run findCentre in %s : x and y dataset lengths do not match (x = %d , y = %d elements)"%(self.getName(), len(xdata), len(ydata))
        return []

    # Find index and value of peak y value
    xdataset = DatasetFactory.createFromObject(xdata)
    ydataset = DatasetFactory.createFromObject(ydata)

    # Find the peak y value and its index :
    maxY = max(ydata)
    maxYIndex = ydataset.maxPos()[0]
    
    peakX = xdata[maxYIndex]
    print "Peak at x = %.4e (y value = %.4e at y index %d)"%(peakX, maxY, maxYIndex)
    
    # Normalise the y dataset to help with the fitting
    range = max(ydata)-min(ydata)
    ydataset.isubtract(min(ydata))
    ydataset.imultiply(1.0/range)

    # Define the Gaussian Fit function and range of values for the parameters
    # peak range, max fwhm and max area"
    
    rangeStart = peakX-0.5*fitPeakRange
    rangeEnd = peakX+0.5*fitPeakRange
    print "X axis range for fit : %.4f ... %.4f (range = %.4e)"%(rangeStart, rangeEnd, fitPeakRange)
    fitFunc = Gaussian(rangeStart, rangeEnd, fitMaxFwhm, fitMaxArea)

    i = 0
    while i < len(xdata) :
        print xdataset.getDouble(i), ydataset.getDouble(i)
        i = i + 1
    
    # Fit the data
    Fitter.geneticFit([xdataset], ydataset, fitFunc);
    return fitFunc

# Test Gaussian 'fitGaussian' function on a noisy gaussian curve
def testFitGaussian(noise=0.0):
    gaussianCurve = generateGaussian(noise)
    results = fitGaussian(gaussianCurve[0], gaussianCurve[1])
    print results
    return results

# Generate Gaussian curve : range = 0...100, centre=50, width = 10, with optional random noise) 
# Return array of x and array of y values
def generateGaussian(noise=0.00) :
    mygauss = lambda x : 2.0*gaussian(x, centre=50.0, width=10.0, noiseLevel=noise) 
    xvals = range(100)
    yvals = map(mygauss, xvals)
    return [xvals, yvals]

# Generate y value on Gaussian curve : y(pos) = exp(-[(pos-centre)/width]**2 )
def gaussian(pos, centre=50, width=5, noiseLevel=0.1) :
    gval = math.exp( -(float(pos-centre)/width)**2.0 )
    return gval + random.random()*noiseLevel

overlapDet = OverlapDetector('overlapDet')
overlapDet.configure()
if LocalProperties.isDummyModeEnabled() :
    overlapDet.setEdeDetector(xstrip)
else :
    overlapDet.setEdeDetector(frelon)

# Functions for setting PVs on the Mar detector
def getMarPvString(value) :
    marBasePv = "BL20J-EA-MAR-01:"
    return marBasePv+value


def testFit(overlapDet, datafile) :
    ydata = overlapDet.getDataFromFile(datafile, "data")
    xdata = overlapDet.getDataFromFile(datafile, "turbo_slit_x")
    axisRange = max(xdata)-min(xdata)
    fitRangeFrac = overlapDet.fitPeakRangeFrac
    maxFwhm = axisRange
    maxArea = axisRange*10

    print "X axis range = %.4e, using %.2f of range about peak when fitting"%(axisRange, fitRangeFrac)
    return fitGaussian(xdata, ydata, axisRange*fitRangeFrac, maxFwhm, maxArea)


# Set same PV value on both the CAM and TIFF plugins (for setting file name, path etc)
def setMarPv(pvName, value, loopOverPlugins=True) :
    caclient = CAClient()
    pluginNames = ["CAM:", "TIFF:"]
    if loopOverPlugins == False :
        pluginNames = [""]
    for pluginPv in pluginNames :
        fullPv = getMarPvString(pluginPv+pvName)
        if LocalProperties.isDummyModeEnabled() :
            return

        if (type(value) == str) :
            print "Setting Mar string PV : %s = %s"%(fullPv, str(value))
            caclient.caputStringAsWaveform(fullPv, str(value)+"\0")
        else :
            print "Setting Mar PV : %s = %s"%(fullPv, str(value))
            caput(fullPv, str(value)) # caput(fullPv, value)

def setMarFilePath(filepath) :
    setMarPv("FilePath", filepath)

def setMarFilePathToVisit(subDir=""):
    p=InterfaceProvider.getPathConstructor()
    fullPath = p.getVisitDirectory()+"/"+subDir
    if fullPath.endswith('/') == False :
        fullPath = fullPath+'/'
    setMarFilePath(str(fullPath))

def setMarFileName(filename) :
    setMarPv("FileName", filename)

def setMarFileNumber(filenumber) :
    setMarPv("FileNumber", filenumber)

def setMarFileTemplate(filetemplate):
    setMarPv("FileTemplate", filetemplate)

def closeMarCover() :
    print("Closing Mar cover...")
    caput(getMarPvString("CLOSE_COVER.PROC"), 1)
    sleep(1)
    cagetWaitForValue(getMarPvString("COVER:CLOSED"), 1)
    print("Mar cover closed")

def openMarCover() :
    print("Opening Mar cover...")
    caput(getMarPvString("OPEN_COVER.PROC"), 1)
    sleep(1)
    cagetWaitForValue(getMarPvString("COVER:OPENED"), 1)
    print("Mar cover open")

def readoutMar() :
    caput(getMarPvString("CAM:Acquire"), 1)

def eraseMar() :
    caput(getMarPvString("CAM:Erase"), 1)


from gda.epics import LazyPVFactory
from java.util.function import Predicate

class lambdaFunction(Predicate):
    def __init__(self, func):
        self.func = func
        
    def test(self, t) :
        return self.func(t)

def cagetWaitForValue(pvName, value) :
    pvPosition = LazyPVFactory.newReadOnlyDoublePV(pvName);
    pvPosition.waitForValue(lambdaFunction(lambda x : x == value), 60.0)   	

# Set some reasonable defaults on the TIFF and CAM plugins
setMarFilePathToVisit("nexus")
setMarPv("CAM:FileTemplate", "%s%s_%03d", False)
setMarPv("TIFF:FileTemplate", "%s%s_%03d.tiff", False)
setMarPv("AutoIncrement", 1)
setMarPv("NumCapture", 1)
setMarPv("AutoSave", 1)

if LocalProperties.isDummyModeEnabled() == False :
    caput(getMarPvString("CAM:ImageMode"), 0)
    caput(getMarPvString("CAM:NumExposures"), 1)
    caput(getMarPvString("CAM:NumImages"), 1)

