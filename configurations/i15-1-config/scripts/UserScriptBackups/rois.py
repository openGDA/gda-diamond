# from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessor, DetectorDataProcessorWithRoi, HardwareTriggerableDetectorDataProcessor
# from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
# 
# #def setRoi(self, x1, y1=None, x2=None, y2=None):
# 
# roi1 = DetectorDataProcessorWithRoi('roi1', bpm2, [SumMaxPositionAndValue()])
# roi1.setRoi(642,1,646,964)
# 
# 
# ###############################################################################################################
# 
# # small centred
# roi1 = scroi=HardwareTriggerableDetectorDataProcessor('roi1', bmp2, [SumMaxPositionAndValue()])
# iw=13; jw=15; roi1.setRoi(int(ci-iw/2.),int(cj-jw/2.),int(ci+iw/2.),int(cj+jw/2.))





#testroi1 = DetectorDataProcessorWithRoi('testroi1', cam1, [SumMaxPositionAndValue()])
#testroi1.setRoi(642,1,646,963)
#scan dummy1 1 1 1 cam1 0.04 testroi3

#NOTE: cam1max2d is defined in this same way.
#cam1max2d = DetectorDataProcessorWithRoi('testcam1roiXline', cam1, [SumMaxPositionAndValue()])


#testcam1roiXline = DetectorDataProcessorWithRoi('testcam1roiXline', cam1, [SumMaxPositionAndValue()])
#testcam1roiXline.setRoi(x1,y1,x2,y2) #FORMAT FOR ROI
#testcam1roiXline.setRoi(546,480,746,484)
#cscan samY 2 0.5 cam1 0.004 testcam1roiXline

import scisoftpy as dnp

def getImageData(beanname):
    beanname = dnp.plot.getdatabean()
    data = beanname.data[0].data
    print(data.shape)
    print(data.max())
    print(data.min())

#def setBean(beanname):
#    db = dnp.plot.getd

print "roi scripts loaded"