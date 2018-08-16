#############################################
# Test 6circles
#############################################
from math import *
from Jama import Matrix
import UBmatrix
import Reflmanagement
import Crystal
import StoredAngles
import gettth
import RecSpace
import beamline_info as BLi
import Azimuth
import CalcAngles
CA=CalcAngles.CalcAngles()

BLi.setEnergy(8.09503)


san=StoredAngles.StoredAngles()
ub = UBmatrix.UBmatrix()
rr = Reflmanagement.Reflmanagement()
az = Azimuth.Azimuth()
ub.setReflmanagement(rr)
rs=RecSpace.RecSpace()
cr=Crystal.Crystal()



az.setUBm(ub)
az.setRecSpace(rs)
az.Angles(san)
az.setCrystal(cr)
rr.setRecSpaceMan(rs)
rr.Angles(san)
rr.setRecSpaceMan(rs)
rr.setAzMan(az)
rr.setAzMan(az)

rs.setUBman(ub)
rs.setSA(san)


ub.setCrystalmanagement(cr)
gt =gettth.gettth()
gt.setCrystalmanagement(cr)
ub.set2theta(gt)

CA.sethklLink(rs)
CA.setUBm(ub)
CA.setAzman(az)
CA.setCalc2theta(gt)
CA.setSA(san)
CA.setCrystal(cr)




cr.setCrystal('LuVOxx')
ab = [5.573,7.534,5.215,90.0,90.0,90.0]
cr.setLattice(ab)
cr.setBMatrix()
#cr.getBMatrix().print(10,5)

az.setAzimuthalReference([0., 0.,1.])

rr.setReflectionsFileName('LUVOxx.refl')

san.ChangeAngle('Eta',20.436)
san.ChangeAngle('Mu',0.)
san.ChangeAngle('Chi',92.1545)
san.ChangeAngle('Phi',10.)
san.ChangeAngle('Delta',66.686)
san.ChangeAngle('Gamma',0.)

rr.Addreflections('1',[4.,0.,0.],None,None)
#rr.Addreflections(None,None,None,7.69145)

san.ChangeAngle('Eta',31.582)
san.ChangeAngle('Chi',92.1105)
san.ChangeAngle('Phi',10.)
san.ChangeAngle('Delta',67.976)
rr.Addreflections('2',[4.,1.,0.],None,None)
#rr.Addreflections(None,None,None,7.691)
ub.setOrient('1','2')
ub.setUB()
ub.getUB().print(5,5)


print "------------------------------------------------------------------------"
r3=CA.getBisecting_new(Matrix([3.,-3.,0.],3))

print "Phi",r3.Phi
print "Chi",r3.Chi
print "eta",r3.Eta
print "Mu",r3.Mu
print "Delta",r3.Delta
print "Gamma",r3.Gamma
print "theta_az",r3.theta_az
print "psi", r3.Psi
san.ChangeAngle('Eta',r3.Eta)
san.ChangeAngle('Mu',r3.Mu)
san.ChangeAngle('Chi',r3.Chi)
san.ChangeAngle('Phi',r3.Phi)
san.ChangeAngle('Delta',r3.Delta)
san.ChangeAngle('Gamma',r3.Gamma)
rs.calcHKL(r3.Mu,r3.Eta,r3.Chi,r3.Phi,r3.Delta,r3.Gamma).print(10,10)

print "------------------------------------------------------------------------"
san.ChangeAngle('Phi',10.)
r3=CA.getPhiFixed_new([4.,0.,1.])

