
#import gda
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

class EpicsCamserverConnector(ScannableMotionBase):
	"""
	This class implements the communication between EPICS and Camserver.
	It will pass a command string for interpretation by camserver, 
	and listen to the response from camserver. 

	Example usage: 
	>>>ecc = EpicsCamserverConnector("ecc")

	>>>pos ecc "command" ?
	
	PVs for Camserver communications:
	BL07I-EA-PILAT-01:GEN - write the string you want to send here
	BL07I-EA-PILAT-01:GEN:SEND - write 1 to send it to the camserver
	BL07I-EA-PILAT-01:GENIN - the reply message gets set in here
	"""

	camserverCommandPV = "BL07I-EA-PILAT-01:GEN"
	camserverWriterPV = "BL07I-EA-PILAT-01:GEN:SEND"
	camserverReaderPV = "BL07I-EA-PILAT-01:GENIN"
	
	def __init__(self,name):
		self.name = name
		self.epicsClient = CAClient("camserver")
		#self.epicsClient.configure()
		print "epicsClient: " + str(self.epicsClient)
		self.camserverCommandClient = CAClient(self.camserverWriterPV)
		print "camserverCommandClient: " + str(self.camserverCommandClient)
		self.camserverWriterClient = CAClient(self.camserverWriterPV)
		print "camserverWriterClient: " + str(self.camserverWriterClient)
		self.camserverReaderClient = CAClient(self.camserverReaderPV)
		print "camserverReaderClient: " + str(self.camserverReaderClient)
		
	def sendCommand(self, command):
		print "EpicsCamserverConnector.sendCommand(), command: " + command
		self.epicsClient.caput(self.camserverCommandPV, String2ByteArray(command))
		self.epicsClient.caput(self.camserverWriterPV, 1)
		self.result = self.epicsClient.caget(self.camserverReaderPV)
		print "result: " + self.result
		
	def sendCommand2(self, command):
		pass
		
	# put in all available camserver commands
	def callMenu(self):
		pass
	
	def callExptime(self, exptime):
		pass
	
	def menu(self):
		arr=[]
		for each in "menu":
			arr.append(ord(each))
		self.epicsClient.caput(self.camserverCommandPV, arr)
		
	def exposure(self, time):
		arr=[]
		for each in "exposure ":
			arr.append(ord(each))
		arr.append(ord(str(time)))
		self.epicsClient.caput(self.camserverCommandPV, arr)
		
		
def String2ByteArray(command):
	# 1. split into character array
	# 2. convert char to int (ascii code)
	# 3. put ascii code into array (of int)
	# 4. return the int array
	pass
	
		
def testCamserverComms():
	print "testCamserverComms"

if __name__ == '__main__':
	testCamserverComms()

		
		
