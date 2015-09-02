import diffcalc
from diffcalc.gdasupport.factory import create_objects, add_objects_to_namespace
from gdascripts.scannable.dummy import SingleInputDummy
from diffcalc.ub.persistence import UBCalculationJSONPersister


print "Creating a dummy energy Scannable"
dummy_energy = SingleInputDummy('dummy_energy')
dummy_energy(12.39842)
demoCommands = []

diffcalcObjects = create_objects(
	#axisScannableList = (alpha, delta, omega, chi, phi), #@UndefinedVariable
	axes_group_scannable = _fivec, #@UndefinedVariable
	energy_scannable = dummy_energy, #@UndefinedVariable
	energy_scannable_multiplier_to_get_KeV = 1,
	geometry = diffcalc.hkl.you.geometry.FiveCircle(),
	hklverbose_virtual_angles_to_report=('theta','alpha','beta','psi'),
	demo_commands = demoCommands,
	engine_name = 'you',
	simulated_crystal_counter_name = 'ct'
	)


#diffcalcObjects['diffcalcdemo'].commands = demoCommands
add_objects_to_namespace(diffcalcObjects, globals())

# does not work yet:
diffcalc.gdasupport.factory.override_gda_help_command(globals())
alias('help')


from math import cos, sin, pi, atan2
from gda.device.scannable import ScannableMotionBase

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
		