from org.slf4j import LoggerFactory
#from uk.ac.diamond.daq.guigenerator  exists
#from uk.ac.diamond.daq.scanning      exists
#from uk.ac.diamond.daq.detectors     doesn't!
from uk.ac.diamond.daq.detectors.addetector import AbstractAreaDetectorRunnableDevice 

class JythonAreaDetectorRunnableDevice (AbstractAreaDetectorRunnableDevice):

    def __init__(self):
        self.logger = LoggerFactory.getLogger("JythonAreaDetectorRunnableDevice");
        self.logger.info("__init__()")
        #AbstractAreaDetectorRunnableDevice.__init__()
        # TypeError'> constructor requires self argument

        #AbstractAreaDetectorRunnableDevice.__init__(self)
        # TypeError'> org.python.proxies.jythonAreaDetectorRunnableDevice$JythonAreaDetectorRunnableDevice$480(): expected 1 args; got 0

        #AbstractAreaDetectorRunnableDevice.__init__(self, self.getRunnableDeviceService())
        # TypeError'> Default constructor failed for Java superclass uk.ac.diamond.daq.detectors.addetector.AbstractAreaDetectorRunnableDevice

        AbstractAreaDetectorRunnableDevice.__init__(self, None)

    # interface IRunnableDevice (AbstractRunnableDevice)

    def run(self, position):
        self.logger.trace("run({})", position);

    # interface IWritableDetector

    def write(self, position):
        self.logger.trace("write({}) returning False", position);
        return False;

    # interface INexusDevice

    def getNexusProvider(self, info):
        self.logger.trace("getNexusProvider({}) returning None", info);
        return None

    # Class methods (from AbstractAreaDetectorRunnableDevice)

    def preConfigure(self, model):
        self.logger.info("preConfigure(%r)", model)
        AbstractAreaDetectorRunnableDevice.preConfigure(model);

    def postConfigure(self, model):
        self.logger.info("postConfigure(%r)", model)
        AbstractAreaDetectorRunnableDevice.postConfigure(model);

    def levelStart(self, info):
        self.logger.info("levelStart(%r)", info)
        AbstractAreaDetectorRunnableDevice.levelStart(info);

    def levelEnd(self, info):
        self.logger.info("levelEnd(%r)", info)
        AbstractAreaDetectorRunnableDevice.levelEnd(info);

    def pointStart(self, point):
        self.logger.info("pointStart(%r)", point)
        AbstractAreaDetectorRunnableDevice.pointStart(point);

    def pointEnd(self, point):
        self.logger.info("pointEnd(%r)", point)
        AbstractAreaDetectorRunnableDevice.pointEnd(point);

    def scanStart(self, info):
        self.logger.info("scanStart(%r)", info)
        AbstractAreaDetectorRunnableDevice.scanStart(info);

    def scanEnd(self, info):
        self.logger.info("scanEnd(%r)", info)
        AbstractAreaDetectorRunnableDevice.scanEnd(info);

    def scanAbort(self, info):
        self.logger.info("scanAbort(%r)", info)
        AbstractAreaDetectorRunnableDevice.scanAbort(info);

    def scanFault(self, info):
        self.logger.info("scanFault(%r)", info)
        AbstractAreaDetectorRunnableDevice.scanFault(info);

    def scanFinally(self, info):
        self.logger.info("scanFinally(%r)", info)
        AbstractAreaDetectorRunnableDevice.scanFinally(info);

    def scanPaused(self):
        self.logger.info("scanPaused()")
        AbstractAreaDetectorRunnableDevice.scanPaused();

    def scanResumed(self):
        self.logger.info("scanResumed()")
        AbstractAreaDetectorRunnableDevice.scanResumed();
