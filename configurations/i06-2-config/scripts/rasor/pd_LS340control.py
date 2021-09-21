from gda.device.scannable import ScannableMotionBase
from misc_functions import caput, caget, frange
from time import sleep

class EpicsLScontrol(ScannableMotionBase):
	'''
	self(value) - command value (pseudo-device)
	self.hrange(value) - heater range: 0=OFF, 1-5: increasing power (use 0 or 5)
	self.heater(): read only of the power of the heater
	self.control_chan(channel_string) sets control channel ('A', 'B', 'C' or 'D')
	self.pid(): read PID values
	self.pid([P,I,D]): set PID values
	'''
	def __init__(self, name, pvstring, unitstring, formatstring,ch1,ch2):
		self.setName(name);
		self.setInputNames(['Tset'])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)
		self.pvstring=pvstring
		self.ch1=ch1
		self.ch2=ch2
		self.speed=1

	def getPosition(self):
	#	sleep(1)
		Tset=float(caget(self.pvstring+'SETP'))
		return Tset

	def isBusy(self):
		return 0

	def asynchronousMoveTo(self,newT):
		caput(self.pvstring+'SETP_S',newT)

	def ramp(self,rate=None):
		'''ramp(): returns the status of the ramp \n''' \
		'''ramp([5]): set ramp ON at 5 K/min \n''' \
		'''ramp([0]): set ramp OFF'''
		if rate==None:
			caput(self.pvstring+'ASYN.AOUT','RAMP? 1')
			sleep(2)
			string = caget(self.pvstring+'ASYN.AINP')
			print 'ramp on te (on/off,K/min): ' + string
		elif len(rate)>0:
			if rate[0]>0:
				cmdstr = 'RAMP 1, 1, '+str(rate[0])
				caput(self.pvstring+'ASYN.AOUT',cmdstr)
			else:
				caput(self.pvstring+'ASYN.AOUT','RAMP 1, 0')

	def onRamp(self):
		caput(self.pvstring+'ASYN:AOUT','RAMP 1,1,'+self.speed)

	def offRamp(self):
		caput(self.pvstring+'','1,0,'+str(self.speed))

	def speed(self,speed):
		self.speed=speed

	def pid(self,xx=None):
		if xx != None:
			sleep(1)
			caput(self.pvstring+'P_S',xx[0])
			sleep(1)
			caput(self.pvstring+'I_S',xx[1])
			sleep(1)
			caput(self.pvstring+'D_S',xx[2])
			sleep(1)
			caput(self.pvstring+'P_S',xx[0])
			sleep(1)
			caput(self.pvstring+'I_S',xx[1])
			sleep(1)
			caput(self.pvstring+'D_S',xx[2])
			sleep(1)
		#	caput(self.pvstring+'ASYN.AOUT','PID '+str(x[0])+','+str(x[1])+','+str(x[2]))
		#	return caput(self.pvstring+'ASYN.AINP','PID?')
		P = caget(self.pvstring+'P')
		I = caget(self.pvstring+'I')
		D = caget(self.pvstring+'D')
		return [P,I,D]

	def hrange(self,xx=None):
		if xx!=None:
			caput(self.pvstring+'RANGE_S',xx)
			sleep(1)
		return caget(self.pvstring+'RANGE')

	def mout(self,xx=None):
		if xx != None:
			caput(self.pvstring+'MOUT_S',xx)
			sleep(1)
		return caget(self.pvstring+'MOUT')

	def heater(self):
		return caget(self.pvstring+'HTR')

	def cmod(self,xx=None):
		if xx!=None:
			caput(self.pvstring+'CMODE_S',xx)
			sleep(1)
			caget(self.pvstring+'CMODE')
		return caget(self.pvstring+'CMODE')

	def autotune(self,terange,channel):
		self.cmod(1)
		self.mout(0)
		if float(self.mout()) > 0.0:
			print "just started Warning Mout>0"
		caput(self.pvstring+'ASYN.AOUT','CSET 1,'+channel)
		caget(self.pvstring+'ASYN.AINP')
		oppid=[]
		self.cmod(4)
		temper=frange(terange[0],terange[1],terange[2])		
		if float(self.mout()) > 0.0:
			print "Switching to mode 4 set Mout>0"

		for temp in temper:
			self.asynchronousMoveTo(temp)
			print self.getPosition()
			print self.getPosition()
			sleep(2)
			status=1
			while status==1:
				if float(self.mout()) > 0.0:
					print "Warning during the tuning Mout>0"	
				caput(self.pvstring+'TUNEST')
				sleep(5)	
				status=int(caget(self.pvstring+'ASYN.AINP')[0])
#			caput(self.pvstring+'ASYN.AOUT','KRDG?'+channel)
#			sleep(1)
#			Tchant1=caget(self.pvstring+'ASYN.AINP')
#			sleep(1)
#			caput(self.pvstring+'ASYN.AOUT','KRDG?'+channel)
##			sleep(1)
#			Tchant2=caget(self.pvstring+'ASYN.AINP')
			tpid=[self.getPosition()]+self.pid()
			oppid=oppid+tpid
			print tpid
			if float(self.mout()) > 0.0:
				print "Warning Mout>0"
		self.cmod(1)
		return oppid

	def control_chan(self,channel):
		caput(self.pvstring+'ASYN.AOUT','CSET 1,'+channel)
		sleep(1)
		return caget(self.pvstring+'ASYN.AOUT')

