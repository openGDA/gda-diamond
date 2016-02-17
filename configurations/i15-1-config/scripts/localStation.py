import java, sys, time

from gdascripts.analysis.datasetprocessor.oned.GaussianEdge import GaussianEdge
from gdascripts.analysis.datasetprocessor.oned.scan_stitching import Lcen, Rcen
from gdascripts.messages.handle_messages import simpleLog, log
from gdascripts.pd.epics_pds import DisplayEpicsPVClass
from gdascripts.pd.time_pds import waittimeClass2
from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
scan_processor.rootNamespaceDict=globals()
from gdascripts.utils import caget, caput # @UnusedImport

global run

localStation_exceptions = []

def localStation_exception(exc_info, msg):
    typ, exception, traceback = exc_info
    simpleLog("! Failure %s !" % msg)
    localStation_exceptions.append("    %s" % msg)
    log(None, "Error %s -  " % msg , typ, exception, traceback, False)

try:
    simpleLog("%s ================ INITIALISING I15-1 GDA ================" % time.strftime("%Y-%m-%d %H:%M"))

    scan_processor.processors.append(GaussianEdge())
    scan_processor.processors.append(Lcen())
    scan_processor.processors.append(Rcen())

    w = waittimeClass2('w')

    ringCurrent = DisplayEpicsPVClass("ringCurrent", "SR-DI-DCCT-01:SIGNAL", "mA", "%f")
    d1 = DisplayEpicsPVClass("d1", "BL15J-EA-IAMP-02:CHA:PEAK", "mV", "%f")
    d2 = DisplayEpicsPVClass("d2", "BL15J-EA-IAMP-02:CHB:PEAK", "mV", "%f")

    from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
    from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
    from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue #@UnusedImport
    from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
    global cam1, cam2, bpm1, bpm2

    def wrappedDetectorFactory(camdet):
        try:
            pdw_name, peak2d_name, max2d_name= camdet.name+"pdw", camdet.name+"Peak2d", camdet.name+"Max2d"
            print "Creating %s, %s and %s detector wrappers" % (pdw_name, peak2d_name, max2d_name)
            cam    = ProcessingDetectorWrapper   (pdw_name, camdet, [], panel_name='GigE Camera', panel_name_rcp='Plot 1')
            peak2d = DetectorDataProcessorWithRoi(peak2d_name, cam, [TwodGaussianPeak()])
            max2d  = DetectorDataProcessorWithRoi(max2d_name, cam, [SumMaxPositionAndValue()])
            return cam, peak2d, max2d
        except:
            localStation_exception(sys.exc_info(), "creating %s detector wrappers" % camdet.name)

    cam1pdw, cam1Peak2d, cam1Max2d  = wrappedDetectorFactory(cam1)
    cam2pdw, cam2Peak2d, cam2Max2d2 = wrappedDetectorFactory(cam2)
    bpm1pdw, bpm1Peak2d, bpm1Max2d3 = wrappedDetectorFactory(bpm1)
    bpm2pdw, bpm2Peak2d, bpm1Max2d4 = wrappedDetectorFactory(bpm2)

except:
    localStation_exception(sys.exc_info(), "in localStation")

print "*"*80
print "Attempting to run localStationStaff.py from users script directory"
try:
    run("localStationStaff")
    print "localStationStaff.py completed."
except java.io.FileNotFoundException, e:
    print "No localStationStaff.py found in user scripts directory"
except:
    localStation_exception(sys.exc_info(), "running localStationStaff user script")

print "*"*80
print "Attempting to run localStationUser.py from users script directory"
try:
    run("localStationUser")
    print "localStationUser.py completed."
except java.io.FileNotFoundException, e:
    print "No localStationUser.py found in user scripts directory"
except:
    localStation_exception(sys.exc_info(), "running localStationUser user script")

if len(localStation_exceptions) > 0:
    simpleLog("=============== %r ERRORS DURING STARTUP ================" % len(localStation_exceptions))

for localStationException in localStation_exceptions:
    simpleLog(localStationException)

simpleLog("%s ================ GDA I15-1 ONLINE ================" % time.strftime("%Y-%m-%d %H:%M"))