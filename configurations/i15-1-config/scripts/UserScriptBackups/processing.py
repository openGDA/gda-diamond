
from gdascripts.analysis.datasetprocessor.oned.XYDataSetProcessor import XYDataSetFunction
import scisoftpy as dnp
from org.eclipse.dawnsci.analysis.dataset.impl import Maths

class _GaussianPeak(XYDataSetFunction):
    def __init__(self, name, labelList, formatString, plotPanel, offset, keyxlabel):
        XYDataSetFunction.__init__(self, name, labelList, keyxlabel, formatString)
        self.plotPanel = plotPanel
        self.offset = offset
    
    def _process(self, xDataset, yDataset):
        if yDataset.max()-yDataset.min() == 0:
            raise ValueError("There is no peak")
        
        x, y = toDnpArrays(xDataset, yDataset)
        fitResult = self.getFitResult(x,y)
        if self.plotPanel != None:
            plotGaussian(x, fitResult, self.plotPanel)
        results = self.getResults(fitResult)
        return [results.get(label, float('NaN')) for label in self.labelList]
    
    def getFitResult(self, x, y):
        funcs = getFitFunctions(self.offset)
        initial = gaussianInitialParameters(x, y, offset=self.offset)
        fitResult_p = dnp.fit.fit(funcs, x, y, initial, bounds=gaussianBounds(x, y, offset=self.offset), optimizer='global')
        fitResult_n = dnp.fit.fit(funcs, x, y, initial, bounds=gaussianBounds(x, y, negative_peak=True, offset=self.offset), optimizer='global')
        return fitResult_p if fitResult_p.residual < fitResult_n.residual else fitResult_n


class GaussianPeakAndBackgroundDK(_GaussianPeak):
    def __init__(self, name='peak', labelList=('pos','offset','top', 'fwhm', 'residual'),formatString='Gaussian at %f (pos) with offset: %f, top: %f, fwhm: %f and residual: %f', plotPanel='Gaus. Peak', keyxlabel='pos'):
        _GaussianPeak.__init__(self, name, labelList, formatString, plotPanel, offset=True, keyxlabel=keyxlabel)
    
    def getResults(self, fitResult):
        peak, fwhm, area, offset = fitResult.parameters[:4]
        residual = fitResult.residual
        top = area / fwhm
        return {'pos': peak, 'offset': offset, 'top': top, 'fwhm': fwhm,'residual': residual}


class GaussianPeak(_GaussianPeak):
    def __init__(self, name='peak', labelList=('pos','top', 'fwhm','residual'), formatString='Gaussian at %f (pos) with top: %f, fwhm: %f and residual: %f', plotPanel=None, keyxlabel='pos'):
        _GaussianPeak.__init__(self, name, labelList, formatString, plotPanel, offset=False, keyxlabel=keyxlabel)
    
    def getResults(self, fitResult):
        peak, fwhm, area = fitResult.parameters[:3]
        residual = fitResult.residual
        top = area / fwhm
        return {'pos': peak, 'top': top, 'fwhm': fwhm, 'residual': residual}


def gaussianInitialParameters(x, y, offset=False):
    initialParameters = [x.mean(), x.ptp()*.5, x.ptp()*y.ptp()]
    if offset:
        initialParameters += [y.mean()]
    return initialParameters

def getFitFunctions(offset):
    funcs = [dnp.fit.function.gaussian]
    if offset:
        funcs += [dnp.fit.function.offset]
    return funcs

def getLinearFitFunction(offset):
    return [dnp.fit.function.linear]

def gaussianBounds(x, y, negative_peak=False, offset=False):
    bounds = [(x.min(), x.max()), (0, x.ptp())]
    bounds += [(x.ptp()*y.ptp()*-1, 0, x.ptp()*y.ptp())[negative_peak:negative_peak+2]]
    if offset:
        bounds += [(y.min(), y.max())]
    return bounds

def toDnpArrays(*args):
    return [dnp.array(arg) for arg in args]

def plotGaussian(x, fitResult, plotPanel):
    plotData = fitResult.makeplotdata()
    dnp.plot.line(x, toDnpArrays(plotData[0],plotData[1], plotData[2], plotData[3]),
                            name=plotPanel)

