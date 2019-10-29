import java
from Jama import Matrix
from mathd import *
import ShelveIO
import Rotations
import Diffractometer as sixC
import MatrixAlgebra as MA

class Searchref2(java.lang.Object):
	def __init__(self,cr,ub,blinfo,calctth):
		self.cr=cr
		self.ub=ub
		self.blinfo =blinfo
		self.or0=self.ub.or0
		self.calctth=calctth
		self.I = Matrix([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]])


	def locateref(self,hkl,phi2,eta2=None,mu2=None):
		Ki= 2.*pi/self.blinfo.getEnergy()
		Kivec=[0.,Ki,0.]
		qvp=Matrix([Kivec]).transpose()

		## angle between the two reflections
		alpha=self.cr.Angle(hkl,self.ub.or0.hkl)
#		print "The angle is:",alpha
		## Measured configuration of the diffractometer for the first reflection
		Z1inv=sixC.setZ(self.or0.sixC.Mu,self.or0.sixC.Eta,self.or0.sixC.Chi,self.or0.sixC.Phi).inverse()
		DA1=sixC.setDA(self.or0.sixC.Delta,self.or0.sixC.Gamma)
		qv1=(DA1.minus(self.I)).times(qvp)
		qv1=qv1.times(1./qv1.normF())
		A=Z1inv.times(qv1)

		W=[A.get(0,0),A.get(1,0),A.get(2,0)]
#		print "W",W
		##  Configuration of the diffractometer for the second reflection assume bisecting an mu =0 but it can work with eta fixed
		try:
			ETAinv=sixC.setZ(0,eta2,0,0).inverse()
		except:
			eta2=  self.calctth.calctth(hkl)/2.
			ETAinv=sixC.setZ(0,eta2,0,0).inverse()
		MUinv=sixC.setZ(0,0,0,0).inverse()
		delta2=self.calctth.calctth(hkl)
		DA2=sixC.setDA(delta2,0.)
		qv2=(DA2.minus(self.I)).times(qvp)
		qv2=qv2.times(1./qv2.normF())
		B=ETAinv.times(MUinv.times(qv2))
		U=[B.get(0,0),B.get(1,0),B.get(2,0)]
#		print "U",U
		B0=U[2]*(W[0]*cosd(phi2)+W[1]*sind(phi2))+U[0]*W[2]
		A0=U[0]*(W[0]*cosd(phi2)+W[1]*sind(phi2))+ W[2]*U[2]+ U[1]*(W[0]*sind(phi2)-W[1]*cosd(phi2))+cosd(alpha)
		C0=-U[0]*(W[0]*cosd(phi2)+W[1]*sind(phi2))-W[2]*U[2]+U[1]*(W[0]*sind(phi2)-W[1]*cosd(phi2))+cosd(alpha)
#		print "coeff",A0,B0,C0
		try:
#			print B0**2-A0*C0
			s1=-atan((-B0+sqrt(B0**2-A0*C0))/A0)*2.*180./pi
			s2=-atan((-B0-sqrt(B0**2-A0*C0))/A0)*2.*180./pi
		except:
			print "I am in the exception"
			return
		return [phi2,s1,s2,eta2,delta2]
		



