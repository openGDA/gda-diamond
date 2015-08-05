from gda.scan import ConcurrentScan
from gda.device.detector.nxdetector.andor.proc import FlatAndDarkFieldPlugin
from gda.device.detector.nxdetector.andor.proc.FlatAndDarkFieldPlugin import ScanType
from gda.jython.commands.Input import requestInput

class ScanForImageCorrection:

    def __init__(self, andor):
        self.andor=andor

    def createScanForImageCorrection(self,scanType, scannable,exposureTime):
        self.scanType = scanType
        self.scannable = scannable
        self.exposureTime = exposureTime
        print "Exposure time is ", self.exposureTime
        isReady = self.prepareForCollection()
        if (isReady == True):
            self.doCollection()

    def prepareForCollection(self):
        if self.scanType == ScanType.DARK_FIELD:
            str = requestInput("Waiting for dark field setup  ... When finished press a key")
        elif  self.scanType == ScanType.FLAT_FIELD:
            str = requestInput("Waiting for flat field setup  ... When finished press a key")
        FlatFieldAndDarkFielPluginExists = False
        for item in self.andor.getAdditionalPluginList()[:]:
            if isinstance(item,FlatAndDarkFieldPlugin):
                item.setScanType(self.scanType)
                self.scanargs = [self.scannable, 0, 0, 1, self.andor, self.exposureTime]
                FlatFieldAndDarkFielPluginExists = True
                break
        if FlatFieldAndDarkFielPluginExists != True:
            raise Exception('Flat and Dark Field plugin is not in the andor plugin list')
        return FlatFieldAndDarkFielPluginExists

    def doCollection(self):
        thisscan = ConcurrentScan(self.scanargs)
        print 'Running scan'
        thisscan.runScan()