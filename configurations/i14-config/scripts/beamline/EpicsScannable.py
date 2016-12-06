"""

Updated 8/1/16 -  Updated createPVMotor and createPVMonitor - use EpicsMotor/Scannable Motor for better handling in 
GDA (units, errors etc. )
 

"""

from gda.device.motor import EpicsMotor
from gda.device.monitor import EpicsMonitor
from gda.device.scannable import EpicsScannable
from gda.device.scannable import ScannableMotor
from gda.jython import InterfaceProvider
from gda.device.scannable import PseudoDevice
from gda.epics import CAClient
from time import sleep,time
from math import log


def createPVMotor( name, pv, addToNameSpace=True):
    """
    utility function to create a scannable from a PV
    arguments:
    name - of scannable
    pv - pv 
    addToNameSpace = if True the scannable is accessible from the commandline after the call
    
    e.g.
    createPVMotor("dcm_braggo","BL14I-OP-DCM-01:BRAGG")
    
    """
    try:
        em = EpicsMotor()
        em.pvName=pv
        em.name = name
        em.configure()
        sc=ScannableMotor()
        sc.motor = em
        sc.name = name
        sc.configure()
        if addToNameSpace:
            commandServer = InterfaceProvider.getJythonNamespace()    
            commandServer.placeInJythonNamespace(name,sc)
        return sc
    except:
        print 'Error creating PVMotor', name
        return None


def createPVMonitor( name, pv, addToNameSpace=True):
    """
    utility function to create a monitor scannable from a PV
    arguments:
    name - of scannable
    pv - pv 
    addToNameSpace = if True the scannable is accessible from the commandline after the call
    
    e.g.
    createPVMonitor("dblah","BL14I-DI-PHDGN-03:FEMTO2:I")
    """
    try:
        sc = EpicsMonitor()
        sc.pvName=pv
        sc.name = name
        sc.configure()
        if addToNameSpace:
            commandServer = InterfaceProvider.getJythonNamespace()    
            commandServer.placeInJythonNamespace(name,sc)
        return sc
    except:
        print 'Error creating PVMonitor', name
        return None


class ExafsDetector(PseudoDevice):
    """
    records  log(i0/it)
    Arguments:
    name  -  of scannable
    i0    -  existing i0 monitor to use
    it    -  existing it monitor to use
     
    exafs_scatter = ExafsDetector("exafs_scatter",d3_diode1,d4_diode2)
    
    
    """
    def __init__(self, name, i0,it):
            self.setName(name);
            self.setInputNames([name])
            self.setOutputFormat(["%5.5g"])
            self.iambusy=False
            self.i0=i0
            self.it=it

    def rawGetPosition(self):
            self.iambusy=1
            i0val=float(self.i0.getPosition())
            itval=float(self.it.getPosition())
            self.iambusy=0
            return log(i0val/itval)
            
    def rawAsynchronousMoveTo(self,position):
            pass

    def rawIsBusy(self):
            return self.iambusy
    

class RatioDetector(PseudoDevice):
    """
    records  log(i0/it)
    Arguments:
    name  -  of scannable
    i0    -  existing i0 monitor to use
    it    -  existing it monitor to use
     
    exafs_scatter = ExafsDetector("exafs_scatter",d3_diode1,d4_diode2)
    
    
    """
    def __init__(self, name, i0,it):
            self.setName(name);
            self.setInputNames([name])
            self.setOutputFormat(["%5.5g"])
            self.iambusy=False
            self.i0=i0
            self.it=it

    def rawGetPosition(self):
            self.iambusy=1
            i0val=float(self.i0.getPosition())
            itval=float(self.it.getPosition())
            self.iambusy=0
            return i0val/itval
            
    def rawAsynchronousMoveTo(self,position):
            pass

    def rawIsBusy(self):
            return self.iambusy
    


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

def caputStringAsWaveform(pv, val):
    """
    Usage: "caputStringAsWaveform BL13J-OP-ACOLL-01:AVERAGESIZE" "This is some text"
    """
    CAClient.putStringAsWaveform(pv, val)
    
