import math
from gda.analysis.utils import GeneticAlg
from gda.analysis import DataSet
from gda.analysis import Plotter
from time import sleep
from gda.factory import Finder

#ref = refinement()
#ref.calibrateElement(20.0,0,23. 24. 22.4 0.001)

class refinement() : 
	
	def __init__(self):
		self.edxd = Finder.getInstance().find("edxdcontroller")	   
		self.tfg = Finder.getInstance().find("tfg")
		self.vortex = Finder.getInstance().find("xmapMca")

	def collectdata(self,time) :
	
		# collect the data
		self.ds =  self.acquire(time)

	def calibrateElement(self,time, chan, min, max, value, toll) :
		count = 0
		self.ppos = -10.0
		while (math.fabs(self.ppos-value)) > toll:
			print (math.fabs(self.ppos-value)), count
			self.ds =  self.acquire(time)
			gain = ref.refine(chan, min, max, value)
			self.edxd.getSubDetector(chan).setPreampGain(gain)
			if count > 10 :
				break
				

	def refine(self,chan, min, max, value) : 

		print "getting preamp"
		preamp =  self.edxd.getSubDetector(chan).getPreampGain()
		print "peakpos"
		peakpos = self.getPeakPos(chan, min, max)
		print "newPreamp"
		newPreamp = (preamp*peakpos)/value
		print preamp, peakpos, value, newPreamp
		self.ppos = peakpos
		return newPreamp


	def getPeakPos(self,chan, min, max) :

		print chan
		self.be =  self.edxd.getSubDetector(chan).getEnergyBins()

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
	
		xds=DataSet(self.be)[start:stop]

		print "here"
		yds=self.ds[chan][start:stop]

		print "fitting the data"
		# Fit the data using a GA
		fit = Fitter.fit (xds, yds,GeneticAlg(0.01),[StraightLine(-yds.max(),yds.max(),yds.min(),yds.max()), Gaussian(min,max,2*(max-min),1000)])

		Plotter.plot("Plot 1", xds ,[yds, fit.getFunction().makeDataSet([xds])])
	
		# get out the 2 peak values
		peak1 = fit[2].getValue()
		fwhm1 = fit[3].getValue()

		print "peak position = %f with width %f " % (peak1, fwhm1)

		return peak1
	
	def acquire(self, acquisitionTime, verbose=True):
		self.edxd.setCollectionTime(acquisitionTime)
		self.edxd.collectData()
		try:
			sleep(2.0)
		except:
			self.interrupted = 1  
		self.tfg.countAsync(acquisitionTime * 1000)
		try:
			sleep(acquisitionTime)
		except:
			self.interrupted = 1 
		
		while(self.tfg.getStatus() == 1):
			if(verbose):
				print "Acquiring"
			sleep(1)
		if(verbose):
			print "Done"
		self.edxd.stop()
		try:
			sleep(1.5)
		except:
			self.interrupted = 1  
		#self.edxd.verifyData()
		data =[]
		for i in range(self.edxd.getNUMBER_OF_ELEMENTS()):
			det = self.edxd.getSubDetector(i)
			data.append(DataSet(det.getName(), det.readoutDoubles()))
			
		yaxis = DataSet("Energy", self.edxd.getSubDetector(0).getEnergyBins())
		##plot
		Plotter.plot("Plot 1", yaxis, data);
		return data
