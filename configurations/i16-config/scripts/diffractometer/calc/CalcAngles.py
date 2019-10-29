## @file CalcAngles.py  contains a class that
#  allows to calculate the setting angles for a given reflection
#  with different settings of the four circles
#  @author Alessandro Bombardi
#  @version 1.0 (alpha release)
#  Please report bugs to Alessandro.Bombardi@diamond.ac.uk
#  Diamond Light Source Ltd.

import java
import Jama
from Jama import Matrix
#from math import *
from mathd import *
import DiffractometerInfo as EDI
import Diffractometer as sixC
import StoredAngles
import Angles
from beamline_info import getWavelength as gWL
from beamline_info import getEnergy as gE
import MatrixAlgebra as MaAl
from Orthonormalize import orthonormalize as orto


## Class dealing with the angle calculation. To work correctly
#  links to other classes instantiation need to be set
#
class CalcAngles(java.lang.Object):
   def __init__(self):
      self.CA=StoredAngles.StoredAngles('CA')
      self.angles=Angles.Angles()
      self.d=Angles.Angles()


   ## This void function establish a link with the instantiation of the Azimuth
   #  class passed as argument.
   #
   def setAzman(self,x):
      self.az=x
      return

   ## This void function establish a link with the instantiation of the RecSpace
   #  class passed as argument.
   #
   def sethklLink(self,x):
      self.hkl=x
      return

   ## This void function establish a link with the instantiation of the UBmatrix
   #  class passed as argument.
   #
   def setUBm(self,x):
      self.ubm=x
      return

   ## This void function establish a link with the instantiation of the gettth
   #  class passed as argument.
   #
   def setCalc2theta(self,x):
      self.c2t=x
      return
      

   ## This void function establish a link with the instantiation of the storedangles
   #  class passed as argument.
   def setSA(self,x):
      self.SA=x
      return

   def setCrystal(self,x):
      self.cry=x
      return


   def calcNl(self,azr=None,hkl=None,theta_az=None):
      orto(hkl_L,azr_L)

   def calcNphi(self,azr=None,hkl=None,UB=None):
         if azr==None:
            azr=[self.az.getAzimuthalReference().get(0,0),self.az.getAzimuthalReference().get(1,0),self.az.getAzimuthalReference().get(2,0)]
         if hkl ==None:

            hkl=[self.rs.calcHKL().get(0,0),self.rs.calcHKL().get(1,0),self.rs.calcHKL().get(1,0)]
         if UB == None:
            UB=self.ubm.getUB()
         Qphim = UB.times(Matrix(hkl,3))
         nphim = UB.times(Matrix(azr,3))
         Qphim = Qphim.times(1./Qphim.normF())
         nphim = nphim.times(1./nphim.normF())
         Qphi  =  [ Qphim.get(0,0),Qphim.get(1,0),Qphim.get(2,0)]
         nphi= [nphim.get(0,0),nphim.get(1,0),nphim.get(2,0)]
         nphi3=MaAl.CROSS(Qphi,nphi)
         if Matrix(nphi3,3).normF() < 1e-4:
            print "Warning::Vector and Azimuthal reference //, azimuthal reference not used"
            nphim = nphim.plus(Matrix([0.00013,0.0002,-0.00017],3))
            nphim = nphim.times(1./nphim.normF())
            nphi  = [nphim.get(0,0),nphim.get(1,0),nphim.get(2,0)]
            nphi3 = MaAl.CROSS(Qphi,nphi)
         nphi2 = MaAl.CROSS(nphi3,Qphi)
         Nphi2=Matrix(nphi2,3)
         Nphi3 = Matrix(nphi3,3)
         Nphi2=Nphi2.times(1./Nphi2.normF())
         Nphi3=Nphi3.times(1./Nphi3.normF())
         self.N_phi = Matrix(3,3)
         self.N_phi.setMatrix(0,2,0,0,Qphim)
         self.N_phi.setMatrix(0,2,1,1,Nphi2)
         self.N_phi.setMatrix(0,2,2,2,Nphi3)
         return self.N_phi




