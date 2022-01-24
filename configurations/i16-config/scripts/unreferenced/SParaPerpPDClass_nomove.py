class SParaPerpPDClassnomove(ScannableMotionBase):
	'''
	help stuff
	'''
	def __init__(self,name,xpd,ypd,phipd,phioffset,help=None):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.xpd=xpd
		self.ypd=ypd
		self.phipd=phipd
		self.phioffset=phioffset
		self.setInputNames([name])
		self.setExtraNames([]);
		self.setOutputFormat(['%.3f'])
		self.setLevel(5)

# Changed and ready to test
	def asynchronousMoveTo(self,xpos):
		self.phi=(self.phipd()+self.phioffset)*pi/180
		self.ypos=self.xpd()*sin(self.phi)+self.ypd()*cos(self.phi)
		self.xpos=xpos
		self.x=self.xpos*cos(self.phi)-self.ypos*sin(self.phi)
		self.y=self.xpos*sin(self.phi)+self.ypos*cos(self.phi)
		self.xpd.a(self.x); self.ypd.a(self.y);

	def getPosition(self):
		self.phi=(self.phipd()+self.phioffset)*pi/180
		self.x=self.xpd()
		self.y=self.ypd()
		self.xpos=self.x*cos(self.phi)-self.y*sin(self.phi)
		return self.xpos
	
	def isBusy(self):
		return (self.xpd.isBusy() or self.ypd.isBusy())

	def stop(self):
		self.xpd.stop()
		self.ypd.stop()	

	def calcpos(self,xpos):
		self.phi=(self.phipd()+self.phioffset)*pi/180
		self.ypos=self.xpd()*sin(self.phi)+self.ypd()*cos(self.phi)
		self.xpos=xpos
		self.x=self.xpos*cos(self.phi)-self.ypos*sin(self.phi)
		self.y=self.xpos*sin(self.phi)+self.ypos*cos(self.phi)
#		self.xpd.a(self.x); self.ypd.a(self.y);
		return [self.x,self.y] 


sperp_nomove=SParaPerpPDClassnomove('sperpnm',sx,sy,phi,90,help='Sample motion perp to beam')
spara_nomove=SParaPerpPDClassnomove('sparanm',sx,sy,phi,0,help='Sample motion parallel to beam')
