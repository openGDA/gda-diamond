from gda.epics import CAClient 
from gda.device.scannable import PseudoDevice

class Struck_with_fastshutter(PseudoDevice):
	'''
	counter timer with fast shutter
	'''
	def __init__(self, name, struck_pd, shutter_pd):
		self.setName(name)
		self.struck_pd=struck_pd
		self.shutter_pd=shutter_pd
		self.setInputNames(self.struck_pd.getInputNames())
		self.setExtraNames(self.struck_pd.getExtraNames())
		self.setOutputFormat(self.struck_pd.getOutputFormat())
		self.setLevel(self.struck_pd.getLevel())
	
	def getPosition(self):
		return self.struck_pd.getPosition()

	def isBusy(self):
		return self.struck_pd.isBusy()
			
	def asynchronousMoveTo(self,new_position):
		self.shutter_pd(1)
		#sleep(.05) #fast shutter
		#XIA shutter .25 not quite enough 0.3 OK
		sleep(.4)
		self.struck_pd(new_position)
		self.shutter_pd(0)

	def stop(self):
		try:		
			self.struck_pd.clock.caput("0")
		except:
			print "Struck::stop failure"


class ADC_with_fastshutter(PseudoDevice):
	'''
	adc (diode etc) with fast shutter
	'''
	def __init__(self, name, adc_pd, shutter_pd):
		self.setName(name)
		self.adc_pd=adc_pd
		self.shutter_pd=shutter_pd
		self.setInputNames(self.adc_pd.getInputNames())
		self.setExtraNames(self.adc_pd.getExtraNames())
		self.setOutputFormat(self.adc_pd.getOutputFormat())
		self.setLevel(self.adc_pd.getLevel())
		self.delay_before_reading=0.5
	
	def getPosition(self):
		self.shutter_pd(1)
		sleep(self.delay_before_reading)
		self.adc_signal=self.adc_pd()
		self.shutter_pd(0)
		return self.adc_signal

	def isBusy(self):
		return 0
			



ts=Struck_with_fastshutter('Struck_with_fastshutter',t,x1)
diodes=ADC_with_fastshutter('diode_with_fastshutter',diode,x1)
