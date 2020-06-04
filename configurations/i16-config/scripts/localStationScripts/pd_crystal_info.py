from gda.device.scannable import ScannableMotionBase

class crystalinfo(ScannableMotionBase):
	def __init__(self,name, unitstring,formatstring,link1,link2,help=None):
		self.setName(name);
		self.setInputNames([])
		ubnames=['UB11','UB12','UB13','UB21','UB22','UB23','UB31','UB32','UB33']
		lattnames=['a','b','c','alpha1','alpha2','alpha3']
		self.setExtraNames(ubnames+lattnames);
		self.setOutputFormat([formatstring]*15)
		
		self.unitstring=unitstring

		self.setLevel(9)
		self.link1=link1
		self.link2=link2


	

	
	
	def getPosition(self):
		MatriceUB=self.link1.getUB().getRowPackedCopy()
		lattice=self.link2.getLattice()
		lista=[]
		for l in range(9):
			lista.append(MatriceUB[l])
		
 		return lista+lattice


	def isBusy(self):
		return 0 

#Xtalinfo=crystalinfo('xtal','A','%7.5f',ub,cr)
