import math
from uk.ac.diamond.scisoft.analysis.optimize import GeneticAlg
from gda.analysis import RCPPlotter
from time import sleep
from gda.factory import Finder
from uk.ac.diamond.scisoft.analysis.fitting import Fitter
from uk.ac.diamond.scisoft.analysis.fitting.functions import StraightLine, Gaussian
from org.eclipse.january.dataset import DatasetFactory
#ref = refinement()
#ref.calibrateElement(20.0,0,23. 24. 22.4 0.001)

class refinement() : 
	
	def __init__(self):
		self.edxd = Finder.find("edxdcontroller")	   
		self.tfg = Finder.find("tfg")
		self.vortex = Finder.find("xmapMca")

	def collectdata(self,time) :
	
		# collect the data
		self.ds =  self.acquire(time)

	def calibrateElement(self,time, chan, min, max, value, toll) :
		count = 0
		self.ppos = -10.0
		while (math.fabs(self.ppos-value)) > toll:
			print (math.fabs(self.ppos-value)), count
			self.ds =  self.acquire(time)
			gain = self.refine(chan, min, max, value)
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
	
		xds=DatasetFactory.createFromObject(self.be).getSlice([start], [stop], [1])

		print "here"
		yds=self.ds[chan][start:stop]

		print "fitting the data"
		# Fit the data using a GA
		fit = Fitter.fit (xds, yds,GeneticAlg(0.01),[StraightLine(-yds.max(),yds.max(),yds.min(),yds.max()), Gaussian(min,max,2*(max-min),1000)])

		RCPPlotter.plot("Scan Plot 1", xds ,[yds, fit.getFunction(0).makeDataset([xds])])
	
		# get out the 2 peak values
		gaussian=fit.getFunction(1)
		peak1 = gaussian.getPosition()
		fwhm1 = gaussian.getFWHM()

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
		for i in range(self.edxd.getNumberOfElements()):
			det = self.edxd.getSubDetector(i)
			ds = DatasetFactory.createFromObject(det.readoutDoubles())
			ds.setName(det.getName())
			data.append(ds)
			
		yaxis = DatasetFactory.createFromObject(self.edxd.getSubDetector(0).getEnergyBins())
		yaxis.setName("Energy")
		##plot
		RCPPlotter.plot("Scan Plot 1", yaxis, data);
		return data
