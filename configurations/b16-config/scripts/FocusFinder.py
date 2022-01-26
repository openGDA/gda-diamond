from gda.jython.commands.InputCommands import requestInput
from  org.eclipse.january.dataset import Dataset
from gda.analysis import ScanFileHolder
from gda.analysis import RCPPlotter
from uk.ac.diamond.scisoft.analysis.fitting import Fitter
from uk.ac.diamond.scisoft.analysis.optimize import GeneticAlg
from uk.ac.diamond.scisoft.analysis.fitting.functions import Gaussian
import gda.data.NumTracker
from gda.jython.commands.ScannableCommands import pos, scan

import math
import time


#88	reset_namespace
#89	import FocusFinder
#90	ff = FocusFinder.FocusFinder(keyMonitor=z, extraMonitorList=[])
#91	ff.dummymode=True
#92	ff.focusscan(x, -5, 5, 1, y, 2, 3, .5)
#93	xx=[3,6,9,12]
#94	yy=[4,5,0,4]
#95	yy.min()
#96	min(yy)
#97	ff = FocusFinder.FocusFinder(keyMonitor=z, extraMonitorList=[])
#98	ff.dummymode=True
#99	ff.focusscan(x, -5, 5, 1, y, 2, 3, .5)
#100	import FocusFinder
#101	ff = FocusFinder.FocusFinder(keyMonitor=z, extraMonitorList=[])
#102	ff.dummymode=True
#103	ff.focusscan(x, -5, 5, 1, y, 2, 3, .5)
#104	ff.moveToBestFocus()






class FocusFinder(object):
	
	def __init__(self, detector, extraMonitorList, countTime, widthFraction=0.7):
		self.monitor = detector 
		self.extraMonitorList = extraMonitorList
		self.dummymode = False
		self.numTracker = gda.data.NumTracker('tmp')
		self.countTime = countTime
		self.widthFraction = widthFraction
		self.smoothwidth = 1
	
	def focusscan(self,axisToScan, start, stop, step, wireScannable, wirestart, wirestop, wirestep):

		self.axisToScan = axisToScan
		self.wireScannable = wireScannable
		
		print "="*80
		print "Scanning %s from %f to %f in steps of %f," % (axisToScan.getName(), start, stop, step)
		print "at each step scanning %s from %f to %f in steps of %f and recording %s," % (wireScannable.getName(), wirestart, wirestop, wirestep, self.monitor.getName())
		print "where:"
		for extra in self.extraMonitorList:
			print "   %s: %f" % (extra.getName(), extra.getPosition())
		print "="*80	
		
		## Perform the scan of axisToScan ##
		self.xvalues = self.__frange(start, stop, step)
		
		self.centroidX = [None] * len(self.xvalues)
		self.stddevWidth = [None] * len(self.xvalues)
		self.kawalsWidth = [None] * len(self.xvalues)
		self.gaussfitWidth = [None] * len(self.xvalues)
		self.gaussfitX = [None] * len(self.xvalues)
		self.scanNumber = [None] * len(self.xvalues)
		
		for self.currentPoint, x in enumerate(self.xvalues):
			time.sleep(1)
			pos([axisToScan, x])
			time.sleep(1)
			print "Moved %s to %f, and scanning..." % (axisToScan.getName(), x)
			print "="*20
			
			(centroidx, stddevWidth, kawalsWidth, gaussfitX, gaussfitWidth ) = self.scanWire(wireScannable, wirestart, wirestop, wirestep)		
			i = self.currentPoint
			self.centroidX[i] = centroidx
			self.stddevWidth[i]  = stddevWidth
			self.kawalsWidth[i]  = kawalsWidth
			self.gaussfitX[i]    = gaussfitX
			self.gaussfitWidth[i]= gaussfitWidth
			self.scanNumber[i]   = self.numTracker.getCurrentFileNumber()
			
			self.plotAxisToScanVersusStepWidth()
			self.printTable()

		print "### Scans complete ###\n"
		
		## Look for minimum widths ##

		# stdev
		(self.minimumStddevWidthPosition, minwidth) = self.findMinimum(self.xvalues,self.stddevWidth )
		print "The best stddevWidth of %f was at %s: %f --> ff.minimumStddevWidthPosition " % (minwidth, self.axisToScan.getName(), self.minimumStddevWidthPosition)

		
		# kawals
		(self.minimumKawalsWidthPosition, minwidth) = self.findMinimum(self.xvalues,self.kawalsWidth )
		print "The best kawalsWidth of %f was at %s: %f --> ff.minimumKawalsWidthPosition" % (minwidth, self.axisToScan.getName(), self.minimumKawalsWidthPosition)

		# gaussfit
		(self.minimumGaussfitWidthPosition, minwidth) = self.findMinimum(self.xvalues,self.gaussfitWidth )
		print "The best gaussfitWidth of %f was at %s: %f --> ff.minimumGaussfitWidthPosition (used for moveToOptimalFocus)" % (minwidth, self.axisToScan.getName(), self.minimumGaussfitWidthPosition)
		

	
	def scanWire(self,wireScannable, wirestart, wirestop, wirestep):
		"""(centroidx, stddevx, kawalsWidth, gaussfitX, gaussfitFWHM ) = scanwire()"""
		
		scan([wireScannable, wirestart, wirestop, wirestep] + self.extraMonitorList + [self.monitor, self.countTime])
		data = ScanFileHolder()
		##
		if self.dummymode:
			print "!!!!!!!!!!!!!!! DUMMY FILE !!!!!!!!!!!!!!!!!!!"
			#data.loadSRS("/home/zrb13439/workspace/gda_7_8/config/base/users/data/10041.dat")
			data.loadSRS("/dls/b16/data/2009/nt498-1/10998.dat")
			xdataset = data.getDataSet('tbdiagY') # Scannable or field name? -- RobW
			ydataset = data.getDataSet('ch16')
