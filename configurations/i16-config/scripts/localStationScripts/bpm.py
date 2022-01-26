#beam position monitor

from gdascripts.scannable.epics.PvManager import PvManager
from time import sleep

class BpmStats(ScannableMotionBase):
	'''Device to read stats from beam position monitor'''
	def __init__(self, name, comchan='BL16I-DI-BPM-01:STATS:', help=None):
		self.name = name		
		self.inputNames = []
		self.extraNames = ['centroid_x', 'centroid_y', 'sigma_x', 'sigma_y','bpmsum']
		self.outputFormat =['%4.4f'] * 5
		self.level = 9
		self.pvs = PvManager(pvroot = comchan)
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help 

	def getPosition(self):
		bpmsum = float(self.pvs['Total_RBV'].caget())
		bpmx = float(self.pvs['CentroidX_RBV'].caget())
		bpmy = float(self.pvs['CentroidY_RBV'].caget())
		sigmax = float(self.pvs['SigmaX_RBV'].caget())
		sigmay = float(self.pvs['SigmaY_RBV'].caget())
		return [bpmx,bpmy,sigmax,sigmax,bpmsum]

	def isBusy(self):
		return False

bpmstats=BpmStats("bpmstats")

def bpmin():
	caput('BL16I-DI-BPM-01:DIAG.VAL',-20)
	print "Screen in (-20)"

def bpmout():
	caput('BL16I-DI-BPM-01:DIAG.VAL',-2)
	print "Screen out (-2)"

