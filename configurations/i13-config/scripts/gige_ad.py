from gda.device.detector import DetectorDeletegator
from scisoft import dnp
class NXDetectorDataToNXDetectorDataWithFilepathForSrsConverterScannable(DetectorDeletegator):
    def __init__(self, delegate):
        super.__init__(self, delegate)
    def readout(self):
        data = super.readout()
        dat=data.getData(super.getName(),"data","SDS")
        ds = dnp.array(dat.getBuffer()).reshape(dat.dimensions[0], data.dimensions[1])
        if self.filepath is not None:
            self.saveImage(time.strftime("%Y%m%d%H%M%S.png", time.localtime()))
        
        
        