#			xdataset = xdataset.getSubset([150,299])
#			ydataset = ydataset.getSubset([150,299])
		else:
			data.loadSRS()
			xdataset = data.getDataSet(self.getDataSetNameForScannable(wireScannable))
			ydataset = data.getDataSet(self.getDataSetNameForScannable(self.monitor))
		dydataset = ydataset.diff(xdataset, self.smoothwidth)
#		Plotter.plot('Data Vector', xdataset, [ydataset])
		centroidx = data.centroid(xdataset,dydataset)
		stddevx =  self.calcStddev(xdataset,dydataset) * 2.35
		kawalsWidth = self.kawalsFWHM(xdataset, dydataset, self.widthFraction)
		(gaussfitX, gaussfitWidth) = self.gaussfit(xdataset, dydataset)
		
		if self.dummymode:
			stddevx = stddevx * abs(self.axisToScan.getPosition())
			kawalsWidth = kawalsWidth* abs(self.axisToScan.getPosition())
			gaussfitWidth = gaussfitWidth * abs(self.axisToScan.getPosition())
		return (centroidx, stddevx, kawalsWidth, gaussfitX, gaussfitWidth )
	
	def gaussfit(self, xds, fds):
		"""(xdataset, ydataset, smoothing)"""
		width = xds.max() - xds.min()
		height = fds.max() - fds.min()
		
		result=Fitter.fit(xds, fds,GeneticAlg(0.0001),[Gaussian(xds.min(),xds.max(), width, width*height)])
		RCPPlotter.plot("Data Vector", xds ,[fds, result.getFunction(0).makeDataset([xds])]) 
		
		x = result[0].getValue()
		fwhm = result[1].getValue()
		return (x, fwhm)
		
	
	def printTable(self):
		colwidth=15
		header = ""
		header += "scan".ljust(6)
		header += self.axisToScan.getName().ljust(colwidth) + "| "
		
		header += self.wireScannable.getName().ljust(colwidth)
		header += "kawalsWidth".ljust(colwidth)
		header += "stddevWidth".ljust(colwidth) + "| "
		
		header += self.wireScannable.getName().ljust(colwidth)
		header += "gaussfitWidth"
		
		print header
		print "-"*(colwidth*7 + 4)
		
		for i in range(self.currentPoint+1):
			ln = ''

			ln += ( "%d"%self.scanNumber[i] ).ljust(6)
			ln += ( "%1.10f"%self.xvalues[i] ).ljust(colwidth) +"| "
			
			ln += ( "%1.10f"%self.centroidX[i] ).ljust(colwidth)
			ln += ( "%1.10f"%self.kawalsWidth[i]).ljust(colwidth)
			ln += ( "%1.10f"%self.stddevWidth[i] ).ljust(colwidth) +"| "
			
			ln += ( "%1.10f"%self.gaussfitX[i] ).ljust(colwidth)
			ln += ( "%1.10f"%self.gaussfitWidth[i] ).ljust(colwidth)
			print ln
		print "-"*(colwidth*7 + 4)	
	
	def plotAxisToScanVersusStepWidth(self):
		xdataset = Dataset(self.xvalues[0:self.currentPoint+1])
		xdataset.setName(self.axisToScan.getName())
		f = Dataset(self.gaussfitWidth[0:self.currentPoint+1])
		f.setName('gaussfitWidth (FWHM)')	
		Plotter.plot("Focus Finder",xdataset, [ f])

			
	def getDataSetNameForScannable(self, scn):
		try:  # new code added in run, so being careful
			if len(scn.getInputNames()) > 0:
				return scn.getInputNames()[0]
			if len(scn.getExtraNames()) > 0:
				return scn.getExtraNames()[0]
		except: # fall back to tested behaviour
			return scn.getName()

	def moveToOptimalFocus(self):
		print "Moving %s to %f..." % (self.axisToScan.getName(), self.minimumWidthPosition)
		pos([self.axisToScan, self.minimumGaussfitWidthPosition])
		print "Done"

	def __frange(self, limit1, limit2, increment):
		"""Range function that accepts floats (and integers).
		"""
