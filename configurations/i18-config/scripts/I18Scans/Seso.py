from java.io import BufferedReader
from java.io import InputStreamReader
from java.io import PrintWriter
from java.net import Socket
from java.net import UnknownHostException
from java.lang import *
from time import sleep
from gda.device.scannable import PseudoDevice
#
#
# A class for creating a seso scannable which you can use to read x and y centroid values 
#
#
class DisplaySesoClass(PseudoDevice):
	'''Create PD to display single EPICS PV'''
	def __init__(self, name, direction, unitstring, formatstring):
		# name (displayed when you do a pos
		# direction 0 = x y = 1
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([name]);
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(6)
		self.direction = direction


	def getPosition(self):
		try:
			#sleep(4)
			sock =  Socket("172.23.118.71", 20)
			out = PrintWriter(sock.getOutputStream(), 1)
			out.print('?')
			out.flush()
			bufin = BufferedReader(InputStreamReader(sock.getInputStream()))
			instring = bufin.readLine()
			strTrim   = instring.strip()
			j = strTrim.find(",")
			if j == -1:
				strPosition = strTrim.split("  ")
			else:
				strPosition = strTrim.split(",")
			print strPosition[0],strPosition[1],len(strPosition)
			xy = [0.0,0.0]
			xy[0] = Double.parseDouble(strPosition[0])
			xy[1] = Double.parseDouble(strPosition[1])
			sock.close()
			if self.direction == 0: 
				return xy[0]
			else:
				return xy[1]
				
		except:
			print "Error connecting to and reading from seso"
			return 0.0
				
	def isBusy(self):
		return 0


sesoX=DisplaySesoClass('sesoX',0,' squares', '%.12e')
sesoY=DisplaySesoClass('sesoY',1,' squares', '%.12e')

