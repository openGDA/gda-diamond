from gda.jython import InterfaceProvider
from gda.device.scannable import EpicsScannable
def createPVScannable( name, pv, addToNameSpace=True, hasUnits = True):
    """
    utility function to create a scannable from a PV
    arguments:
    name - of scannable
    pv - pv 
    addToNameSpace = if True the scannable is accessible from the commandline after the call
    
    e.g.
    createPVScannable("acoll_average_size", "BL13J-OP-ACOLL-01:AVERAGESIZE", True)
    """
    sc = EpicsScannable()
    sc.setName(name)
    sc.setPvName(pv)
    sc.setUseNameAsInputName(True)
    sc.setHasUnits(hasUnits)
    sc.afterPropertiesSet()
    sc.configure()
    if addToNameSpace:
        commandServer = InterfaceProvider.getJythonNamespace()    
        commandServer.placeInJythonNamespace(name,sc)
    return sc

from gda.device.scannable import EpicsScannable
from gda.epics import CAClient

def caput(pv,val):
    """
    Usage: "caput BL13J-OP-ACOLL-01:AVERAGESIZE" "10"
    """
    CAClient.put(pv, val)

def caget(pv):
    """
    Usage: "caget BL13J-OP-ACOLL-01:AVERAGESIZE"
    """
    return CAClient.get(pv)

