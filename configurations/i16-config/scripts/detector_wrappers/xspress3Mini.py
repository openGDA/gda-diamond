'''
Created on Jul 15, 2026

@author: grc37356
'''

from uk.ac.gda.devices.detector.xspress3mini.controllerimpl import EpicsXspress3MiniController
from uk.ac.gda.devices.detector.xspress3.controllerimpl import DummyXspress3Controller
from uk.ac.gda.devices.detector.xspress3 import Xspress3Detector, Xspress3MiniDetector, TRIGGER_MODE
from uk.ac.gda.devices.detector.xspress3.Xspress3MiniDetector import XspressHelperMethods as xsp_help
from gda.device import DeviceException
from gda.jython import InterfaceProvider
import scisoftpy as dnp
import installation
import os
from time import sleep
from gda.device.detector import NXDetectorData
from gda.data.nexus.extractor import NexusGroupData

class xspress3MiniDet(Xspress3MiniDetector):

    def __init__(self, name):
        if installation.isLive() :
            self.ctr = EpicsXspress3MiniController()
            self.ctr.setEpicsTemplate("BL16I-EA-XSP3-01")
            self.ctr.setFileTemplate("%s%s%d.hdf5")
            self.ctr.setHDFNDArrayPort("XSP3.STAT")
        else :
            self.ctr = DummyXspress3Controller(None, None)
        self.setController(self.ctr)
        
        self.setWriteHDF5Files(True)
        self.setName(name)
        self.setLevel(100)
        self.setExtraNames(["Window_1", "Window_2", "Total"])
        self.setOutputFormat(["%s","%d","%d","%d"])

    def atScanLineStart(self):
        """Ignored to prevent the detector from taking an extra image per scan."""
        pass

    def atScanStart(self):
        self.ctr.setTriggerMode(TRIGGER_MODE.Software)
        self.ctr.setArrayCounter(0)
        self.prepareFileWriting()
        self.framesCollected = 0
        self.setFramesRead(0)
        scanInfo = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation();
        self.expectedFrames = scanInfo.numberOfPoints
        if self.expectedFrames == 1 :
            raise ValueError("Please do not run single point scans with this detector.")
        self.ctr.setHDFNumFramesToAcquire(self.expectedFrames)
        self.ctr.setSavingFiles(True);

    def collectData(self):
        sleep(0.1)
        self.ctr.doStart();
        self.ctr.waitUntilFrameAvailable(self.framesCollected + 1)
        self.framesCollected+=1
        sleep(0.5)

    def atScanEnd (self):
        self.ctr.setSavingFiles(False);

    def readout(self):
        framesRead = self.getFramesRead()
        if (framesRead == self.ctr.getTotalFramesAvailable()) :
            raise DeviceException("Cannot readout - no more data in buffer")

        FFs_sca5 = self.ctr.readoutDTCorrectedSCA1(framesRead, framesRead, 0, 0);
        FFs_sca6 = self.ctr.readoutDTCorrectedSCA2(framesRead, framesRead, 0, 0);
        all_good_count = self.ctr.readoutScalerValues(framesRead, framesRead, 0, 0)[0][0][4]

        # results = NXDetectorData()[1]

        thisFrame = NXDetectorData(self)
        thisFrame.setPlottableValue(self.getExtraNames()[0], FFs_sca5[0][0]);
        thisFrame.setPlottableValue(self.getExtraNames()[1], FFs_sca6[0][0]);
        thisFrame.setPlottableValue(self.getExtraNames()[2], all_good_count)

        detTree = thisFrame.getDetTree(self.getName())
        NXDetectorData.addData(detTree, "Window 1", NexusGroupData(int(FFs_sca5[0][0])), "counts", 1)
        NXDetectorData.addData(detTree, "Window 2", NexusGroupData(int(FFs_sca6[0][0])), "counts", 1)
        NXDetectorData.addData(detTree, "Total", NexusGroupData(all_good_count), "counts", 1)
        NXDetectorData.addData(detTree, "count_time", NexusGroupData([self.ctr.getAcquireTime()]), "s", 1, None, False)

        thisFrame.addScanFileLink(self.getName(), "nxfile://" + self.ctr.getFullFileName() + "#entry/instrument/detector/data")

        return thisFrame

    def prepareFileWriting(self):
        path = xsp_help.getFilePath("", "")
        self.ctr.setFilePath(path);
        self.ctr.setFilePrefix(xsp_help.getFilePrefix("xspress3_"));
        self.ctr.setNextFileNumber(0);

    def setExtraNames(self, names):
        self.workaround_extra_names = names

    def getExtraNames(self):
        return self.workaround_extra_names

xsp3 = xspress3MiniDet("xsp3")