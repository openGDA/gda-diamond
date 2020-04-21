import gda
from gdaserver import GDAMetadata as meta

def setTitle(title):
    meta["title"] = title

def getTitle():
    return meta["title"]

def setVisit(visit):
#     user = meta["federalid"]
#     if user != "p38user":
#         oldvisit = meta["visit"]
#         try:
#             ElogEntry.post("visit manually changed from %s to %s by %s" % (oldvisit, visit, user), "", "gda", None, "BLI22", "BLI22-USR", None)
#         except:
#             pass
    meta["visit"] = visit

def getVisit():
    return meta["visit"]

def setSubdirectory(title):
    meta["subdirectory"] = title

def getSubdirectory():
    return meta["subdirectory"]

def setSampleBackground(back_ground_file):
    meta["sample_background"] = back_ground_file

def getSampleBackground():
    return meta["sample_background"]

class SampleNameScannable(gda.device.scannable.ScannableBase):
    """ This is the constructor for the class. """
    def __init__(self, name, metadataname):
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(["%s"])
        self.metadata = gda.factory.Finder.getInstance().find(metadataname)

    """ Mandatory method.  It should return 1 if the device is moving and 0 otherwise."""
    def isBusy(self):
        return False

    """ Mandatory method.  Return the current position as a scalar or as a vector."""
    def getPosition(self):
        return self.metadata.readActualValue()

    """ Mandatory method.  Must return immediately; the move should be controlled by a separate thread."""
    def asynchronousMoveTo(self, newPosition):
        self.metadata.setValue(newPosition) 

