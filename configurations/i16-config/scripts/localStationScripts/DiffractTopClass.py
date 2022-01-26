# Initialise diffractometer code objects
import beamline_objects as BLobjects
from Jama import Matrix
# 

from diffractometer.calc import UBmatrix
reload(UBmatrix)
from diffractometer.calc import Reflmanagement
reload(Reflmanagement)
from diffractometer.calc import Crystal
reload(Crystal)
from diffractometer.calc import StoredAngles
reload(StoredAngles)
from diffractometer.calc import gettth
reload(gettth)
from diffractometer.calc import RecSpace
import beamline_info as BLi
reload(BLi)
from diffractometer.calc import Azimuth
reload(Azimuth)
from diffractometer.calc import CalcAngles
reload(CalcAngles)



CA = CalcAngles.CalcAngles()
san = StoredAngles.StoredAngles()
ub = UBmatrix.UBmatrix()
rr = Reflmanagement.Reflmanagement()
az = Azimuth.Azimuth()
rs = RecSpace.RecSpace()
cr = Crystal.Crystal()
gt = gettth.gettth()

ub.setReflmanagement(rr)

az.setUBm(ub)
az.setRecSpace(rs)
az.Angles(san)
az.setCrystal(cr)

rr.setRecSpaceMan(rs)
rr.Angles(san)
rr.setRecSpaceMan(rs)
rr.setAzMan(az)
rs.setUBman(ub)
rs.setSA(san)

gt.setCrystalmanagement(cr)

ub.setCrystalmanagement(cr)
ub.set2theta(gt)

CA.sethklLink(rs)
CA.setUBm(ub)
CA.setAzman(az)
CA.setCalc2theta(gt)
CA.setSA(san)

def xtal(arg=None):
	if arg == None:
		return cr.getCrystal()
	else:
		cr.setCrystal(arg)
		return cr.getCrystal(arg)


def latt(arg=None):
	if arg == None:
		return cr.getLattice()
	else:
		if len(arg)==1:
			cr.setLattice([arg[0],arg[0],arg[0],90.,90.,90.]) # cubic
		if len(arg)==2:
			cr.setLattice([arg[0],arg[0],arg[1],90.,90.,90.]) # tetragonal
		if len(arg)==3:
			cr.setLattice([arg[0],arg[1],arg[2],90.,90.,90.]) # orto
		if len(arg)==4:
			cr.setLattice([arg[0],arg[1],arg[2],90.,90.,arg[3]]) # mono
		if len(arg)==5:
			print "Wrong argument number"
		if len(arg)==6:
			cr.setLattice(arg) # tricl
		return cr.getLattice()

				

def ubm(or0=None,or1=None,or2=None):
	if or2 is None:
		if or0==None and or1 == None: 
			return ub.getUB().getRowPackedCopy()
		if or0 is not None and or1 is not None:
			if type(or1) is list:
				ub.setOrient(str(or0))
				ub.setUB(or1)
			elif type(or1) is not list:
				ub.setOrient(str(or0),str(or1))
				ub.setUB()
	if or2 is not None:
		print "Not implemented yet"
	return ub.getUB().getRowPackedCopy()


def ubAll(lista=None):
	"""Syntax  ubAll(lista=None) if lista is None it uses all the reflections in the reffile to \n calculate the ubmatrix, otherwise you can specify the reflections you want \n to use providing the list of strings, warning the UB matrix is uncostrained!!! \n e.g. ubAll(['ref1','ref2','ref3','ref4',....]) """
	xxx=ub.setUBnref(lista)
	calculated_lattice=ub.UB2Lat(xxx)
	latt(calculated_lattice)
	print "New Lattice parameter is:", calculated_lattice
	print "The new UB matrix is:", xxx.getRowPackedCopy()
	return

def getUB():
	lista=[]
	matriceUB=ub.getUB().getRowPackedCopy()
	for indice in range(9):
		lista.append(matriceUB[indice])
	return lista

def getU():
	return ub.getU()


def setUB(matrice):
	""" Enter the UB matrix as [[],[],[]] """
	ub.UB=None
	ub.SaveMatrix('UB',Matrix(matrice))
	return ub.getUB().getRowPackedCopy()

def getB():
	lista=[]
	MatriceB=cr.getBMatrix().getRowPackedCopy()
	for indice in range(9):
		lista.append(MatriceB[indice])
	return lista


def azir(ll=None):
	"""Syntax azir([h,k,l]=None):: [h,k,l] optional if the argument is None gets the current azimuthal reference \n otherwise it sets it to the value specified (if hkl is // to the reflection studied the calculation won't work.)""" 
	if ll is not None: 	
		az.setAzimuthalReference(ll)
	return az.getAzimuthalReference().getRowPackedCopy()


## Useful functions
def c2th(hkl,energy=None):
	"""Syntax c2th([h,k,l],energy optional) :: Returns the calculated value of 2theta for the given hkl"""
	return gt.calctth(hkl,energy)

def d_hkl(hkl):
	"""Syntax d_hkl([h,k,l]) :: Returns the calculated lattice spacings for the given hkl"""
	return cr.d_hkl(hkl)

def angle(r1,r2):
	"""Syntax cr.Angle(r1,r2) :: Returns the calculated angle between the give reflections r1 and r2"""
	return cr.Angle(r1,r2)

def calcalpha():
	return az.getAlpha()

def calcbeta():
	return az.getBeta()

def calcpsi():
	return az.calcPsi()[0]

def wl():
	return BLi.getWavelength()

def calchkl(newhkl,energy=None):
	angles = CA.getAngles(EDi.getMode(),newhkl,None,None,None,energy)
	print "phi would have moved to: ", angles.Phi
	print "chi would have moved to: ", angles.Chi
	print "eta would have moved to: ", angles.Eta
	print "mu would have moved to: ", angles.Mu
	print "delta would have moved to: ", angles.Delta
	print "gamma would have moved to: ", angles.Gamma



## Function to manage the reflections

def reffile(fname=None):
	if fname is not None:
		rr.setReflectionsFileName(fname)
	return rr.getReflectionsFileName()

def showref():
	rr.showreflections()

def showKref():
	rr.showKreflections()



def saveref(key=None,hkl=None):
	rr.Addreflections(key,hkl)
	try:
		rr.getReflection(str(key))
	except:
		print "reflection", str(key) ,"not added try again"	

def delref(key):
	rr.removeReflection(str(key))

def delrefs(keys):
	for ii in keys:
		rr.removeReflection(str(ii))

def getref(key):
	return rr.getReflection(str(key))
###

def changehkl(key,newkey,newhkl,doshow=0):
	nomeref=rr.getReflection(str(key))
	nomeref.hkl=newhkl
	rr.setReflection(newkey,nomeref)
	if doshow == 1:
		showref()
#rr.setReflectionsFileName('LiF')
latt()




