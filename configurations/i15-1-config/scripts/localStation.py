import java, sys, time, subprocess

from gdascripts.analysis.datasetprocessor.oned.GaussianEdge import GaussianEdge
from gdascripts.analysis.datasetprocessor.oned.scan_stitching import Lcen, Rcen
from gdascripts.messages.handle_messages import simpleLog, log
from gdascripts.pd.epics_pds import DisplayEpicsPVClass
from gdascripts.pd.time_pds import waittimeClass2
from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
scan_processor.rootNamespaceDict=globals()
from gdascripts.utils import caget, caput # @UnusedImport
from gda.factory import Finder

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

    from mapping_scan_commands import *
    print "Imported mapping_scan_commands"

    from jythonAreaDetectorRunnableDeviceDelegate import JythonAreaDetectorRunnableDeviceDelegate

    adc1AreaDetectorRunnableDeviceProxyFinder = Finder.find("adc1AreaDetectorRunnableDeviceProxyFinder")
    adc1AreaDetectorRunnableDeviceProxy = adc1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    adc1JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(adc1AreaDetectorRunnableDeviceProxy)
    adc1AreaDetectorRunnableDeviceProxy.setDelegate(adc1JythonAreaDetectorRunnableDeviceDelegate)
    adc1AreaDetectorRunnableDeviceProxy.register()

    print "Configured adc1 detector"

    arc1AreaDetectorRunnableDeviceProxyFinder = Finder.find("arc1AreaDetectorRunnableDeviceProxyFinder")
    arc1AreaDetectorRunnableDeviceProxy = arc1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    arc1JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(arc1AreaDetectorRunnableDeviceProxy)
    arc1AreaDetectorRunnableDeviceProxy.setDelegate(arc1JythonAreaDetectorRunnableDeviceDelegate)
    arc1AreaDetectorRunnableDeviceProxy.register()

    print "Configured arc1 detector"

    bpm1AreaDetectorRunnableDeviceProxyFinder = Finder.find("bpm1AreaDetectorRunnableDeviceProxyFinder")
    bpm1AreaDetectorRunnableDeviceProxy = bpm1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    bpm1JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(bpm1AreaDetectorRunnableDeviceProxy)
    bpm1AreaDetectorRunnableDeviceProxy.setDelegate(bpm1JythonAreaDetectorRunnableDeviceDelegate)
    bpm1AreaDetectorRunnableDeviceProxy.register()

    print "Configured bpm1 detector"

    bpm2AreaDetectorRunnableDeviceProxyFinder = Finder.find("bpm2AreaDetectorRunnableDeviceProxyFinder")
    bpm2AreaDetectorRunnableDeviceProxy = bpm2AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    bpm2JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(bpm2AreaDetectorRunnableDeviceProxy)
    bpm2AreaDetectorRunnableDeviceProxy.setDelegate(bpm2JythonAreaDetectorRunnableDeviceDelegate)
    bpm2AreaDetectorRunnableDeviceProxy.register()

    print "Configured bpm2 detector"

    cam1AreaDetectorRunnableDeviceProxyFinder = Finder.find("cam1AreaDetectorRunnableDeviceProxyFinder")
    cam1AreaDetectorRunnableDeviceProxy = cam1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    cam1JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(cam1AreaDetectorRunnableDeviceProxy)
    cam1AreaDetectorRunnableDeviceProxy.setDelegate(cam1JythonAreaDetectorRunnableDeviceDelegate)
    cam1AreaDetectorRunnableDeviceProxy.register()

    print "Configured cam1 detector"

    cam2AreaDetectorRunnableDeviceProxyFinder = Finder.find("cam2AreaDetectorRunnableDeviceProxyFinder")
    cam2AreaDetectorRunnableDeviceProxy = cam2AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    cam2JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(cam2AreaDetectorRunnableDeviceProxy)
    cam2AreaDetectorRunnableDeviceProxy.setDelegate(cam2JythonAreaDetectorRunnableDeviceDelegate)
    cam2AreaDetectorRunnableDeviceProxy.register()

    print "Configured cam2 detector"


    eye1AreaDetectorRunnableDeviceProxyFinder = Finder.find("eye1AreaDetectorRunnableDeviceProxyFinder")
    eye1AreaDetectorRunnableDeviceProxy = eye1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    eye1JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(eye1AreaDetectorRunnableDeviceProxy)
    eye1AreaDetectorRunnableDeviceProxy.setDelegate(eye1JythonAreaDetectorRunnableDeviceDelegate)
    eye1AreaDetectorRunnableDeviceProxy.register()

    print "Configured eye1 detector"

    pe1AreaDetectorRunnableDeviceProxyFinder = Finder.find("pe1AreaDetectorRunnableDeviceProxyFinder")
    pe1AreaDetectorRunnableDeviceProxy = pe1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    pe1JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(pe1AreaDetectorRunnableDeviceProxy)
    pe1AreaDetectorRunnableDeviceProxy.setDelegate(pe1JythonAreaDetectorRunnableDeviceDelegate)
    pe1AreaDetectorRunnableDeviceProxy.register()

    print "Configured pe1AD detector"

    pe2AreaDetectorRunnableDeviceProxyFinder = Finder.find("pe2AreaDetectorRunnableDeviceProxyFinder")
    pe2AreaDetectorRunnableDeviceProxy = pe2AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    pe2JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(pe2AreaDetectorRunnableDeviceProxy)
    pe2AreaDetectorRunnableDeviceProxy.setDelegate(pe2JythonAreaDetectorRunnableDeviceDelegate)
    pe2AreaDetectorRunnableDeviceProxy.register()

    print "Configured pe2AD detector"

    web1AreaDetectorRunnableDeviceProxyFinder = Finder.find("web1AreaDetectorRunnableDeviceProxyFinder")
    web1AreaDetectorRunnableDeviceProxy = web1AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    web1JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(web1AreaDetectorRunnableDeviceProxy)
    web1AreaDetectorRunnableDeviceProxy.setDelegate(web1JythonAreaDetectorRunnableDeviceDelegate)
    web1AreaDetectorRunnableDeviceProxy.register()

    print "Configured web1 detector"

    web2AreaDetectorRunnableDeviceProxyFinder = Finder.find("web2AreaDetectorRunnableDeviceProxyFinder")
    web2AreaDetectorRunnableDeviceProxy = web2AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    web2JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(web2AreaDetectorRunnableDeviceProxy)
    web2AreaDetectorRunnableDeviceProxy.setDelegate(web2JythonAreaDetectorRunnableDeviceDelegate)
    web2AreaDetectorRunnableDeviceProxy.register()

    print "Configured web2 detector"

    from jythonRunnableDeviceDelegate import JythonRunnableDeviceDelegate

    beamlineRunnableDeviceProxyFinder = Finder.find("beamlineRunnableDeviceProxyFinder")
    beamlineRunnableDeviceProxy = beamlineRunnableDeviceProxyFinder.getRunnableDevice()

    beamlineJythonRunnableDeviceDelegate = JythonRunnableDeviceDelegate(beamlineRunnableDeviceProxy)
    beamlineRunnableDeviceProxy.setDelegate(beamlineJythonRunnableDeviceDelegate)
    beamlineRunnableDeviceProxy.register()

    print "Configured beamline runnable device"

    metadataRunnableDeviceProxyFinder = Finder.find("metadataRunnableDeviceProxyFinder")
    metadataRunnableDeviceProxy = metadataRunnableDeviceProxyFinder.getRunnableDevice()

    metadataJythonRunnableDeviceDelegate = JythonRunnableDeviceDelegate(metadataRunnableDeviceProxy)
    metadataRunnableDeviceProxy.setDelegate(metadataJythonRunnableDeviceDelegate)
    metadataRunnableDeviceProxy.register()

    print "Configured metadata runnable device"

    multimetaRunnableDeviceProxyFinder = Finder.find("multimetaRunnableDeviceProxyFinder")
    multimetaRunnableDeviceProxy = multimetaRunnableDeviceProxyFinder.getRunnableDevice()

    multimetaJythonRunnableDeviceDelegate = JythonRunnableDeviceDelegate(multimetaRunnableDeviceProxy)
    multimetaRunnableDeviceProxy.setDelegate(multimetaJythonRunnableDeviceDelegate)
    multimetaRunnableDeviceProxy.register()

    print "Configured multimeta runnable device"

    xbpm3AreaDetectorRunnableDeviceProxyFinder = Finder.find("xbpm3AreaDetectorRunnableDeviceProxyFinder")
    xbpm3AreaDetectorRunnableDeviceProxy = xbpm3AreaDetectorRunnableDeviceProxyFinder.getRunnableDevice()

    xbpm3JythonAreaDetectorRunnableDeviceDelegate = JythonAreaDetectorRunnableDeviceDelegate(xbpm3AreaDetectorRunnableDeviceProxy)
    xbpm3AreaDetectorRunnableDeviceProxy.setDelegate(xbpm3JythonAreaDetectorRunnableDeviceDelegate)
    xbpm3AreaDetectorRunnableDeviceProxy.register()

    print "Configured xbpm3 detector"

    cryojetRunnableDeviceProxyFinder = Finder.find("cryojetRunnableDeviceProxyFinder")
    cryojetRunnableDeviceProxy = cryojetRunnableDeviceProxyFinder.getRunnableDevice()

    cryojetJythonRunnableDeviceDelegate = JythonRunnableDeviceDelegate(cryojetRunnableDeviceProxy)
    cryojetRunnableDeviceProxy.setDelegate(cryojetJythonRunnableDeviceDelegate)
    cryojetRunnableDeviceProxy.register()

    print "Configured cryojet runnable device"

    xtalRunnableDeviceProxyFinder = Finder.find("xtalRunnableDeviceProxyFinder")
    xtalRunnableDeviceProxy = xtalRunnableDeviceProxyFinder.getRunnableDevice()

    xtalJythonRunnableDeviceDelegate = JythonRunnableDeviceDelegate(xtalRunnableDeviceProxy)
    xtalRunnableDeviceProxy.setDelegate(xtalJythonRunnableDeviceDelegate)
    xtalRunnableDeviceProxy.register()

    print "Configured xtal runnable device"

    positionerRunnableDeviceProxyFinder = Finder.find("positionerRunnableDeviceProxyFinder")
    positionerRunnableDeviceProxy = positionerRunnableDeviceProxyFinder.getRunnableDevice()

    positionerJythonRunnableDeviceDelegate = JythonRunnableDeviceDelegate(positionerRunnableDeviceProxy)
    positionerRunnableDeviceProxy.setDelegate(positionerJythonRunnableDeviceDelegate)
    positionerRunnableDeviceProxy.register()

    print "Configured positioner runnable device"

    blowerRunnableDeviceProxyFinder = Finder.find("blowerRunnableDeviceProxyFinder")
    blowerRunnableDeviceProxy = blowerRunnableDeviceProxyFinder.getRunnableDevice()

    blowerJythonRunnableDeviceDelegate = JythonRunnableDeviceDelegate(blowerRunnableDeviceProxy)
    blowerRunnableDeviceProxy.setDelegate(blowerJythonRunnableDeviceDelegate)
    blowerRunnableDeviceProxy.register()

    print "Configured blower runnable device"

    if dummy_mode:
        print "*"*80
        print "Dummy mode specific setup - Start"
        print "*"*80

        pass

        from jythonRunnableDeviceDelegate import JythonRunnableDeviceDelegate

        testRunnableDeviceProxyFinder = Finder.find("testRunnableDeviceProxyFinder")
        testRunnableDeviceProxy = testRunnableDeviceProxyFinder.getRunnableDevice()

        testJythonRunnableDeviceDelegate = JythonRunnableDeviceDelegate(testRunnableDeviceProxy)
        testRunnableDeviceProxy.setDelegate(testJythonRunnableDeviceDelegate)
        testRunnableDeviceProxy.register()

        print "Configured test runnable device"

        print "*"*80
        print "Dummy mode specific setup - End"
        print "*"*80

    else:
        pass

    def checkthreads():
        """
        Count the number of threads in use by gda2, including activemq
        and GDA servers.
        """
        print subprocess.check_output(['bash','-c', 'ps huxH | wc -l'])

    alias checkthreads
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
