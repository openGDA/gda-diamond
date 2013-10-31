class VortexElements():
    
    def __init__(self, xmapController, xmapMca):
        self.xmapController = xmapController
        self.xmapMca = xmapMca

    def switchTo1Element(self):
        self.xmapController.setNumberOfElements(1)
        self.xmapMca.setOutputFormat([u'%.2f'])
        self.xmapMca.setEventProcessingTimes([1.1029752060937018E-7])
        self.xmapMca.setExtraNames([u'Element1', u'Element1_ROI 1', u'FF'])
        
    def switchTo4Elements(self):
        self.xmapController.setNumberOfElements(4)
        self.xmapMca.setOutputFormat([u'%.2f',u'%.2f',u'%.2f',u'%.2f'])
        self.xmapMca.setEventProcessingTimes([1.1029752060937018E-7,1.1029752060937018E-7,1.1029752060937018E-7,1.1029752060937018E-7])
        self.xmapMca.setExtraNames([u'Element1', u'Element1_ROI 1', u'Element2', u'Element2_ROI 1', u'Element3', u'Element3_ROI 1', u'Element4', u'Element4_ROI 1', u'FF'])