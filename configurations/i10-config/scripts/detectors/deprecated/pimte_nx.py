'''
Created on 4 Apr 2018

@author: fy65
'''
from gdascripts.scannable.detector.ProcessingDetectorWrapper import SwitchableHardwareTriggerableProcessingDetectorWrapper
from uk.ac.diamond.scisoft.analysis.io import TIFFImageLoader
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessor
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
import sys
from utils.ExceptionLogs import localStation_exception
try: # Based in I16 configuration GDA-mt/configurations/i16-config/scripts/localStation.py at 3922edf
    global pimte1det, pimte1det_for_snaps #these objects are defined in PIMTE_nx.xml

    # the pimte has no hardware triggered mode configured. This class is used to hijack its DetectorSnapper implementation.
    pimte1 = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pimte1', pimte1det, None, pimte1det_for_snaps, [], 
        panel_name=None, panel_name_rcp='Plot 1', 
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader, 
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)

    pimteSMPV = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pimteSMPV', pimte1det, None, pimte1det_for_snaps,
        panel_name=None, panel_name_rcp='Plot 1',
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)
    pimteSMPV.display_image = True
    #pimteSMPV.processors=[DetectorDataProcessorWithRoi('max', pimte1det, [SumMaxPositionAndValue()], False)]
    pimteSMPV.processors=[DetectorDataProcessor        ('max', pimte1det, [SumMaxPositionAndValue()], False)]

    pimte2d = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pimte2d', pimte1det, None, pimte1det_for_snaps,
        panel_name=None, panel_name_rcp='Plot 1',
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)
    pimte2d.display_image = True
    #pimteSMPV.processors=[DetectorDataProcessorWithRoi('max', pimte1det, [TwodGaussianPeak()], False)]
    pimte2d.processors=[DetectorDataProcessor        ('max', pimte1det, [TwodGaussianPeak()], False)]

except:
    localStation_exception(sys.exc_info(), "creating pimte objects")