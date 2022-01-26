## @file qSpace.py This file contains the class dealing with the HKL calculations
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

## This class deals with the reciprocal space of the sample (q-space), not of the crystal (hkl-space)
# Adapted from RecSpace

class qSpace(java.lang.Object):

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

   ##  Public void setQ(double[] hkl)
   #
   def setQ(self,q):
      "@sig public void setQ(double[] q)"
      self.q = Matrix(q,3)
      return

   ## Public function, no arguments. It returns the q as a Jama Matrix
   #
   def getQ(self):
      "@sig public getQ()"
      return self.q
      
## Public function. Six optional arguments, the first four arguments are
#  the 4 Eulerian angles tth, th, chi, phi in degrees. The fifth argument is
#  an UB matrix (Jama 3*3 Matrix), the sixth argument the wavelength in Angstrom
#  If no angles are provided they will be retrieved from the values in the
#  modules managing the angles concerned.
#  If setUBman was set and no UB matrix is provided the UB matrix is taken from
#  the UBmatrix class
#  If no wavelength is provided it will be retrieved from the module BLinfo
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
         U=self.ubm.getU()
      if wl == None:
         wl=BLi.getWavelength()
#      qq=2.*sin(abs(acos(cos(delta*pi/180.)*cos(gamma*pi/180.)))/2.)/wl
      qv=[0.,1/wl,0.]
      qv=Matrix(qv,3)
      Z=sixC.setZ(mu,eta,chi,phi)
      DA=sixC.setDA(delta,gamma)
      qv=DA.minus(self.ubm.I).times(qv)
#     qv=qv.times(1/qv.normF()).times(qq)
      q_calc=U.inverse().times(Z.inverse().times(qv))
      return q_calc

## Return an error message
#
   def __repr__(self):
      return '<qSpace Bean Error>'
