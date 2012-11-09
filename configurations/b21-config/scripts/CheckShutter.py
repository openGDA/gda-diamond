import java
import gda.device.scannable.ScannableBase
from time import sleep

"""
    Purpose:     check shutter status at start
    Author:      Tobias Richter
    Date:        2007-2008

    Mandatory methods for Pseudo Devices:
        isBusy(self)
        getPosition(self)
        asynchronousMoveTo(self,newPosition)
"""
 
class CheckShutter(PseudoDevice):
  
   """ This is the constructor for the class. """
   def __init__(self):
       self.setName("shutterChecker")
       self.setInputNames(["shutterChecker"])
       self.shutterObj=shutter
       self.setOutputFormat(["%1.0f"])

   """ Mandatory method.  It should return 1 if the device is moving and 0 otherwise."""
   def isBusy(self):
       return 0
       #return getPositon(self)

   """ Mandatory method.  Return the current position as a scalar or as a vector."""
   def getPosition(self):
       if (shutter.getPosition() == "Open"):
           return 0
       else:
           return 1
 
   """ Mandatory method.  Must return immediately; the move should be controlled by a separate thread."""
   def asynchronousMoveTo(self,newPosition):
       return 

   def atScanStart(self):
       if self.getPosition() == 0:
          return
       else:
          print "your shutter appears to be closed"
          print "maybe you want to abort the scan?"
          print "sleeping for some seconds"
          sleep(5)

   
shutterChecker=CheckShutter()

