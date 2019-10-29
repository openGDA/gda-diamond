from gda.device.scannable import PseudoDevice

import RecSpace
import CalcAngles

import java
import Jama
from Jama import Matrix
from jarray import array
from java.lang import String
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


class qPseudoDevice(PseudoDevice):

   def __init__(self,name,euler,tth,rs,cal,EDi,delta,gam,az):
      self.setName("q")
      self.setInputNames(['qx','qy','qz'])
      self.setOutputFormat(["%4.3f","%4.3f","%4.3f"])
      self.name = name
      self.euler = euler
      self.tth = tth
      self.delta = delta
      self.gam = gam
      self.rs = rs
      self.cal= cal
      self.EDi = EDi
      self.az=az

   def asynchronousMoveTo(self,new_position):
      if U == None:
         #U=self.ubm.getU()
         U=Matrix(self.ubm.UBdata.getValue('U'))
      if UB == None:
         UB=self.ubm.getUB()
      new_hkl = UB.inverse().times(U.times(new_position))
      if self.EDi.getMode() == 3: 
         angles = self.cal.getAngles(self.EDi.getMode(),new_hkl,None,self.az.getPsi())
      else:
         angles = self.cal.getAngles(self.EDi.getMode(),new_hkl)
      euler_positions = [angles.Phi,angles.Chi,angles.Eta,angles.Mu,angles.Delta,angles.Gamma]
      #self.euler.asynchronousMoveTo(euler_positions)
      #self.delta.asynchronousMoveTo(angles.Delta)
      #self.gam.asynchronousMoveTo(angles.Gamma)
      print "phi would have moved to: ", angles.Phi
      print "chi would have moved to: ", angles.Chi
      print "eta would have moved to: ", angles.Eta
      print "mu would have moved to: ", angles.Mu
      print "delta would have moved to: ", angles.Delta
      print "gamma would have moved to: ", angles.Gamma

	#
	# If the euler PD is busy then so is this device
	#
   def isBusy(self):
      return self.euler.isBusy()

	#
	# Returns the current Eulerian coordinates as an array
	#
   def getPosition(self,mu=None,eta=None,chi=None,phi=None,delta=None,gamma=None,U=None,wavelength=None):
      matrix = self.rs.calcQ(mu,eta,chi,phi,delta,gamma,U,wavelength)
      qx = matrix.get(0,0)
      qy = matrix.get(1,0)
      qz = matrix.get(2,0)
#      print "Euler,delta",self.isBusy(), self.delta.isBusy()	
      return [qx,qy,qz]

   #string representation of the data in an object
#   def toString(self):
#      return self.getName() + ":" + `self.getPosition()`


