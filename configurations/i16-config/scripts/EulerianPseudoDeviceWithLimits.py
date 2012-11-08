#
#   A Scannable (pseudo device) which creates three pseudo devices representing
#   the Eulerian angles for a six circle diffractometer
# [phi, chi, eta,mu,delta,gamma]
#
from java.lang import Double
from java.lang import Thread
from java.lang import String
from jarray import array

from gda.device.scannable import PseudoDevice

import EulerianKconversionModes
import beamline_objects as BLobjects
import ShelveIO
import Angles

class EulerianPseudoDevice(PseudoDevice):

   ### limit stuff ->
   limitPhiLow = None
   limitPhiHigh = None
   limitChiLow = None
   limitChiHigh = None
   limitEtaLow = None
   limitEtaHigh = None   
### <- limit stuff

   #
   # Constructor.  Must have six motors to control.
   #
   def __init__(self,name,storedAngles,mu,delta,gam):
      self.setName(name)
      self.setInputNames(array(['eta','phi','chi'], String))  ### SHOULD BE PHI,CHI,ETA ???
      self.setExtraNames(['mu','delta','gamma'])
      self.ekcm = EulerianKconversionModes.EulerianKconversionModes()
      self.storedAngles = storedAngles
      self.mu = mu
      self.delta = delta
      self.gam = gam

      self.SO = 'SO'
      self.SO=ShelveIO.ShelveIO()
      self.SO.path=ShelveIO.ShelvePath+'SO'
      self.SO.setSettingsFileName('SO')
      self.Etaoff=None
      


   def setEtaOffset(self,angle):
      self.Etaoff=angle
      self.SO.ChangeValue('Eta',angle)

   def getEtaOffset(self):
      if self.Etaoff == None:
         self.Etaoff = self.SO.getValue('Eta')
      return self.Etaoff
     

	#
	# Sets the mode the convertor is to work in
	#
   def setMode(self,mode):
      self.ekcm.setEuleriantoKmode(mode)

	#
	# Returns the mode the convertor is working in
	#
   def getMode(self):
      return self.ekcm.getEuleriantoKmode()

	#
	# Simply return the modes of the convertor
	#
   def __repr__(self):
      positions = self.getPosition();
      phi_pos = self.formatPosition(None,positions[0])
      chi_pos = self.formatPosition(None,positions[1])
      eta_pos = self.formatPosition(None,positions[2])
      mu_pos = self.formatPosition(None,positions[3])
      delta_pos = self.formatPosition(None,positions[4])
      gamma_pos = self.formatPosition(None,positions[5])
      return self.getName() + ".phi : " + phi_pos +"\n" + self.getName() + ".chi : " + chi_pos +"\n" + self.getName() + ".eta : " + eta_pos + "\n" +self.getName() + ".mu : " + mu_pos +"\n" + self.getName() + ".delta : " + delta_pos +"\n" + self.getName() + ".gamma : " + gamma_pos

      
   def toString(self):
      return self.__repr__()
	#
	#  Assume new position is in the form [phi, chi, theta]
	#
   def asynchronousMoveTo(self,new_position):
      # Check new_poition in limits (throws exception if they are not)
      self.checkPositionInLimits(new_position)

      # Move them (RDW) Leaving old limits in for now!!!

      if abs(new_position[1]) <= 99.5: 
         new_positions = self.ekcm.getKPossibleAngles(new_position[2::-1])
         #need a class reference to the correct StoredAngles
         #print "get here"
         #kth.isPositionValid(new_positions.KTheta)
         self.storedAngles.ChangeAngle("Kth",new_positions.KTheta)
#         while self.isBusy() == 1:
#            Thread.sleep(100) 
         self.storedAngles.ChangeAngle("Kap",new_positions.K)
#         while self.isBusy() == 1:
#            Thread.sleep(100) 
         self.storedAngles.ChangeAngle("Kphi",new_positions.KPhi)
         #self.delta.asynchronousMoveTo(new_position[4])
         #self.gam.asynchronousMoveTo(new_position[5])
      else:
         print "Demanded position exceeds chi current limits (-99.5,+99.5)"	

      
	#
	# Returns true if any of the six motors is busy
	#
   def isBusy(self):
      return BLobjects.isBusy()

	#
	# Returns the current Eulerian coordinates as an array
	#
   def getPosition(self):
      angles = self.storedAngles.getAngles()
