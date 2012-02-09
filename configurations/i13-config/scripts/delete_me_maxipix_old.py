import time
import gda.device.TangoDeviceProxy

import sys    
from gdascripts.messages import handle_messages

try:
    del maxiPix2Detector
except:
    pass

try:
    from fr.esrf.Tango import DevFailed
    #dev = TangoDeviceProxy("tango://172.23.4.19:20000/dls/limampx/mpx");
    lima_dev = gda.device.TangoDeviceProxy("tango://172.23.4.19:20000/dls/limaccd/mpx");
    from gda.device.lima import LimaCCD
    from gda.device.lima.impl import LimaCCDImpl
    limaCCD = LimaCCDImpl()
    limaCCD.setTangoDeviceProxy(lima_dev)
    limaCCD.afterPropertiesSet()
    from gda.device.lima.impl import LimaSavingHeaderDelimiterImpl
    
    maxipix2_dev = gda.device.TangoDeviceProxy("tango://172.23.4.19:20000/dls/limampx/mpx");
    
    from gda.device.maxipix2 import MaxiPix2
    from gda.device.maxipix2.impl import MaxiPix2Impl
    maxipix2 = MaxiPix2Impl()
    maxipix2.setTangoDeviceProxy(maxipix2_dev)
    maxipix2.afterPropertiesSet()
    #byteData = limaCCDAttribute.getImage(0)
    
    from gda.device.detector.maxipix2 import MaxiPix2Detector
    
    maxiPix2Detector = MaxiPix2Detector()
    maxiPix2Detector.setName("maxiPix2Detector")
    maxiPix2Detector.setLimaCCD(limaCCD)
    maxiPix2Detector.setMaxiPix2(maxipix2)
    maxiPix2Detector.configure()
    print "done"
#    maxiPix2Detector.setSavingDirectory("/home/opid00/paulg/")
#    maxiPix2Detector.setSavingFormat( LimaCCDImpl.SavingFormat.EDF)
    
    
    hefm=finder.find("highestExistingFileMonitor")
    from gda.device.detectorfilemonitor import HighestExitingFileMonitorSettings
    settings= HighestExitingFileMonitorSettings(maxiPix2Detector.getSavingDirectory(), maxiPix2Detector.getSavingFileTemplate(),1 )
    hefm.setHighestExitingFileMonitorSettings(settings)
    hefm.setRunning(True)
    
#    limaCCD.setSavingPrefix("test2")
    print "setSavingPrefix done"
except :
    exceptionType, exception, traceback = sys.exc_info()
    print exception.__class__
    if isinstance(exception, DevFailed):
        exception=maxiPix2Detector.createDeviceExceptionStack(exception)
    handle_messages.log(None, "Error setting up maxiPix2", exceptionType,exception, traceback, False)
    

class maxipix:
    """
    Help for maxipix
    """