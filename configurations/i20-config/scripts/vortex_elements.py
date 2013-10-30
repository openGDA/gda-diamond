class VortexElements():
    
    def __init__(self, edxdcontroller, xmapController, xmapMca):
        self.edxdcontroller = edxdcontroller
        self.xmapController = xmapController
        self.xmapMca = xmapMca

    def switchTo1Element(self):
        print "Switching to 1 element"
        self.xmapController.setNumberOfMca(1)#EpicsXmapController3ROI
        self.xmapMca.setOutputFormat([u'%.2f'])
        self.xmapMca.setEventProcessingTimes([1.1029752060937018E-7])
        self.xmapMca.setExtraNames([u'Element1', u'Element1_ROI 1', u'FF'])
        self.edxdcontroller.addElements()#EDXDMappingController
        self.xmapController.configureNumberOfMca()#EpicsXmapController3ROI
        print "Switching to 1 element complete"
        
    def switchTo4Elements(self):
        print "Switching to 4 element"
        self.xmapController.setNumberOfMca(4)#EpicsXmapController3ROI
        self.xmapMca.setOutputFormat([u'%.2f',u'%.2f',u'%.2f',u'%.2f'])
        self.xmapMca.setEventProcessingTimes([1.1029752060937018E-7,1.1029752060937018E-7,1.1029752060937018E-7,1.1029752060937018E-7])
        self.xmapMca.setExtraNames([u'Element1', u'Element1_ROI 1', u'Element2', u'Element2_ROI 1', u'Element3', u'Element3_ROI 1', u'Element4', u'Element4_ROI 1', u'FF'])
        self.edxdcontroller.addElements()#EDXDMappingController
        self.xmapController.configureNumberOfMca()#EpicsXmapController3ROI
        print "Switching to 4 element complete"
