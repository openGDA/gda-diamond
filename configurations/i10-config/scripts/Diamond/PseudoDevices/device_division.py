'''
This module provides a class definition for creating a scannable that returns the division of scannable1 over scannable2
while scanning scannable1 and scannable2.
Usage:
	>>>c17dbc16= DeviceDivisionClass("c17dbc16", mcsr17_g, mcsr16_g);;
	>>> cvscan egy_g 695 705 1 mcsr17_g 0.4 mcsr16_g c17dbc16

Created on 24 Jun 2010

@author: fy65
'''
from gda.device.continuouscontroller import CSViacontrollerScannable
#from gda.factory import Finder
#from scannable.continuous.try_continuous_energy import mcsr16_g, mcsr17_g

class DeviceDivisionClass(CSViacontrollerScannable):
	def __init__(self, name, scannable1, scannable2):
		'''constructor parameters:
				name:   Name of the new device
				scannableX: Name of the scannable on X-axis (for example: "mcsr17_g")
				scannableY: Name of the scannable on Y-axis (for example: "mcsr16_g")
		'''
		self.setName(name);
		self.setInputNames([name]);
		#self.Units=[strUnit]
		#self.setOutputFormat([strFormat])
		#self.setLevel(8);
		self.s1values = []
		self.s2values = []		
		self.normalisedvalues = []
		self.refObj1 = scannable1
		self.refObj2 = scannable2
		
	def getPosition(self):
		'''return the element-wise division of the two scannables. '''
		self.s1values=list(self.refObj1.getPosition())
		self.s2values=list(self.refObj2.getPosition())
		self.normalisedvalues = self.elementWiseDivision(self.s1values, self.s2values);
		return self.normalisedvalues;


	def asynchronousMoveTo(self, new_position):
		print "Can not set position for this derivative type device";

	def isBusy(self):
		'''returns busy if the two scannables are busy'''
		return (self.refObj1.isBusy() & self.refObj2.isBusy());

	def elementWiseDivision(self, x1=[], x2=[]):
		'''returns the element-wise division of the two array'''
		if len(x1)==0:
			print "1st scannable no value returned"
		if len(x2)==0:
			print "2nd scannable no value returned"
		if len(x1)!=len(x2):
			print "The number of elements returned from 2 scannables are different"
		y=[float(a)/float(b) for a,b in zip(x1, x2)]
		return y;

c17dbc16= DeviceDivisionClass("c17dbc16", mcsr17_g, mcsr16_g);  # @UndefinedVariable