
import math
import os, time;

from gda.device.scannable import ScannableMotionBase, ScannableBase
from gda.device import Scannable

from gda.scan import ConcurrentScan
from gda.scan import ScanPositionProviderFactory
from gda.jython.commands.GeneralCommands import alias
from gda.jython import InterfaceProvider
from gda.jython import JythonServerFacade;
from gda.configuration.properties import LocalProperties

import java.lang.InterruptedException #@UnresolvedImport

from Diamond.Scans.BasicScan import BasicScanClass;

class CentroidScanClass(BasicScanClass):
	def __init__(self):
		BasicScanClass.__init__(self);
		self.scanType='cscan';
		self.centreDict=dict();

		self.returnToCentre=True;

#	def __call__(self, *args):
#		BasicScanClass.__call__(self, *args);
		
	def postScanRestoration(self):
		if self.returnToCentre:
			for k, v in self.centreDict.iteritems():
				print "Move motor %s back to central position %f" %(k.getName(), v);
				k.asynchronousMoveTo(v);

			busy=True;
			while busy:
				#print "Waiting all motors to finish the their move.";
				time.sleep(1);
				busy=False;
				for k, v in self.centreDict.iteritems():
					if k.isBusy():
						busy=True;

	def parseArgs(self, devices, parameters):
		""" To change the sections with range and steps into a single individual position list
		eg: [x, (1, 2, 3, 3.5, 4, 4.5, 5), y, (3, 4, 5), z]
		"""
		newArgs=[]
		self.centreDict=dict();
		
		for k, v in zip(devices, parameters):
			if len(v) == 3:# v = [centre, width, step]
				[centre, width, step]=v;
				self.centreDict[k]=centre;#To back up the centre position for after scan position restore
				vp=[ centre-abs(width), centre+abs(width), step ];
				newArgs.append(k);
				newArgs.extend(vp);
			elif len(v) == 2:# v = [width, step]#The default centre position will be k's current position;
				[width, step]=v;
				centre=k.getPosition();
				self.centreDict[k]=centre;#To back up the centre position for after scan position restore
				vp=[ centre-abs(width), centre+abs(width), step ];
				newArgs.append(k);
				newArgs.extend(vp);
			else:
				newArgs.append(k);
				newArgs.extend(v);
		
		return newArgs;

#Usage
#del cscan
#cscan=CentroidScanClass()
#alias('cscan');
