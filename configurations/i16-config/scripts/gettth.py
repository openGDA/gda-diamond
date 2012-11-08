## @file gettth.py  contains the class calculating the Bragg angle
#  @author Alessandro Bombardi
#  @version 1.0 (alpha release)
#  Please report bugs to Alessandro.Bombardi@diamond.ac.uk
#  Diamond Light Source Ltd.
#
#
import java
from math import *
import beamline_info as BLi

## Calculates the Bragg angle
#
class gettth(java.lang.Object):



   ## Establish a link with the Crystal class
   #
   def setCrystalmanagement(self,x):
      self.cry=x
      return

   ## Establish a link with the RecSpace class
   #
   def setRecSpaceManagement(self,x):
      self.hkl=x
      return

   ## public double calctth(hkl=None,energy=None,d_hkl=None)
   #
   def calctth(self,hkl=None,energy=None,Y=None):
      "@sig public double double []"
      try:
         if hkl == None:
            hkl=self.hkl.getHKL()
         if energy == None:
            energy=BLi.getEnergy()
         if Y == None:
            Y=self.cry.d_hkl(hkl)
         X=12.39842/energy
         ret=2.0*asin(X/(Y*2))*180.0/pi
      except:
         print "gettth::calctth:The reflection is not accessible @ this energy?"
         ret="gettth::calctth:The reflection is not accessible @ this energy?"
      return ret

   ## Throws an error Message
   #
   def __repr__(self):
      return '<gettth bean error>'


