## @file Azimuth.py  allows to set and get the azimuthal settings and
#  to calculate the value of the azimuthal angle for a given
#  reflection.
#  @author Alessandro Bombardi
#  @version 1.0 (alpha release)
#  Please report bugs to Alessandro.Bombardi@diamond.ac.uk
#  Diamond Light Source Ltd.

import java
from Jama import Matrix
from math import *
import ShelveIO
import Rotations
import Diffractometer as sixC
import MatrixAlgebra as MaAl

VERBOSE = True
## This class allows to set and get the azimuathal settings and it
#  allows to calculate the value of the azimuthal angle for a given
#  reflection.
class Azimuth(java.lang.Object):

   ## The Constructor
   def __init__(self):

      self.R0_azr=Matrix(3,3)
      self.debug=0

###########  Please do not modify ###################

      ## These variables store the path and the database fileName for the azimuthal
      #  settings. These settings should not be modified
      self.Az=ShelveIO.ShelveIO()  ##
      self.Az.path=ShelveIO.ShelvePath+'AzSettings'
      self.Az.setSettingsFileName('AzSettings') ##

      ## Set the initial value of the azimuthal reference reflection and of the
      #  azimuthal angles to None.
      #  These variables should not be accessed/modified directly
      self.azr = None
      self.psi_now = None
      try:
         self.getAzimuthalReference()
      except: 
         pass 
###################################################


################ LINKS WITH THE OTHER CLASSES  #################################

   ## This void function establish a link with the instantiation of the UBmatrix
   #  class passed as argument.
   #
   def setUBm(self,x):
      self.ubm=x
      return
      
   ## This void function establish a link with the instantiation of the RecSpace
   #  class passed as argument.
   #
   def setRecSpace(self,x):
      self.rs=x
      return


   def Angles(self,x):
      self.SA=x
      return
      
      
   def setCrystal(self,x):
      self.cry=x
      return
################################################################################

   ## Set the required value for the azimuthal angle
   #  and stores it in a file
   def setPsi(self,psi):
      "@sig public void setPsi(double psi)"
      self.psi_now=psi
      self.Az.ChangeValue('Psi',psi)
      return

   ## Return the required value for the azimuthal angle
   #  either from the locally stored value or from a file
   def getPsi(self):
      "@sig public double getPsi()"
      if self.psi_now == None:
         self.psi_now=self.Az.getValue('Psi')
      return self.psi_now

   ## Define the azimuthal rotation matrix as a left hand rotation about x.
   #  These function takes as argument the angle psi in degree and returns
   #  the corresponding JAMA rotation matrix.
   def R_psi(self,psi):
      "@sig public double R_PSI(double PSI)"
      psi=psi*pi/180.0
      PSI=Matrix(Rotations.R_x_l(psi))
      return PSI

   ## Set the Azimuthal Reference, the argument is a list [h,k,l],
   #  and stores it in a file
   def setAzimuthalReference(self,azr):
      "@sig public void setAzimuthalReference(double [] azr)"
      self.Az.ChangeValue('AzimuthalReference',azr)
      self.azr = Matrix(azr,3)
      return

   ## Get/Restore the Azimuthal Reference either from
   #  a locally strored variable or from a file , no arguments are given.
   #  A Jama matrix is returned
   def getAzimuthalReference(self):
      if self.azr == None:
         self.azr=Matrix(self.Az.getValue('AzimuthalReference'),3)
      return self.azr


   def calcQsys(self,da=None,hkl=None,UB=None):
         if da==None:
            da=self.SA.getAngles()
         if hkl ==None:
            hkl=[self.rs.calcHKL().get(0,0),self.rs.calcHKL().get(1,0),self.rs.calcHKL().get(1,0)]
         if UB == None:
            UB=self.ubm.getUB()
         Z=sixC.setZ(da.Mu,da.Eta,da.Chi,da.Phi)
         self.yL=sixC.setDA(da.Delta,da.Gamma).times(Matrix([0.,1.,0.],3))
         self.yL=self.yL.times(1./self.yL.normF())
         self.qL=Z.times(UB.times(Matrix(hkl,3)))
         self.qL=self.qL.times(1./self.qL.normF())
         self.yLn= [ self.yL.get(0,0),self.yL.get(1,0),self.yL.get(2,0)]
         self.qLn= [ self.qL.get(0,0),self.qL.get(1,0),self.qL.get(2,0)]
