print "removing defaults"
remove_default meta
remove_default ic1monitor
remove_default rc
#remove_default waitforinjection

print "clearing all ROI"
for _roi in (roi1, roi2, roi3, roi4, roi5, roi6, roi7):
    _roi.setRoi(None)


print "removing pil processing and creating max2d"
pil.processors = []
max2d=HardwareTriggerableDetectorDataProcessor('max2d', pil, [SumMaxPositionAndValue()], prefix_name_to_extranames=False)
pil.panelNameRCP = "Plot 1"
pil.panel_name_rcp = "Plot 1"
# scans
print "removing most scan processors and time printing"
scan_processor.duplicate_names = {}
scan_processor.processors = [scan_processor.processors[0], scan_processor.processors[3]]
gdascripts.scan.concurrentScanWrapper.PRINTTIME = False

# trajscans
PERFORM_SECOND_SCAN_TO_SHOW_ACTUAL_POSITIONS = False

import Azimuth as _azimuth_module
_azimuth_module.VERBOSE = False

class DummyShutter(ScannableBase):
    
    def __init__(self, name):
        self.name = name
        self.inputNames = []
        self.extraNames = []
        self.outputFormates = []
        
    def waitWhileBusy(self):
        return
    
    def isBusy(self):
        return
    
    def getPosition(self):
        return None
    
    def atScanStart(self):
        print "### Opening shutter"
        sleep(2)

    def atScanEnd(self):
        print "### Closing shutter"
        sleep(2)
        
slowshutter = DummyShutter('slowshutter')

dt = inctime
dt.name = "dt"

print """
rscan ?
scan x _ _ _
scan x _ _ _ ct2 .5
scan x _ _ _ rc ct2 .5
scan x _ _ _ rc ct2 .5 slowshutter
list_defaults

##change delta offset##
scan x _ _ _ pil .5
scan x _ _ _ pil .5 max2d
scan x 1 100 1 pil .01 max2d dt

scan hkl ?

trajscan delta mcs2 .05 pil .05 max2d
trajscan hkl
"""