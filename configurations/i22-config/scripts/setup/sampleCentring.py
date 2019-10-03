from gda.data import NumTracker
from gda.jython import InterfaceProvider
import scisoftpy as dnp
from uk.ac.gda.server.ncd.optimiser import LadderSampleFinder as LSF

def _getAxes(file, dir=None):
    if dir is None:
        dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    
    data = dnp.io.load(dir + file)
    
    default = data.entry1.default
    
    for key in default.keys():
        if hasattr(default[key], 'attrs'):
            attributesOfFile = default[key].attrs
            if 'primary' in attributesOfFile:
                xAxis = default[key]
            else:
                yAxis = default[key]
    xAxis = xAxis._getdata().getSlice(None).data
    yAxis = yAxis._getdata().getSlice(None).data
    return xAxis, yAxis

def findPeaks(file, dir=None):
    xAxis, yAxis = _getAxes(file, dir)
    
    lsf = LSF()
    l = lsf.process(xAxis, yAxis)
    print l