#===============================================================================
# class DummyDetector(PseudoDevice):
#     def __init__(self, name, unitstring, formatstring):
#             self.setName(name);
#             self.setInputNames([])
#             self.setExtraNames([name])
#             self.Units=[unitstring]
#             self.setOutputFormat([formatstring])
#             self.iambusy=False
#             self.pausetime=1.0
# 
#     def rawGetPosition(self):
#             return self.pausetime
# 
#     def rawAsynchronousMoveTo(self,position):
#             self.pausetime=position
#             self.iambusy=True
#             sleep(position)
#             self.iambusy=False
#             
#     def rawIsBusy(self):
#             return self.iambusy
#===============================================================================
#===============================================================================
# class DummyTime(PseudoDevice):
#     def __init__(self, name, unitstring, formatstring):
#             self.setName(name);
#             self.setInputNames([])
#             self.setExtraNames([name])
#             self.Units=[unitstring]
#             self.setOutputFormat([formatstring])
#             self.starttime = 0.0
#             
#             
#     def resetStart(self):
#         self.starttime=time()
# 
#     def rawGetPosition(self):
#             currenttime=time()
#             return currenttime - self.starttime
# 
#     def rawAsynchronousMoveTo(self,position):
#             pass
# 
#     def rawIsBusy(self):
#             return False
#===============================================================================

#===============================================================================
# def createPVScannable( name, pv, addToNameSpace=True, hasUnits=True, getAsString=False):
#     """
#     utility function to create a scannable from a PV
#     arguments:
#     name - of scannable
#     pv - pv 
#     addToNameSpace = if True the scannable is accessible from the commandline after the call
#     hasUnits - default True. The value is a number  and support is given for setUserUnits
#     getAsString - default False. Useful if the PV is an enum as it returns the string representation. 
#                  If true also set hasUnits to False 
#     
#     e.g.
#     createPVScannable("acoll_average_size", "BL13J-OP-ACOLL-01:AVERAGESIZE", True)
#     """
#     sc = EpicsScannable()
#     sc.setName(name)
#     sc.setPvName(pv)
#     sc.setUseNameAsInputName(True)
#     sc.setHasUnits(hasUnits)
#     sc.setGetAsString(getAsString)
#     sc.afterPropertiesSet()
#     sc.configure()
#     if addToNameSpace:
#         commandServer = InterfaceProvider.getJythonNamespace()    
#         commandServer.placeInJythonNamespace(name,sc)
#     return sc
# 
# def ls_pv_scannables( PV=""):
#     """
#     Function to list Scannables associated with EPICs PVs, the PV and the associated DESC field
#     Usage:
#         >ls_pv_scannables()
#     
#     or
#     
#         >ls_pv_scannables(<PV>)
#     """
#     from gda.device.scannable import ScannableMotor
#     from gda.device.motor import EpicsMotor
#     scannableConnectedToPV=None
#     a=InterfaceProvider.getJythonNamespace().getAllFromJythonNamespace()
#     l=filter(lambda x: isinstance(x, EpicsScannable) or (isinstance(x, ScannableMotor) and isinstance(x.motor, EpicsMotor)), a.values().toArray())
#     for x in l:
#         description="unknown"
#         pvName ="unknown"
#         if isinstance(x, EpicsScannable):
#             pvName=x.pvName
#         if isinstance(x, ScannableMotor) and isinstance(x.motor, EpicsMotor):
#             pvName=x.motor.pvName
#             
#         if PV != "":
#             if PV.upper() == pvName.upper():
#                 scannableConnectedToPV=x
#                 break
#         else:
#             if x.configured:
#                 try:
#                     description = caget(pvName + ".DESC")
#                 except:
#                     description = "Unable to read description"
#                     pass
#             else:
#                 description = "Not configured!"
#             print x.name, pvName, description
# 
#     if PV != "":
#         if scannableConnectedToPV is None:
#             print "No scannable found for PV " + PV
#         print "Scannable " + x.name  + " is connected to ", PV
#     
#     
#===============================================================================

