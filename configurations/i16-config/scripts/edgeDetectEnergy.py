#Gareth 2016
import scisoftpy as dnp
from gda.analysis.io import *
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.analysis import ScanFileHolder
from org.eclipse.january.dataset import DatasetUtils
from uk.ac.diamond.scisoft.analysis.fitting.functions import CubicSpline
import traceback

numTracker = NumTracker("scanbase_numtracker")
def get_file(relativefilenumber=0):
    if relativefilenumber > 0:
        file = InterfaceProvider.getPathConstructor().createFromDefaultProperty()    
        file = file + "/" + `relativefilenumber`+".dat"
    else:
        file = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
        file = file + "/" + `int(numTracker.getCurrentFileNumber()+relativefilenumber)`+".dat"
    return file

def eEdge(relativefilenumber=0,axis1='energy2',axis2='ic1'):
    if relativefilenumber > 0:
        file = InterfaceProvider.getPathConstructor().createFromDefaultProperty()    
        file = file + "/" + `relativefilenumber`+".dat"
        filenumber=relativefilenumber
    else:
        file = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
        file = file + "/" + `int(numTracker.getCurrentFileNumber()+relativefilenumber)`+".dat"
        filenumber=int(numTracker.getCurrentFileNumber()+relativefilenumber)
    print(file)
    data=dnp.io.load(file)
    xdata = data[axis1]._jdataset().getData()
    ydata = (dnp.log(data[axis2] + 1))._jdataset().getData()
    c_spline = CubicSpline(xdata, ydata, 0)
    xdatainterp = dnp.linspace(min(xdata), max(xdata), 10*len(xdata))
    ydatainterp = c_spline.calculateValues(xdatainterp._jdataset())
    miny = dnp.array(ydatainterp).min()
    maxy = dnp.array(ydatainterp).max()
    dnp.plot.plot(dnp.array(xdata),dnp.array(ydata),name='Plot 1')
    dnp.plot.addline(dnp.array(xdatainterp),dnp.array(ydatainterp),name='Plot 1')
    return DatasetUtils.crossings(xdatainterp._jdataset(), ydatainterp, (miny+maxy)/2.)[0]

eEdge.__doc__='0 is last file, -1 previous or +ve absolute file no.\nReturns edge of ln(ydata)'
