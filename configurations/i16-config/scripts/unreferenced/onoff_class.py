from gda.device.scannable import ScannableMotionBase
import time

class PD_onoff(ScannableMotionBase):
	'''
	onoff device
	'''
	def __init__(self, name, onoffdevice, help=None):
		self.setName(name);
		self.onoffpd=onoffdevice
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames([name])
		#self.Units=[unitstring]
		self.setOutputFormat(['%.3f'])
		self.setLevel(9)
		self.count_time=0
		self.end_time=0
		self.on_val=1
		self.off_val=0
	
	def getPosition(self):
		return self.count_time

	def asynchronousMoveTo(self,new_position):
		self.count_time=new_position
		self.end_time=time.clock()+new_position
		self.onoffpd.asynchronousMoveTo(self.on_val)
		while time.clock()<self.end_time:
			pass
		self.onoffpd.asynchronousMoveTo(self.off_val)
		sleep(1.0)

	def isBusy(self):
		return 0



#	def asynchronousMoveTo(self,new_position):
#		self.end_time=time.clock()+new_position
#		self.onoffpd.asynchronousMoveTo(self.on_val)
#		self.start_time=self.end_time-new_position
#	def isBusy(self):
#		if time.clock()>self.end_time:
#			self.onoffpd.asynchronousMoveTo(self.off_val)
#			return 0				
#		else:
#			return 1

an=PD_onoff('Exp_time',x1)