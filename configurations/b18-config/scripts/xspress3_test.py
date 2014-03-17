from uk.ac.gda.devices.detector.xspress3 import Xspress3Detector, TRIGGER_MODE, ROI, Xspress3BufferedDetector
from uk.ac.gda.devices.detector.xspress3.controllerimpl import EpicsXspress3Controller, DummyXspress3Controller

#epicsXspress3Controller = EpicsXspress3Controller()
#epicsXspress3Controller.setEpicsTemplate("BL18B-EA-XSP3-01")
dummyXspress3Controller = DummyXspress3Controller()
epicsXspress3Controller.configure();
epicsXspress3Controller.setTriggerMode(TRIGGER_MODE.TTl_Veto_Only);
epicsXspress3Controller.setPerformROICalculations(True);
epicsXspress3Controller.setPerformROIUpdates(True);

rois = [1];
rois[0] = ROI();
rois[0].setStart(100);
rois[0].setEnd(200);
xspress3Detector = Xspress3Detector(epicsXspress3Controller);
xspress3Detector.setName("xspress3Detector");
xspress3Detector.setNumberOfChannelsToRead(4);
xspress3Detector.setFirstChannelToRead(0);
xspress3Detector.configure();
xspress3Detector.setRegionsOfInterest(rois);
xspress3Detector.setFilePath("/dls/b18/data/2014/cm4972-1")
xspress3Detector.setWriteHDF5Files(True);
xspress3Detector.setNumberOfFramesToCollect(6);

xspress3BufferedDetector = Xspress3BufferedDetector(x3c)
xspress3BufferedDetector.setName("xspress3BufferedDetector");
xspress3BufferedDetector.setNumberOfChannelsToRead(4);
xspress3BufferedDetector.setFirstChannelToRead(0);
xspress3BufferedDetector.configure();
xspress3BufferedDetector.setWriteHDF5Files(True);

#scan test 0 5 1 x3d counterTimer01 0.1

#cvscan  qexafs_energy 20800 20900 71 20 qx3d qexafs_counterTimer01