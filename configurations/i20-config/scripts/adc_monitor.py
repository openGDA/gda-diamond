from gda.device.detector import DetectorBase
from gda.epics import CAClient
import time

class adcmonitor(DetectorBase):

	def __init__(self,name,pvPrefix,readoutPV,columnName):
		self.setName(name)
		self.pvPrefix = pvPrefix
		self.ca = CAClient()
		self.readoutPV = readoutPV
		self.inputNames = []
		self.extraNames = [columnName]
		self.outputFormat = ["%.5g"]
		self.integrating = False
		self.collectionTime = 1.0

	def collectData(self):
		integrationTime = self.collectionTime
		self.ca.caput(self.pvPrefix + ":PERIOD",integrationTime)
		#self.ca.caput(self.pvPrefix + ":MODE","Trigger")
		self.integrating = True
		#self.ca.caputWait(self.pvPrefix + ":SOFTTRIGGER.VAL",1)
		self.ca.caput(self.pvPrefix + ":SOFTTRIGGER.VAL",1)
		time.sleep(0.25)

	def getStatus(self):
		if self.integrating == False:
			return 0
		
		triggering = str(self.ca.caget(self.pvPrefix + ":SOFTTRIGGER.VAL"))
		if triggering == "Done" or triggering == "0":
			self.integrating = False

		if self.integrating :
			return 1
		
		return 0

	def readout(self):
		return [float(self.ca.caget(self.readoutPV))]

	def getDescription(self):
		return " "

	def getDetectorID(self):
		return " "

	def getDetectorType(self):
		return " "
	
	def createsOwnFiles(self):
		return False
	
d1 = adcmonitor("d1","BL20I-DI-ADC-01","BL20I-DI-PHDGN-01:DIODE:I","d1")
d3plus = adcmonitor("d3plus","BL20I-DI-ADC-01","BL20I-DI-PHDGN-03:Y:PLUS:I","d3plus")
d3minus = adcmonitor("d3minus","BL20I-DI-ADC-01","BL20I-DI-PHDGN-03:Y:MINUS:I","d3minus")
d4  = adcmonitor("d4", "BL20I-DI-ADC-01","BL20I-DI-PHDGN-04:DIODE1:I","d4")
d5  = adcmonitor("d5", "BL20I-DI-ADC-01","BL20I-DI-PHDGN-05:DIODE:I","d5")
d9  = adcmonitor("d9", "BL20I-DI-ADC-02","BL20I-DI-PHDGN-09:DIODE:I","d9")
d10 = adcmonitor("d10","BL20I-DI-ADC-02","BL20I-DI-PHDGN-10:DIODE:I","d10")