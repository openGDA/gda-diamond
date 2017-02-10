from gdascripts.utils import caget, caput
from org.eclipse.scanning.api.scan import ScanningException
from org.slf4j import LoggerFactory
from peAdTest import PeAdTest
from uk.ac.diamond.daq.detectors.addetector.api import DarkImageAreaDetectorWritingFilesRunnableDeviceModel


class PeAdDarkTest (PeAdTest):
    logger = LoggerFactory.getLogger("PeAdDarkTest");

    def preConfigure(self, info):
        self.logger.info("postConfigure({})", info)

        PeAdTest.preConfigure(self, info);
        self.mainHdf5Plugin = self.hdfPlugin
        self.hdfPlugin = "HDF5B:"

    def configure(self, model):
        self.logger.info("configure({})", model)

        if not isinstance(model, DarkImageAreaDetectorWritingFilesRunnableDeviceModel):
            message = "DarkImageAreaDetectorWritingFilesRunnableDeviceModel expected!"
            self.logger.error(message)
            raise ScanningException(message)

        PeAdTest.configure(self, model);

    def run(self, position):
        self.logger.info("run({})", position);

        if (position.getStepIndex() % self.model.getFrequency() == 0):

            caput("BL15J-EA-DET-01:PROC2:EnableBackground",0)

            self.logger.info("PeAdTest.run()...");
            PeAdTest.run(self, position)
            self.logger.info("...PeAdTest.run()");

            caput("BL15J-EA-DET-01:PROC2:SaveBackground","1")
            caput("BL15J-EA-DET-01:PROC2:EnableBackground","1")