#         print self.qLn,self.yLn
         self.zLn=MaAl.CROSS(self.qLn,self.yLn)
         self.zL=Matrix(self.zLn,3)
         self.zL=self.zL.times(1./self.zL.normF())
         self.zLn=[ self.zL.get(0,0),self.zL.get(1,0),self.zL.get(2,0)]
         self.yLn =MaAl.CROSS(self.zLn,self.qLn)
         self.yL=Matrix(self.yLn,3)
#         print qL.normF(),yL.normF(),zL.normF()
         return #[qLn,yLn,zLn]
         
   ## Calculate and return the value of the azimuthal angle psi for the given Eulerian angles
   #  omega, chi, phi (in degrees), a given reflection [h,k,l] and a given UB matrix.
   #  Without argument the stored [hkl] values and UB are used.
   #
   def calcN_L(self,da=None,hkl=None,UB=None):
         if da==None:
            da=self.SA.getAngles()
         if hkl ==None:
#            hkl=self.rs.getHKL()
            hkl=self.rs.calcHKL()
            hkl=[hkl.get(0,0),hkl.get(1,0),hkl.get(2,0)]
         if UB == None:
            UB=self.ubm.getUB()
         Z=sixC.setZ(da.Mu,da.Eta,da.Chi,da.Phi)
         n_phi=UB.times(self.azr)
         n_phi=n_phi.times(1./n_phi.normF())
         self.n_Lm = Z.times(n_phi)
         n_L  =[ self.n_Lm.get(0,0),self.n_Lm.get(1,0),self.n_Lm.get(2,0)]
         self.calcQsys(da,hkl,UB)
         temp=self.n_Lm.transpose().times(self.yL).get(0,0)
         self.n_Lm_par= self.yL.times(temp)
         self.n_Lm_perp=self.n_Lm.minus(self.n_Lm_par)
         self.n_L_perp=[self.n_Lm_perp.get(0,0),self.n_Lm_perp.get(1,0),self.n_Lm_perp.get(2,0)]
         temp=Matrix(MaAl.CROSS(self.n_L_perp,self.qLn),3)
         self.flag=temp.plus(self.yL).normF()
         return n_L

   def getAlpha(self,da=None,hkl=None,UB=None):
      N_L=self.calcN_L(da,hkl,UB)
      alpha = asin(-N_L[1])*180./pi
      return alpha

   def getPhi_az(self,da=None,hkl=None,UB=None):
      N_L=self.calcN_L(da,hkl,UB)
      self.phi_az= atan(N_L[0]/N_L[2])*180./pi
      return self.phi_az

   def getTau(self,da=None,hkl=None,UB=None):
      if hkl is None:
            hkl=self.rs.calcHKL()
            hkl=[hkl.get(0,0),hkl.get(1,0),hkl.get(2,0)]
      self.tau = self.cry.Angle(hkl,[self.azr.get(0,0),self.azr.get(1,0),self.azr.get(2,0)])*pi/180.
      return self.tau

   def getBeta(self,da=None,hkl=None,UB=None):
      if da ==None:
         da=self.SA.getAngles()
      ttheta_mes = acos(cos(da.Delta*pi/180.)*cos(da.Gamma*pi/180.))*180./pi
      N_L=self.calcN_L(da,hkl,UB)
      self.getTau(da,hkl,UB)
