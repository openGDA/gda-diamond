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
from gdaserver import pimtetiff

print "-"*100
print "Create PIMTE detector wrapper to support TIFF image process and plot in 'Plot 1' view"
print "    1. 'pimte_tiff' - show image in 'Plot 1' view only;"
print "    2. 'pimteSMPV'  - show image in 'Plot 1' view and maximum positions, maximum intensity, and total intensity;"
print "    3. 'pimte2d'    - show image in 'Plot 1' view and background, peakx+xoffset, peaky+yoffset, topx, topy, fwhmx, fwhmy, fwhmarea of the image"

try: # Based in I16 configuration GDA-mt/configurations/i16-config/scripts/localStation.py at 3922edf

    # the pimte has no hardware triggered mode configured. This class is used to hijack its DetectorSnapper implementation.
    pimte_tiff = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pimte_tiff', pimtetiff, None, None, [], 
        panel_name=None, panel_name_rcp='Plot 1', 
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader, 
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)

    pimteSMPV = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pimteSMPV', pimtetiff, None, None,
        panel_name=None, panel_name_rcp='Plot 1',
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)
    pimteSMPV.display_image = True
    #pimteSMPV.processors=[DetectorDataProcessorWithRoi('max', pimtetiff, [SumMaxPositionAndValue()], False)]
    pimteSMPV.processors=[DetectorDataProcessor        ('max', pimtetiff, [SumMaxPositionAndValue()], False)]

    pimte2d = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pimte2d', pimtetiff, None, None,
        panel_name=None, panel_name_rcp='Plot 1',
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)
    pimte2d.display_image = True
    #pimteSMPV.processors=[DetectorDataProcessorWithRoi('max', pimtetiff, [TwodGaussianPeak()], False)]
    pimte2d.processors=[DetectorDataProcessor        ('max', pimtetiff, [TwodGaussianPeak()], False)]

except:
    localStation_exception(sys.exc_info(), "creating pimte objects")