# For use when the hexapod is attached with mount facing up to create a
# vertical surface normal mode of operation, where the scattering plane tends to
# the horizontal.
#
raise DeprecationWarning("This script is no longer supported (as of November 2018) and should not be used")

print "<<< Running  /i07-config/scripts/BeamlineI07/diff1_horizontal_geometry.py"

try:
	import diffcalc
except ImportError:
	from gda.jython import InterfaceProvider
	import sys
	# XXX: this is pointing to diffcalc_trunk, not diffcalc
	diffcalc_path = InterfaceProvider.getPathConstructor().createFromProperty("gda.install.git.loc") + '/diffcalc_trunk'
	sys.path = [diffcalc_path] + sys.path
	print diffcalc_path + ' added to GDA Jython path.'
	import diffcalc #@UnusedImport
from diffcalc.gdasupport.GdaDiffcalcObjectFactory import createDiffcalcObjects, addObjectsToNamespace

from diffcalc.hkl.willmott.calcwill_horizontal import WillmottHorizontalGeometry
demoCommands = []

diffcalcObjects=createDiffcalcObjects(
#	dummyAxisNames = ('dummy1vdelta', 'dummy1vgamma', 'dummy1halpha', 'dummy1homega'),
	axisScannableList = (diff1vdelta, diff1vgamma, diff1halpha, diff1homega),
	diffractometerScannableName = 'sixc', #  staff prefer these to be the same across configurations
	energyScannable = dcm1energy,
	geometryPlugin = WillmottHorizontalGeometry(),
	hklverboseVirtualAnglesToReport=('betain', 'betaout'),
	engineName='willmott'
)

diffcalcObjects['diffcalcdemo'].commands = demoCommands;
addObjectsToNamespace( diffcalcObjects, globals() )



from diffcalc.gdasupport.scannable.slave_driver import NuDriverForWillmottHorizontalGeometry

def enable_nu_rotation_for_point_detector():
	driver = NuDriverForWillmottHorizontalGeometry([diff1dets1rot, diff1dets2rot], area_detector=False)
	sixc.slave_driver = driver
	print "Enabled nu rotation for point driver (diff1dets1rot = diff1dets2rot = nu)"
	
def enable_nu_rotation_for_pilatus():
	driver = NuDriverForWillmottHorizontalGeometry([diff1prot], area_detector=True)
	sixc.slave_driver = driver
	print "Enabled nu rotation for area driver (diff1prot = nu)"

def disable_nu_rotation():
	sixc.slave_driver = None
	print "Disabled nu rotation"

alias('enable_nu_rotation_for_point_detector')
alias('enable_nu_rotation_for_pilatus')
alias('disable_nu_rotation')