#      if self.getOffset('Eta') != 0.:
 #        xxx=angles.Eta+self.getOffset('Eta')
#         return [angles.Phi,angles.Chi,xxx,angles.Mu,angles.Delta,angles.Gamma]
      return [angles.Phi,angles.Chi,angles.Eta,angles.Mu,angles.Delta,angles.Gamma]
#      return [angles.Phi,angles.Chi,angles.Eta]


   ####### limit stuff ->
   def displayLimits(self):
     
      print "phi limits: ( " + str(self.limitPhiLow) + " <-> " + str(self.limitPhiHigh) + " )"
      print "chi limits: ( " + str(self.limitChiLow) + " <-> " + str(self.limitChiHigh) + " )"
      print "eta limits: ( " + str(self.limitEtaLow) + " <-> " + str(self.limitEtaHigh) + " )"
   
   def setLimits(self, limName, lowLim, highLim):
      # If both limnts defined, check lowLim <= highLim
      if ((lowLim != None) and (highLim != None)):
         if lowLim > highLim:
            raise Exception("If both limits set, low limit must be less than or equal to high limit.")
      
      # Set limits
    
      if limName == 'phi':
         self.limitPhiLow  = lowLim
         self.limitPhiHigh = highLim
      elif limName == 'chi':
         self.limitChiLow  = lowLim
         self.limitChiHigh = highLim
      elif limName == 'eta':
         self.limitEtaLow  = lowLim
         self.limitEtaHigh = highLim
      else:
         raise Exception("Invalid input name. Must be eta, phi or chi.")
      
   def checkPositionInLimits(self, position):
      # position: [phi, chi, eta]
      Thread.sleep(200)
      print "Requested position: " + str(position)      
      Thread.sleep(1000)
      if (self.limitPhiLow != None):
         if (position[0] < self.limitPhiLow):
            print "<< Attempt to move phi to " + str(position[0]) + " below lower Pseudo Device limit of " + str(self.limitPhiLow) +" FAILED. >>"
            raise Exception("Attempt to move phi to " + str(position[0]) + " below lower Pseudo Device limit of " + str(self.limitPhiLow) +" FAILED.")
      
      if (self.limitPhiHigh != None):
         if (position[0] > self.limitPhiHigh):
            print "<< Attempt to move phi to " + str(position[0]) + " above upper Pseudo Device limit of " + str(self.limitPhiHigh) +" FAILED. >>"
            raise Exception("Attempt to move phi to " + str(position[0]) + " above upper Pseudo Device limit of " + str(self.limitPhiHigh) +" FAILED.")
         
         
      if (self.limitChiLow != None):
         if (position[1] < self.limitChiLow):
            print "<< Attempt to move chi to " + str(position[1]) + " below lower Pseudo Device limit of " + str(self.limitChiLow) +" FAILED. >>"
            raise Exception("Attempt to move chi to " + str(position[1]) + " below lower Pseudo Device limit of " + str(self.limitChiLow) +" FAILED.")
      
      if (self.limitChiHigh != None):
         if (position[1] > self.limitChiHigh):
            print "<< Attempt to move chi to " + str(position[1]) + " above upper Pseudo Device limit of " + str(self.limitChiHigh) +" FAILED. >>"
            raise Exception("Attempt to move chi to " + str(position[1]) + " above upper Pseudo Device limit of " + str(self.limitChiHigh) +" FAILED.")

      if (self.limitEtaLow != None):
         if (position[2] < self.limitEtaLow): 
            print "<< Attempt to move eta to " + str(position[2]) + " below lower Pseudo Device limit of " + str(self.limitEtaLow) +" FAILED. >>"
            raise Exception("Attempt to move eta to " + str(position[2]) + " below lower Pseudo Device limit of " + str(self.limitEtaLow) +" FAILED.")
      
      if (self.limitEtaHigh != None):
         if (position[2] > self.limitEtaHigh):
            print "<< Attempt to move eta to " + str(position[2]) + " above upper lPseudo Device imit of " + str(self.limitEtaHigh) +" FAILED. >>"
            raise Exception("Attempt to move eta to " + str(position[2]) + " above upper Pseudo Device limit of " + str(self.limitEtaHigh) +" FAILED.")
      
      
   ###### <-limit stuff

