from gda.device.scannable import TwoDScanSwingPlotter, TwoDScanPlotter

import random
from gdascripts.scan.concurrentScanWrapper import ConcurrentScanWrapper
from gda.scan import ConstantVelocityRasterScan
from gda.device.detector import DetectorBase
from gdascripts.utils import caput_wait, caput_string2waveform


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
    
    _plotter = TwoDScanSwingPlotter()
    _plotter.setSwingPlotViewName('Medipix')
    _plotter.setX_colName('pieX')
    _plotter.setY_colName('pieY')
    _plotter.setZ_colName(zname)
    _plotter.setName('pieplotter_' + zname)
    _plotter.setXArgs(xstart, xstep, xstop)
    _plotter.setYArgs(ystart, ystop, ystep)
    return _plotter


def xyplotter(ystart, ystop, ystep, xstart, xstep, xstop, zname):
    
    _plotter = TwoDScanSwingPlotter()
    #_plotter = TwoDScanPlotter()
    _plotter.setSwingPlotViewName('Medipix')
    _plotter.setX_colName('x')
    _plotter.setY_colName('y')
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
    
  rasterscan scn1 start stop step [scnN [start [stop [step]]]] ...

  e.g.: scan pieY 1 100 1 pieX 1 100 1 det .1 pieplotter(1, 100, 1, 1, 100, 1, 'roi1_total')
        
        Use scan.yaxis = 'axis_name' to determine which axis will be analysed and plotted by default.
        
"""
    def __init__(self, scanListeners = None):
        ConcurrentScanWrapper.__init__(self, returnToStart=False, relativeScan=False, scanListeners=scanListeners)
    
    def convertArgStruct(self, argStruct):
        return argStruct  # ConstantVelocityRasterScan will check args for validiy
    
    def _createScan(self, args):
        return ConstantVelocityRasterScan(args)

# Wrap the scan to get the plotting parameters set properly, i.e. show last axis by default only.

exec("dd = DetectorDummy('dd')")
exec('pieX = pie.pieX')
exec('pieY = pie.pieY')

rasterscan = RasterScan()
alias('rasterscan')  # @UndefinedVariable
