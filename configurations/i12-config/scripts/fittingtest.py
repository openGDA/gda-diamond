from uk.ac.diamond.scisoft.analysis.fitting.functions import Offset, CompositeFunction
from uk.ac.diamond.scisoft.analysis.optimize import NelderMead
from uk.ac.diamond.scisoft.analysis.fitting import Fitter 

from org.eclipse.january.dataset import DatasetFactory

from gda.analysis import RCPPlotter

def parser(dataset):
    length = dataset.getDimensions()[0]
    #print length
    
    ds = DatasetFactory.zeros([length])
    peaks = []
    
    for i in range(length) :
        
        # get the backward points
        backpos = i
        backtotal = 0
        backsize = 0
        while backpos > 0:
            if dataset[backpos] > 0 :
                backsize += 1
                backtotal += dataset[backpos]
                backpos -= 1
            else :
                break
        
        # get the forward points    
        forwardpos = i + 1
        forwardtotal = 0
        forwardsize = 0
        while forwardpos < length - 1:
            if dataset[forwardpos] < 0 :
                forwardsize += 1
                forwardtotal -= dataset[forwardpos]
                forwardpos += 1
            else :
                break
            
        if min((backtotal, forwardtotal)) > 0:
            # we have a peak, so add it to our list
            peaks += [(min((backtotal, forwardtotal)), backsize, forwardsize, i)]
            
        ds[i] = min((backtotal, forwardtotal))
           
    peaks.sort(reverse=True)
            
    return peaks

def plotPeak(peaks, peaknumber, values, data):
    print peaks[peaknumber]
    start = peaks[peaknumber][3] - peaks[peaknumber][1]
    end = peaks[peaknumber][3] + peaks[peaknumber][2]
    x = values[start:end]
    y = data[start:end]
    RCPPlotter.plot("Plot 2", x, y)
    return

def fitPeak(peaks, peaknumber, values, data, function):
    start = peaks[peaknumber][3] - peaks[peaknumber][1]
    end = peaks[peaknumber][3] + peaks[peaknumber][2]
    x = values[start:end]
    y = data[start:end]
    peakPos = values[peaks[peaknumber][3]]
    peakWidth = x.range() / 2.0
    peakArea = (x.range()*y.range()) / 2.0
    func = function([peakPos, peakWidth, peakArea])
    background = Offset([y.min()])
    result = Fitter.fit(x, y, NelderMead(0.0001), [func, background])
    return func 

def plotFittedPeak(peaks, peaknumber, values, data, function):
    func = fitPeak(peaks, peaknumber, values, data, function)
    start = peaks[peaknumber][3] - peaks[peaknumber][1]
    end = peaks[peaknumber][3] + peaks[peaknumber][2]
    x = values[start:end]
    y = data[start:end]
    RCPPlotter.plot("Plot 2", x, [y, func.makeDataSet([x])])
    return func

def fitNPeaks(values, data, function, numberOfPeaks, smoothing):
    #first build up the peaks list from the differential of the peaks
    peaks = parser(data.diff(smoothing))
    fits = CompositeFunction()
    for i in range(numberOfPeaks):
        fits.addFunction(fitPeak(peaks, i, values, data, function))
        
    return fits

def plotNPeaks(values, data, function, numberOfPeaks, smoothing):
    func = fitNPeaks(values, data, function, numberOfPeaks, smoothing)
    RCPPlotter.plot("Plot 2", values, [data, func.makeDataSet([values])])
    
    return func
    

def refitNPeaks(values, data, function, numberOfPeaks, smoothing):
    func = fitNPeaks(values, data, function, numberOfPeaks, smoothing)
    result = Fitter.fit(values, data, NelderMead(0.0001), [func])
    RCPPlotter.plot("Plot 2", values, [data, func.makeDataSet([values])])
    

