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

from gda.configuration.properties import LocalProperties
dummy_mode = (LocalProperties.get('gda.mode') == u'dummy')
print "dummy_mode=%r" % dummy_mode
    
try:
    simpleLog("%s ================ INITIALISING I15-1 GDA ================" % time.strftime("%Y-%m-%d %H:%M"))

    scan_processor.processors.append(GaussianEdge())
    scan_processor.processors.append(Lcen())
    scan_processor.processors.append(Rcen())

    w = waittimeClass2('w')

    ringCurrent = DisplayEpicsPVClass("ringCurrent", "SR-DI-DCCT-01:SIGNAL", "mA", "%f")
    d1locum = DisplayEpicsPVClass("d1locum", "BL15J-EA-IAMP-02:CHA:PEAK", "mV", "%f")
    d2locum = DisplayEpicsPVClass("d2locum", "BL15J-EA-IAMP-02:CHB:PEAK", "mV", "%f")
    d1 = DisplayEpicsPVClass("d1", "BL15J-EA-ADC-01:STAT4:MeanValue_RBV", "V", "%f")
    d2 = DisplayEpicsPVClass("d2", "BL15J-EA-ADC-01:STAT5:MeanValue_RBV", "V", "%f")

    from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper
    from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
    from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue #@UnusedImport
    from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
    global cam1rawNx, cam1rgbRawNx, cam2rawNx, bpm1rawNx, bpm2rawNx, eyeRawNx

    def wrappedDetectorFactory(camdet, cam_name):
        try:
            pdw_name, peak2d_name, max2d_name= cam_name, cam_name+"Peak2d", cam_name+"Max2d"
            print "Creating %s, %s and %s detector wrappers" % (pdw_name, peak2d_name, max2d_name)
            cam    = ProcessingDetectorWrapper   (pdw_name, camdet, [], panel_name_rcp='Plot 1')
            peak2d = DetectorDataProcessorWithRoi(peak2d_name, cam, [TwodGaussianPeak()])
            max2d  = DetectorDataProcessorWithRoi(max2d_name, cam, [SumMaxPositionAndValue()])
            return cam, peak2d, max2d
        except:
            localStation_exception(sys.exc_info(), "creating %s detector wrappers" % camdet.name)

    cam1, cam1Peak2d, cam1Max2d = wrappedDetectorFactory(cam1rawNx, 'cam1')
    cam2, cam2Peak2d, cam2Max2d = wrappedDetectorFactory(cam2rawNx, 'cam2')
    bpm1, bpm1Peak2d, bpm1Max2d = wrappedDetectorFactory(bpm1rawNx, 'bpm1')
    bpm2, bpm2Peak2d, bpm2Max2d = wrappedDetectorFactory(bpm2rawNx, 'bpm2')
    eye, eyePeak2d, eyeMax2d = wrappedDetectorFactory(eyeRawNx, 'eye')

    cam1rgb = ProcessingDetectorWrapper   ("cam1rgb", cam1rgbRawNx, [], panel_name_rcp='Plot 1')

    print "Created processing detectors"

    from mapping_scan_commands import *
    print "Imported mapping_scan_commands"

    pe1AreaDetectorRunnableDeviceProxyFinder = finder.find("pe1AreaDetectorRunnableDeviceProxyFinder")
    pe1AreaDetectorRunnableDeviceProxy = pe1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    from jythonAreaDetectorRunnableDeviceDelegate import JythonAreaDetectorRunnableDeviceDelegate

    pe1JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(pe1AreaDetectorRunnableDeviceProxy)
    pe1AreaDetectorRunnableDeviceProxy.setDelegate(pe1JythonAreaDetectorRunnableDeviceDelegate)
    pe1AreaDetectorRunnableDeviceProxy.register()

    print "Configured pe1AD detector"

    pe1DarkAreaDetectorRunnableDeviceProxyFinder = finder.find("pe1DarkAreaDetectorRunnableDeviceProxyFinder")
    pe1DarkAreaDetectorRunnableDeviceProxy = pe1DarkAreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    pe1DarkJythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(pe1DarkAreaDetectorRunnableDeviceProxy)
    pe1DarkAreaDetectorRunnableDeviceProxy.setDelegate(pe1DarkJythonAreaDetectorRunnableDeviceDelegate)
    pe1DarkAreaDetectorRunnableDeviceProxy.register()

    print "Configured pe1AD dark detector"

    adc1AreaDetectorRunnableDeviceProxyFinder = finder.find("adc1AreaDetectorRunnableDeviceProxyFinder")
    adc1AreaDetectorRunnableDeviceProxy = adc1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    adc1JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(adc1AreaDetectorRunnableDeviceProxy)
    adc1AreaDetectorRunnableDeviceProxy.setDelegate(adc1JythonAreaDetectorRunnableDeviceDelegate)
    adc1AreaDetectorRunnableDeviceProxy.register()

    print "Configured adc1 detector"

    cam1AreaDetectorRunnableDeviceProxyFinder = finder.find("cam1AreaDetectorRunnableDeviceProxyFinder")
    cam1AreaDetectorRunnableDeviceProxy = cam1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    cam1JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(cam1AreaDetectorRunnableDeviceProxy)
    cam1AreaDetectorRunnableDeviceProxy.setDelegate(cam1JythonAreaDetectorRunnableDeviceDelegate)
    cam1AreaDetectorRunnableDeviceProxy.register()

    print "Configured cam1 detector"

    cam2AreaDetectorRunnableDeviceProxyFinder = finder.find("cam2AreaDetectorRunnableDeviceProxyFinder")
    cam2AreaDetectorRunnableDeviceProxy = cam2AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    cam2JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(cam2AreaDetectorRunnableDeviceProxy)
    cam2AreaDetectorRunnableDeviceProxy.setDelegate(cam2JythonAreaDetectorRunnableDeviceDelegate)
    cam2AreaDetectorRunnableDeviceProxy.register()

    print "Configured cam2 detector"

    if dummy_mode:
        print "*"*80
        print "Dummy mode specific setup - Start"
        print "*"*80

        pass

        print "*"*80
        print "Dummy mode specific setup - End"
        print "*"*80

    else:
        pass
except:
    localStation_exception(sys.exc_info(), "in localStation")

print "*"*80
print "Attempting to run localStationStaff.py from users script directory"
print "*"*80
try:
    run("localStationStaff")
    print "localStationStaff.py completed."
except java.io.FileNotFoundException, e:
    print "No localStationStaff.py found in user scripts directory"
except:
    localStation_exception(sys.exc_info(), "running localStationStaff user script")

print "*"*80
print "Attempting to run localStationUser.py from users script directory"
print "*"*80
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