## @file RecSpace.py This file contains the class dealing with the HKL calculations
#
#  @author Alessandro Bombardi
#  @version 1.0 (alpha release)
#  Please report bugs to Alessandro.Bombardi@diamond.ac.uk
#  Diamond Light Source Ltd.

import java
from Jama import Matrix
from math import *
import Diffractometer as sixC
import beamline_info as BLi

## This class deals with the [H K L] calculations
#
class RecSpace(java.lang.Object):

#   def  __init__(self):

## Public void function establish a link with the instantiation of the UBmatrix
#  class passed as argument. Notice that the UB matrix can also be passed in an explicit
#  way, so this link is not strictly necessary.
#
   def setUBman(self,x):
      self.ubm=x
      return

   def setSA(self,x):
      self.SA=x
      return

   ##  Public void setHKL(double[] hkl)
   #
   def setHKL(self,hkl):
      "@sig public void setHKL(double[] hkl)"
      self.hkl = Matrix(hkl,3)
      return

   ## Public function, no arguments. It returns the hkl as a Jama Matrix
   #
   def getHKL(self):
      "@sig public getHKL()"
      return self.hkl
      
## Public function. Six optional arguments, the first four arguments are
#  the 4 Eulerian angles tth, th, chi, phi in degrees. The fifth argument is
#  an UB matrix (Jama 3*3 Matrix), the sixth argument the wavelength in Angstrom
#  If no angles are provided they will be retrieved from the values in the
#  modules managing the angles concerned.
#  If setUBman was set and no UB matrix is provided the UB matrix is taken from
#  the UBmatrix class
#  If no wavelength is provided it will be retrieved from the module BLinfo
   def calcHKL(self,mu=None,eta=None,chi=None,phi=None,delta=None,gamma=None,UB=None,wl=None):
      d=self.SA.getAngles()
      if eta  == None:
         eta = d.Theta
      if mu  == None:
         #mu = d.Mu
         mu  = d.Kmu
      if chi == None:
         chi =  d.Chi
      if phi == None:
         phi =  d.Phi
      if delta == None:
         delta =  d.Delta
      if gamma == None:
         gamma =  d.Gam
      if UB == None:
         UB=self.ubm.getUB()
      if wl == None:
         wl=BLi.getWavelength()
      qq=2.*sin(abs(acos(cos(delta*pi/180.)*cos(gamma*pi/180.)))/2.)/wl
      qv=[0.,1.,0.]
      qv=Matrix(qv,3)
      Z=sixC.setZ(mu,eta,chi,phi)
      DA=sixC.setDA(delta,gamma)
      qv=DA.minus(self.ubm.I).times(qv)
      if qv.normF() == 0:
         return Matrix([[0],[0],[0]])
      qv=qv.times(1/qv.normF()).times(qq)
      hkl_calc=UB.inverse().times(Z.inverse().times(qv))
      return hkl_calc

   def calcHKL_K(self,mu=None,Kth=None,Kap=None,Kphi=None,delta=None,gamma=None,UB=None,wl=None):
      d=self.SA.getAngles()
      if Kth  == None:
         Kth = d.Kth 
      if mu  == None:
         #mu = d.Mu
         mu  = d.Kmu
      if Kap == None:
         Kap =  d.Kap
      if Kphi == None:
         Kphi =  d.Kphi
      if delta == None:
         delta =  d.Delta
      if gamma == None:
         gamma =  d.Gam
      if UB == None:
         UB=self.ubm.getUB()
      if wl == None:
         wl=BLi.getWavelength()
      qq=2.*sin(abs(acos(cos(delta*pi/180.)*cos(gamma*pi/180.)))/2.)/wl
      qv=[0.,1.,0.]
      qv=Matrix(qv,3)
      ZK=sixC.setZK(mu,Kth,Kap,50.,Kphi)
      DA=sixC.setDA(delta,gamma)
      qv=DA.minus(self.ubm.I).times(qv)
      qv=qv.times(1/qv.normF()).times(qq)
      hkl_calc=UB.inverse().times(ZK.inverse().times(qv))
      return hkl_calc

   def calcQ(self,mu=None,eta=None,chi=None,phi=None,delta=None,gamma=None,U=None,wl=None):
      d=self.SA.getAngles()
      if eta  == None:
         eta = d.Theta
      if mu  == None:
         #mu = d.Mu
         mu  = d.Kmu
      if chi == None:
         chi =  d.Chi
      if phi == None:
         phi =  d.Phi
      if delta == None:
         delta =  d.Delta
      if gamma == None:
         gamma =  d.Gam
      if U == None:
#         U=self.ubm.getU()
         U=Matrix(self.ubm.UBdata.getValue('U'))
      if wl == None:
         wl=BLi.getWavelength()
      #qq=2.*sin(abs(acos(cos(delta*pi/180.)*cos(gamma*pi/180.)))/2.)/wl
      qv=[0.,1./wl,0.]
      qv=Matrix(qv,3)
      Z=sixC.setZ(mu,eta,chi,phi)
      DA=sixC.setDA(delta,gamma)
      qv=DA.minus(self.ubm.I).times(qv)
      #qv=qv.times(1/qv.normF()).times(qq)
      #print U.getRowPackedCopy()
      q_calc=U.inverse().times(Z.inverse().times(qv))
      return q_calc

## Return an error message
#
   def __repr__(self):
      return '<RecSpace Bean Error>'
