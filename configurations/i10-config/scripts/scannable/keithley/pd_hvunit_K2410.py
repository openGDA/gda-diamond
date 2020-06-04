from gda.device.scannable import ScannableMotionBase
from time import sleep
from gda.epics import CAClient

class hvunit_K2410(ScannableMotionBase):
	'''Device to set/read voltage and current on the Keithley 2410 unit, 
	   the inizialization sets the unit to operate as V generator, and current reader.
	   It also sets the current limit to 2 mA, if the currents limit is turned above this value or the auto key 
	   is switched
	   the software will give a warning each time the getPosition or an asinchronousmoveto are operated    
	   To instantiate:	
              hv=hvunit_K2410('hv','BL16I-EA-K2400-01:','Volt','%6.3f')
	   format string:
	   hv.setOutputFormat(['%6.3f']*2+['%6.3e']*3)	 
	'''
	def __init__(self, name, pvkeithley,  unitstring, formatstring,help=None):
		self.setName(name);
		self.setInputNames(['Vdem'])
		self.setExtraNames(['Vmes','Cmes','Rmes','Pmes']);
		self.setOutputFormat([formatstring]*5)
		
		self.unitstring=unitstring
		self.setLevel(9)


		self.readcur=CAClient(pvkeithley+'I')
		self.readcur.configure()
		self.readres=CAClient(pvkeithley+'R')
		self.readres.configure()
		self.readvol=CAClient(pvkeithley+'V')
		self.readvol.configure()

		self.sourcelev=CAClient(pvkeithley+'SOUR_LEV')
		self.sourcelev.configure()

		self.sourcemode=CAClient(pvkeithley+'SOUR_MODE')
		self.sourcemode.configure()
		
		self.sourcefunc=CAClient(pvkeithley+'SOUR_FUNC')
		self.sourcefunc.configure()
		
		############### Added By Me ###########################
		
		self.sourcerange=CAClient(pvkeithley+'SOUR_RANG')
		self.sourcerange.configure()
		
		self.command=CAClient(pvkeithley+'COMMAND')
		self.command.configure()
		
		self.response=CAClient(pvkeithley+'RESPONSE')
		self.response.configure()
		

		###########################################################

		self.sourVorC=CAClient(pvkeithley+'SOTX')
		self.sourVorC.configure()


		self.sensVorC=CAClient(pvkeithley+'SETX')
		self.sensVorC.configure()


		self.sensfunc=CAClient(pvkeithley+'SENS_FUNC')
		self.sensfunc.configure()


		self.sensprot=CAClient(pvkeithley+'SENS_PROT')
		self.sensprot.configure()


		self.sensmeasrange=CAClient(pvkeithley+'SENS_RANG')
		self.sensmeasrange.configure()
		

		self.sensrangeauto=CAClient(pvkeithley+'SENS_RANG_AUTO')
		self.sensrangeauto.configure()

		self.souroutp=CAClient(pvkeithley+'OUTP')
		self.souroutp.configure()

		self.reset()

		self.__doc__+='Units for current: '+self.unitstring
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help


	def reset(self):
		self.setSourceMode(0) # 0 set source to V mode, 1 set to curr
		self.setSourceFunc(0) # 0 set source to V mode, 1 set to curr
		self.setSourVorC(0) # 0 set source to V mode, 1 set to curr
		self.setSensVorC(0) # 0 set source to V mode, 1 set to curr
		self.setSensFunc(1) # 0 set sense to V mode, 1 set to curr
		#self.setSensProt(5E-6) # protection to 1mA
		self.setSensMeasRange(1100.0)
		self.setSourceRange(1100)#######delete if problem (testing)
		self.setSensAutoRange(0) 

	def getPosition(self):
		Vdem=float(self.sourcelev.caget())
		Vmes=float(self.readvol.caget())
		Imes=float(self.readcur.caget())
		return [Vdem,Vmes,Imes,Vmes/Imes, Vmes*Imes]

	def asynchronousMoveTo(self,new_position):
		if self.status() == '1':
			self.sourcelev.caput(new_position)
		else:
			print 'First turn the output on using:  '+self.name+".ON()"

	def isBusy(self):
		if abs(float(self.sourcelev.caget()) - float(self.readvol.caget())) < 1e-3:
			return 0
		else:
			return 1

	def setSourceFunc(self,sour_func):
		# 0 set source to V mode, 1 set to curr mode
		self.sourcefunc.caput(sour_func)

	def getSourceFunc(self):
		return self.sourcefunc.caget()

	def setSourceMode(self,sour_mode):
		# 0 set source to V mode, 1 set to curr mode
		self.sourcemode.caput(sour_mode)
		
	############### Added By Gareth ###########################
		
	def setSourceRange(self,sour_range):
		# Up to 1100 V set source to V mode
		self.sourcerange.caput(sour_range)
			
	###########################################################

	def getSourceMode(self):
		return self.sourcemode.caget()


	def setSourVorC(self,VorC):
		# 0 set input to V mode, 1 set to curr mode
		self.sourVorC.caput(VorC)

	def getSourVorC(self):
		return self.sourVorC.caget()

	def ON(self):
		self.souroutp.caput(1)

	def OFF(self):
		self.souroutp.caput(0)
	
	def status(self):
		return self.souroutp.caget()

# sensor functions

	def setSensVorC(self,VorC):
		# 0 set input to V mode, 1 set to curr mode
		self.sensVorC.caput(VorC)

	def getSensVorC(self):
		return self.sensVorC.caget()

	def setSensFunc(self,sensfunc):
		# 0 set input to V mode, 1 set to curr mode
		self.sensfunc.caput(sensfunc)

	def setSensProt(self,sensprot):
		# 0 set input to V mode, 1 set to curr mode
		self.sensprot.caput(sensprot)

	def getSensFunc(self):
		return float(self.sensprot.caget())

	def setSensMeasRange(self,sensrange):
		# 0 set input to V mode, 1 set to curr mode
		self.sensmeasrange.caput(sensrange)

	def getSensMeasRange(self):
		return float(self.sensmeasrange.caget())


	def setSensAutoRange(self,autorange):
		# 0 set input to man, 1 set to auto
		self.sensrangeauto.caput(autorange)

	def getSensAutoRange(self):
		# 0 set input to man, 1 set to auto
		return self.sensrangeauto.caget()
	
	def setCurrProt(self,value):
		self.command.caput(':SENS:CURR:PROT:LEV'+' '+str(value))
		sleep(1)
		self.command.caput(':SENS:CURR:PROT:LEV'+'?')
	
	def getCurrProt(self):
		self.command.caput(':SENS:CURR:PROT:LEV'+'?')
		sleep(1)
		return self.response.caget()
		

class currentunit(hvunit_K2410):
	'''
	modified version of hvunit_K2410 class
	this version always returns 0 for isBusy status
	current=currentunit('current','BL16I-EA-K2400-01:','A','%6.3f')
	'''
	def isBusy(self):
		return 0


