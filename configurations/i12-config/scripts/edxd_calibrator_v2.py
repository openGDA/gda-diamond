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

	def calibrateElement(self,time, channel, minv, maxv, value, toll) :
		chan = channel-1
		count = 0
		self.ppos = -10.0
		self.min = minv
		self.max = maxv
		while (math.fabs(self.ppos-value)) > toll:
			print (math.fabs(self.ppos-value)), count
			self.ds = edxd.acquire(time) #@UndefinedVariable
			gain = self.refine(chan, self.min, self.max, value)
			edxd.getSubDetector(chan).setPreampGain(gain) #@UndefinedVariable
			if count > 10 :
				break
				

	def refine(self,chan, minv, maxv, value) : 

		print "getting preamp"
		preamp = edxd.getSubDetector(chan).getPreampGain() #@UndefinedVariable
		print "peakpos"
		peakpos = self.getPeakPos(chan, minv, maxv)
		# adjust the min and max values to track to the peak
		diff = value-peakpos
		self.min = self.min + diff
		self.max = self.max + diff
		print "newPreamp"
		newPreamp = (preamp*peakpos)/value
		print preamp, peakpos, value, newPreamp
		self.ppos = peakpos
		return newPreamp


	def getPeakPos(self,chan, minv, maxv) :

		print chan
		self.be = edxd.getSubDetector(chan).getEnergyBins() #@UndefinedVariable

		minval = math.fabs(minv-self.be[0])
		maxval = math.fabs(maxv-self.be[0])
		print('minval = {0}, maxval = {1}'.format(minval, maxval))
		print('tmp[0] = {0}'.format(minv-self.be[0]))

		for i in range(len(self.be)):
			tmp = math.fabs(minv-self.be[i])
			if tmp < minval:
				start = i
				minval = tmp
			tmp = math.fabs(maxv-self.be[i])
			if tmp < maxval:
				stop = i
				maxval = tmp
	
		print start
		print stop
	
		print("Creating datasets")
		xds=DatasetFactory.createFromObject(self.be).getSlice([start], [stop], [1])
		yds=DatasetFactory.createFromObject(self.ds[chan].getData()[start:stop])

		print "fitting the data"
		# Fit the data using a GA
		max_yds = max(yds.getData())
		min_yds = min(yds.getData())
		fit = Fitter.fit(xds, yds, GeneticAlg(0.01), [StraightLine(-max_yds, max_yds, min_yds, max_yds), Gaussian(minv, maxv, 2 * (maxv - minv), 1000)])

		RCPPlotter.plot("Plot 1", xds ,[yds, fit.getFunction().makeDataSet([xds])])
	
		# get out the 2 peak values
		peak1 = fit[2].getValue()
		fwhm1 = fit[3].getValue()

		print "peak position = %f with width %f " % (peak1, fwhm1)

		return peak1
