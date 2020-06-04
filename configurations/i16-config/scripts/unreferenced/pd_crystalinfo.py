#from gda.device.scannable import ScannableMotionBase



class CrystalInfo():



	def inizializza(self,name, unitstring,formatstring,link1,link2,help=None):
		self.setName(name);
		self.setInputNames([])
		ubnames=['UB11','UB12','UB13','UB21','UB22','UB23','UB31','UB32','UB33']
		lattnames=['a','b','c','alp','bet','gam']
		self.setExtraNames(ubnames+lattnames);
		self.setOutputFormat([formatstring]*15)
		
		self.unitstring=unitstring
		self.setLevel(9)
		self.link1=link1
		self.link2=link2


	

	
	
	def getPosition(self):
		MatriceUB=self.link1.getUB()
		lattice=self.link2.getLattice()
		return MatriceUB+lattice


	def isBusy(self):
		return 0 

#Xtalinfo=("pd_crystalinfo")
#Xtalinfo('xtal','A','7.5%f',ub,cr)