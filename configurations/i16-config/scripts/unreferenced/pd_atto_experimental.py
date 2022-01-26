from gda.device.scannable import ScannableMotionBase
from time import sleep


class AttoClass(ScannableMotionBase):
	'''
	Experimental scannable attocube class
	'''
	def __init__(self, name, pvinstring, pvtweaksize, pvtweakpos, pvtweakneg, unitstring, formatstring):
		self.setName(name);
		if help is not None:
			print self.__doc__
			print type(self.__doc__)
			print help
			print type(help)
			self.__doc__+='\nHelp specific to '+self.name+':\n'+str(help)
		self.setInputNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(5)

		self.getpos=CAClient(pvinstring)
		self.getpos.configure()
		self.tweaksize=CAClient(pvtweaksize)
		self.tweaksize.configure()
		self.tweakpos=CAClient(pvtweakpos)
		self.tweakpos.configure()
		self.tweakneg=CAClient(pvtweakneg)
		self.tweakneg.configure()

	def getPosition(self):
		#print 'Returned position sring: '+self.outcli.caget()
		#print 'twsize', float(self.tweaksize.caget())
		#print 'pos', float(self.getpos.caget())
		return float(self.getpos.caget())

	def asynchronousMoveTo(self,new_position):
		ntweaks=int(round(new_position-self.getPosition())/float(self.tweaksize.caget()))
		#print 'need tweaks:', ntweaks
		if ntweaks>0:
			for i in range(ntweaks):
				self.tweakpos.caput(1)
				sleep(.25)
		else:
			for i in range(-ntweaks):
				self.tweakneg.caput(1)
				sleep(.25)	

	def isBusy(self):
		return 0

att1_1=AttoClass('att1_1', 'BL16I-EA-ANC-01:M1:POS', 'BL16I-EA-ANC-01:M1:TWSIZE', 'BL16I-EA-ANC-01:M1:TWPOS.PROC', 'BL16I-EA-ANC-01:M1:TWNEG.PROC','nm','%.0f')
att1_2=AttoClass('att1_2', 'BL16I-EA-ANC-01:M2:POS', 'BL16I-EA-ANC-01:M2:TWSIZE', 'BL16I-EA-ANC-01:M2:TWPOS.PROC', 'BL16I-EA-ANC-01:M2:TWNEG.PROC','nm','%.0f')
att1_3=AttoClass('att1_3', 'BL16I-EA-ANC-01:M3:POS', 'BL16I-EA-ANC-01:M3:TWSIZE', 'BL16I-EA-ANC-01:M3:TWPOS.PROC', 'BL16I-EA-ANC-01:M3:TWNEG.PROC','nm','%.0f')

att2_1=AttoClass('att2_1', 'BL16I-EA-ANC-02:M1:POS', 'BL16I-EA-ANC-02:M1:TWSIZE', 'BL16I-EA-ANC-02:M1:TWPOS.PROC', 'BL16I-EA-ANC-02:M1:TWNEG.PROC','nm','%.0f')
att2_2=AttoClass('att2_2', 'BL16I-EA-ANC-02:M2:POS', 'BL16I-EA-ANC-02:M2:TWSIZE', 'BL16I-EA-ANC-02:M2:TWPOS.PROC', 'BL16I-EA-ANC-02:M2:TWNEG.PROC','nm','%.0f')
att2_3=AttoClass('att2_3', 'BL16I-EA-ANC-02:M3:POS', 'BL16I-EA-ANC-02:M3:TWSIZE', 'BL16I-EA-ANC-02:M3:TWPOS.PROC', 'BL16I-EA-ANC-02:M3:TWNEG.PROC','nm','%.0f')

att3_1=AttoClass('att3_1', 'BL16I-EA-ANC-03:M1:POS', 'BL16I-EA-ANC-03:M1:TWSIZE', 'BL16I-EA-ANC-03:M1:TWPOS.PROC', 'BL16I-EA-ANC-03:M1:TWNEG.PROC','nm','%.0f')
att3_2=AttoClass('att3_2', 'BL16I-EA-ANC-03:M2:POS', 'BL16I-EA-ANC-03:M2:TWSIZE', 'BL16I-EA-ANC-03:M2:TWPOS.PROC', 'BL16I-EA-ANC-03:M2:TWNEG.PROC','nm','%.0f')
att3_3=AttoClass('att3_3', 'BL16I-EA-ANC-03:M3:POS', 'BL16I-EA-ANC-03:M3:TWSIZE', 'BL16I-EA-ANC-03:M3:TWPOS.PROC', 'BL16I-EA-ANC-03:M3:TWNEG.PROC','nm','%.0f')


#att3_3=AttoClass('att3_3', 'BL16I-EA-ANC-03:M3:POS', 'BL16I-EA-ANC-03:M3:TWSIZE', 'BL16I-EA-ANC-03:M3:TWPOS.PROC', 'BL16I-EA-ANC-03:M3:TWNEG.PROC','nm','%.0f')

