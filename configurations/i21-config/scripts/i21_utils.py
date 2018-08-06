from gda.device.currentamplifier import EpicsCurrAmpSingle
from scannabledevices.cleverAmplifier import gainmap, gainpositions

#
# a pseudo device representing a PV.  It will not change the value of the 
# PV, so is used simply for monitoring.
#
# Example usage:
# img2=DisplayEpicsPVClass('IMG02', 'BL16I-VA-IMG-02:P', 'mbar', '%.1e')
#
class DisplayEpicsPVClass_neg(EpicsCurrAmpSingle):
	'''Create EpicsCurrAmpSingle to display negated value'''
	def __init__(self, name, scannable):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames(["Actual_Value"])
		self.scannable=scannable
		
	def getCurrent(self):
		return -self.scannable.getCurrent()
	
	def getGain(self):
		return self.scannable.getGain()
	
	def setGain(self,position):
		self.scannable.setGain(position)

	def getPosition(self):
		currentValue=self.getCurrent()
		currentGain=self.getGain()
		return [currentValue,currentValue/float(gainmap[gainpositions[currentGain]])]

class DisplayEpicsPVClass_pos(EpicsCurrAmpSingle):
	'''Create EpicsCurrAmpSingle to display positive value'''
	def __init__(self, name, scannable):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames(["Actual_Value"])
		self.scannable=scannable
		
	def getCurrent(self):
		return self.scannable.getCurrent()
	
	def getGain(self):
		return self.scannable.getGain()
	
	def setGain(self,position):
		self.scannable.setGain(position)

	def getPosition(self):
		currentValue=self.getCurrent()
		currentGain=self.getGain()
		return [currentValue,currentValue/float(gainmap[gainpositions[currentGain]])]


