from gda.device.scannable import ScannableMotionBase

import RecSpace
import CalcAngles

from Jama import Matrix

from jarray import array
from java.lang import String
from java.lang import Thread


class hklAxisPseudoDevice(ScannableMotionBase):

   def __init__(self,name,hkl):
      self.name = name
      self.hkl = hkl
      if name == 'h':
         self.axis = 0
      elif name == 'k':
         self.axis = 1
      elif name == 'l':
         self.axis = 2


   def asynchronousMoveTo(self,new_position):
      while self.hkl.isBusy():
         Thread.sleep(200)
      current_position = self.hkl.getPosition()
      current_position[self.axis] = new_position
      #print "About to call hkl.asynchronousMoveTo(", current_position ,")"
      self.hkl.asynchronousMoveTo(current_position)

	#
	# If the euler PD is busy then so is this device
	#
   def isBusy(self):
      return self.hkl.isBusy()

	#
	# Returns the current Eulerian coordinates as an array
	#
   def getPosition(self,mu=None,eta=None,chi=None,phi=None,delta=None,gamma=None,UB=None,wavelength=None):
      current_position = self.hkl.getPosition()
      return current_position[self.axis]
