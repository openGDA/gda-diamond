from gda.device.scannable import ScannableMotionBase
import Searchref2
reload(Searchref2)
SearchRef=Searchref2.Searchref2(cr,ub,BLi,gt)

class pd_searchref2(ScannableMotionBase):
	""" This pseudodevice search for a second reflection once the
	first reflection in the ub matrix is known.
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
	IF YOU UPDATE THE UB MATRIX PLEASE DELETE AND RERUN THE INSTANTIATION,
	OTHERWISE IT WILL NOT WORK
	!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

	It doesn't matter if 
	the first reflection is specular or not and the second reflection 
	found will belong to the same grain!!
	to use the pd first type
	the input value is the phi angle
	self.setref2([h,k,l]) to establish the reflection you want to look for
	Two solutions are possible so you need also to type:
	self.setSolution(0 or 1)
	if you wish to calculate the positon without  moving use:
	self.calcPos(newphi)
	if you wish to scan just as all the other pd:
	e.g.
	scan sr2 0 10 1 t .5 
	Warning: Some of the values of phi would produce a not acceptable 
	solution, in this case the devce does not return any value. 
	"""

	def __init__(self,name,formatstring,unitstring,eulerian,delta,searchref,hkl):
		self.setName(name)
		self.setInputNames(['phi'])
		self.setExtraNames(['chi','eta','mu','delta','gam']);
		self.setOutputFormat([formatstring]*6)
		self.unitstring=unitstring
		self.setLevel(5)
		self.eu=eulerian
#		self.sr=searchref
		self.sol = 0
		self.hkl =hkl
		self.delta=delta
		
	def setSolution(self,sol):
		if sol==1 or sol==0:
			self.sol =sol
			return
		else:
			print "Warning sol has not been provided: default solution is 0"
			return

	def getSol(self):
		return self.sol

	def setref2(self,hkl2):
		self.hkl2 =hkl2

	def getref2(self):
		return self.hkl2

	def asynchronousMoveTo(self,newphi):
		newpos=SearchRef.locateref(self.hkl2,newphi)
		#print newpos
		if self.sol == 0:
			self.eu.asynchronousMoveTo([newpos[0],newpos[1],newpos[3],0,newpos[4],0])
		elif self.sol == 1:
			self.eu.asynchronousMoveTo([newpos[0],newpos[2],newpos[3],0,newpos[4],0])
		else:
			return
		#self.delta.asynchronousMoveTo(newpos[4])

	def calcPos(self,newphi):
		newpos=SearchRef.locateref(self.hkl2,newphi)
		print "newpos",newpos
		#angles = self.eu.storedAngles.getAngles()
		print "phi would have moved to: ", newpos[0]
		if self.sol == 0: 
			print "chi would have moved to: ", newpos[1]
		if self.sol == 1:
			print "chi would have moved to: ", newpos[2]
		print "eta would have moved to: ", newpos[3]
		print "mu would have moved to: ", 0
		print "delta would have moved to: ", newpos[4]
		print "gamma would have moved to: ", 0
			


		
	def getPosition(self):
		angles = self.eu()
		return angles



	def isBusy(self):
		return BLobjects.isBusy()

sr2=pd_searchref2('sr2','%6f','deg',euler,delta,SearchRef,hkl)