## Public getAngles(mode=None,hkl=None,omega=None,chi=None,phi=None,psi=None,UB=None,energy=None) function
   #  calls different methods to calculate the angles and returns
   #  the calculated values.
   #  In normal use the function does not need any external value but it can be also used passing all
   #  the arguments explicitely
   #
   def getAngles(self,mode=None,hkl=None,phi=None,psi=None,UB=None,energy=None):
      "@sig public double[] getAngles()"
#      try:
      if mode==None:
         mode=EDI.getMode()
      if hkl==None:
         hkl=self.hkl.getHKL()
      if phi==None:
         xx=self.SA.getAngles()
         phi=xx.Phi
      if UB == None:
         UB = self.ubm.getUB()
      if psi==None:
         psi=self.az.getPsi()
      if energy ==None:
         energy=gE()
      if mode == 1:
#################################################
# bisecting
#################################################
         ang=self.getBisecting_new(hkl,UB,energy)
      elif mode == 2:
#################################################
# phi fixed
#################################################
         ang=self.getPhiFixed_new(hkl,phi,UB,energy)
      elif mode == 3:
#################################################
# PSI Fixed
#################################################
         ang=self.getPsiFixed_new(hkl,psi,UB,energy)
#      except:
#        ang=None
#         print "Warning:: getAngles raised an exception"
      return ang

   ## public double [] getBisecting(self,hkl=None,UB=None,energy=None)
   #  Calculate the angles assuming @f$ \omega=0 \f$
   def getBisecting_new(self,hkl=None,UB=None,energy=None):
      angles=self.angles
      d=self.d
      if energy ==None:
         energy=gE()
      wl=12.39842/energy
      if hkl==None:
         hkl=self.hkl.getHKL()
      if UB == None:
         UB = self.ubm.getUB()
#         d=self.ubm.or0
      else:
         pass
#         d=self.ubm.or0
      d.sixC=self.SA.getAngles()
      try:
         ttheta = self.c2t.calctth(hkl.getRowPackedCopy(),energy)
      except:	
         ttheta = self.c2t.calctth(hkl,energy)
      theta  = ttheta/2.0
      if abs(d.sixC.Delta) >= 1e-3 and abs(d.sixC.Gamma) <= 1e-2:
#      if abs(d.sixC.Delta) >= 1e-3 and abs(d.sixC.Gamma) <= 1e-3:
# VERTICAL
         angles.theta_az =90.0
         angles.Gamma =0.0
         angles.Delta = ttheta
         angles.Mu = 0.0
         angles.Eta = theta
#         print "I am vertical"
      elif abs(d.sixC.Delta) <= 1e-3 and abs(d.sixC.Gamma) >= 1e-3:
# Horizontal
         angles.theta_az =0.0
         angles.Gamma =ttheta
         angles.Delta = 0.0
         angles.Mu = theta
         angles.Eta = 0.0
#         print "I am horizontal"
      else:
        
         print "Mode not implemented yet, choose Horizontal or Vertical geometry by setting"
         print "the detector motion not used to zero"
         print "Delta",d.sixC.Delta
         print "Gamma",d.sixC.Gamma
         raise Exception("gam=delta=0 so cannot infer if a horizontal or vertical scattering solution should be provided")
      ETA=sixC.R_eta(angles.Eta)
      MU=sixC.R_mu(angles.Mu)
      THETA = sixC.R_phi(theta)
      F=sixC.R_chi(angles.theta_az-90.)
      V=ETA.inverse().times(MU.inverse().times(F.times(THETA)))
      try:
         self.calcNphi(None,hkl.getRowPackedCopy(),UB)
      except:
         self.calcNphi(None,hkl,UB)
