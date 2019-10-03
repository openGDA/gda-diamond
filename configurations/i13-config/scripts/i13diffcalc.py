try:
	import diffcalc
except ImportError:
	from gda.jython import InterfaceProvider
	import sys
	diffcalc_path = InterfaceProvider.getPathConstructor().createFromProperty("gda.root").split('/plugins')[0] + '/diffcalc' 
	sys.path = [diffcalc_path] + sys.path
	print diffcalc_path + ' added to GDA Jython path.'
	import diffcalc #@UnusedImport
from diffcalc.gdasupport.GdaDiffcalcObjectFactory import createDiffcalcObjects, addObjectsToNamespace
from diffcalc.geometry.sixc import FivecWithGammaOnBase
from gda.device.scannable import ScannableMotionBase
from math import cos, sin, pi, atan2
demoCommands = []
demoCommands.append( "newub 'cubic'" )
demoCommands.append( "setlat 'cubic' 10 10 10 90 90 90" )
demoCommands.append( "addref 1 0 0 (60, 0, 30, 0, 0) 1.24" )
demoCommands.append( "addref 0 0 1 (60, 0, 30, 90, 0) 1.24" )
demoCommands.append( "checkub" )
demoCommands.append( "pos wl 10." )
demoCommands.append( "c2th [1 0 0]" )
demoCommands.append( "ub" )
demoCommands.append( "hklmode 4" )
demoCommands.append( "pos azimuth 90." )
demoCommands.append( "pos oopgamma 0." )
demoCommands.append( "hklmode" )


diffcalcObjects=createDiffcalcObjects(
	axesGroupScannable = diff, #@UndefinedVariable
	energyScannable = ix, #@UndefinedVariable
	geometryPlugin = FivecWithGammaOnBase(),
	energyScannableMultiplierToGetKeV = 0.001,
	hklverboseVirtualAnglesToReport=('2theta','Bin','Bout','azimuth'),
	demoCommands = demoCommands,
	simulatedCrystalCounterName = 'dummyct'
)

diffcalcObjects['diffcalcdemo'].commands = demoCommands;
addObjectsToNamespace( diffcalcObjects, globals() )


class QRotator(ScannableMotionBase):
	
	def __init__(self, name, hkl):
		self.name = name
		self._hkl = hkl
		self.inputNames = ['rot']
		self.q_length = 1
	
	def rawAsynchronousMoveTo(self, rot):
		h = cos(rot*pi/180) * self.q_length
		k = sin(rot*pi/180) * self.q_length
		l = 0
		self._hkl.asynchronousMoveTo((h, k, l))
		
	def rawGetPosition(self):
		h, k, l = self._hkl()
		return atan2(k, h) * 180 / pi
	
	def waitWhileBusy(self):
		return self._hkl.waitWhileBusy()
	
qrot = QRotator('qrot', hkl)
		