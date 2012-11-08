import java
import ShelveIO

class DetectorClass:

	def __init__(self):
		#self.setName(name)
		#self.setInputNames([name])
		# as calibrated 10th May 2007
 		self.detectorlist = {'vortex':-19,'apd':-2.5,'scint':17,'camera':29.05,'diode':52}
    		self.detector=ShelveIO.ShelveIO()
      		self.detector.path=ShelveIO.ShelvePath+'offset'
      		self.detector.setSettingsFileName('detector')
		self.getdetector()

	def getdetector(self):
		self.currentdetector = self.detector.getValue('detector')
		self.label=0
		self.offset = self.detectorlist[self.currentdetector]
		return self.currentdetector

	def setdetector(self,new):
		self.detector.ChangeValue('detector',new)
		self.label=1
		self.currentdetector = new
		self.offset = self.detectorlist[new]

detector = DetectorClass()

def getdetector():
	return detector.getdetector()


def setdetector(new):
	detector.setdetector(new)
	return detector.getdetector()
