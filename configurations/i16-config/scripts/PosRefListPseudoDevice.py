class PosRefListPD(PseudoDevice):
	'''Create PD for moving to reflections'''
	def __init__(self, name, reflectionfilelink, help=None):
		self.setName(name);
		self.setInputNames(['reflection'])
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		#self.setExtraNames([name]);
		self.Units=['deg','deg']
		self.setExtraNames(['kphi','k','ktheta','delta','energy'])
		self.setOutputFormat(['%s','%.4f','%.4f','%.4f','%.4f','%.4f'])
		self.setExtraNames(['kphi'])
		self.setOutputFormat(['%s','%.4f'])
		self.setLevel(5)
		self.link=reflectionfilelink
		self.load()
		
	def load(self):
		self.localref={}
		self.refkeys=self.link.getReflectionKeys()
		for i in range(len(self.refkeys)):
			self.localref[str(i)]=self.link.getReflection(self.refkeys[i])
	

	def getPosition(self):
		return kphi() 


	def asynchronousMoveTo(self,nref):
		str(nref)
		if  (nref in self.localref.keys())==1:
			temp=self.localref[nref]
			pos kphi temp.sixC.Kphi kap temp.sixC.Kap


	def isBusy(self):
		return BLobjects.isBusy()	


      
posref=PosRefListPD('posref',rr)
 
