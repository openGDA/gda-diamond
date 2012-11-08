## @file surface.py Currently under construction, it allows to calculate
#  the angles @f$ \alpha @f$ and @f$ \beta @f$, and from their value the azimuthal angle
#  @f$ \psi @f$  as well
#
import java
from math import *
from Jama import Matrix
from beamline_info import getWavelength as gwl
import Eulerian4CDiffractometer as E4C
import ShelveIO
import CalcAngles as CA
import EuSampleAngles as esa
import DetectorAngles as DA

###########  Please do not modify ###################
sInfo=ShelveIO.ShelveIO()  ##
sInfo.path=ShelveIO.ShelvePath+'surfInfo'
sInfo.setSettingsFileName('surfInfo') ##

## Surface class
#  It allows to calculate the angle of the incident/outcoming beam with the surface,
#  provide an alternative method to calculate the azimuthal angle psi
class surface(java.lang.Object):
   def __init__(self):

###########  Please do not modify ###################
      self.sInfo=ShelveIO.ShelveIO()  ##
      self.sInfo.path='surfInfo'
      self.sInfo.setSettingsFileName('surfInfo') ##
#####################################################

   ## This void function establish a link with the instantiation of the CalcAngles
   #  class passed as argument.
   #
   def setca(self,ca):
      self.ca=ca
      return

   ## This void function establish a link with the instantiation of the UBmatrix
   #  class passed as argument.
   #
   def setUBman(self,ub):
      self.ub=ub
      return

   ## This void function establish a link with the instantiation of the Crystal
   #  class passed as argument.
   #
   def setcryman(self,cr):
      self.cry=cr
      return
######################################################

   ## set the direction (n) perpendicular to the crystal surface
   #
   def setn(self,n):
      self.sInfo.ChangeValue('n',n)
      return

   ## return the direction(n) perpendicular to the crystal surface
   #
   def getn(self):
      n=Matrix(self.sInfo.getValue('n'),3)
      return n

   ## return the direction of n with the current diffractometer settings
   #
   def getnor(self,hkl=None):
      if hkl==None:
         Z_now=E4C.setZ(esa.getTheta()-DA.get2th()/2,esa.getChi(),esa.getPhi()).times(self.ub.getUB())
      else:
         ang=self.ca.getAngles(None,Matrix(hkl,3))
         Z_now=E4C.setZ(ang[1]-ang[0]/2,ang[2],ang[3]).times(self.ub.getUB())
      angles=self.ca.getAngles(None,self.getn())
      print "angoli", angles
      rv=Matrix([1.,0.,0.],3)
      Z=E4C.setZ(angles[1]-angles[0]/2,angles[2],angles[3])
      Z=Z.inverse()
      nor=Z_now.times(Z.times(rv))
      return nor

   ## Calculate and return the value of the azimuthal angle psi for the given Eulerian angles
   #  omega, chi, phi (in degrees), a given reflection [h,k,l] and a given UB matrix.
   #  Without argument the stored [hkl] values and UB are used.
   #
   def calcN_L(self,mu=None,eta=None,chi=None,phi=None,hkl=None,UB=None):
      try:
         if hkl ==None:
            hkl=self.rs.getHKL()
         if UB == None:
            UB=self.ubm.getUB()
         Z=sixC.setZ(mu,eta,chi,phi)
         n_phi=UB.times(self.azr)
         n_phi=n_phi.times(1./n_phi.normF())
         self.n_Lm = Z.times(n_phi)
         self.n_L  =[ self.n_Lm.get(0,0),self.n_Lm.get(1,0),self.n_Lm.get(2,0)]
      except:
         print "Reference Vector Problem"
         self.n_L=[0.,0.,0.]
      return self.n_L

   def getAlpha(self,):




   ## Public double  getAlp(double tth=None,double [] hkl=None)
   #
   def getAlp_old(self,tth=None,hkl=None):
      if tth == None:
         tth=DA.get2th()
      ki=[-sin(tth/2.*(pi/180.)),-cos(tth/2.*(pi/180.)),0.]
      ki=Matrix(ki,3)
      salp=ki.transpose().times(self.getnor(hkl))
      salp = salp.get(0,0)/ki.transpose().times(ki).get(0,0)
      alpha=asin(-salp)*180./pi
      return alpha
      
   ## Public double  getBeta(double tth=None,double [] hkl=None)
   #
   def getBeta(self):
      kf=[sin(DA.get2th()/2.*(pi/180.)),-cos(DA.get2th()/2.*(pi/180.)),0.]
      kf=Matrix(kf,3)
      sbet=kf.transpose().times(self.getnor())
      sbet = sbet.get(0,0)/kf.transpose().times(kf).get(0,0)
      beta=asin(sbet)*180./pi
      return beta

   ## Public double  getpsi(double [] hkl=None)
   #
   def getpsi(self,hkl):
      angles=self.ca.getAngles(None,Matrix(hkl,3))
      print "angles",angles[0]
      tau=self.cry.Angle(hkl,self.getn().getRowPackedCopy())
      print "tau",tau
      a=self.getAlp(angles[0],hkl)
      print "alpha=",a
      N1=cos(tau*pi/180.)*sin(angles[0]/2.*(pi/180.))-sin(self.getAlp(angles[0],hkl)*pi/180.)
      D1=sin(tau*pi/180.)*cos(angles[0]/2.*(pi/180.))
      psi=acos(N1/D1)*180./pi
      return psi
      
   ## Throws an error message
   #
   def __repr__(self):
      return '<Surface bean error>'