#   print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)
san.ChangeAngle('Eta',r3.Eta)
san.ChangeAngle('Mu',r3.Mu)
san.ChangeAngle('Chi',r3.Chi)
san.ChangeAngle('Phi',r3.Phi)
san.ChangeAngle('Delta',r3.Delta)
san.ChangeAngle('Gamma',r3.Gamma)
#rs.calcHKL(r3.Mu,r3.Eta,r3.Chi,r3.Phi,r3.Delta,r3.Gamma).print(10,10)
rr.Addreflections('9')
r3=rr.getReflection('9')
print "hkl=%s,Psi=%s" %(r3.hkl,r3.az.psi)
print "Delta=%s,Gamma=%s" %(r3.sixC.Delta,r3.sixC.Gamma)
print "Mu=%s,Eta=%s,Chi=%s,Phi=%s" %(r3.sixC.Mu,r3.sixC.Eta,r3.sixC.Chi,r3.sixC.Phi)
print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)

r3=CA.getPhiFixed_new([4.,1.,0.])

#   print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)
san.ChangeAngle('Eta',r3.Eta)
san.ChangeAngle('Mu',r3.Mu)
san.ChangeAngle('Chi',r3.Chi)
san.ChangeAngle('Phi',r3.Phi)
san.ChangeAngle('Delta',r3.Delta)
san.ChangeAngle('Gamma',r3.Gamma)
#rs.calcHKL(r3.Mu,r3.Eta,r3.Chi,r3.Phi,r3.Delta,r3.Gamma).print(10,10)
rr.Addreflections('9')
r3=rr.getReflection('9')
print "hkl=%s,Psi=%s" %(r3.hkl,r3.az.psi)
print "Delta=%s,Gamma=%s" %(r3.sixC.Delta,r3.sixC.Gamma)
print "Mu=%s,Eta=%s,Chi=%s,Phi=%s" %(r3.sixC.Mu,r3.sixC.Eta,r3.sixC.Chi,r3.sixC.Phi)
print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)

r3=CA.getPhiFixed_new([4.,0.,0.])

#   print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)
san.ChangeAngle('Eta',r3.Eta)
san.ChangeAngle('Mu',r3.Mu)
san.ChangeAngle('Chi',r3.Chi)
san.ChangeAngle('Phi',r3.Phi)
san.ChangeAngle('Delta',r3.Delta)
san.ChangeAngle('Gamma',r3.Gamma)
#rs.calcHKL(r3.Mu,r3.Eta,r3.Chi,r3.Phi,r3.Delta,r3.Gamma).print(10,10)
rr.Addreflections('9')
r3=rr.getReflection('9')
print "hkl=%s,Psi=%s" %(r3.hkl,r3.az.psi)
print "Delta=%s,Gamma=%s" %(r3.sixC.Delta,r3.sixC.Gamma)
print "Mu=%s,Eta=%s,Chi=%s,Phi=%s" %(r3.sixC.Mu,r3.sixC.Eta,r3.sixC.Chi,r3.sixC.Phi)
print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)

r3=CA.getPhiFixed_new([2.0005,0.00025,0.00089])

#   print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)
san.ChangeAngle('Eta',r3.Eta)
san.ChangeAngle('Mu',r3.Mu)
san.ChangeAngle('Chi',r3.Chi)
san.ChangeAngle('Phi',r3.Phi)
san.ChangeAngle('Delta',r3.Delta)
san.ChangeAngle('Gamma',r3.Gamma)
#rs.calcHKL(r3.Mu,r3.Eta,r3.Chi,r3.Phi,r3.Delta,r3.Gamma).print(10,10)
rr.Addreflections('9')
r3=rr.getReflection('9')
print "hkl=%s,Psi=%s" %(r3.hkl,r3.az.psi)
print "Delta=%s,Gamma=%s" %(r3.sixC.Delta,r3.sixC.Gamma)
print "Mu=%s,Eta=%s,Chi=%s,Phi=%s" %(r3.sixC.Mu,r3.sixC.Eta,r3.sixC.Chi,r3.sixC.Phi)
print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)


