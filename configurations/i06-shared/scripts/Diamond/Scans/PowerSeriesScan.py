
import math;
from gda.device.scannable import ScannableMotionBase, ScannableBase
from gda.device import Scannable

from gda.scan import ConcurrentScan
from gda.scan import ScanPositionProviderFactory
from gda.jython.commands.GeneralCommands import alias

import java.lang.InterruptedException #@UnresolvedImport

from Diamond.Scans.BasicScan import BasicScanClass;
	
class PowerSeriesScanClass(BasicScanClass):
	'''Use iscan motor start stop growthRate for scan in a exponential increase of steps.
	The n-th scan point is calculated using a0*(1+q)^n, where a0 is the starting point and q is the growth rate.
	For example:
	    iscan testMotor1 1 100, 1 dummyCounter1 0.1	'''
	
	def __init__(self):
		BasicScanClass.__init__(self);
		self.scanType='iscan';
		self.minimalNoneZero=0.1;
		
	def __call__(self, *args):
		BasicScanClass.__call__(self, *args);

	def parseArgs(self, devices, parameters):
		""" To change the sections with range and steps into a single individual position list
		eg: [[x, (1, 2, 3, 3.5, 4, 4.5, 5), z] = parseArgs([x, (R1, R2, Ri, ...), z])
		where Ri=[start, stop, step]
		"""
		newArgs=[]
		for k, v in zip(devices, parameters):
			if len(v) == 3:
				vp=self.getPowerSeries(*v);
				newArgs.append(k);
				newArgs.append(vp);
			else:
				newArgs.append(k);
				newArgs.extend(v);
		
		return newArgs;


	def getPowerSeries(self, start, end, q):
		
		#To make sure there is no zero start/end
		if start == 0:
				start=self.minimalNoneZero * cmp(end, 0);
		if end == 0:
			end=self.minimalNoneZero* cmp(start, 0);
		q=abs(q);

		if start == end:
			raise Exception("Start and End messed up!");
		
		if start>0 and end>0:
			s=self.powerSeries( start, end, q*cmp(end, start) );
		elif start<0 and end<0:
			s=self.powerSeries( start, end, -q*cmp(end, start) );
		elif start<0 and end>0:
#				print("-10, 5");
				s=self.powerSeries( start, -self.minimalNoneZero, -q );
				s2=self.powerSeries( self.minimalNoneZero, end, q );
				s.extend(s2) 
		elif start>0 and end<0:
#				print("10, -5");
				s=self.powerSeries( start, self.minimalNoneZero, -q );
				s2=self.powerSeries( -self.minimalNoneZero, end, q );
				s.extend(s2) 
		else:
			print("Confused?! ")
			raise Exception("Start and End messed up!")
			
		return tuple(s);
	
	def powerSeries(self, start, end, q):
		a0=float(start);
		a1=float(end);
#		if a0 < self.minimalNoneZero:
#			print("Start/End position should be above zero. Use default minimum value instead")
#			a0=self.minimalNoneZero;
		n=int( math.log(a1/a0)/math.log(1+q) ) + 1; #Number of points
		s=[a0*pow(1+q, i) for i in range(n)];
		s.append(a1);
		return s;
		

#Usage
#iscan=PowerSeriesScanClass()
#alias('iscan');