#		limit1 = float(limit1)
#		limit2 = float(limit2)
		increment = float(increment)
		count = int(math.ceil((limit2 - limit1) / increment))
		result = []
		for n in range(count):
			result.append(limit1 + n * increment)
		return result
	
	def calcStddev(self, xdataset, ydataset):
		data = ScanFileHolder()
		centroidx = data.centroid(xdataset,ydataset)
		xarray= xdataset.doubleArray()
		yarray = ydataset.doubleArray()
		if len(xarray)!=len(yarray):
			raise ValueError
		
		top = bottom = 0
		for i in range(len(xarray)):
			top += yarray[i] * (xarray[i]-centroidx)**2
			bottom += yarray[i]
		try:
			tmpy = math.sqrt(abs(top)/abs(bottom))
		except Exception, e:
			
			raise Exception("Math troubles, all detector values probably the same:"+ str(e) + "top: %f, bottom: %f" % (top, bottom))
		return tmpy
	
	def findMinimum(self, xarray, yarray):
		"""x,y = findMinimum(xarray, yarray)"""
		xresult=xarray[0]
		yresult=yarray[0]		
		for x, y in zip(xarray,yarray):
			if y<yresult:
				xresult = x
				yresult = y 
		return (xresult, yresult)
	
	def kawalsFWHM(self, xdataset, ydataset, fwhmFraction):
		data = ScanFileHolder()	
		centroidx = data.centroid(xdataset,ydataset)
		xarray= xdataset.doubleArray()
		yarray = ydataset.doubleArray()
		centroididx = self.findIndex(xarray, centroidx)
		yarea = sum(yarray)
		sampleWidth=0
		while sum( yarray[centroididx-sampleWidth:centroididx+1+sampleWidth] )/yarea < fwhmFraction:
			sampleWidth += 1
		topIndex = centroididx+1+sampleWidth
		bottomIndex = centroididx-sampleWidth
		if bottomIndex<0:
			bottomIndex = 0
		if topIndex > (len(xarray)-1):
			topIndex = len(xarray)-1
		return abs( xarray[bottomIndex] - xarray[topIndex] )
	
	def findIndex(self, array, val):
		"""array is monotonically increasing or decreasing"""
		increasing = (array[-1] - array[0]) > 0
		for idx in range(len(array)):
			if increasing:
				if array[idx] >= val:
					return idx
			else:
				if array[idx] <= val:
					return idx
		
#ff = FocusFinder2(detector=z, extraMonitorList=[], countTime=0)
#ff.dummymode = True					
#			
#data = ScanFileHolder()
#data.loadSRS("/home/zrb13439/workspace/gda_7_8/config/base/users/data/10041.dat")
#data.info()
#xdataset = data.getDataSet('tbdiagY')
#xdataset = xdataset.getSubset([150,299])
#ydataset = data.getDataSet('pips2')
#ydataset = ydataset.getSubset([150,299])
#
#ydataset = ydataset.diff(xdataset)
#print ff.kawalsFWHM(xdataset, ydataset, 0.75)
#print ff.kawalsFWHM(xdataset, ydataset, 0.98)
