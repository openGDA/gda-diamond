import scisoftpy as dnp

import uk.ac.diamond.scisoft.analysis.fitting.Generic1DFitter as fitter1
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian as Gaussian
import uk.ac.diamond.scisoft.analysis.optimize.GeneticAlg as GeneticAlg
from uk.ac.diamond.scisoft.analysis.fitting import CalibrationUtils
import gdascripts.analysis.datasetprocessor.oned.extractPeakParameters as epp
from org.eclipse.january.dataset import DatasetFactory

def findPeakPosition(approxVal, integerDataSet, leftShift=6, rightShift=6):
    actualVal = approxVal
    start = approxVal - leftShift
    end = approxVal + rightShift
    slice1 = integerDataSet.getSlice([start], [end], [1])
    fittedG = fitter1.fitPeakFunctions(DatasetFactory.createRange(slice1.shape[0]), slice1, Gaussian(1, 1, 1, 1), GeneticAlg(0.0000001), 5, 1)
    if fittedG != None and not fittedG.isEmpty():
        c = fittedG.get(0)
        if c != None:
            peak = c.getPeak(0)
            peakPosition = peak.getPosition()
            actualVal = start + peakPosition
    else:
        print "no peaks found"
    return actualVal

def findA(hev, lev, hec, lec):
    return (hev - lev) / (hec - lec)

def findB(hev, a, hec):
    return hev - a * hec

def testMisAlignmentForElementsPlot():
    d = dnp.io.load("/dls/i12/data/2012/cm5706-3/default/12867.nxs")
    data1 = d.entry1
    index = 0
    peakEnergies = []
    for i in data1.iteritems():
        if i[0][0:-2] == 'EDXD_Element_' and index < 23 and index != 20:
            integerDataSet = DatasetFactory.createFromObject(i[1].data[0])
            print "index:" + `index`
            peakEnergies.append(findPeakPosition(1000, integerDataSet, leftShift=50, rightShift=50))
            index += 1
    dataset = dnp.asarray(peakEnergies)
    dataset.setName("peakEnergies")
    dnp.plot.plot(dataset)


def testPeakFitFunction():
    d = dnp.io.load("/dls/i12/data/2012/cm5706-3/default/12867.nxs")
    data1 = d.entry1.EDXD_Element_01.data
    dnp.plot.plot(data1[0], name="Plot 2")
    e = epp.ExtractPeakParameters()
    print '_________________'
    print 'Method 1'
    id1 = DatasetFactory.createFromObject(data1[0])
    slice1 = id1.getSlice([950], [1050], [1])
    dnp.plot.plot(slice1, name="Plot 1")
    '''
    singlePeakProc = e.singlePeakProcess(DatasetFactory.createRange(slice1.shape[0]), slice1)
    
    print 'Single Peak Process returns ' + `singlePeakProc`
    '''
    print '_________________'
    print 'Method 2'
    fittedG = fitter1.fitPeakFunctions(DatasetFactory.createRange(slice1.shape[0]), slice1, Gaussian(1, 1, 1, 1), GeneticAlg(0.0001), 5, 1)
    print 'Using fitting Algorithm ' + `fittedG`
    print '_________________'
    
    '''
    print '_________________'
    print 'Method 1'
    id1 = IntegerDataset(data1[0])
    slice1 = id1.getSlice([900], [1300], [1])
    dnp.plot.plot(slice1, name="Plot 3")
    singlePeakProc = e.singlePeakProcess(DatasetFactory.createRange(slice1.shape[0]), slice1)
    
    print 'Single Peak Process returns ' + `singlePeakProc`
    '''
    print '_________________'
    print 'Method 2'
    fittedG = fitter1.fitPeakFunctions(DatasetFactory.createRange(slice1.shape[0]), slice1, Gaussian(1, 1, 1, 1), GeneticAlg(0.0001), 5, 1)
    print 'Using fitting Algorithm ' + `fittedG`
    print '_________________'


def testMapAxis():
    d = dnp.io.load("/dls/i12/data/2012/cm5706-3/default/12867.nxs")
    data1 = d.entry1.EDXD_Element_01
    energyAxis = data1.edxd_energy_approx[:]
    originalAxisApproximatePeakPositions = DatasetFactory.createFromObject([34.720, 39.258], [2])
    newAxisExactPeakPositions = DatasetFactory.createFromObject(([34.720, 39.258], [2])
    apeakFunction = Gaussian(1, 1, 1, 1)
    polynomial = 1
    output = CalibrationUtils.mapAxis(data1.data[0], energyAxis, originalAxisApproximatePeakPositions, newAxisExactPeakPositions, apeakFunction, polynomial)
    for i in range(0, 10):
        print output.data[i]
    dnp.plot.plot(output)
    
def testMethod1ForEnergyCalibration():
    alec = 711
    ahec = 804
    hev = 39.258
    lev = 34.720
    a = []
    b = []
    d = dnp.io.load("/dls/i12/data/2012/cm5706-3/default/12867.nxs")
    data1 = d.entry1
    index = 0
    for i in data1.iteritems():
        if i[0][0:-2] == 'EDXD_Element_' and index < 23:
            integerDataSet = DatasetFactory.createFromObject((i[1].data[0])
            hec = findPeakPosition(ahec, integerDataSet)
            lec = findPeakPosition(alec, integerDataSet)
            a.append(findA(hev, lev, hec, lec))
            b.append(findB(hev, a[index], hec))
            index += 1
    print "A is : "
    print a[0]
    print "B is : "
    print b[0]
    print "e is ---------------------------"
    e = []
    for i in range(0, 10):
        e.append(a[0] * i + b[0])
    print e
    dnp.plot.plot(dnp.asarray(e), name="Plot 2")
    
def testCollimatorXyzAlignment():
    pass

def runCollimatorAngularAlignment():
    pass

def runQAxisCalibration():
    pass

def loadEnergyCalibrationFile(fileName):
    print "Energy calibration file will be loaded: " + `fileName`
    
def loadQCalibrationFile(fileName):
    print "Q calibration file will be loaded: " + `fileName`