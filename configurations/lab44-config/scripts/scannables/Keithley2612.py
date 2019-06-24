from gda.epics import CAClient 
from time import sleep

#Create Pseudo Device for Keithley2612A System Source Meter 
#IMPORTANT: use a null modem cable and a LF terminator
#rs232 paramater in the same way as on EPICS (defauls is 9600, 8, 1, none, none)
#use a null modem cable and a LF terminator
#this class does not set up the epics panel rs232 port, so do it manually!!!! (9600, 8, 1, none, none)

class Keithley2612():
	def __init__(self, channel, function, pvBase):
		self.channel = channel
		self.strFunctionSet = ['smua.source.func','smub.source.func']
		self.strFunctionGet = ['print(smua.source.func)','print(smub.source.func)']
		self.strVoltageSet = ['smua.source.levelv','smub.source.levelv'] 
		self.strVoltageGet = ['print(smua.source.levelv)','print(smub.source.levelv)'] 
		self.strCurrentSet = ['smua.source.leveli','smub.source.leveli'] 
		self.strCurrentGet = ['print(smua.measure.i())','print(smub.measure.i())'] 
		self.strVoltageSet = ['smua.source.levelv','smub.source.levelv'] 
		self.strResistanceGet = ['print(smua.measure.r())','print(smub.measure.r())'] 
		self.strSourceSet = ['smua.source.output','smub.source.output']
		self.strVoltRangeSet = ['smua.source.rangev','smub.source.rangev']
		self.chIn=CAClient(pvBase + "TINP")
		self.chIn.configure()
		self.chOut=CAClient(pvBase + "AOUT")
		self.chOut.configure()
		self.setFunction(function)

		print('-> setting Serial port:  '+pvBase+ ' for the Keithley 2621A source meter:' )
		print "Baud = 9600, bit = 8, bitstop = 1, parity = None, Flow Control = None"
		print "Output Terminator \\n, input terminator \\n"
		strcom = pvBase[0:23]
		self.chOut.caput(strcom+"BAUD", "9600")
		sleep(0.5)
		self.chOut.caput(strcom+"DBIT", "8")
		sleep(0.5)
		self.chOut.caput(strcom+"SBIT","1")
		sleep(0.5)
		self.chOut.caput(strcom+"PRTY","None")
		sleep(0.5)
		self.chOut.caput(strcom+"FCTL","None")
		sleep(0.5)
		self.chOut.caput(strcom+"OEOS","\n")
		sleep(0.5)
		self.chOut.caput(strcom+"IEOS","\n")
		print "-> serial port configured"

	def send(self, strCom):
		self.chOut.caput(strCom)
		sleep(0.2)

	def turnOn(self):
		strOut = self.strSourceSet[self.channel] + '=1'
		self.chOut.caput(strOut)
		sleep(0.2)
		
	def turnOff(self):
		strOut = self.strSourceSet[self.channel] + '=0'
		self.chOut.caput(strOut)

	def getFunction(self):
		return int(self._getFloat(self.strFunctionGet[self.channel]), 'Function')

	def getVoltage(self):
		return self._getFloat(self.strVoltageGet[self.channel], 'Voltage')

	def getResistance(self):
		return self._getFloat(self.strResistanceGet[self.channel], 'Resistance')

	def getCurrent(self):
		return self._getFloat(self.strCurrentGet[self.channel], 'Current')

	def _getFloat(self, request, desc):
		self.chOut.caput(request)
		sleep(0.2)
		ret=self.chIn.caget() 
		try:
			return float(ret)
		except:
			raise ValueError('Unable to parse %s float from "%s"' % (desc, ret))

	def setVoltage(self, v):
		strOut = self.strVoltageSet[self.channel] + '=' + str(round(v,5));
		#print "Out String: " + strOut
		self.chOut.caput(strOut)
		sleep(0.2)
		return

	def setCurrent(self, i):
		strOut = self.strCurrentSet[self.channel] + '=' + str(round(i,5));
		#print "Out String: " + strOut;
		self.chOut.caput(strOut)
		return;

	def setFunction(self,i):
		# i = 0, current source, i=1, voltage source 
		strOut = self.strFunctionSet[self.channel]+'='+str(i);
		self.chOut.caput(strOut);
		return;

#pvPatchPanelSerialPort = 'BL06J-EA-USER-01:ASYN6.'

#exec('[volt, curr, Keithley]=[None, None, None]')
#Keithley = Keithley2612(0, 1, pvPatchPanelSerialPort)
