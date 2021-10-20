from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.messages import handle_messages
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
from gdascripts.scannable.detector.ProcessingDetectorWrapper import \
      SwitchableHardwareTriggerableProcessingDetectorWrapper
from uk.ac.diamond.scisoft.analysis.io import TIFFImageLoader

viewerName="Plot 1";

print "-"*100
print "Creating Camera TIFF image processor objects for all diagnostic cameras:"
print "    cam1 - customised 'd1camtiff' to display image in 'Plot 1' view"
print "    peak2d1 - return 2D Gaussian Peak fitting data from d1 camera"
print "    max2d1   - return Position and value of the Maximum intensity and Total intenesity"

def cameraFactory(cam_name, peak2d_name, max2d_name, camdet, camdet_for_snaps):
    # ----------------------------------------------------------------------
    try:
        print "Creating %s, %s and %s" % \
            (cam_name, peak2d_name, max2d_name)
        # This has no hardware triggered mode configured. This class is used to hijack its DetectorSnapper implementation.
        cam = SwitchableHardwareTriggerableProcessingDetectorWrapper(
            cam_name, camdet, None, camdet_for_snaps, [],
            panel_name=None, panel_name_rcp='Plot 1',
            toreplace=None, replacement=None, iFileLoader=TIFFImageLoader,
            fileLoadTimout=15, returnPathAsImageNumberOnly=True)
        peak2d = DetectorDataProcessorWithRoi(peak2d_name, cam, [TwodGaussianPeak()])
        max2d = DetectorDataProcessorWithRoi(max2d_name, cam, [SumMaxPositionAndValue()])
    # ----------------------------------------------------------------------
        return cam, peak2d, max2d
    except:
        import sys
        typ, exception, traceback = sys.exc_info()
        handle_messages.log(None, "%s error -  " % cam_name, typ, exception, traceback, False)


