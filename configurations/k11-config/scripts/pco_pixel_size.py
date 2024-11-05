from gda.device.monitor import MonitorBase  # @UnresolvedImport
from gda.epics import LazyPVFactory  # @UnresolvedImport
from gdascripts.metadata.nexus_metadata_class import meta  # @UnresolvedImport

class PCOPixelSize(MonitorBase):
    '''
    Meta device to inject PCO pixel size (0.54 μm x binning) into NeXus files
    '''
    ABSOLUTE_PIXEL_SIZE = 0.54
    
    def __init__(self, name, binning_pv):
        self.setName(name)
        self.binning_pv = LazyPVFactory.newIntegerPV(binning_pv)

    def rawGetPosition(self):
        return PCOPixelSize.ABSOLUTE_PIXEL_SIZE * self.binning_pv.get()
    
    def getUnit(self):
        return "um"


pco_px_x = PCOPixelSize("pco_px_x", "BL11K-EA-PCO-01:CAM:BinX_RBV")
pco_px_y = PCOPixelSize("pco_px_y", "BL11K-EA-PCO-01:CAM:BinY_RBV")

meta.addScannable("Imaging", pco_px_x)
meta.addScannable("Imaging", pco_px_y)
