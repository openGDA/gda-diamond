from gda.epics import CAClient
from java import lang
import time

class Mover(PseudoDevice):
	'''pseudo device to move stuff, multiple axis simulaniously'''
	def __init__(self, name):
		self.setName(name)
		self.poses={}
		self.target="unknown"
		self.location="unknown"
		self.togo={}


	def addPos(self, name, posDict):
		self.poses[name]=posDict
		

	def getPosition(self):
		return self.location
	
	def asynchronousMoveTo(self,p):
		self.target=p
		self.togo=self.poses[self.target]
		self.location="moving"
		for i in self.togo.keys():
			i.asynchronousMoveTo(self.togo[i])

	def isBusy(self):
		for i in self.togo.keys():
			if i.isBusy():
				return 1
		self.togo={}
		self.location=self.target
		return 0
	

#>>>mover=Mover("mover")
#>>>mover.addPos("orangediode", {basey: 191.25, basex: -51})
#>>>pos mover "orangediode"
#'Move completed: mover orangediode'
#>>>mover.addPos("camera", {basey: 187.95, basex: 71.3})
#>>>pos mover "camera"
