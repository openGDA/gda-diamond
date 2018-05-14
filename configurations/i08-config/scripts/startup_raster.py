from gdascripts.scan import rasterscans
from gda.device.detector.addetector.triggering import HardwareTriggeredAndor


USE_INTERNAL_ANDOR_TRIGGERING = True

col = stxmDummy.stxmDummyX
row = stxmDummy.stxmDummyY


rasterscan = rasterscans.RasterScan()
alias rasterscan
print "INFO - rasterscan is configured to use no default scannables. i.e. as of June 25 2014, it does not include: beamMonitor & topupMonitor"
rasterscans.DEFAULT_SCANNABLES_FOR_RASTERSCANS = []


if USE_INTERNAL_ANDOR_TRIGGERING:
    print "!!!! WARNING - configuring _andorrastor for internal triggering"
    HardwareTriggeredAndor.AndorTriggerMode
    HardwareTriggeredAndor.AndorTriggerMode.EXTERNAL_EXPOSURE
    _andorrastor.driver.triggerMode = HardwareTriggeredAndor.AndorTriggerMode.EXTERNAL_EXPOSURE


print "-" * 80
print """
rasterscan
==========

Try for example:
    
    >>> rasterscan row 1 10 1 col 1 10 1 _andorrastor .1

Include the name of a column in quotes to trigger a raster scan map of that vlaue to be sent to Plot 2:

    >>> rasterscan row 1 10 1 col 1 10 1 _andorrastor .1 'col'
    
NOTE: Currently this will throw exceptions on the server side. Should be a quickish fix for RichW or me --- RobW
"""
print "-" * 80