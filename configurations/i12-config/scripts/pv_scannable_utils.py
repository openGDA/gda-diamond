from gda.jython import InterfaceProvider
from gda.device.scannable import EpicsScannable
def createPVScannable( name, pv, addToNameSpace=True, hasUnits = True):
    """
    utility function to create a scannable from a given PV
    arguments:
    name - user-specified name of a scannable to be created, e.g. dac01_0 
    pv - EPICS identifier of pv to be used by the scannable, e.g. BL12I-EA-DAC-01:00
    addToNameSpace = if True, the scannable is accessible from the commandline after the call
    
    e.g.
    createPVScannable("dac01_0", "BL12I-EA-DAC-01:00", True)
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
    Usage: "caput BL12I-EA-DAC-01:00" "1.2"
    """
    CAClient.put(pv, val)

def caget(pv):
    """
    Usage: "caget BL12I-EA-DAC-01:00"
    """
    return CAClient.get(pv)

