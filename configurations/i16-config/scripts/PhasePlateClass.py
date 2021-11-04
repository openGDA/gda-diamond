from gda.device.scannable import ScannableMotionBase
from math import pi, asin
class PPPClass(ScannableMotionBase):
	'''
	PD for operating Phase Plate Polariser
	inputs: [energy, angle_offset]
	self.calibrate() when on centre to recalculate offset
	'''
	def __init__(self, name, dspace, thpv, offsetpd, help=None):
		self.setName(name)
		self.setInputNames([name+'_energy',name+'_offset'])
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		#self.setExtraNames([name])
		self.Units=['keV','deg']
		self.setOutputFormat(['%.4f','%.5f'])
		self.setLevel(5)
		self.d=dspace
		self.c=6.19921
		self.offsetpd=offsetpd
		self.thpv=thpv
		self.en=999999

	def getPosition(self):
		self.cth=180/pi*asin(self.c/self.d/self.en)
		offset=self.thpv()-self.cth-self.offsetpd()
		return([self.en,offset])

	def asynchronousMoveTo(self,new_position):
		self.new_position=new_position
		#print new_position
		[self.en, self.offsetval]=new_position
		#print [self.en, self.offsetval]
		self.th=180/pi*asin(self.c/self.d/self.en)+self.offsetpd()+self.offsetval
		#print self.th
		self.thpv.asynchronousMoveTo(self.th)
		
	def isBusy(self):
		return self.thpv.isBusy()
	
	def stop(self):
		self.thpv.stop()

	def calibrate(self):
		self.oldoffset=self.offsetpd()
		print 'Old Offset: %.4f deg' % self.oldoffset
		self.offsetpd(self.thpv()-180/pi*asin(self.c/self.d/self.en))
		print 'New Offset: %.4f deg' % self.offsetpd()
		print 'Change in Offset: %.4f deg' % (self.offsetpd()-self.oldoffset)


		
class PPP_noE_Class(ScannableMotionBase):
	'''
	PD for operating Phase Plate Polariser
	inputs: [energy, angle_offset]
	self.calibrate() when on centre to recalculate offset
	'''
	def __init__(self, name, dspace, thpv, offsetpd, help=None):
		self.setName(name)
		self.setInputNames(['ppp_offset'])
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setExtraNames(['ppp_energy'])
		self.Units=['keV','deg']
		self.setOutputFormat(['%.4f','%.5f'])
		self.setLevel(5)
		self.d=dspace
		self.c=6.19921
		self.offsetpd=offsetpd
		self.thpv=thpv
		self.en=en()

	def getPosition(self):
		self.cth=180/pi*asin(self.c/self.d/self.en)
		offset=self.thpv()-self.cth-self.offsetpd()
		return([self.en,offset])

	def asynchronousMoveTo(self,new_position):
		self.new_position=new_position
		#print new_position
		self.offsetval=new_position
		#print [self.en, self.offsetval]
		self.en=en()
		self.th=180/pi*asin(self.c/self.d/self.en)+self.offsetpd()+self.offsetval
		#print self.th
		self.thpv.asynchronousMoveTo(self.th)
		
	def isBusy(self):
		return self.thpv.isBusy()
	
	def stop(self):
		self.thpv.stop()

	def calibrate(self):
		self.oldoffset=self.offsetpd()
		print 'Old Offset: %.4f deg' % self.oldoffset
		self.offsetpd(self.thpv()-180/pi*asin(self.c/self.d/self.en))
		print 'New Offset: %.4f deg' % self.offsetpd()
		print 'Change in Offset: %.4f deg' % (self.offsetpd()-self.oldoffset)
