from uk.ac.gda.devices.detector.xspress3 import Xspress3Detector, TRIGGER_MODE, ROI, Xspress3BufferedDetector
from uk.ac.gda.devices.detector.xspress3.controllerimpl import EpicsController


x3c = EpicsController()
x3c.setEpicsTemplate("BL18B-EA-XSP3-01")
x3c.configure();
x3c.setTriggerMode(TRIGGER_MODE.TTl_Veto_Only);

x3c.setPerformROICalculations(True);
x3c.setPerformROIUpdates(True);



x3d = Xspress3Detector(x3c);
x3d.setName("x3d");
x3d.setNumberOfChannelsToRead(4);
x3d.setFirstChannelToRead(0);
x3d.configure();

rois = [1];
rois[0] = ROI();
rois[0].setStart(100);
rois[0].setEnd(200);
x3d.setRegionsOfInterest(rois);

x3d.setFilePath("/dls/b18/data/2014/cm4972-1")
x3d.setWriteHDF5Files(True);
x3d.setNumberOfFramesToCollect(6);


qx3d = Xspress3BufferedDetector(x3c)
qx3d.setName("qx3d");
qx3d.setNumberOfChannelsToRead(4);
qx3d.setFirstChannelToRead(0);
qx3d.configure();

qx3d.setWriteHDF5Files(True);

#scan test 0 5 1 x3d counterTimer01 0.1

#cvscan  qexafs_energy 20800 20900 71 20 qx3d qexafs_counterTimer01


