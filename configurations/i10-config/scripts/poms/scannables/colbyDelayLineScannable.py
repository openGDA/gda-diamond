""" #########################################################################################################
Scannable for communicating with a Colby Delay Line PDL-100A-10ns with a socket connection


Network settings were input manually to the colby delay line over rs232 connection:
gateway ip:   172.23.110.254
network mask: 255.255.255.0
dhcp:         on

delay line has picked up ip address on I10:	172.23.110.130 and uses port: 1234

David Burn - 8/8/17

######################################################################################################### """


from gda.device.scannable import ScannableMotionBase
from java.lang import Thread, Runnable
import socket


class colbyDelayLineScannable(ScannableMotionBase):
	def __init__(self,name,host):
		self.name = name
		self.setInputNames(['delay'])
		self.setExtraNames([])
		self.setOutputFormat(["%3d"])
		self.Units = ['ps']
		
		self.host = host
		
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((self.host, 1234))
			self.sock.send(str.encode("*IDN?\n"))
			self.sock.recv(2056)
		except:
			print "No connection to Colby Delay Line"

		self.iambusy = 0 
	


	def getPosition(self):
		tries = 0
		while True:
			try:	
				self.sock.send(str.encode("DEL?\n"))
				response = self.sock.recv(2056)
				break
			except (socket.error, socket.timeout):
				tries = tries + 1
				if tries == 3: raise Exception('Colby Delay Line error', 'Failed connection to colby delay line after 3 attempts')
				self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.sock.connect((self.host, 1234))
		return int(float(response) / 1e-12)


	def asynchronousMoveTo(self, delay):
		self.iambusy = 1
		tries = 0
		while True:
			try:	
				self.sock.send("DEL %03d\n" % delay)
				self.sock.send(str.encode("*OPC?\n")) 
				response = self.sock.recv(2056)   # wait for operation complete message
				break
			except (socket.error, socket.timeout):
				tries = tries + 1
				if tries == 3: raise Exception('Colby Delay Line error', 'Failed connection to colby delay line after 3 attempts')
				self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.sock.connect((self.host, 1234))
		self.iambusy = 0	
		
	
	def isBusy(self):
		return self.iambusy


	def atScanEnd(self):
		pass
		#self.moveTo(0)
