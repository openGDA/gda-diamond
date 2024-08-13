'''
Created on 19 Dec 2023

@author: eir17846
'''
from gda.device.scannable import ScannableMotionBase
from gdascripts.pd.epics_pds import DisplayEpicsPVClass
from detector.iseg_instances import kenergy
from gda.factory import Finder
from time import sleep

class AverageMonitor():
	def __init__(self, scannable, n_points = 20):
		self.pollTime = 0.01
		if n_points>0:
			self.points = n_points
		else:
			self.points = 1
		self.scannable = scannable

	def getPosition(self):
		counter = 0
		average = 0.0
		while counter<self.points:
			counter+=1
			average=(average+self.scannable.getPosition())
			sleep(self.pollTime)
		return (average/counter)

class bindingEnergyScannable(ScannableMotionBase):

	def __init__(self, name, pgm_scannable, pgm_demand, sample_bias_scannable, averageMonitor, unitstring, formatstring, work_function=4.45):
		self.setName(name);
		self.setInputNames([name])
		self.pgm_scannable = pgm_scannable
		self.sample_bias_scannable = sample_bias_scannable
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		# Level must be higher than default level(5) of scannables - pgm (level=5) must be set first!
		self.setLevel(6)
		self.work_function = work_function
		self.pgm_demand = pgm_demand
		self.threshold = 0.05
		self.averageMonitor = averageMonitor

	def rawGetPosition(self):
		try:
			if (abs(self.pgm_demand.getPosition() - self.pgm_scannable.getPosition())<self.threshold):
				#print "PGM demand and readback difference less than threshold"
				be = self.pgm_demand.getPosition() - self.sample_bias_scannable.getPosition() - self.work_function
			else:
				print "PGM demand and readback difference MORE than threshold"
				be = self.getAverageEnergy() - self.sample_bias_scannable.getPosition() - self.work_function
			return be
		except:
			print "Error returning position"
			return 0

	def rawAsynchronousMoveTo(self, new_position):
		try:
				if (abs(self.pgm_demand.getPosition() - self.pgm_scannable.getPosition())<self.threshold):
						result = self.pgm_demand.getPosition() - new_position - self.work_function
				else:
						result = self.getAverageEnergy() - new_position - self.work_function
				self.sample_bias_scannable.moveTo(result)
		except:
				print "error moving to position"

	def getAverageEnergy(self):
		try:
				average = self.averageMonitor.getPosition()
				return average
		except:
				print "Failed to average pgm energy - returning immediate value"
				return self.pgm_scannable.getPosition()

	def isBusy(self):
		try:
				return self.sample_bias_scannable.isBusy()
		except:
				print "problem moving: Returning busy status"
				return 0

	def setWF(self, value):
		try:
				self.work_function = value
				print "Work function set to new value ", value
		except:
				print "Setting work function failed"

	def getWF(self):
		print "Work function value is ", self.work_function
		return self.work_function

pgmenergy = Finder.find("pgmenergy")
pgmDemand = DisplayEpicsPVClass("pgmDemand","BL09J-MO-PGM-01:ENERGY.VAL", "keV", "%f")
pgmAverageMonitor = AverageMonitor(pgmenergy)

benergy=bindingEnergyScannable("benergy", pgmenergy, pgmenergy, kenergy, pgmAverageMonitor, "", "%d", 4.3)
Benergy=bindingEnergyScannable("Benergy", pgmenergy, pgmDemand, kenergy, pgmAverageMonitor, "", "%d", 4.3)
