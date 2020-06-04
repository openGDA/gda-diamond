'''
Created on 18 Jul 2011

@author: fy65
'''

import sys

from gda.device.scannable import ScannableMotionBase
from gda.device import Detector
#from gda.device.detector.pco import PCODetector
#pco=PCODetector()
class PCODetectorWrapper(ScannableMotionBase):
    def __init__(self, name, detector): #@UndefinedVariable
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%s"])
        self.pco = detector;
        self.setLevel(9)

    def asynchronousMoveTo(self,new_position):
        try:
            #print "set collection time : %f" % float(new_position)
            self.pco.setCollectionTime(float(new_position))
            #print "set NumImages : %d" % int(new_position[1])
            #self.pco.getController().setNumImages(new_position[1])
            #print "set NumCaptures : %d" % int(new_position[2])
            #self.pco.getController().getHdf().getFile().setNumCapture(int(new_position[2]))
            self.pco.collectData()
        except:
            print "error moving to position: (%f)" %(float(new_position))
            raise
        
    def getPosition(self):
        try:
            return self.pco.readout()
        except:
            print "failed to readout from detector: ", sys.exc_info()[0]
            raise
        
    def isBusy(self):
        return self.getStatus()== Detector.BUSY
   
    def getStatus(self):
        return self.pco.getStatus()

    def atScanStart(self):
        self.pco.atScanStart()

    def stop(self):
        self.pco.stop()

    def atScanEnd(self):
        self.pco.atScanEnd()
    
    def collectDarkSet(self, numImages):
        self.pco.collectDarkSet(numImages)
    
    def collectFlatSet(self, numImages, flatset):
        self.pco.collectFlatSet(numImages, flatset)
    
    def getFullFilename(self):
        return self.pco.getFilePath(self.pco.getFullFilename())
    
    def resetFileNumber(self):
        self.pco.resetFileNumber()
    
    def setCollectionTime(self, time):
        self.pco.setCollectionTime(time)
    
    def setNumImagesPerPoint(self, num):
        self.pco.setNumImages(num)
    
    def setNumberOfImageToCapture(self, num):
        self.pco.setNumCapture(num)
    
