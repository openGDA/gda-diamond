try:
	import diffcalc
except ImportError:
	from gda.jython import InterfaceProvider
	import sys
	diffcalc_path = InterfaceProvider.getPathConstructor().createFromProperty("gda.install.git.loc") + '/diffcalc_trunk'
	sys.path = [diffcalc_path] + sys.path
	print diffcalc_path + ' added to GDA Jython path.'
	import diffcalc #@UnusedImport
from diffcalc.gdasupport.GdaDiffcalcObjectFactory import createDiffcalcObjects, addObjectsToNamespace


demoCommands = []
demoCommands.append( "newub 'cubic'" )
demoCommands.append( "setlat 'cubic' 1 1 1 90 90 90" )
demoCommands.append( "pos wl 1" )
demoCommands.append( "pos sixc [0 60 0 30 1 0]" )
demoCommands.append( "addref 1 0 0" )
demoCommands.append( "pos chi 91" )
demoCommands.append( "addref 0 0 1" )
demoCommands.append( "checkub" )
demoCommands.append( "ub" )
demoCommands.append( "hklmode" )

diffcalcObjects=createDiffcalcObjects(
	axisScannableList = (alpha, delta, gamma, omega, chi, phi),
	energyScannable = dcm1energy,
	geometryPlugin = 'sixc',
	hklverboseVirtualAnglesToReport=('2theta','Bin','Bout','azimuth'),
	demoCommands = demoCommands
)

diffcalcObjects['diffcalcdemo'].commands = demoCommands;
addObjectsToNamespace( diffcalcObjects, globals() )
