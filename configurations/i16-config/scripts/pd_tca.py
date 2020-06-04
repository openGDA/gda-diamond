from gda.device.scannable import ScannableMotionBase

class tcasca(ScannableMotionBase):
	def __init__(self, name,formatstring,link,unitstring,number):
		self.setName(name);
		self.setLevel(3)
		self.link=link
		self.setInputNames([name+'_low',name+'_hi'])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring,formatstring])
		self.number=number
		
	def asynchronousMoveTo(self,new_position):
		if new_position[0] >= new_position[1]:
			print "error: wrong values"
		else:
			self.link.setProperty('SCA'+self.number+'_LOW',new_position[0])
			self.link.setProperty('SCA'+self.number+'_HI',new_position[1])


	def isBusy(self):
		return 0

	def getPosition(self):
		scalow=self.link.getProperty('SCA'+self.number+'_LOW')
		scahi=self.link.getProperty('SCA'+self.number+'_HI')
		return [float(scalow), float(scahi)]

	def on(self):
		stringa='SCA'+self.number+'_GATE'
		self.link.setProperty(stringa,1)
		return self.link.getProperty(stringa)


	def off(self):
		stringa='SCA'+self.number+'_GATE'
		self.link.setProperty(stringa,0)
		return self.link.getProperty(stringa)