#      print "tau",self.tau*180./pi
      beta  = asin(2.*sin(ttheta_mes/2.*pi/180.)*cos(self.tau) + N_L[1])*180./pi
      return beta

   def calcPsi(self,da=None,hkl=None,UB=None):
      if da ==None:
         da=self.SA.getAngles()
      ttheta_mes = acos(cos(da.Delta*pi/180.)*cos(da.Gamma*pi/180.))*180./pi
      alpha=self.getAlpha(da,hkl,UB)
      beta =self.getBeta(da,hkl,UB)
      if self.tau==0.0:
         psi1=90.
         psi2=90.
      else:
         try:
            psi1 = acos((cos(self.tau)*sin(ttheta_mes/2.*pi/180.)-sin(alpha*pi/180.))/(sin(self.tau)*cos(ttheta_mes/2.*pi/180.)))*180./pi
            psi2 = acos((-cos(self.tau)*sin(ttheta_mes/2.*pi/180.)+sin(beta*pi/180.))/(sin(self.tau)*cos(ttheta_mes/2.*pi/180.)))*180./pi
#            print "psi1,psi2",psi1,psi2
            if self.flag < 1:
               psi1=-psi1
               psi2=-psi2
         except:
            argpsi=(-cos(self.tau)*sin(ttheta_mes/2.*pi/180.)+sin(beta*pi/180.))/(sin(self.tau)*cos(ttheta_mes/2.*pi/180.))
            if VERBOSE:
                print "Warning::psi not well defined"
                print  "arg of the cos >1?", argpsi                 
            if argpsi >1: 
               psi1=0.
               psi2=0.
            elif argpsi < -1:
               psi1=180.
               psi2=180.
            else:
               psi1=-6666
               psi2=-6666
      return [psi1,psi2]


##########################################################################################
##########################################################################################





   ## Calculate the rotation Matrix to apply to a given reflection
   #  to bring it in the plane where its azimuth is zero
   #
   def getAzimuthZero(self,hkl=None,UB=None):
      "@sig public void getAzimuthZero( Matrix hkl, Jama Matrix )"
      try:
         if hkl==None:
            hkl=self.rs.getHKL()
         if UB==None:
            hphi_azr = self.ubm.UB.times(hkl)
            h0phi_azr = self.ubm.UB.times(self.azr)
         else:
            hphi_azr = UB.times(hkl)
            h0phi_azr = UB.times(self.azr)
         t3_phi_az=Matrix(MaAl.CROSS(hphi_azr.getRowPackedCopy(),h0phi_azr.getRowPackedCopy()),3)
         t2_phi_az=Matrix(MaAl.CROSS(t3_phi_az.getRowPackedCopy(),hphi_azr.getRowPackedCopy()),3)
         t1_phi_azr=hphi_azr.times(1/hphi_azr.normF())
         t2_phi_azr=t2_phi_az.times(1/t2_phi_az.normF())
         t3_phi_azr=t3_phi_az.times(1/t3_phi_az.normF())
         self.R0_azr.setMatrix([0],0,2,t1_phi_azr.transpose())
         self.R0_azr.setMatrix([1],0,2,t2_phi_azr.transpose())
         self.R0_azr.setMatrix([2],0,2,t3_phi_azr.transpose())
      except:
         print "Warning:Probably the reflection and the azimuthal reference are //"
      return  self.R0_azr


   ## Calculate the settings of the Eulerian angles to obtain a the given azimutal
   #  angle value (in degrees) and returns the angles as [omega, chi, phi] in degrees
   def calcAzangles(self,psi):
      self.psi_g=psi
      self.R_azr=self.MaAl.MMultiply(self.R_psi(self.psi_g),self.R0_azr)
      chi_g = atan2(abs(sqrt(self.R_azr[2][0]**2+self.R_azr[2][1]**2)),self.R_azr[2][2])
      phi_g = atan2(-self.R_azr[2][1],-self.R_azr[2][0])
      omega_g = atan2(self.R_azr[0][2],-self.R_azr[1][2])
      angles = [omega_g*180.0/pi,chi_g*180.0/pi,phi_g*180.0/pi]
      if self.debug==1:
         print angles
      return angles


   ## Throws an error message
   #
   def __repr__(self):
      return self.getAzimuthalReference()
