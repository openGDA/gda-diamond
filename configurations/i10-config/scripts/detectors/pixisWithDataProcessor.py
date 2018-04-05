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
from gdaserver import pixistiff
import sys

print "-"*100
print "Create PIXIS detector wrapper to support TIFF image process and plot in 'Plot 1' view"
print "    1. 'pixis_tiff' - show image in 'Plot 1' view only;"
print "    2. 'pixisSMPV'  - show image in 'Plot 1' view and maximum positions, maximum intensity, and total intensity;"
print "    3. 'pixis2d'    - show image in 'Plot 1' view and background, peakx+xoffset, peaky+yoffset, topx, topy, fwhmx, fwhmy, fwhmarea of the image"


try: # Based in I16 configuration GDA-mt/configurations/i16-config/scripts/localStation.py at 3922edf

    # the pixis has no hardware triggered mode configured. This class is used to hijack its DetectorSnapper implementation.
    pixis_tiff = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pixis_tiff', pixistiff, None, None, [], 
        panel_name=None, panel_name_rcp='Plot 1', 
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader, 
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)

    pixisSMPV = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pixisSMPV', pixistiff, None, None,
        panel_name=None, panel_name_rcp='Plot 1',
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)
    pixisSMPV.display_image = True
    #pixisSMPV.processors=[DetectorDataProcessorWithRoi('max', pixistiff, [SumMaxPositionAndValue()], False)]
    pixisSMPV.processors=[DetectorDataProcessor        ('max', pixistiff, [SumMaxPositionAndValue()], False)]

    pixis2d = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pixis2d', pixistiff, None, None,
        panel_name=None, panel_name_rcp='Plot 1',
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)
    pixis2d.display_image = True
    #pixisSMPV.processors=[DetectorDataProcessorWithRoi('max', pixistiff, [TwodGaussianPeak()], False)]
    pixis2d.processors=[DetectorDataProcessor        ('max', pixistiff, [TwodGaussianPeak()], False)]

except:
    localStation_exception(sys.exc_info(), "creating pixis objects")
