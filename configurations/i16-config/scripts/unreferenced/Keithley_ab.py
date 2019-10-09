# Keithley 2000 Multimeter

from gda.epics import CAClient
from java import lang
from gda.device.scannable import PseudoDevice
from gda.device import Scannable
from time import sleep

class KeithleyMM(PseudoDevice):
	'''Device to control Keithley 2000 Multimeter \n Connect to X31'''
	def __init__(self, name, port='lab',help=None):
		if port=='lab':
			self.port='LA84R-EA-LABTS-01:ASYN4.'
		elif port=='bl':
			self.port='BL16I-EA-SPARE-03:asyn.'
		print self.port

		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames([])
		self.setExtraNames(['keithley']);
		self.setOutputFormat(['%8.8e'])
		self.setLevel(3)
		terminatorin=CAClient(self.port+'IEOS');terminatorin.configure(); terminatorin.caput("\r"); terminatorin.clearup();
		terminatorout=CAClient(self.port+'OEOS');terminatorout.configure(); terminatorout.caput("\r"); terminatorout.clearup();
	
	def setVoltageDC(self):
		print 'DC voltage mode'
		keithpv=CAClient(self.port+'AOUT');keithpv.configure(); keithpv.caput(":FUNC 'VOLT:DC'"); keithpv.clearup();
		self.setExtraNames(['DC_V'])
		
	
	def setVoltageAC(self):
		print 'AC voltage mode'
		keithpv=CAClient(self.port+'AOUT');keithpv.configure(); keithpv.caput(":FUNC 'VOLT:AC'"); keithpv.clearup();
		self.setExtraNames(['AC_V'])
		
		
	def setCurrentDC(self):
		print 'DC current mode'
		keithpv=CAClient(self.port+'AOUT');keithpv.configure(); keithpv.caput(":FUNC 'CURR:DC'"); keithpv.clearup();
		self.setExtraNames(['DC_A'])
		

	def setCurrentAC(self):
		print 'AC current mode'
		keithpv=CAClient(self.port+'AOUT');keithpv.configure(); keithpv.caput(":FUNC 'CURR:DC'"); keithpv.clearup();
		self.setExtraNames(['AC_A'])
	

	def setResistance(self):
		print 'Resistance mode'
		keithpv=CAClient(self.port+'AOUT');keithpv.configure(); keithpv.caput(":FUNC 'RES'"); keithpv.clearup();
		self.setExtraNames(['Res_ohm'])
		

	def setFrequency(self):
		print 'Frequency mode'
		keithpv=CAClient(self.port+'AOUT');keithpv.configure(); keithpv.caput(":FUNC 'FREQ'"); keithpv.clearup();
		self.setExtraNames(['Freq_Hz'])
		
		
	def setFresistance(self):
		print 'Fresistance mode'
		keithpv=CAClient(self.port+'AOUT');keithpv.configure(); keithpv.caput(":FUNC 'FRES'"); keithpv.clearup();
		self.setExtraNames(['Fres_ohm'])
		
	def setPeriod(self):
		print 'Period mode'
		keithpv=CAClient(self.port+'AOUT');keithpv.configure(); keithpv.caput(":FUNC 'PER'"); voltagepv.clearup();
		self.setExtraNames(['Period_sec'])
	
	def getPosition(self):
		pv=CAClient(self.port+'AOUT');pv.configure(); pv.caput(":DATA?"); pv.clearup();
		sleep(0.5)
		pv=CAClient(self.port+'TINP');pv.configure(); self.returnstring=pv.caget(); pv.clearup()
#		print self.returnstring
		return float(self.returnstring)

	def isBusy(self):
		return 0


#MultimLab=KeithleyMM(name="MultimLab",help="To change measurement mode type:\n keith.setVoltageDC() for DC voltage mode\n keith.setVoltageAC() for AC voltage mode\n keith.setCurrentDC() for DC current mode\n keith.setCurrentAC() for AC current mode\n keith.setFrequency() for frequency mode\n keith.setResistance() for resistance (2-wire resistance) mode\n keith.setFresistance() for fresistance (4-wire resistance) mode\n keith.setPeriod() for period mode")
keithley=KeithleyMM(name="MultimLab",port='bl',help="To change measurement mode type:\n keith.setVoltageDC() for DC voltage mode\n keith.setVoltageAC() for AC voltage mode\n keith.setCurrentDC() for DC current mode\n keith.setCurrentAC() for AC current mode\n keith.setFrequency() for frequency mode\n keith.setResistance() for resistance (2-wire resistance) mode\n keith.setFresistance() for fresistance (4-wire resistance) mode\n keith.setPeriod() for period mode")
