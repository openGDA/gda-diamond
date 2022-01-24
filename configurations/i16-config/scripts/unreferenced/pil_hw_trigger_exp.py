from gda.device.detector.addetector.triggering import HardwareTriggeredPilatus
from gda.device.detector import HardwareTriggeredNXDetector
from gda.device.detector.areadetector.v17.ADDriverPilatus import PilatusTriggerMode
from pd_dummy import dummyClass

class FixedImageCountHwTrigger(HardwareTriggeredPilatus):
    def __init__(self, adBase, driver, readoutTime, triggerMode, trigger, num_images=1):
        HardwareTriggeredPilatus.__init__(self, adBase, driver, readoutTime, triggerMode)
        self.num_images = num_images
        self.trigger = trigger

    def prepareForCollection(self, collectionTime, numImages, scanInfo):
        self.trigger.moveTo(0)
        return HardwareTriggeredPilatus.prepareForCollection(
                self, collectionTime, self.num_images, scanInfo)

    def collectData(self):
        self.trigger.moveTo(1)
        HardwareTriggeredPilatus.collectData(self)


pil1_adbase = zebrapil1.collectionStrategy.adBase
pil1_driver = zebrapil1.collectionStrategy.adDriverPilatus
exec("pil1_triggering = FixedImageCountHwTrigger( \
        pil1_adbase, pil1_driver, .003, \
        PilatusTriggerMode.MULTIPLE_EXTERNAL_TRIGGER,\
        x2_ttl)")

exec("pil1_hw = HardwareTriggeredNXDetector()")
pil1_hw.name = "pil1_hw" 
pil1_hw.collectionStrategy = pil1_triggering
pil1_hw.additionalPluginList = zebrapil1.additionalPluginList
