from gda.util import ElogEntry
from gda.data.metadata import GDAMetadataProvider
import gda.device.scannable.ScannableBase
from gda.factory import Finder
from gda.configuration.properties import LocalProperties

def setSubdirectory(title):
    GDAMetadataProvider.getInstance().setMetadataValue("subdirectory", title)

def getSubdirectory():
    return GDAMetadataProvider.getInstance().getMetadataValue("subdirectory")

def setVisit(visit):
    user=GDAMetadataProvider.getInstance().getMetadataValue("federalid")
    beamline = LocalProperties.get("gda.beamline.name")
    beamline_user = beamline+"user"
    if user != beamline_user:
        oldvisit = GDAMetadataProvider.getInstance().getMetadataValue("visit")
        if beamline == "i05":
            beamline_epics = "BL05I"
        elif beamline == "i05-1":
            beamline_epics = "BL05J"
        try:
            ElogEntry.post("visit manually changed from %s to %s by %s" % (oldvisit, visit, user),
                            "", "gda", None, beamline_epics, beamline_epics+"-USR", None)
        except:
            pass
    GDAMetadataProvider.getInstance().setMetadataValue("visit", visit)

def getVisit():
    return GDAMetadataProvider.getInstance().getMetadataValue("visit")


class SampleNameScannable(gda.device.scannable.ScannableBase):

    """ This is the constructor for the class. """
    def __init__(self, name, metadataname, isgoldpost=None):
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(["%s"])
        self.metadata=Finder.find(metadataname)
        self.isgoldpost=isgoldpost

    def getfalse(self):
        return False

    """ Mandatory method.  It should return 1 if the device is moving and 0 otherwise."""
    def isBusy(self):
        return False

    """ Mandatory method.  Return the current position as a scalar or as a vector."""
    def getPosition(self):
        if (self.isgoldpost != None) and self.isgoldpost():
            return "Gold"
        return self.metadata.readActualValue()

    """ Mandatory method.  Must return immediately; the move should be controlled by a separate thread."""
    def asynchronousMoveTo(self,new_position):
        self.metadata.setValue(new_position)

