# For use when the hexapod is attached with mount facing up to create a
# vertical surface normal mode of operation, where the scattering plane tends to
# the horizontal.
#
try:
	import diffcalc
except ImportError:
	from gda.data.PathConstructor import createFromProperty
	import sys
	# XXX: this is pointing to diffcalc_trunk, not diffcalc
	diffcalc_path = createFromProperty("gda.install.git.loc") + '/diffcalc_trunk' 
	sys.path = [diffcalc_path] + sys.path
	print diffcalc_path + ' added to GDA Jython path.'
	import diffcalc #@UnusedImport

from diffcalc.external.GdaDiffcalcObjectFactory import createDiffcalcObjects, addObjectsToNamespace

from diffcalc.hkl.willmott.calcwill_horizontal import WillmottHorizontalPosition
demoCommands = []

diffcalcObjects=createDiffcalcObjects(
	axisScannableList = (diff1vdelta, diff1vgamma, diff1halpha, diff1homega),
	diffractometerScannableName = 'sixc', #  staff prefer these to be the same across configurations
	energyScannable = dcm1energy,
	geometryPlugin = WillmottHorizontalPosition,
	hklverboseVirtualAnglesToReport=('betain', 'betaout'),
	engineName='willmott'
)

diffcalcObjects['diffcalcdemo'].commands = demoCommands;
addObjectsToNamespace( diffcalcObjects, globals() )