print "-------------------------------------------------------------------------"
san.ChangeAngle('Delta',10.)
san.ChangeAngle('Gamma',0.)
for psi in range(-180,360,10):
   r3=CA.getPsiFixed_new([4.,0.,0.],psi)
   san.ChangeAngle('Eta',r3.Eta)
   san.ChangeAngle('Mu',r3.Mu)
   san.ChangeAngle('Chi',r3.Chi)
   san.ChangeAngle('Phi',r3.Phi)
   san.ChangeAngle('Delta',r3.Delta)
   san.ChangeAngle('Gamma',r3.Gamma)
#rs.calcHKL(r3.Mu,r3.Eta,r3.Chi,r3.Phi,r3.Delta,r3.Gamma).print(10,10)
   rr.Addreflections('9')
   r3=rr.getReflection('9')
   print "########################"
   print "Azimuth Richiesto=", psi
   print "hkl=%s,Psi=%s" %(r3.hkl,r3.az.psi)
   print "Delta=%s,Gamma=%s" %(r3.sixC.Delta,r3.sixC.Gamma)
   print "Mu=%s,Eta=%s,Chi=%s,Phi=%s" %(r3.sixC.Mu,r3.sixC.Eta,r3.sixC.Chi,r3.sixC.Phi)
#   print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)
   print
   print
   
   
san.ChangeAngle('Delta',0.)
san.ChangeAngle('Gamma',1.)
for psi in range(-180,360,10):
   print "-------------------------------------------------------------------------"
   psi=1.*psi
   r3=CA.getPsiFixed_new([4.,0.,0.],psi)
   san.ChangeAngle('Eta',r3.Eta)
   san.ChangeAngle('Mu',r3.Mu)
   san.ChangeAngle('Chi',r3.Chi)
   san.ChangeAngle('Phi',r3.Phi)
   san.ChangeAngle('Delta',r3.Delta)
   san.ChangeAngle('Gamma',r3.Gamma)
#rs.calcHKL(r3.Mu,r3.Eta,r3.Chi,r3.Phi,r3.Delta,r3.Gamma).print(10,10)
   rr.Addreflections('9')
   r3=rr.getReflection('9')
   print "########################"
   print "Azimuth Richiesto=", psi
   print "hkl=%s,Psi=%s" %(r3.hkl,r3.az.psi)
   print "Delta=%s,Gamma=%s" %(r3.sixC.Delta,r3.sixC.Gamma)
   print "Mu=%s,Eta=%s,Chi=%s,Phi=%s" %(r3.sixC.Mu,r3.sixC.Eta,r3.sixC.Chi,r3.sixC.Phi)
#   print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)
   print
   print "############ Comparison Phi fixed ###################################"
   r3=CA.getPhiFixed_new([4.,0.,0.],r3.sixC.Phi)
   san.ChangeAngle('Eta',r3.Eta)
   san.ChangeAngle('Mu',r3.Mu)
   san.ChangeAngle('Chi',r3.Chi)
   san.ChangeAngle('Phi',r3.Phi)
   san.ChangeAngle('Delta',r3.Delta)
   san.ChangeAngle('Gamma',r3.Gamma)
#rs.calcHKL(r3.Mu,r3.Eta,r3.Chi,r3.Phi,r3.Delta,r3.Gamma).print(10,10)
   rr.Addreflections('9')
   r3=rr.getReflection('9')
   print "hkl=%s,Psi=%s" %(r3.hkl,r3.az.psi)
   print "Delta=%s,Gamma=%s" %(r3.sixC.Delta,r3.sixC.Gamma)
   print "Mu=%s,Eta=%s,Chi=%s,Phi=%s" %(r3.sixC.Mu,r3.sixC.Eta,r3.sixC.Chi,r3.sixC.Phi)
#   print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)



