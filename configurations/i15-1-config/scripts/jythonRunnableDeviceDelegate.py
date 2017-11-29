from org.slf4j import LoggerFactory
from org.eclipse.scanning.sequencer import AbstractRunnableDeviceDelegate

class JythonRunnableDeviceDelegate (AbstractRunnableDeviceDelegate):
    logger = LoggerFactory.getLogger("JythonRunnableDeviceDelegate");

    # Delegated AbstractRunnableDevice<AreaDetectorRunnableDeviceModel> methods

    def configure(self, model):
        self.logger.info("configure({})", model)
        AbstractRunnableDeviceDelegate.configure(self, model)

    # Delegated interface IRunnableDevice<AreaDetectorRunnableDeviceModel> methods

    def run(self, position):
        self.logger.info("run({})", position);
        AbstractRunnableDeviceDelegate.run(self, position)

    # Delegated interface IWritableDetector<AreaDetectorRunnableDeviceModel> methods

    def write(self, position):
        self.logger.info("write({})", position);
        return AbstractRunnableDeviceDelegate.write(self, position);

    # Delegated interface INexusDevice<NXdetector> methods

    def getNexusProvider(self, info):
        self.logger.info("getNexusProvider({}) returning None", info);
        return AbstractRunnableDeviceDelegate.getNexusProvider(self, info)

    # Delegated annotated methods

    def preConfigure(self, scanModel, scanBean, publisher):
        self.logger.info("preConfigure({}, {}, {})", scanModel, scanBean, publisher)
        AbstractRunnableDeviceDelegate.preConfigure(self, scanModel, scanBean, publisher);

    def postConfigure(self, scanModel, scanBean, publisher):
        self.logger.info("postConfigure({}, {}, {})", scanModel, scanBean, publisher)
        AbstractRunnableDeviceDelegate.postConfigure(self, scanModel, scanBean, publisher);

    def levelStart(self, info):
        self.logger.info("levelStart({})", info)
        AbstractRunnableDeviceDelegate.levelStart(self, info);

    def levelEnd(self, info):
        self.logger.info("levelEnd({})", info)
        AbstractRunnableDeviceDelegate.levelEnd(self, info);

    def pointStart(self, point):
        self.logger.info("pointStart({})", point)
        AbstractRunnableDeviceDelegate.pointStart(self, point);

    def pointEnd(self, point):
        self.logger.info("pointEnd({})", point)
        AbstractRunnableDeviceDelegate.pointEnd(self, point);

    def scanStart(self, info):
        self.logger.info("scanStart({})", info)
        AbstractRunnableDeviceDelegate.scanStart(self, info);

    def scanEnd(self, info):
        self.logger.info("scanEnd({})", info)
        AbstractRunnableDeviceDelegate.scanEnd(self, info);

    def scanAbort(self, info):
        self.logger.info("scanAbort({})", info)
        AbstractRunnableDeviceDelegate.scanAbort(self, info);

    def scanFault(self, info):
        self.logger.info("scanFault({})", info)
        AbstractRunnableDeviceDelegate.scanFault(self, info);

    def scanFinally(self, info):
        self.logger.info("scanFinally({})", info)
        AbstractRunnableDeviceDelegate.scanFinally(self, info);

    def scanPause(self):
        self.logger.info("scanPause()")
        AbstractRunnableDeviceDelegate.scanPause(self);

    def scanResume(self):
        self.logger.info("scanResume()")
        AbstractRunnableDeviceDelegate.scanResume(self);
