import scisoftpy as dnp
import uk.ac.diamond.scisoft.analysis.dataset.IntegerDataset as IntegerDataset

import uk.ac.diamond.scisoft.analysis.fitting.Generic1DFitter as fitter1
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian as Gaussian
import uk.ac.diamond.scisoft.analysis.optimize.GeneticAlg as GeneticAlg
import uk.ac.diamond.scisoft.analysis.dataset.DoubleDataset as DoubleDataset

def findPeakPosition(approxVal, integerDataSet, leftShift=6, rightShift=6):
    actualVal = approxVal
    start = approxVal - leftShift
    end = approxVal + rightShift
    slice1 = integerDataSet.getSlice([start], [end], [1])
    fittedG = fitter1.fitPeakFunctions(IntegerDataset.arange(slice1.shape[0]), slice1, Gaussian(1, 1, 1, 1), GeneticAlg(0.0001), 5, 1)
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
        integerDataSet = IntegerDataset(i[1].data[0])
        hec = findPeakPosition(ahec, integerDataSet)
        lec = findPeakPosition(alec, integerDataSet)
        a.append(findA(hev, lev, hec, lec))
        b.append(findB(hev, a[index], hec))
        index += 1
print a
print b





import gdascripts.analysis.datasetprocessor.oned.extractPeakParameters as epp


d = dnp.io.load("/dls/i12/data/2012/cm5706-3/default/12867.nxs")
data1 = d.entry1.EDXD_Element_01.data
dnp.plot.plot(data1[0], name="Plot 2")
e = epp.ExtractPeakParameters()
print '_________________'
print 'Method 1'
id1 = IntegerDataset(data1[0])
slice1 = id1.getSlice([650], [750], [1])
dnp.plot.plot(slice1, name="Plot 1")
singlePeakProc = e.singlePeakProcess(IntegerDataset.arange(slice1.shape[0]), slice1)

print 'Single Peak Process returns ' + `singlePeakProc`

print '_________________'
print 'Method 2'
fittedG = fitter1.fitPeakFunctions(IntegerDataset.arange(slice1.shape[0]), slice1, Gaussian(1, 1, 1, 1), GeneticAlg(0.0001), 5, 1)
print 'Using fitting Algorithm ' + `fittedG`
print '_________________'

print '_________________'
print 'Method 1'
id1 = IntegerDataset(data1[0])
slice1 = id1.getSlice([900], [1300], [1])
dnp.plot.plot(slice1, name="Plot 3")
singlePeakProc = e.singlePeakProcess(IntegerDataset.arange(slice1.shape[0]), slice1)

print 'Single Peak Process returns ' + `singlePeakProc`

print '_________________'
print 'Method 2'
fittedG = fitter1.fitPeakFunctions(IntegerDataset.arange(slice1.shape[0]), slice1, Gaussian(1, 1, 1, 1), GeneticAlg(0.0001), 5, 1)
print 'Using fitting Algorithm ' + `fittedG`
print '_________________'

