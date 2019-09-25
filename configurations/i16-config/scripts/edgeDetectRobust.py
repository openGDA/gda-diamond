#Gareth 11/06/2010
#dir(gda.analysis.functions)
import scisoftpy as dnp
from gda.analysis.io import *
#from uk.ac.gda.diamond.analysis.io import *
from math import exp
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from math import exp
from gda.analysis import ScanFileHolder

numTracker = NumTracker("scanbase_numtracker")
def edgeDetectRobust(relativefilenumber,axis1,axis2):
	if relativefilenumber > 0:
		file = InterfaceProvider.getPathConstructor().createFromDefaultProperty()	
		file = file + "/" + `relativefilenumber`+".dat"
		filenumber=relativefilenumber
	else:
		file = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
		file = file + "/" + `int(numTracker.getCurrentFileNumber()+relativefilenumber)`+".dat"
		filenumber=int(numTracker.getCurrentFileNumber()+relativefilenumber)
	data = ScanFileHolder()
	data.loadSRS(file)
	xdata=data.getAxis(axis1)
	ydata=data.getAxis(axis2)
	ydiffdata = dnp.gradient(ydata)
	maxyindex=ydiffdata.argmax()
	minyindex=ydiffdata.argmin()
	maxpos=xdata.getData()[maxyindex]
	minpos=xdata.getData()[minyindex]
	dnp.plot.plot(dnp.array(xdata),dnp.array(ydata),name='Plot 1')
	dnp.plot.addline(dnp.array(xdata),dnp.array(ydiffdata._jdataset()),name='Plot 1')
	peakproximitytolerance=0.01
	intercepts=data.getInterpolatedX(xdata,ydata,(ydata.max()+ydata.min())/2.,peakproximitytolerance)
	if minpos > maxpos:
		midpoint1=maxpos+(minpos-maxpos)/2.
		firstintercept1=maxpos
		secondintercept1=minpos
	else:
		midpoint1=minpos+(maxpos-minpos)/2.
		firstintercept1=minpos
		secondintercept1=maxpos
	if len(intercepts) > 1:
		if intercepts[0] > intercepts[1]:
			midpoint2=intercepts[1]+(intercepts[0]-intercepts[1])/2.
			firstintercept2=intercepts[1]
			secondintercept2=intercepts[0]
		else:
			midpoint2=intercepts[0]+(intercepts[1]-intercepts[0])/2.
			firstintercept2=intercepts[0]
			secondintercept2=intercepts[1]
	else:
		firstintercept2=intercepts[0]
		secondintercept2=intercepts[0]
		midpoint2=intercepts[0]
		
	return [firstintercept1, firstintercept2, secondintercept1, secondintercept2, midpoint1, midpoint2, filenumber]

edgeDetectRobust.__doc__='0 is last file, -1 previous or +ve absolute file no.\nreturns list [left1,left2,right1,right2,centre1,centre2,filenum)\n1=halfway; 2=max/min derivative'
