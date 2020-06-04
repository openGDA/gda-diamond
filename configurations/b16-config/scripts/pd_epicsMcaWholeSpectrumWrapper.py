from gda.device.scannable import ScannableMotionBase
from gda.device.detector.analyser import EpicsMCAPresets

class EpicsMcaWholeSpectrumWrapper(ScannableMotionBase):
	
	def __init__(self, name, epicsmca):
		self.name = name
		self.epicsmca = epicsmca
		self.lastLivetime = 0.0
		#self.noChannels = self.epicsmca.getNumberOfChannels() # proves unreliable
		self.noChannels = len(self.epicsmca.readout().tolist())
		self.setInputNames([name+"_livetime"])
		chnames = []
		for i in range(0,self.noChannels):
			chnames.append("ch") # +str(i))# Breaks pos if too long!  str(i))
		self.setExtraNames(chnames)
		self.setOutputFormat(['%.3f'] + ['%.0f']*self.noChannels)
		self.setLevel(9)

	def isBusy(self):
		return self.epicsmca.isBusy()

	def getPosition(self):
		return [self.lastLivetime] + self.epicsmca.readout().tolist()

	def asynchronousMoveTo(self,livetime):
		self.epicsmca.setPresets( EpicsMCAPresets(0,float(livetime),0,0,0,0) )
		self.lastLivetime = float(livetime)
		self.epicsmca.eraseStartAcquisition()
