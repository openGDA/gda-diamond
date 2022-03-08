'''
Created on 4 Apr 2018

@author: fy65
'''
from gdascripts.scannable.detector.ProcessingDetectorWrapper import SwitchableHardwareTriggerableProcessingDetectorWrapper
from uk.ac.diamond.scisoft.analysis.io import TIFFImageLoader
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessor,\
    DetectorDataProcessorWithRoi
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
import sys
from utils.ExceptionLogs import localStation_exception
from gdaserver import pimtetiff  # @UnresolvedImport

print "-"*100
print "Create PIMTE detector wrapper to support TIFF image process and plot in 'Plot 1' view"
print "    1. 'pimteSMPV'  - show image in 'Plot 1' view and maximum positions, maximum intensity, and total intensity;"
print "    2. 'pimte2d'    - show image in 'Plot 1' view and background, peakx+xoffset, peaky+yoffset, topx, topy, fwhmx, fwhmy, fwhmarea of the image"

try: # Based in I16 configuration GDA-mt/configurations/i16-config/scripts/localStation.py at 3922edf

    # the pimte has no hardware triggered mode configured. This class is used to hijack its DetectorSnapper implementation.
    pimte_tiff = SwitchableHardwareTriggerableProcessingDetectorWrapper(
        'pimte_tiff', pimtetiff, None, None, [], 
        panel_name=None, panel_name_rcp='Plot 1', 
        toreplace=None, replacement=None, iFileLoader=TIFFImageLoader, 
        fileLoadTimout=15, returnPathAsImageNumberOnly=True)

    #pimteSMPV = DetectorDataProcessorWithRoi('pimteSMPV', pimte_tiff, [SumMaxPositionAndValue()])
    pimteSMPV = DetectorDataProcessor('pimteSMPV', pimte_tiff, [SumMaxPositionAndValue()])
    #pimte2d = DetectorDataProcessorWithRoi('pimte2d', pimte_tiff, [TwodGaussianPeak()])
    pimte2d = DetectorDataProcessor('pimte2d', pimte_tiff, [TwodGaussianPeak()])

except:
    localStation_exception(sys.exc_info(), "creating pimte objects")