# Works with You
      if  sixC.flag == "You":
         angles.Phi = asin(-V.get(1,0)/sqrt(self.N_phi.get(0,0)**2+self.N_phi.get(1,0)**2))+atan2(self.N_phi.get(1,0),self.N_phi.get(0,0))*180./pi
         temp=self.N_phi.get(0,0)*cosd(angles.Phi)+self.N_phi.get(1,0)*sind(angles.Phi)
         angles.Chi = atan2(self.N_phi.get(2,0)*V.get(0,0)-temp*V.get(2,0),self.N_phi.get(2,0)*V.get(2,0)+temp*V.get(0,0))*180./pi
         N=self.N_phi.get(0,1)*V.get(1,2)*tand(angles.Phi)-self.N_phi.get(0,2)*V.get(1,1)*tand(angles.Phi)+self.N_phi.get(1,2)*V.get(1,1)-self.N_phi.get(1,1)*V.get(1,2)
         D=V.get(1,2)*(self.N_phi.get(0,2)*tand(angles.Phi)-self.N_phi.get(1,2))+V.get(1,1)*(self.N_phi.get(0,1)*tand(angles.Phi)-self.N_phi.get(1,1))
         angles.Psi = atan2(N,D)*180./pi
# test me
      elif sixC.flag == "Me":
         angles.Phi = asin(-V.get(1,0)/sqrt(self.N_phi.get(0,0)**2+self.N_phi.get(1,0)**2))+atan2(self.N_phi.get(1,0),-self.N_phi.get(0,0))*180./pi
         temp=self.N_phi.get(0,0)*cosd(angles.Phi)-self.N_phi.get(1,0)*sind(angles.Phi)
         angles.Chi = atan2(-self.N_phi.get(2,0)*V.get(0,0)+temp*V.get(2,0),self.N_phi.get(2,0)*V.get(2,0)+temp*V.get(0,0))*180./pi
         N=self.N_phi.get(0,1)*V.get(1,2)*tand(angles.Phi)-self.N_phi.get(0,2)*V.get(1,1)*tand(angles.Phi)-self.N_phi.get(1,2)*V.get(1,1)+self.N_phi.get(1,1)*V.get(1,2)
         D=V.get(1,2)*(self.N_phi.get(0,2)*tand(angles.Phi)+self.N_phi.get(1,2))+V.get(1,1)*(self.N_phi.get(0,1)*tand(angles.Phi)+self.N_phi.get(1,1))
         angles.Psi = atan2(N,D)*180./pi
      return angles

   def getPhiFixed_new(self,hkl=None,phi=None,UB=None,energy=None):
#      Calculation done with phi fixed
      angles=self.angles
      d=self.d
      if energy ==None:
         energy=gE()
      wl=12.39842/energy
      if hkl==None:
         hkl=self.hkl.getHKL()
      else:
         hkl=Matrix(hkl,3)
      if UB == None:
         UB = self.ubm.getUB()
#         d=self.ubm.or0
      else:
# fix it properly
#         d=self.ubm.or0
         pass
      d.sixC=self.SA.getAngles()
      if phi == None:
         phi = d.sixC.Phi
      ttheta = self.c2t.calctth(hkl.getRowPackedCopy(),energy)
      if abs(d.sixC.Delta) >= 1e-3 and abs(d.sixC.Gamma) <= 1e-2:
#      if abs(d.sixC.Delta) >= 1e-3 and abs(d.sixC.Gamma) <= 1e-3:
# VERTICAL
         angles.theta_az =90.0
         angles.Gamma =0.0
         angles.Delta = ttheta
         angles.Mu = 0.0
         angles.Phi = phi
#         print "Vertical"
      elif abs(d.sixC.Delta) <= 1e-3 and abs(d.sixC.Gamma) >= 1e-3:
# "Horizontal"
         angles.theta_az =0.0
         angles.Gamma =ttheta
         angles.Delta = 0.0
         angles.Phi = phi
         angles.Eta = 0.0
#         print "Horizontal"
      else:
         print "Mode not implemented yet, choose Horizontal or Vertical geometry by setting"
         print "the detector motion not used to zero"
         print "Delta",d.sixC.Delta
         print "Gamma",d.sixC.Gamma
         raise Exception("gam=delta=0 so cannot infer if a horizontal or vertical scattering solution should be provided")

      PHI=sixC.R_phi(angles.Phi)
      DELTA =sixC.R_delta(angles.Delta)
      GAMMA =sixC.R_gamma(angles.Gamma)
      hkl_phi=UB.times(hkl)
      hkl_phi  = [hkl_phi.get(0,0),hkl_phi.get(1,0),hkl_phi.get(2,0)]
      DA=sixC.setDA(angles.Delta,angles.Gamma)
      k =2.*pi/wl
      Q_L=(DA.minus(self.ubm.I)).times(Matrix([0.,k,0.],3))
      Q_L = [Q_L.get(0,0),Q_L.get(1,0),Q_L.get(2,0)]
      if angles.Gamma == 0.0:
