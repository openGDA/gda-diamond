from gda.scan import ConstantVelocityRasterScan
from gdascripts.scan import rasterscans
from gdascripts.scan.rasterscans import RasterScan
from gdascripts.scan.trajscans import setDefaultScannables


class AndorMap(RasterScan):
     
    def __init__(self,rowScannable,columnScannable,andor):
        RasterScan.__init__(self)
        self.map_size = 50 # default
        self.rowScannable = rowScannable
        self.columnScannable = columnScannable
        self.andor = andor
         
         
    def __call__(self, *args):

        # if one arg, then use that as the map size, else ignore any and all args
        if len(args) == 1:
            self.map_size = int(args[0])
        else :
            from gda.epics import CAClient
            self.map_size = CAClient().get("BL08I-EA-DET-01:HDF5:ExtraDimSizeX_RBV")
            print "Map size will be",str(self.map_size)
        self.scanargs = [self.rowScannable, 1, float(self.map_size), 1, self.columnScannable, 1, float(self.map_size), 1, self.andor, 0.1]
        RasterScan.__call__(self,self.scanargs)
     
    def _createScan(self, args):

        # TODO create/ configure a scannable which will oberve data points and broadcast out transmission/phase-contrast to plotting system
        
        # TODO get scan size from Epics PVs to replace self.map_size
        
        # TODO check Epics PV holding STXM status as a safety check

        #rasterscan row 1 20 1 col 1 20 1 _andorrastor .1 'col'
#         args = [self.rowScannable, 1, float(self.map_size), 1, self.columnScannable, 1, float(self.map_size), 1, self.andor]
        myscan = ConstantVelocityRasterScan(self.scanargs)
        
        # TODO set a PV to tell stxm the scan number
        #scanNumber = scan.getScanNumber()
        
        # TODO tell the stxm the scan number, or the file prefix at this point

        return myscan
        
# first, configure the ROIs for both the step and raster andor objects
print "Setting up Regions of Interest for andor and _andorrastor objects..."
andor.roistats1.setRoi(0,0,256,256,"quadrant1")
andor.roistats2.setRoi(0,256,256,256,"quadrant2")
andor.roistats3.setRoi(256,0,256,256,"quadrant3")
andor.roistats4.setRoi(256,256,256,256,"quadrant4")
andor.roistats5.setRoi(0,0,512,512,"transmission")
_andorrastor.roistats1.setRoi(0,0,256,256,"quadrant1")
_andorrastor.roistats2.setRoi(0,256,256,256,"quadrant2")
_andorrastor.roistats3.setRoi(256,0,256,256,"quadrant3")
_andorrastor.roistats4.setRoi(256,256,256,256,"quadrant4")
_andorrastor.roistats5.setRoi(0,0,512,512,"transmission")

# then create the scan wrapper for map scans
# col = stxmDummy.stxmDummyX
# row = stxmDummy.stxmDummyY
andormap = AndorMap(stxmDummy.stxmDummyY,stxmDummy.stxmDummyX,_andorrastor)
print "Command andormap() created for arming the Andor detector before running STXM maps"
