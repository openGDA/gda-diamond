import scisoftpy as dnp
import uk.ac.diamond.scisoft.analysis.dataset.IntegerDataset as IntegerDataset
import gdascripts.analysis.datasetprocessor.oned.extractPeakParameters as epp

import uk.ac.diamond.scisoft.analysis.fitting.Generic1DFitter as fitter1
import uk.ac.diamond.scisoft.analysis.fitting.functions.Gaussian as Gaussian
import uk.ac.diamond.scisoft.analysis.optimize.GeneticAlg as GeneticAlg

d=dnp.io.load("/dls/i12/data/2012/cm5706-3/default/12867.nxs")
data1=d.entry1.EDXD_Element_01.data
dnp.plot.plot(data1[0], name="Plot 2")

print '_________________'
print 'Method 1'
id1=IntegerDataset(data1[0])
slice1=id1.getSlice([650], [750], [1])
dnp.plot.plot(slice1, name="Plot 1")
singlePeakProc = e.singlePeakProcess(IntegerDataset.arange(slice1.shape[0]), slice1)

print 'Single Peak Process returns '+`singlePeakProc`

print '_________________'
print 'Method 2'
fittedG=fitter1.fitPeakFunctions(IntegerDataset.arange(slice1.shape[0]), slice1, Gaussian(1,1,1,1), GeneticAlg(0.0001), 5, 1)
print 'Using fitting Algorithm '+`fittedG`
print '_________________'

print '_________________'
print 'Method 1'
id1=IntegerDataset(data1[0])
slice1=id1.getSlice([900], [1300], [1])
dnp.plot.plot(slice1, name="Plot 3")
singlePeakProc = e.singlePeakProcess(IntegerDataset.arange(slice1.shape[0]), slice1)

print 'Single Peak Process returns '+`singlePeakProc`

print '_________________'
print 'Method 2'
fittedG=fitter1.fitPeakFunctions(IntegerDataset.arange(slice1.shape[0]), slice1, Gaussian(1,1,1,1), GeneticAlg(0.0001), 5, 1)
print 'Using fitting Algorithm '+`fittedG`
print '_________________'