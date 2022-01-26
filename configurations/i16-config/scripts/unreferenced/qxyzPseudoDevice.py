from gda.device.scannable import ScannableMotionBase

import qSpace
import CalcAngles

from Jama import Matrix

from jarray import array
from java.lang import String
from java.lang import Thread


class qxyzPseudoDevice(ScannableMotionBase):

   def __init__(self,name,q):
      self.name = name
      self.q = q
      if name == 'qx':
         self.axis = 0
      elif name == 'qy':
         self.axis = 1
      elif name == 'qz':
         self.axis = 2


   def asynchronousMoveTo(self,new_position):
      while self.hkl.isBusy():
         Thread.sleep(200)
      current_position = self.q.getPosition()
      current_position[self.axis] = new_position
      self.q.asynchronousMoveTo(current_position)

	#
	# If the euler PD is busy then so is this device
	#
   def isBusy(self):
      return self.q.isBusy()

	#
	# Returns the current Eulerian coordinates as an array
	#
   def getPosition(self,mu=None,eta=None,chi=None,phi=None,delta=None,gamma=None,U=None,wavelength=None):
      current_position = self.q.getPosition()
      return current_position[self.axis]
