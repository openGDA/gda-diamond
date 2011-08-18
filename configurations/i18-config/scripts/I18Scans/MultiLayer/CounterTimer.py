import gda.device.CounterTimer;
import gda.device.Detector;
import gda.device.DeviceException;
from gda.device.detector.analyser import EpicsMCA
from  gda.device.detector.analyser import EpicsMCARegionOfInterest
from gda.jython.scannable import ScannableBase
from java.lang import *
from jarray import *
#
#
# Represents a Tfg and EpicsMCA acting as a CounterTimer combination. Since the
# Tfg will generally also be part of a TfgScaler combination there is a slave
# mode. In this mode methods which set things on the Tfg do nothing.
#
# 
class MultiCounterTimer:

	def __init__(self):
		self.ic=[]
		self.ic.append(ScriptedEpicsMca("BL18I-DI-PHDGN-07:B:I:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-IONC-02:I:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-IONC-01:I:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I1:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I2:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I3:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I1:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I2:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I3:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I4:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I5:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I6:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I7:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I8:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I9:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I10:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I11:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I12:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I13:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I14:MCA"))
		self.ic.append(ScriptedEpicsMca("BL18I-EA-DET-02:I15:MCA"))
		self.adc1=ip330("BL18I-EA-IP330-01")
		self.adc2=ip330("BL18I-EA-IP330-02")
		self.das=finder.find("daserver")
		self.collectionTime=1000.0
		self.setCollectionTime(self.collectionTime)	

	#
	# Set collection time
	# 1.1 * collection so we collect past the edge of a pulse
	#
	def setCollectionTime(self,collectionTime):
		self.collectionTime=collectionTime
		# Get the size of the channel (in time)
		for i in range(len(self.ic)):
			self.ic[i].setCollectionTime(collectionTime)

	def collectData(self):
		for i in range(len(self.ic)):
			self.ic[i].eraseAndStart()
		sleep(2.0)	
		values=[0.0]*len(self.ic)
		sum=0.0
		for i in range(3,len(self.ic)):
			values[i]=self.ic[i].readout()
		for i in range(3):
			values[i]=values[i]-(self.ic[i].getNoOfChannels()*32768)

		return values

	
	#
	# Collect data
	#
	def collectDataOld(self):


		# Start the tfg
		self.das.sendCommand("tfg init")
		command = "tfg setup-groups cycles 1 \n 1 0.01 %f 0 1 0 0 \n -1 0 0 0 0 0 0"  %((self.collectionTime/1000.0))
		self.das.sendCommand(command)
		self.clearAndPrepare()
		self.das.sendCommand("tfg start")
		while (self.das.sendCommand("tfg read status") == 'RUNNING'):
			sleep(0.1)
			pass
		# just have to sleep to ensure the roi's are ready
		sleep(2.0)

		values=[0.0]*len(self.ic)
		for i in range(len(self.ic)):
			values[i]=self.ic[i].readout()

		for i in range(3):
			values[i]=values[i]-(self.ic[i].getNoOfChannels()*32768)

		return values
	
					

	def clearAndPrepare(self):
		# Disable ADC from responding to trigger.
		self.adc1.disable()
		self.adc2.disable()

		# Loop over each MCA and press the button.
		for i in range(len(self.ic)):
			self.ic[i].eraseAndStart()


		# Reset ADC trigger mode
		self.adc1.setBurstCont()
		self.adc2.setBurstCont()

		#
		# Now waits for a trigger
		#
	def closeAll(self):
		for i in range(len(self.ic)):
			self.ic[i].closeAll()
		


