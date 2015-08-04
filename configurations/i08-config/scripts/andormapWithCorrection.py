from gda.device.detector.nxdetector.andor.proc.FlatAndDarkFieldPlugin import ScanType
from gda.device.detector.nxdetector.andor.proc import FlatAndDarkFieldPlugin
from andormap import AndorMap
import time
from gda.epics import CAClient
from gda.device.scannable import DummyScannable
from gda.device.detector.addetector.triggering.HardwareTriggeredAndor import AndorTriggerMode


class AndorMapWithCorrection(AndorMap):

    def __init__(self, rowScannable, columnScannable, andor,scanForImageCorrection):
        AndorMap.__init__(self,rowScannable,columnScannable,andor)
        self.scanForImageCorrection = scanForImageCorrection
        self.exposureTime = 1
        self.enableDark = False
        self.enableFlat = False

    def __call__(self, *args):
        scannable = DummyScannable()
        scannable.setName("correctionDummy")
        if (self.enableDark == True):
            self.configureArrayPlugin()
            self.scanForImageCorrection.createScanForImageCorrection(ScanType.DARK_FIELD,scannable,self.exposureTime)
        if (self.enableFlat == True):
            self.configureArrayPlugin()
            self.scanForImageCorrection.createScanForImageCorrection(ScanType.FLAT_FIELD,scannable,self.exposureTime)

        del scannable
        FlatFieldAndDarkFielPluginExists = False
        self.configureArrayPlugin()

        for item in self.andor.getAdditionalPluginList()[:]:
            if isinstance(item,FlatAndDarkFieldPlugin):
                item.setScanType(ScanType.CORRECTED_IMAGES)
                AndorMap.__call__(self,*args)
                FlatFieldAndDarkFielPluginExists = True
                break
        if FlatFieldAndDarkFielPluginExists == False:
            raise Exception('Flat and Dark Field plugin is not in the andor plugin list')

    def setExposureTime(self,exposureTime):
        self.andor.getCollectionStrategy().getADBase().setAcquireTime(exposureTime)
        self.exposureTime = self.andor.getCollectionStrategy().getAdBase().getAcquireTime()

    def configureArrayPlugin(self):
        CAClient().put("BL08I-EA-DET-01:ARR:NDArrayPort","DET1.proc")
        time.sleep(1)
        CAClient().put("BL08I-EA-DET-01:ARR:ArrayCounter","0")
        time.sleep(1)

    def isEnableDarkAndFlat(self,enable):
        self.enableDark = enable
        self.enableFlat = enable

    def isEnableDark(self,enable):
        self.enableDark = enable

    def isEnableFlat(self,enable):
        self.enableFlat = enable
