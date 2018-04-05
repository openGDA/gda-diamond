from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gdascripts.messages import handle_messages
from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
from gdascripts.scannable.detector.ProcessingDetectorWrapper import \
      SwitchableHardwareTriggerableProcessingDetectorWrapper
from uk.ac.diamond.scisoft.analysis.io import TIFFImageLoader
from gdaserver import d1camtiff

global cam1det, cam1det_for_snaps, cam2det, cam2det_for_snaps
global cam3det, cam3det_for_snaps, cam4det, cam4det_for_snaps
global cam6det, cam6det_for_snaps
global camj1det, camj1det_for_snaps, camj3det, camj3det_for_snaps

viewerName="Plot 1";

print "-------------------------------------------------------------------"

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

print "Usage: use cam6det, cam6, peak2d6, max2d6 for the camera on D6 etc."

cam1, peak2d1, max2d1 = cameraFactory(
    'cam1', 'peak2d1', 'max2d1', d1camtiff, None)

cam2, peak2d2, max2d2 = cameraFactory(
    'cam2', 'peak2d2', 'max2d2', cam2det, cam2det_for_snaps)

cam3, peak2d3, max2d3 = cameraFactory(
    'cam3', 'peak2d3', 'max2d3', cam3det, cam3det_for_snaps)

cam4, peak2d4, max2d4 = cameraFactory(
    'cam4', 'peak2d4', 'max2d4', cam4det, cam4det_for_snaps)

cam6, peak2d6, max2d6 = cameraFactory(
    'cam6', 'peak2d6', 'max2d6', cam6det, cam6det_for_snaps)

camj1, peak2dj1, max2dj1 = cameraFactory(
    'camj1', 'peak2dj1', 'max2dj1', camj1det, camj1det_for_snaps)

camj3, peak2dj3, max2dj3 = cameraFactory(
    'camj3', 'peak2dj3', 'max2dj3', camj3det, camj3det_for_snaps)