#         print "Sto testando gamma =0b  "
#         elif sixC.flag == "You":
         angles.Chi = atan2(hkl_phi[2],cosd(angles.Phi)*hkl_phi[0]+sind(angles.Phi)*hkl_phi[1])*180./pi
         x1 =  cosd(angles.Phi)*Q_L[0]*hkl_phi[1]
         x2 =  cosd(angles.Chi)*Q_L[1]*hkl_phi[0]*cosd(angles.Phi)
         x3 =  sind(angles.Chi)*Q_L[1]*hkl_phi[2]
         x4 =  sind(angles.Phi)*Q_L[0]*hkl_phi[0]
         x5 =  cosd(angles.Chi)*Q_L[1]*hkl_phi[1]*sind(angles.Phi)

         y1 =  cosd(angles.Phi)*Q_L[1]*hkl_phi[1]
         y2 =  sind(angles.Chi)*Q_L[0]*hkl_phi[2]
         y3 =  sind(angles.Phi)*Q_L[1]*hkl_phi[0]
         y4 =  cosd(angles.Chi)*Q_L[0]*hkl_phi[0]*cosd(angles.Phi)
         y5 =  cosd(angles.Chi)*Q_L[0]*hkl_phi[1]*sind(angles.Phi)

         angles.Eta = atan2(-(-x1+x2+x3+x4+x5),(y1+y2-y3+y4+y5))*180./pi
      elif angles.Delta == 0.0:
#         elif sixC.flag == "You":
#         print "Lo sto testando"
         angles.Chi = atan2(-cosd(angles.Phi)*hkl_phi[0]-sind(angles.Phi)*hkl_phi[1],hkl_phi[2])*180./pi

         x1 = -cosd(angles.Chi)*Q_L[1]*hkl_phi[2]
         x2 =  cosd(angles.Phi)*Q_L[2]*hkl_phi[1]
         x3 =  cosd(angles.Phi)*Q_L[1]*hkl_phi[0]*sind(angles.Chi)
         x4 = -sind(angles.Phi)*Q_L[2]*hkl_phi[0]
         x5 =  sind(angles.Phi)*Q_L[1]*hkl_phi[1]*sind(angles.Chi)

         y1 =  cosd(angles.Phi)*Q_L[1]*hkl_phi[1]
         y2 =  cosd(angles.Chi)*Q_L[2]*hkl_phi[2]
         y3 = -cosd(angles.Phi)*Q_L[2]*hkl_phi[0]*sind(angles.Chi)
         y4 = -sind(angles.Phi)*Q_L[1]*hkl_phi[0]
         y5 = -sind(angles.Phi)*Q_L[2]*hkl_phi[1]*sind(angles.Chi)
         angles.Mu = atan2(x1+x2+x3+x4+x5,y1+y2+y3+y4+y5)*180./pi
      angles.Psi=self.az.calcPsi(angles,[hkl.get(0,0),hkl.get(1,0),hkl.get(2,0)],UB)[0]
      return  angles

   ## public double [] getPsiFixed(self,hkl=None,psi=None,UB=None,energy=None)
   #  Calculates the angles assuming @f$ \psi=\psi_f \f$
   def getPsiFixed_new(self,hkl=None,psi=None,UB=None,energy=None):
      angles=self.angles
      d=self.d
      if energy ==None:
         energy=gE()
      wl=12.39842/energy
      if hkl==None:
         hkl=self.hkl.getHKL()
      else:
         hkl=Matrix(hkl,3)
      if UB == None:
         UB = self.ubm.getUB()
#         d=self.ubm.or0
      else:
