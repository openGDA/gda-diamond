import math
from uk.ac.diamond.scisoft.analysis.optimize import GeneticAlg
from gda.analysis import RCPPlotter
from uk.ac.diamond.scisoft.analysis.fitting.functions import StraightLine, Gaussian

from  org.eclipse.january.dataset import DatasetFactory
from uk.ac.diamond.scisoft.analysis.fitting import Fitter

#ref = refinement()
#ref.calibrateElement(20.0,0,23. 24. 22.4 0.001)

class refinement() :		

	def collectdata(self,time) :
	
		# collect the data
		self.ds = edxd.acquire(time) #@UndefinedVariable

	def calibrateElement(self,time, channel, min, max, value, toll) :
		chan = channel-1
		count = 0
		self.ppos = -10.0
		self.min = min
		self.max = max
		while (math.fabs(self.ppos-value)) > toll:
			print (math.fabs(self.ppos-value)), count
			self.ds = edxd.acquire(time) #@UndefinedVariable
			gain = self.refine(chan, self.min, self.max, value)
			edxd.getSubDetector(chan).setPreampGain(gain) #@UndefinedVariable
			if count > 10 :
				break
				

	def refine(self,chan, min, max, value) : 

		print "getting preamp"
		preamp = edxd.getSubDetector(chan).getPreampGain() #@UndefinedVariable
		print "peakpos"
		peakpos = self.getPeakPos(chan, min, max)
		# adjust the min and max values to track to the peak
		diff = value-peakpos
		self.min = self.min + diff
		self.max = self.max + diff
		print "newPreamp"
		newPreamp = (preamp*peakpos)/value
		print preamp, peakpos, value, newPreamp
		self.ppos = peakpos
		return newPreamp


	def getPeakPos(self,chan, min, max) :

		print chan
		self.be = edxd.getSubDetector(chan).getEnergyBins() #@UndefinedVariable

		minval = math.fabs(min-self.be[0])
		maxval = math.fabs(max-self.be[0])

		for i in range(len(self.be)):
			tmp = math.fabs(min-self.be[i])
			if tmp < minval:
				start = i
				minval = tmp
			tmp = math.fabs(max-self.be[i])
			if tmp < maxval:
				stop = i
				maxval = tmp
	
		print start
		print stop
	
		xds=DatasetFactory.createFromObject(self.be).getSlice([start], [stop], [1])

		print "here"
		yds=self.ds[chan][start:stop]

		print "fitting the data"
		# Fit the data using a GA
		fit = Fitter.fit(xds, yds, GeneticAlg(0.01), [StraightLine(-yds.max(),yds.max(),yds.min(),yds.max()), Gaussian(min,max,2*(max-min),1000)])

		RCPPlotter.plot("Plot 1", xds ,[yds, fit.getFunction().makeDataSet([xds])])
	
		# get out the 2 peak values
		peak1 = fit[2].getValue()
		fwhm1 = fit[3].getValue()

		print "peak position = %f with width %f " % (peak1, fwhm1)

		return peak1



