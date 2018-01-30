from org.slf4j import LoggerFactory
from uk.ac.diamond.daq.detectors.addetector import AbstractAreaDetectorRunnableDeviceDelegate

# Copied from /i15-1-config/scripts/jythonAreaDetectorRunnableDeviceDelegate.py at commit cbcd71a4

class JythonAreaDetectorRunnableDeviceDelegate (AbstractAreaDetectorRunnableDeviceDelegate):
    logger = LoggerFactory.getLogger("JythonAreaDetectorRunnableDeviceDelegate");

    # Delegated AbstractRunnableDevice<AreaDetectorRunnableDeviceModel> methods

    def configure(self, model):
        self.logger.info("configure({})", model)
        AbstractAreaDetectorRunnableDeviceDelegate.configure(self, model)

    # Delegated interface IRunnableDevice<AreaDetectorRunnableDeviceModel> methods

    def run(self, position):
        self.logger.info("run({})", position);
        AbstractAreaDetectorRunnableDeviceDelegate.run(self, position)

    # Delegated interface IWritableDetector<AreaDetectorRunnableDeviceModel> methods

    def write(self, position):
        self.logger.info("write({})", position);
        return AbstractAreaDetectorRunnableDeviceDelegate.write(self, position);

    # Delegated interface INexusDevice<NXdetector> methods

    def getNexusProvider(self, info):
        self.logger.info("getNexusProvider({}) returning None", info);
        return AbstractAreaDetectorRunnableDeviceDelegate.getNexusProvider(self, info)

    # Delegated annotated methods

    def preConfigure(self, scanModel, scanBean, publisher):
        self.logger.info("preConfigure({}, {}, {})", scanModel, scanBean, publisher)
        AbstractAreaDetectorRunnableDeviceDelegate.preConfigure(self, scanModel, scanBean, publisher);

    def postConfigure(self, scanModel, scanBean, publisher):
        self.logger.info("postConfigure({}, {}, {})", scanModel, scanBean, publisher)
        AbstractAreaDetectorRunnableDeviceDelegate.postConfigure(self, scanModel, scanBean, publisher);

    def levelStart(self, info):
        self.logger.info("levelStart({})", info)
        AbstractAreaDetectorRunnableDeviceDelegate.levelStart(self, info);

    def levelEnd(self, info):
        self.logger.info("levelEnd({})", info)
        AbstractAreaDetectorRunnableDeviceDelegate.levelEnd(self, info);

    def pointStart(self, point):
        self.logger.info("pointStart({})", point)
        AbstractAreaDetectorRunnableDeviceDelegate.pointStart(self, point);

    def pointEnd(self, point):
        self.logger.info("pointEnd({})", point)
        AbstractAreaDetectorRunnableDeviceDelegate.pointEnd(self, point);

    def scanStart(self, info):
        self.logger.info("scanStart({})", info)
        AbstractAreaDetectorRunnableDeviceDelegate.scanStart(self, info);

    def scanEnd(self, info):
        self.logger.info("scanEnd({})", info)
        AbstractAreaDetectorRunnableDeviceDelegate.scanEnd(self, info);

    def scanAbort(self, info):
        self.logger.info("scanAbort({})", info)
        AbstractAreaDetectorRunnableDeviceDelegate.scanAbort(self, info);

    def scanFault(self, info):
        self.logger.info("scanFault({})", info)
        AbstractAreaDetectorRunnableDeviceDelegate.scanFault(self, info);

    def scanFinally(self, info):
        self.logger.info("scanFinally({})", info)
        AbstractAreaDetectorRunnableDeviceDelegate.scanFinally(self, info);

    def scanPause(self):
        self.logger.info("scanPause()")
        AbstractAreaDetectorRunnableDeviceDelegate.scanPause(self);

    def scanResume(self):
        self.logger.info("scanResume()")
        AbstractAreaDetectorRunnableDeviceDelegate.scanResume(self);
