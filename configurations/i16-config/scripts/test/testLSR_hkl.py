#############################################
# Test 6circles
#############################################
from java import lang
from gda.analysis.numerical.optimization.objectivefunction import AbstractObjectiveFunction
#from gda.analysis.numerical.optimization.objectivefunction import AbstractLSQObjectiveFunction
from gda.analysis.numerical.linefunction import Parameter
from gda.analysis.numerical.optimization.objectivefunction import chisquared
from gda.analysis.numerical.optimization.optimizers.leastsquares import minpackOptimizer
#from gda.analysis.numerical.optimization.optimizers.filtering import iffco
from gda.analysis.numerical.optimization.optimizers.differentialevolution import DEOptimizer
from gda.analysis.numerical.optimization.optimizers.simplex import NelderMeadOptimizer
#from gda.analysis.datastructure import DataVector1D
from java.lang import *
from org.python.modules.jarray import *
from org.python.modules.math import *
import jarray



from math import *
from Jama import Matrix
#import UBmatrix
#import Reflmanagement
#import Crystal
#import StoredAngles
#import gettth
#import RecSpace
#import BLinfo as BLi
#import Azimuth
#import CalcAngles
#import LSR_HKL

import LSR_HKL_K
reload(LSR_HKL_K)


#import LSRn
#import LSRorto
#CA=CalcAngles.CalcAngles()



#san=StoredAngles.StoredAngles()
#ub = UBmatrix.UBmatrix()
#rr = Reflmanagement.Reflmanagement()
#az = Azimuth.Azimuth()
#ub.setReflmanagement(rr)
#rs=RecSpace.RecSpace()

#az.setUBm(ub)
#az.setRecSpace(rs)
#az.Angles(san)

#rr.setRecSpaceMan(rs)
#rr.Angles(san)
#rr.setRecSpaceMan(rs)
#rr.setAzMan(az)
#rr.setAzMan(az)

#rs.setUBman(ub)
#rs.setSA(san)


#cr=Crystal.Crystal()
#ub.setCrystalmanagement(cr)
#gt =gettth.gettth()
#gt.setCrystalmanagement(cr)
#ub.set2theta(gt)

#CA.sethklLink(rs)
#CA.setUBm(ub)
#CA.setAzman(az)
#CA.setCalc2theta(gt)
#CA.setSA(san)
#CA.setCrystal(cr)


#cr.setCrystal('HoMn2O5')
#rr.setReflectionsFileName('Ho1')
#rr.setReflectionsFileName('Ho2')

#print "ub",ub.getUB().getRowPackedCopy()
#az.setCrystal(cr)

params=ub.getUB().getRowPackedCopy()
lower=[]
upper=[]
param=[]
for iii in params:
	low=iii-0.1
	upp=iii+0.1
	param+=[iii]
	lower+=[low]
	upper+=[upp]

param+=[0,0,0]
lower+=[-0.1,-0.1,-0.1]
upper+=[0.1,0.1,0.1]

print "ub",param
print "L",lower
print "U",upper
listaref=['lt1','lt2','lt3','lt4','lt5','lt6','lt7','lt8','lt9','lt10','lt11','lt12','lt13','lt14','lt15','lt16','lt17','lt18','lt19']
#LSR=LSR_HKL.LSR_HKL(param,lower,upper,rr,rs)
LSR=LSR_HKL_K.LSR_HKL_K(param,lower,upper,rr,rs,listaref)




# To use a nelder mead algorithm
mymin = NelderMeadOptimizer(LSR)


# The Following 3 methods not available in the version installed in the GDA
mymin.setDefaultStep(0.01)
mymin.setSteps(jarray.array([0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01,0.01],'d'))
mymin.setStepOption(2)



print "Numero iterazioni",mymin.getMaxNoOfIterations()
mymin.setMaxNoOfIterations(50)
mymin.setTolerance(1.e-8)
print "Tolerance",mymin.tolerance
mymin.reset()
print "Tolerance",mymin.tolerance
print "Numero iterazioni",mymin.getMaxNoOfIterations()
print  "LSR",LSR.evaluate(param)



mymin.optimize()
mymin.getConverganceStatus()
xxx=mymin.getBest()
UBref=Matrix([[xxx[0],xxx[1],xxx[2]],[xxx[3],xxx[4],xxx[5]],[xxx[6],xxx[7],xxx[8]]])

for i in range(len(xxx)):
	print "parametri",xxx[i],param[i]

print  "LSR",LSR.evaluate(mymin.getBest())

newlat=ub.UB2Lat(UBref)
oldlat=ub.UB2Lat(ub.getUB())
print oldlat
print newlat

print "Number of iteration",LSR.nn




