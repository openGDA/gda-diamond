from java import lang
from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from time import sleep

class R2K(ScannableMotionBase):
	def __init__(self, name, link,unitstring='K'):
		self.dev=link
		self.extraNames = ['res']
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames(['Tsam','res']);
		self.setOutputFormat(['%8.8e']*2)
		self.setLevel(3)
		self.A=[5.563859,-6.404804,2.813635,-1.01185,0.299789,-0.069194,0.009109,0.001,-0.001586,0.000831]
		self.B=[42.619385,-37.941622,8.498099,-1.107799,0.117638,-0.003078,-0.006278]
		self.C=[177.509895,-126.78469,22.158399,-3.054182,0.590631,-0.124122,0.02722,-0.010308,0.001136,0.004396]

	def getPosition(self):
		tempK=0
		val=self.dev.getPosition()
		Z=log10(val)
		if val<=6341 and val>=581.7:
			self.Zl=2.72670581186
			self.Zu=3.92586240806
			self.k=((Z-self.Zl)-(self.Zu-Z))/(self.Zu-self.Zl)
			for order in range(10):
				tempK=tempK+self.A[order]*cos(order*acos(self.k))
		if val<581.7 and val>=175.2:
			self.Zl=2.20564180972
			self.Zu=2.81005333992
			self.k=((Z-self.Zl)-(self.Zu-Z))/(self.Zu-self.Zl)
			for order in range(7):
				tempK=tempK+self.B[order]*cos(order*acos(self.k))
		if val<175.2 and val>=57.75:
			self.Zl=1.75603357036
			self.Zu=2.28605345593
			self.k=((Z-self.Zl)-(self.Zu-Z))/(self.Zu-self.Zl)
			for order in range(10):
				tempK=tempK+self.C[order]*cos(order*acos(self.k))
		return [tempK,val]

	def isBusy(self):
		return self.dev.isBusy()
	

r2k=R2K('r2k',keithley)