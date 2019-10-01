from gda.device.scannable import PseudoDevice

import RecSpace
import CalcAngles
import beamline_objects as BLobjects
from gda.jython import JythonServerFacade

from Jama import Matrix

from jarray import array
from java.lang import String


class hklPseudoDevice_offset(PseudoDevice):

   def __init__(self,name,euler,tth,rs,cal,EDi,delta,gam,az,eta_offsetpd,flag):
      self.name = name
      self.euler = euler
      self.tth = tth
      self.rs = rs
      self.cal= cal
      self.EDi = EDi
      self.setInputNames(['h', 'k','l','eta'])
      self.delta = delta
      self.gam = gam
      self.setName("hkl_eta")
      self.setOutputFormat(["%4.4f","%4.4f","%4.4f","%4.4f"])
      self.az=az
      self.eta_offset = eta_offsetpd
      self.flag =flag
      self.statichelp= """This modified hkl pseudodevices takes hkl and an offset in eta as arguments.
      It positions hkl to the required hkl + the offset in eta. It returns, depending on the flag argument (1 or 2)
      either the hkl initially required and the offset, or the real position in hkl and the offset.
      It needs to be linked to an instance of the offset class containing the offset in eta.
      """
#      if help is not None:
#         self.__doc__+='\nHelp specific to '+self.name+':\n'+help
#      else:
#         self.__doc__+='\nHelp specific to '+self.name+':\n'+self.statichelp
      

   def asynchronousMoveTo(self,new_position):
      self.eta_offset(new_position[3])
      if self.EDi.getMode() == 3: 
         angles = self.cal.getAngles(self.EDi.getMode(),new_position[0:3],None,self.az.getPsi())
      else:
         angles = self.cal.getAngles(self.EDi.getMode(),new_position[0:3])
      euler_positions = [angles.Phi,angles.Chi,angles.Eta+new_position[3],angles.Mu,angles.Delta,angles.Gamma]
      
      ########################## SAFETY IMPROVEMENTS (RDW) ########################
      # bypass storedAngles and check limits of motors directly
      # Euler
      # There is no outside method to go all the way and check all the limits on euler, as this would also
      # have to check the limits on the motors it moves.  However if a request is made it will not 
      # be able to perform it will throw an exception.  As long as delta and gamma are moved after it, then we 
      # logically safe (assuming the exception really stops program flow)
      panicStop = JythonServerFacade.getInstance().beamlineHalt
      
      # No need to checkEuler, as it will stop code if a limit is exceeded. 
      # Delta

      report=self.delta.checkPositionValid(angles.Delta)
      if (report != None):
         raise RuntimeError, "\nMove not performed because: \n" + report
         
#      # Gamma
#      self.gam.interuptIfPositionNotValid(angles.Gamma)
#      if self.gam.isPositionWithinScannableLimits(angles.Gamma):
#         raise Exception, self.gam.isPositionWithinScannableLimits(angles.Gamma)


      # euler will stop the code if the move is outside limits or if another error prevents a move
      self.euler.asynchronousMoveTo(euler_positions)
      #self.delta.asynchronousMoveTo(angles.Delta)
      #self.gam.asynchronousMoveTo(angles.Gamma)

      try:
         self.delta.asynchronousMoveTo(angles.Delta)
      except:
         print "<<HKL move failed: problem moving Delta. Axis may be disabled, unhomed or kaput. Calling PanicStop incase other axes are allready moving...>>"
         panicStop()


#      try:
#         self.gam.asynchronousMoveTo(angles.Gamma)
#      except:
#         print "<<HKL move failed: problem moving Gamma. Axis may be disabled, unhomed or kaput. Calling PanicStop incase other axes are allready moving...>>"
#         panicStop()



	#
	# If the euler PD is busy then so is this device
	# TODO: Must also check delta ang gamma!
   def isBusy(self):
      return self.euler.isBusy()

	#
	# Returns the current Eulerian coordinates as an array
	#
   def getPosition(self,mu=None,eta=None,chi=None,phi=None,delta=None,gamma=None,UB=None,wavelength=None):
      if self.flag == 1:
         matrix = self.rs.calcHKL(mu,eta,chi,phi,delta,gamma,UB,wavelength)
      if self.flag == 2:
         matrix = self.rs.calcHKL(mu,eta,chi,phi,delta,gamma,UB,wavelength)
#      print "Euler,delta",self.isBusy(), self.delta.isBusy()
      h = matrix.get(0,0)
      k = matrix.get(1,0)
      l = matrix.get(2,0)
      return [h,k,l,self.eta_offset()]

   #string representation of the data in an object
#   def toString(self):
#      return self.getName() + ":" + `self.getPosition()`