#         d=self.ubm.or0
         pass
      d.sixC=self.SA.getAngles()
      if psi == None:
         psi = d.sixC.Psi
      ttheta = self.c2t.calctth(hkl.getRowPackedCopy(),energy)
      if abs(d.sixC.Delta) >= 1e-3 and abs(d.sixC.Gamma) <= 1e-2:
# VERTICAL
         angles.theta_az =90.0
         angles.Gamma =0.0
         angles.Delta = ttheta
         angles.Mu = 0.0
         angles.Eta=None
#         print "Vertical"
      elif abs(d.sixC.Delta) <= 1e-3 and abs(d.sixC.Gamma) >= 1e-3:
# "Horizontal"
         angles.theta_az =0.0
         angles.Gamma =ttheta
         angles.Delta = 0.0
         angles.Eta = 0.0
         angles.Mu = None
#         print "Horizontal"
      else:
         print "Mode not implemented yet, choose Horizontal or Vertical geometry by setting"
         print "the detector motion not used to zero"
         print "Delta",d.sixC.Delta
         print "Gamma",d.sixC.Gamma
         raise Exception("gam=delta=0 so cannot infer if a horizontal or vertical scattering solution should be provided")
     
      PSI=sixC.R_mu(psi)
#      PSI.print(5,5)
      THETA =sixC.R_delta(ttheta/2.)
#      THETA.print(5,5)
      F =sixC.R_chi(angles.theta_az-90.)
#      F.print(5,5)
      N_phi=self.calcNphi(None,hkl.getRowPackedCopy(),UB)
      R=F.times(THETA.times(PSI.times(N_phi.inverse())))
      if angles.Mu == 0.0:
#         print "Verticale"
         angles.Chi =atan2(sqrt(R.get(2,0)**2+R.get(2,1)**2),R.get(2,2))*180./pi
         angles.Phi =atan2(-R.get(2,1),-R.get(2,0))*180./pi
         angles.Eta=atan2(-R.get(1,2),R.get(0,2))*180./pi
      if angles.Eta == 0.0:
#         print "horizontal"
         angles.Chi =atan2(R.get(0,2),sqrt(R.get(0,1)**2+R.get(0,0)**2))*180./pi
         angles.Phi =atan2(R.get(0,1),R.get(0,0))*180./pi
         angles.Mu=atan2(-R.get(1,2),R.get(2,2))*180./pi
#      else:
#         print "Not implemented yet"
      angles.Psi=self.az.calcPsi(angles,[hkl.get(0,0),hkl.get(1,0),hkl.get(2,0)],UB)[0]
      return angles

# needs completion
   def getThetazfixed_mufixed(self,hkl=None,mu=None,theta_az=None,UB=None,energy=None):
      angles=self.angles
      if energy ==None:
         energy=gE()
      wl=12.39842/energy
      if hkl==None:
         hkl=self.hkl.getHKL()
      else:
         hkl=Matrix(hkl,3)
      if UB == None:
         UB = self.ubm.getUB()
         d=self.ubm.or0
      else:
         pass
      d.sixC=self.SA.getAngles()
      if mu == None:
         mu = d.sixC.Mu
      if theta_az==None:
         theta_az = atan(tan(d.sixC.Delta*pi/180.)/sin(d.sixC.Gamma*pi/180.))*180./pi
         if theta_az < 0 or theta_az > 90:
            print "Warning: the value of theta_az exceeds the limts"
      ttheta = self.c2t.calctth(hkl.getRowPackedCopy(),energy)
      if abs(theta_az) < 1e-4:
         angles.Delta = 0.
         angles.Gamma = ttheta
      elif  abs(theta_az-90.) <1.e-4:
         angles.Delta = ttheta
         angles.Gamma = 0
      else:
         angles.Delta = asin(1./(2.*tand(ttheta/2.))*sind(theta_az))*180./pi
         angles.Gamma = acos(cosd(ttheta)/cosd(angles.Delta))*180./pi
      return


   ## Calculates the current value of @f $ \omega $@f
   #
   # Obsolete to change
   def calcOmega(self):
      tth=DA.get2th()
      theta=EuS.getTheta()
      omega=-(tth/2-theta)
      return omega


      
   ## Throws an error message
   #
   def __repr__():
      return '<CalcAngles error>'
      
      