print "############ Comparison Phi fixed ###################################"
san.ChangeAngle('Delta',1.)
san.ChangeAngle('Gamma',0.)
r3=CA.getPhiFixed_new([3.9995,-0.000939,1.0038],10.)
san.ChangeAngle('Eta',r3.Eta)
san.ChangeAngle('Mu',r3.Mu)
san.ChangeAngle('Chi',r3.Chi)
san.ChangeAngle('Phi',r3.Phi)
san.ChangeAngle('Delta',r3.Delta)
san.ChangeAngle('Gamma',r3.Gamma)
#rs.calcHKL(r3.Mu,r3.Eta,r3.Chi,r3.Phi,r3.Delta,r3.Gamma).print(10,10)
rr.Addreflections('9')
r3=rr.getReflection('9')
print "hkl=%s,Psi=%s" %(r3.hkl,r3.az.psi)
print "Delta=%s,Gamma=%s" %(r3.sixC.Delta,r3.sixC.Gamma)
print "Mu=%s,Eta=%s,Chi=%s,Phi=%s" %(r3.sixC.Mu,r3.sixC.Eta,r3.sixC.Chi,r3.sixC.Phi)
#   print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)
ab = [5.574,7.534,5.215,90.0,90.0,90.0]

san.ChangeAngle('Eta',19.197)
san.ChangeAngle('Mu',0.)
san.ChangeAngle('Chi',2.4985)
san.ChangeAngle('Phi',10.)
san.ChangeAngle('Delta',66.6705)
san.ChangeAngle('Gamma',0.)

rr.Addreflections('3',[4.,0.,0.],None,None)
#rr.Addreflections(None,None,None,7.69145)

san.ChangeAngle('Eta',30.344)
san.ChangeAngle('Chi',2.4985)
san.ChangeAngle('Phi',10.)
san.ChangeAngle('Delta',67.927)
rr.Addreflections('4',[4.,1.,0.],None,None)
#rr.Addreflections(None,None,None,7.691)
ub.setOrient('3','4')
az.setAzimuthalReference([0., 1.,0.])
ub.setUB()
ub.getUB().print(5,5)

BLi.setEnergy(5.4)
r3=CA.getPhiFixed_new([3.,0.,0.],10.)
san.ChangeAngle('Eta',r3.Eta)
san.ChangeAngle('Mu',r3.Mu)
san.ChangeAngle('Chi',r3.Chi)
san.ChangeAngle('Phi',r3.Phi)
san.ChangeAngle('Delta',r3.Delta)
san.ChangeAngle('Gamma',r3.Gamma)
#rs.calcHKL(r3.Mu,r3.Eta,r3.Chi,r3.Phi,r3.Delta,r3.Gamma).print(10,10)
rr.Addreflections('9')
r3=rr.getReflection('9')
print "hkl=%s,Psi=%s" %(r3.hkl,r3.az.psi)
print "Delta=%s,Gamma=%s" %(r3.sixC.Delta,r3.sixC.Gamma)
print "Mu=%s,Eta=%s,Chi=%s,Phi=%s" %(r3.sixC.Mu,r3.sixC.Eta,r3.sixC.Chi,r3.sixC.Phi)
print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)

san.ChangeAngle('Eta',24.022)
san.ChangeAngle('Mu',0.)
san.ChangeAngle('Chi',2.797)
san.ChangeAngle('Phi',10.)
san.ChangeAngle('Delta',76.313)
san.ChangeAngle('Gamma',0.)
#rs.calcHKL(r3.Mu,r3.Eta,r3.Chi,r3.Phi,r3.Delta,r3.Gamma).print(10,10)
rr.Addreflections('9')
r3=rr.getReflection('9')
print "hkl=%s,Psi=%s" %(r3.hkl,r3.az.psi)
print "Delta=%s,Gamma=%s" %(r3.sixC.Delta,r3.sixC.Gamma)
print "Mu=%s,Eta=%s,Chi=%s,Phi=%s" %(r3.sixC.Mu,r3.sixC.Eta,r3.sixC.Chi,r3.sixC.Phi)
print "alpha=%s,beta=%s" %(r3.sample.alpha,r3.sample.beta)




