'''
Created on 5 Apr 2018

@author: fy65
'''
from gdascripts.scannable.detector.ProcessingDetectorWrapper import SwitchableHardwareTriggerableProcessingDetectorWrapper
from uk.ac.diamond.scisoft.analysis.io import TIFFImageLoader
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessor
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from utils.ExceptionLogs import localStation_exception
import sys
try: # Based in I16 configuration GDA-mt/configurations/i16-config/scripts/localStation.py at 3922edf
    global pixis1det, pixis1det_for_snaps # require beans from PIXIS_nx.xml

    # the pixis has no hardware triggered mode configured. This class is used to hijack its DetectorSnapper implementation.
    pixis = SwitchableHardwareTriggerableProcessingDetectorWrapper('pixis', pixis1det, None, pixis1det_for_snaps, [], panel_name=None, panel_name_rcp='Plot 1', toreplace=None, replacement=None, iFileLoader=TIFFImageLoader, fileLoadTimout=15, returnPathAsImageNumberOnly=True)

    pixisSMPV = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pixisSMPV', pixis1det, None, pixis1det_for_snaps,
        panel_name=None, panel_name_rcp='Plot 1',
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)
    pixisSMPV.display_image = True
    #pixisSMPV.processors=[DetectorDataProcessorWithRoi('max', pixis1det, [SumMaxPositionAndValue()], False)]
    pixisSMPV.processors=[DetectorDataProcessor        ('max', pixis1det, [SumMaxPositionAndValue()], False)]

    pixis2d = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pixis2d', pixis1det, None, pixis1det_for_snaps,
        panel_name=None, panel_name_rcp='Plot 1',
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)
    pixis2d.display_image = True
    #pixisSMPV.processors=[DetectorDataProcessorWithRoi('max', pixis1det, [TwodGaussianPeak()], False)]
    pixis2d.processors=[DetectorDataProcessor        ('max', pixis1det, [TwodGaussianPeak()], False)]

except:
    localStation_exception(sys.exc_info(), "creating pixis objects")
