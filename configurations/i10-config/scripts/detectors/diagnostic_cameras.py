from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.messages import handle_messages
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
from gdascripts.scannable.detector.ProcessingDetectorWrapper import \
      SwitchableHardwareTriggerableProcessingDetectorWrapper
from uk.ac.diamond.scisoft.analysis.io import TIFFImageLoader
from gdaserver import d1camtiff, d2camtiff,d3camtiff,d4camtiff,d6camtiff,\
    dj1camtiff, dj3camtiff

viewerName="Plot 1";

print "-"*100
print "Creating Camera TIFF image processor objects for all diagnostic cameras:"
print "    cam1 - customised 'd1camtiff' to display image in 'Plot 1' view"
print "    peak2d1 - return 2D Gaussian Peak fitting data from d1 camera"
print "    max2d   - return Position and value of the Maximum intensity and Total intenesity"

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


cam1, peak2d1, max2d1 = cameraFactory(
    'cam1', 'peak2d1', 'max2d1', d1camtiff, None)

cam2, peak2d2, max2d2 = cameraFactory(
    'cam2', 'peak2d2', 'max2d2', d2camtiff, None)

cam3, peak2d3, max2d3 = cameraFactory(
    'cam3', 'peak2d3', 'max2d3', d3camtiff, None)

cam4, peak2d4, max2d4 = cameraFactory(
    'cam4', 'peak2d4', 'max2d4', d4camtiff, None)

cam6, peak2d6, max2d6 = cameraFactory(
    'cam6', 'peak2d6', 'max2d6', d6camtiff, None)

camj1, peak2dj1, max2dj1 = cameraFactory(
    'camj1', 'peak2dj1', 'max2dj1',dj1camtiff, None)

camj3, peak2dj3, max2dj3 = cameraFactory(
    'camj3', 'peak2dj3', 'max2dj3', dj3camtiff, None)