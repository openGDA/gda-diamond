from gda.device.scannable import ScannableMotionBase
from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from gda.epics import CAClient

from gdascripts.messages import handle_messages
from gdascripts.parameters import beamline_parameters
ca=CAClient()
# to read a floating point number from EPICS use
# float(ca.caget("PVNAME"))
# to set a value in EPICS use
# ca.put("PVNAME", value)

class beamLineEnergy(ScannableMotionBase):
	def __init__(self):
		self.name = "bl"
		self.reload()
	def rawIsBusy(self):
		return self.dcm_energy.isBusy()

	def getPosition(self):
		return self.dcm_energy.getPosition()

	def asynchronousMoveTo(self, new_energy):
		self.dcm_energy.asynchronousMoveTo(new_energy)
#		self.id_gap.asynchronousMoveTo(nnnn)

	def setFromScript(self, position):
		try:
			self.asynchronousMoveTo(position)
		except :
			exceptionType, exception, traceback = sys.exc_info()
			handle_messages.log(None, "beamLineEnergy:" + self.name + ". Error in asynchronousMoveTo", exceptionType, exception, traceback, False)
		return "ok"
	def log(self, msg):
		handle_messages.log(self.scriptcontroller,msg )
	def reload(self):
		self.jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
		self.finderNameMap = beamline_parameters.FinderNameMapping()
		self.beamlineMap   = beamline_parameters.Parameters()
		self.dcm_energy = self.jythonNameMap.dcm_energy
		self.id_gap = self.jythonNameMap.id_gap
