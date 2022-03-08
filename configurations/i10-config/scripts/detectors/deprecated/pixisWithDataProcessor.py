'''
Created on 5 Apr 2018

@author: fy65
'''
from gdascripts.scannable.detector.ProcessingDetectorWrapper import SwitchableHardwareTriggerableProcessingDetectorWrapper
from uk.ac.diamond.scisoft.analysis.io import TIFFImageLoader
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessor,\
    DetectorDataProcessorWithRoi
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from utils.ExceptionLogs import localStation_exception
from gdaserver import pixistiff  # @UnresolvedImport
import sys

print "-"*100
print "Create PIXIS detector wrapper to support TIFF image process and plot in 'Plot 1' view"
print "    1. 'pixisSMPV'  - show image in 'Plot 1' view and maximum positions, maximum intensity, and total intensity;"
print "    2. 'pixis2d'    - show image in 'Plot 1' view and background, peakx+xoffset, peaky+yoffset, topx, topy, fwhmx, fwhmy, fwhmarea of the image"


try: # Based in I16 configuration GDA-mt/configurations/i16-config/scripts/localStation.py at 3922edf

    # the pixis has no hardware triggered mode configured. This class is used to hijack its DetectorSnapper implementation.
    pixis_tiff = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pixis_tiff', pixistiff, None, None, [], 
        panel_name=None, panel_name_rcp='Plot 1', 
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader, 
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)

#     pixis2d = DetectorDataProcessorWithRoi("pixis2d", pixis_tiff, [TwodGaussianPeak()])
#     pixisSMPV = DetectorDataProcessorWithRoi("pixisSMPV", pixis_tiff, [SumMaxPositionAndValue()])
    pixis2d = DetectorDataProcessor("pixis2d", pixis_tiff, [TwodGaussianPeak()])
    pixisSMPV = DetectorDataProcessor("pixisSMPV", pixis_tiff, [SumMaxPositionAndValue()])

except:
    localStation_exception(sys.exc_info(), "creating pixis objects")
