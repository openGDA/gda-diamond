from gda.device.detector import DetectorBase
from gda.device.scannable import TwoDScanPlotter
from gda.scan import ConstantVelocityRasterScan
from gdascripts.scan.concurrentScanWrapper import ConcurrentScanWrapper
from gdascripts.scan.trajscans import setDefaultScannables
from gdascripts.utils import caput_wait
import random

DEFAULT_SCANNABLES_FOR_RASTERSCANS = []

class DetectorDummy(DetectorBase):
    
    '''Dummy PD Class'''
    def __init__(self, name):
        self.name = name
        
    def isBusy(self):
        return 0

    def readout(self):
#         return self.getCollectionTime()
        return abs(random.gauss(self.getCollectionTime(), 1))


def pieplotter(ystart, ystop, ystep, xstart, xstep, xstop, zname):
    _plotter = TwoDScanPlotter()
    _plotter.setPlotViewname('Plot 2')
    #_plotter.setX_colName('pieX')
    #_plotter.setY_colName('pieY')
    _plotter.setZ_colName(zname)
    _plotter.setName('pieplotter_' + zname)
    _plotter.setXArgs(xstart, xstep, xstop)
    _plotter.setYArgs(ystart, ystop, ystep)
    return _plotter


def xyplotter(ystart, ystop, ystep, xstart, xstep, xstop, zname):
    _plotter = TwoDScanPlotter()
    _plotter.setPlotViewname('Plot 2')
    #_plotter.setX_colName('x')
    #_plotter.setY_colName('y')
    _plotter.setZ_colName(zname)
    _plotter.setName('xylotter_' + zname)
    _plotter.setXArgs(xstart, xstep, xstop)
    _plotter.setYArgs(ystart, ystop, ystep)
    return _plotter


def setup_overlay_plugin(pvbase_det='BL16I-EA-DET-30:'):
    for i in range(1, 7):
        pvbase_roi = pvbase_det + 'ROI' + str(i) + ':'
        pvbase_overlay = pvbase_det + 'OVER:' + str(i) + ':'
        _link_overlay_to_roi_plugin_and_enable(pvbase_roi, pvbase_overlay)
        caput_wait(pvbase_overlay + 'Name', 'roi' + str(i))
    caput_wait(pvbase_det + 'OVER:EnableCallbacks', True)


def _link_overlay_to_roi_plugin_and_enable(pvbase_roi='BL16I-EA-DET-30:ROI1:',
                                           pvbase_overlay='BL16I-EA-DET-30:OVER:1:'):
    
    caput_wait(pvbase_overlay + 'Use', True)
    caput_wait(pvbase_overlay + 'Shape', 'Rectangle')
    caput_wait(pvbase_overlay + 'DrawMode', 'XOR')
    
    caput_wait(pvbase_overlay + 'PositionXLink.DOL', pvbase_roi + 'MinX_RBV CP')
    caput_wait(pvbase_overlay + 'SizeXLink.DOL', pvbase_roi + 'SizeX_RBV CP')

    caput_wait(pvbase_overlay + 'PositionYLink.DOL', pvbase_roi + 'MinY_RBV CP')
    caput_wait(pvbase_overlay + 'SizeYLink.DOL', pvbase_roi + 'SizeY_RBV CP')


class RasterScan(ConcurrentScanWrapper):
    """USAGE:
    
  rasterscan scnY start stop step scnX start stop step det [time] [det [time]] ... ['column_name']

  e.g.: scan pieY 1 100 1 pieX 1 100 1 rasterpil1 .1 'roi1_total'
        
        Use scan.yaxis = 'axis_name' to determine which axis will be analysed and plotted by default.
        
"""
    def __init__(self, scanListeners = None):
        ConcurrentScanWrapper.__init__(self, returnToStart=False, relativeScan=False, scanListeners=scanListeners)
    
    def convertArgStruct(self, argStruct):
        return argStruct  # ConstantVelocityRasterScan will check args for validiy
    
    def parseArgsIntoArgStruct(self, args):
        args = list(args)
        args = self._tweaks_args(args)
        return ConcurrentScanWrapper.parseArgsIntoArgStruct(self, args)
    
    def _tweaks_args(self, args):
        yscn, ystart, ystop, ystep, xscn, xstart, xstep, xstop = args[0:8]
        del yscn  # unused
        
        # ConstantVelocityRasterScan does not properly set the user listed scannables
        # which would otherwise determine the x axis name automatically
        self.xaxis = xscn.name

        
        # Replace last arg with a raster plotter if a string
        if isinstance(args[-1], str):
            zname = args[-1]
            print "'Plot 2' will show: " + zname
            args[-1] = pieplotter(ystart, ystop, ystep, xstart, xstep, xstop, zname)
            self.yaxis = zname
        else:
            print "'Plot 2' will show nothing"
        
        return args
    
    def _createScan(self, args):
        original_default_scannables = setDefaultScannables(DEFAULT_SCANNABLES_FOR_RASTERSCANS)
        try:
            scan = ConstantVelocityRasterScan(args)
        finally:
            setDefaultScannables(original_default_scannables)
        return scan
