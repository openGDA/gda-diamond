from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import EpicsScannable

class RawScannableExposer(ScannableMotionBase):

	def __init__(self, scn):
		self.scn = scn
		
		self.name = scn.name
		self.inputNames = scn.inputNames
		self.extraNames = scn.extraNames
		self.outputFormat = scn.outputFormat

	def isBusy(self):
		return self.scn.isBusy()

	def getPosition(self):
		return "'" + self.scn.rawGetPosition() + "'"

	def asynchronousMoveTo(self, pos):
		self.scn.asynchronousMoveTo(pos)


tmp = EpicsScannable()
tmp.name = 'femto1gain'
tmp.setUseNameAsExtraName(True)
tmp.outputFormat = ['%s']
tmp.pvName = 'BL16B-DI-FEMTO-01:GAIN'
tmp.setGetAsString(True)
tmp.configure()
femto1gain = RawScannableExposer(tmp)

tmp = EpicsScannable()
tmp.name = 'femto2gain'
tmp.setUseNameAsExtraName(True)
tmp.outputFormat = ['%s']
tmp.pvName = 'BL16B-DI-FEMTO-02:GAIN'
tmp.setGetAsString(True)
tmp.configure()
femto2gain = RawScannableExposer(tmp)

tmp = EpicsScannable()
tmp.name = 'femto3gain'
tmp.setUseNameAsExtraName(True)
tmp.outputFormat = ['%s']
tmp.pvName = 'BL16B-DI-FEMTO-03:GAIN'
tmp.setGetAsString(True)
tmp.configure()
femto3gain = RawScannableExposer(tmp)

del tmp

