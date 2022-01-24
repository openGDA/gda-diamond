class SParaPerpPDClass(ScannableMotionBase):
	'''
	help stuff
	'''
	def __init__(self,name,xpd,ypd,phipd,phioffset,mupd,help=None):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.xpd=xpd
		self.ypd=ypd
		self.phipd=phipd
		self.phioffset=phioffset
		self.mupd=mupd
		self.setInputNames([name])
		self.setExtraNames([]);
		self.setOutputFormat(['%.3f'])
		self.setLevel(5)

# Changed and ready to test
	def asynchronousMoveTo(self,xpos):
		self.phi=(self.phipd()+self.phioffset)*pi/180
		self.ypos=self.xpd()*sin(self.phi-self.mupd()*pi/180)+self.ypd()*cos(self.phi-self.mupd()*pi/180)
		self.xpos=xpos
		self.x=self.xpos*cos(self.phi-self.mupd()*pi/180)-self.ypos*sin(self.phi-self.mupd()*pi/180)
		self.y=self.xpos*sin(self.phi-self.mupd()*pi/180)+self.ypos*cos(self.phi-self.mupd()*pi/180)
#		self.xpd.a(self.x); self.ypd.a(self.y);
		print self.x,self.y

	def getPosition(self):
		self.phi=(self.phipd()+self.phioffset)*pi/180
		self.x=self.xpd()
		self.y=self.ypd()
		self.xpos=self.x*cos(self.phi-self.mupd()*pi/180)-self.y*sin(self.phi-self.mupd()*pi/180)
		return self.xpos
	
	def isBusy(self):
		return (self.xpd.isBusy() or self.ypd.isBusy())

	def stop(self):
		self.xpd.stop()
		self.ypd.stop()	


#sperph=SParaPerpPDClass('sperp',sx,sy,phi,90,mu,help='Sample motion perp to beam')
#sparah=SParaPerpPDClass('sperp',sx,sy,phi,0,mu,help='Sample motion parallel to beam')

sperph=SParaPerpPDClass('sperp',sx,sy,phi,90,mu,help='Sample motion perp to beam')
sparah=SParaPerpPDClass('sperp',sx,sy,phi,0,mu,help='Sample motion parallel to beam')
