#Gareth 11/06/2010
#dir(gda.analysis.functions)
from gda.analysis.io import *
from gda.analysis.functions import *
import math
from gda.data import NumTracker
from gda.data import PathConstructor
import random

numTracker = NumTracker("tmp")
def replot(relativefilenumber,axis1,axis2):
	if relativefilenumber > 0:
		file = PathConstructor.createFromDefaultProperty()	
		file = file + "/" + `relativefilenumber`+".dat"
		filenumber=relativefilenumber
	else:
		file = PathConstructor.createFromDefaultProperty()
		file = file + "/" + `int(numTracker.getCurrentFileNumber()+relativefilenumber)`+".dat"
		filenumber=int(numTracker.getCurrentFileNumber()+relativefilenumber)
	data = ScanFileHolder()
	data.loadSRS(file)
	xdata=data.getAxis(axis1)
	ydata=data.getAxis(axis2)
	ydiffdata=ydata.diff(3)
	ymax=ydata.max()
	ymin=ydata.min()
	maxyindex=ydata.maxPos()[0]
	minyindex=ydata.minPos()[0]
	maxpos=xdata[maxyindex]
	minpos=xdata[minyindex]
	Plotter.plot('Data Vector',xdata,ydata)
	#Gaussian(double minPeakPosition, double maxPeakPosition, double maxFWHM, double maxArea)
	#output1=Fitter.plot(xdata,ydata.diff(3),GradientDescent(0.00001),[Gaussian(maxpos-3,maxpos+3,3,3) Gaussian(minpos-3,minpos+3,2,3)])
	return [maxpos ymax minpos ymin filenumber]
