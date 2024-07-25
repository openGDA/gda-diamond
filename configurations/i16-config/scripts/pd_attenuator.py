from gda.device.scannable import ScannableMotionBase
from inttobin import int2bin

class Atten(ScannableMotionBase):

	def __init__(self,name,FoilList):
		self.setName(name)
		self.setInputNames(["Atten"])
		self.setExtraNames(["Transmission"])
		self.setOutputFormat(['%4.6f','%4.10f'])
		self.foils = FoilList
		self.Position = [0]*len(FoilList)
		self.bin=None
		#(robw- can fail if bad energy value) self.getPosition()

	def getTransmission(self,energy=None,numero=None):
		positions = self.Position
		if numero != None:
			numero= int2bin(int(numero))
			for k in range(len(positions)):
				positions[k] = int(numero[k])
		self.transmission = 1.
		for k in range(len(self.foils)):
			if positions[k]==1:
				self.transmission = self.transmission*self.foils[k].getTransmission(energy)
		return self.transmission

	def getPosition(self,energy=None):
		if self.bin is None:
			self.bin = 0
			for k in range(len(self.foils)):

				self.Position[k] = self.foils[k]()[0]
				if self.Position[k]==1:
					self.bin = self.bin+2**k
		else:
			pass
		self.getTransmission()
		return [float(self.bin), self.transmission]

	def asynchronousMoveTo(self,numero):
		self.bin=None
		stringa=int2bin(int(numero))
		if int(numero)>=2**len(self.foils):
			print "Error: number too high"
			return
		if len(stringa) != len(self.foils):
			print "Error: wrong length of input string"
		else:
			#To prevent damage, all insertions must be done before any removals
			for k in range(len(self.foils)):
				if stringa[k]=='1':
					try:
						self.foils[len(self.foils)-1-k](1)
					except:
						print "Error: foil [%d] did not move" %k
			for k in range(len(self.foils)):
				if stringa[k]=='0':
					try:
						self.foils[len(self.foils)-1-k](0)
					except:
						print "Error: foil [%d] did not move" %k

	def isBusy(self):
		for foil in self.foils :
			if foil.isBusy() :
				return True
		return False
