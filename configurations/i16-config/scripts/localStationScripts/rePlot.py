#Gareth 11/06/2010
from gda.analysis.io import *
from gda.data import NumTracker
from gda.jython import InterfaceProvider

numTracker = NumTracker("scanbase_numtracker")
def replot(relativefilenumber,axis1,axis2):
	if relativefilenumber > 0:
		srs_file = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
		srs_file = srs_file + "/spool/" + `relativefilenumber`+".dat"
		filenumber=relativefilenumber
	else:
		srs_file = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
		srs_file = srs_file + "/spool/" + `int(numTracker.getCurrentFileNumber()+relativefilenumber)`+".dat"
		filenumber=int(numTracker.getCurrentFileNumber()+relativefilenumber)
	data = ScanFileHolder()
	data.loadSRS(srs_file)
	xdata=data.getAxis(axis1)
	ydata=data.getAxis(axis2)
	ymax=ydata.max()
	ymin=ydata.min()
	maxyindex=ydata.maxPos()[0]
	minyindex=ydata.minPos()[0]
	maxpos=xdata[maxyindex]
	minpos=xdata[minyindex]
	Plotter.plot('Data Vector',xdata,ydata)
	return [maxpos, ymax, minpos, ymin, filenumber]
