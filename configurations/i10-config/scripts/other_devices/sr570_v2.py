""" #########################################################################################################
Device commands for communicating with a Stanford Research SR570 current amplifier

Communication is only one direction
Can be used to set the sensitivity

David Burn - 1/4/16

######################################################################################################### """


from other_devices.rs232Device import rs232Device
import time

class sr570Device(rs232Device):
	def __init__(self, branch, port):
		rs232Device.__init__(self, branch, port)
		self.setOutputTerminator("\n")
		self.sens = None
		
		self.maxOutput = 5.0
		self.minOutput = 0.5

	def setSens(self, value):
		if value >= 1 or value == 0:
			pass
		else:
			value = self.lookup(value)

		self.sens = value
		self.write("SENS "+str(value))
		return True

	def getSens(self):
		return self.sens
	
	def getSensValue(self):
		if self.sens == None:
			return 0.0
		else:
			return self.lookupB(self.sens)
	
	def increaseSens(self):
		if self.getSens() == 0:
			raise ValueError('SR current amplifier cannot increase sens, already on maximum sensitivity') 
			#raise Exception('SR current amplifier on maximum sensitivity')
		newSens = self.getSens() - 3
		if newSens < 0: newSens = 0
		self.setSens(newSens)
		time.sleep(0.5)		#time to allow current amplifier to react (there is no readback)
		
	def decreaseSens(self):
		if self.getSens() == 27:
			raise ValueError('SR current amplifier cannot decrease sens, already on minimum sensitivity') 
			#raise Exception('SR current amplifier on minimum sensitivity')
		newSens = self.getSens() + 1
		if newSens > 27: newSens = 27
		self.setSens(newSens)
		time.sleep(0.5)		#time to allow current amplifier to react (there is no readback)

	def lookupB(self,var):   #=self.getSens()
		values = [1e-12, 2e-12, 5e-12, 1e-11, 2e-11, 5e-11, 1e-10, 2e-10, 5e-10, 1e-9, 2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7,2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4, 1e-3]
		return values[int(var)]

	def lookup(self,mag):
		if mag == 1e-12: return 0
		elif mag == 2e-12: return 1
		elif mag == 5e-12: return 2
		elif mag == 1e-11: return 3
		elif mag == 2e-11: return 4
		elif mag == 5e-11: return 5
		elif mag == 1e-10: return 6
		elif mag ==  2e-10: return 7
		elif mag == 5e-10: return 8
		elif mag == 1e-9: return 9
		elif mag == 2e-9: return 10
		elif mag == 5e-9: return 11
		elif mag == 1e-8: return 12
		elif mag == 2e-8: return 13
		elif mag == 5e-8: return 14
		elif mag == 1e-7: return 15
		elif mag ==  2e-7: return 16
		elif mag == 5e-7: return 17
		elif mag == 1e-6: return 18
		elif mag == 2e-6: return 19
		elif mag == 5e-6: return 20
		elif mag == 1e-5: return 21
		elif mag == 2e-5: return 22
		elif mag == 5e-5: return 23
		elif mag == 1e-4: return 24
		elif mag ==  2e-4: return 25
		elif mag == 5e-4: return 26
		elif mag == 1e-3: return 27
		else:
			print "incorrect setting: default to 1 pA"
			return 0
