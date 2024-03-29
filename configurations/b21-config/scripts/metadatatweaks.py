import os
import gda
from gda.util import ElogEntry
from gda.data.metadata import GDAMetadataProvider
from gda.jython import InterfaceProvider
from gda.configuration.properties import LocalProperties

def _valid_visit(visit):
    visit_drectory = InterfaceProvider.getPathConstructor().createFromProperty(LocalProperties.GDA_VISIT_DIR, {"visit": visit})
    return os.path.exists(visit_drectory) and os.path.isdir(visit_drectory)

def setTitle(title):
    GDAMetadataProvider.getInstance().setMetadataValue("title", title)

def getTitle():
    return GDAMetadataProvider.getInstance().getMetadataValue("title")

def setVisit(visit):
    user=GDAMetadataProvider.getInstance().getMetadataValue("federalid")
    if not _valid_visit(visit):
        raise ValueError(visit + " is not a valid visit")
    if user != "b21user":
        oldvisit = GDAMetadataProvider.getInstance().getMetadataValue("visit")
        try:
            ElogEntry.post("visit manually changed from %s to %s by %s" % (oldvisit, visit, user), "", "gda", None, "BLB21", "BLB21-USR", None)
        except:
            pass
    GDAMetadataProvider.getInstance().setMetadataValue("visit", visit)

def getVisit():
    return GDAMetadataProvider.getInstance().getMetadataValue("visit")

def setSubdirectory(title):
    GDAMetadataProvider.getInstance().setMetadataValue("subdirectory", title)

def getSubdirectory():
    return GDAMetadataProvider.getInstance().getMetadataValue("subdirectory")


class SampleNameScannable(gda.device.scannable.ScannableBase):
  
   """ This is the constructor for the class. """
   def __init__(self, name, metadataname):
       self.setName(name)
       self.setInputNames([name])
       self.setOutputFormat(["%s"])
       self.metadata=gda.factory.Finder.find(metadataname)

   """ Mandatory method.  It should return 1 if the device is moving and 0 otherwise."""
   def isBusy(self):
       return False

   """ Mandatory method.  Return the current position as a scalar or as a vector."""
   def getPosition(self):
       return self.metadata.readActualValue()
 
   """ Mandatory method.  Must return immediately; the move should be controlled by a separate thread."""
   def asynchronousMoveTo(self,newPosition):
       self.metadata.setValue(newPosition) 

