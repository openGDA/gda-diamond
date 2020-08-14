from gda.device.scannable import ScannableBase

""" Scannable to be use as base for 'default' scannables; override atScanStart atScanEnd etc with suitable implementations.
    atScanEnd is called if exception is thrown during the scan
"""
class DefaultScannable(ScannableBase):

    def __init__(self, name):
        self.name = name
        self.inputNames = [name]
        self.setOutputFormat({});
        self.setInputNames({});

    def stop(self):
        self.atScanEnd()

    def atCommandFailure(self):
        self.atScanEnd()

    def isBusy(self):
        return False

    def rawAsynchronousMoveTo(self,new_position):
        pass

    def rawGetPosition(self):
        return None

# Switch Xspress4 Mca PVs off at start of scan and back on at the end.
# This uses setEnableMca(True|False) function from detector_setup_functions.py file.
from gda.jython import InterfaceProvider
class Xspress4McaSwitcher(DefaultScannable) :
    
    def setDetectorNames(self, detectorNames):
        self.detectorNames = detectorNames
        
    def atScanStart(self):
        if self.hasDetector() :
            print "Switching Xspress4 MCA PVs off"
            self.switchMcas(False)
    
    def atScanEnd(self):
        if self.hasDetector() :
            print "Switching Xspress4 MCA PVs on"
            self.switchMcas(True)
    
    def switchMcas(self, enable):
        try :
            setEnableMca(enable)
        except :
            print "Problem setting MCA enable state to %s"%(enable)
            pass
    
    def hasDetector(self):
        try :
            inf = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation()
            for detName in self.detectorNames :
                if detName in inf.getDetectorNames() :
                    return True
            return False
        except :
            ## Do nothing
            pass
        return False

## Remove any previously added default scannable
try :
    remove_default xsp4McaSwitcher
except :
    pass

xsp4McaSwitcher = Xspress4McaSwitcher("xsp4McaSwitcher")
xsp4McaSwitcher.setDetectorNames({xspress4.getName(), qexafs_xspress4.getName()})
add_default xsp4McaSwitcher