class GaussianDiscontinuity(XYDataSetFunction):
    def __init__(self, name='discontinuity', labelList=('pos','slope', 'fwhm', 'residual'),formatString='Discontinuity at %f (pos) with sharpness proportional to: %f, fwhm: %f and residual: %f', plotPanel='Gaus. Disc.', keyxlabel='pos'):
        XYDataSetFunction.__init__(self, name, labelList, keyxlabel, formatString)
        self.smoothwidth = 1
        self.plotPanel = plotPanel
    
    def _process(self,xDataSet, yDataSet):
        dyDataSet = Maths.derivative(xDataSet, yDataSet, self.smoothwidth)
        d2yDataSet = Maths.derivative(xDataSet, dyDataSet, self.smoothwidth)
        minVal, maxVal = d2yDataSet.min(), d2yDataSet.max()
        if maxVal - minVal == 0:
            raise ValueError("There is no edge")
        
        labels = [label if label != 'slope' else 'top' for label in self.labelList]
        return GaussianPeak(self.name, labels, self.formatString, self.plotPanel)._process(xDataSet, d2yDataSet)


# class LinearIntersectionDiscontinuityP(XYDataSetFunction):
#     """ Linear intersection discontinuity fitting with plotting.
#     
#     Fits a straight line to the first m points and to the last n points, and finds the point at which these intersect. 
#     Good for scans over small ranges close to discontinuities. (i.e. with no strong features in the scan data
#     away from the discontinuity.)
#     The trailing P in the class name denotes that this version plots the output
#     to a GUI plot panel.
#     """
#     def __init__(self, name='discontinuity', labelList=('pos'),formatString='Discontinuity at %f (pos)', plotPanel='Lin. Int. Disc.', keyxlabel='pos'):
#         XYDataSetFunction.__init__(self, name, labelList, keyxlabel, formatString)
#         self.smoothwidth = 1
#         self.plotPanel = plotPanel
#     
#     def _process(self,xDataSet, yDataSet):
#         dyDataSet = Maths.derivative(xDataSet, yDataSet, self.smoothwidth)
#         d2yDataSet = Maths.derivative(xDataSet, dyDataSet, self.smoothwidth)
#         minVal, maxVal = d2yDataSet.min(), d2yDataSet.max()
#         idx = d2yDataSet.argmax()
#         n = d2yDataSet.size
#         if maxVal - minVal == 0:
#             raise ValueError("There is no edge?")
#         if idx < 4 or idx > n-4:
#             raise ValueError("Edge detected too close to scan limits")
#         
#         return TwoStraightLines(self.name, labels, self.formatString, self.plotPanel)._process(xDataSet, d2yDataSet)
#     
# class _TwoStraightLines(XYDataSetFunction):
#     def __init__(self, name, labelList, formatString, plotPanel, idx, keyxlabel):
#         XYDataSetFunction.__init__(self, name, labelList, keyxlabel, formatString)
#         self.plotPanel = plotPanel
#         self.idx = idx
#     
#     def _process(self, xDataset, yDataset):
#         if yDataset.max()-yDataset.min() == 0:
#             raise ValueError("There is no peak")
#         
#         x, y = toDnpArrays(xDataset, yDataset)
#         fitResult = self.getFitResult(x,y)
#         if self.plotPanel != None:
#             plotGaussian(x, fitResult, self.plotPanel)
#         results = self.getResults(fitResult)
#         return [results.get(label, float('NaN')) for label in self.labelList]
#     
#     def getFitResult(self, x, y):
#         funcs = getLinearFitFunction()
#         initial = gaussianInitialParameters(x, y, offset=self.offset)
#         fitResult_p = dnp.fit.fit(funcs, x, y, initial, bounds=gaussianBounds(x, y, offset=self.offset), optimizer='global')
#         fitResult_n = dnp.fit.fit(funcs, x, y, initial, bounds=gaussianBounds(x, y, negative_peak=True, offset=self.offset), optimizer='global')
#         return fitResult_p if fitResult_p.residual < fitResult_n.residual else fitResult_n
# 
# 
# class TwoStraightLines(_GaussianPeak):
#     def __init__(self, name='peak', labelList=('pos','top', 'fwhm','residual'), formatString='Gaussian at %f (pos) with top: %f, fwhm: %f and residual: %f', plotPanel=None, keyxlabel='pos'):
#         _TwoStraightLines.__init__(self, name, labelList, formatString, plotPanel, offset=False, keyxlabel=keyxlabel)
#     
#     def getResults(self, fitResult):
#         peak, fwhm, area = fitResult.parameters[:3]
#         residual = fitResult.residual
#         top = area / fwhm
#         return {'pos': peak, 'top': top, 'fwhm': fwhm, 'residual': residual}





print "got to the end"