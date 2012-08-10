import math
from gda.analysis.utils import GeneticAlg
from gda.analysis import DataSet, Fitter, RCPPlotter
from gda.analysis.functions import Gaussian, StraightLine

#ref = refinement()
#ref.calibrate(20.0,23. 24. 22.4 0.001)

class refinement() :		

	def collectdata(self,time) :
	
		# collect the data
		self.ds = edxd.acquire(time) #@UndefinedVariable

	def calibrate(self,time, min, max, value, toll) :
		count = 0
		self.error = toll+10.0
		self.errors = {}
		for i in range(23):
			self.errors[i] = toll+5.0
		self.min = min
		self.max = max
		while self.error > toll:
			print "Worst error is %f and number of iterations so far is %i" % (self.error, count)
			self.error = 0.0
			count += 1
			self.ds = edxd.acquire(time) #@UndefinedVariable
			for i in range(23):
				if self.errors[i] > toll :
					gain = self.refine(i, self.min, self.max, value, toll)
					edxd.getSubDetector(i).setPreampGain(gain) #@UndefinedVariable
				else :
					print "Channel %i is now complete" % (i+1)

			if count > 10 :
				print "Did 10 itterations, might be an OK solution but check visually"
				return
		print "All done, energy calibration complete"
				

	def refine(self,chan, min, max, value, toll) : 
		preamp = edxd.getSubDetector(chan).getPreampGain() #@UndefinedVariable
		peakpos = self.getPeakPos(chan, min, max)
		
		diff = value-peakpos
		# dont move more then 100 times the tollerence in a single step
		# this avoids issues with the fitting if something goes wrong
		max_displacement = toll*100
		if diff > max_displacement :
			diff = max_displacement
		if diff < -max_displacement :
			diff = -max_displacement
		newPreamp = (preamp*peakpos)/value
		
		print "Channel %i : old preamp = %f, peakpos = %f, correct peak values = %f, diff = %f,  new preamp = %f" % (chan+1, preamp, peakpos, value, diff, newPreamp)
		error = math.fabs(peakpos-value)
		self.errors[chan] = error
		if (error > self.error) :
			print "replaceing error ", self.error, " with ", error 
			self.error = error
			
		return newPreamp


	def getPeakPos(self,chan, min, max) :

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

	
		xds=DataSet(self.be)[start:stop]

		yds=self.ds[chan][start:stop]

		# Fit the data using a GA
		fit = Fitter.fit (xds, yds,GeneticAlg(0.001),[StraightLine(-yds.max(),yds.max(),yds.min(),yds.max()), Gaussian(min,max,2*(max-min),1000),Gaussian(min,max,2*(max-min),1000)])

		RCPPlotter.plot("Plot 1", xds ,[yds, fit.getFunction().makeDataSet([xds])])
	
		# get out the 2 peak values
		peak1 = fit[2].getValue()
		fwhm1 = fit[3].getValue()

		peak2 = fit[5].getValue()
		fwhm2 = fit[6].getValue()

		# return the second peak
		if peak1 > peak2:
			return peak1

		return peak2



