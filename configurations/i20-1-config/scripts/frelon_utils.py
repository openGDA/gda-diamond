import time
import sys

from jarray import zeros, array
from gda.factory import Finder

from gda.device.lima.LimaCCD import AcqStatus, AcqMode, AccTimeMode
from gda.device.lima import LimaBin
from gda.device.frelon.FrelonCCD import RoiMode
from gda.device.lima import LimaUtils
from gda.device.lima.impl import LimaBinImpl, LimaROIIntImpl
from fr.esrf.TangoApi import DeviceAttribute

class frelon:
    def __init__(self):
        self.frelon_obj = Finder.find("frelon_objects")
        self.lima=self.frelon_obj.get("limaCCD")
        self.frelon=self.frelon_obj.get("frelonCCD")
        
    def status(self):
        return self.lima.getStatus()
    def acq_status(self):
        return self.lima.getAcqStatus()
    def acquireImages(self):
        if self.acq_status() != AcqStatus.READY:
            raise Exception("acq_status is not in Ready state")
        self.lima.prepareAcq()
        self.lima.startAcq()
        imageCount = -1
        while (self.acq_status() != AcqStatus.READY) :
            #print "Waiting for acquisition to complete"
            # Test duplicated!!!
            lastImageCounter = self.lima.getLastImageReady()
            if lastImageCounter > imageCount:
                imageCount = lastImageCounter
                print "Frame " + `imageCount` + " is ready"
            time.sleep(1)
            
        lastImageCounter = self.lima.getLastImageReady()
        if lastImageCounter > imageCount:
            imageCount = lastImageCounter
            print "Frame " + `imageCount` + " is ready"
            
        print "acquireImages complete"
        
    def useAccumulationMode(self, max_expo_time_per_frame=.01, acq_expo_time=1, acq_nb_frames=3):
        """
        Sets acqMode to Accumulation and accTimeMode to Live,
        Sets max_expo_time_per_frame and acq_expo_time
        Sets acq_nb_frames
        """
        self.lima.setAcqMode(AcqMode.ACCUMULATION)
        self.lima.setAccTimeMode(AccTimeMode.LIVE)
# needs restart of the server        
        self.lima.setAccMaxExpoTime(max_expo_time_per_frame)
        self.lima.setAcqExpoTime(acq_expo_time)
# needs restart of the server          
        print "Effective accumulation total exposure time:" + `self.lima.getAccExpoTime()`
        self.lima.setAcqNbFrames(acq_nb_frames)
        print "Number of frames per image:" + `self.lima.getAccNbFrames()`
        
    def getImage(self, number):
        return LimaUtils().getImage(self.lima,
                           self.lima.getImageWidth(), 
                           self.lima.getImageHeight(),
                           self.lima.getImageType(),
                           number  )
    def setFastMode(self, roi_bin_offset):
        # Setting vertical bin
        deviceAttribute = DeviceAttribute("image_bin", 2, 1)
        deviceAttribute.insert_ul(array([1, 1024], 'i'))
        self.lima.getTangoDeviceProxy().write_attribute(deviceAttribute)
        
        self.frelon.setROIMode(RoiMode.KINETIC)
        
        print self.frelon.getROIMode()
        
        deviceAttribute = DeviceAttribute("image_roi", 4, 1)
        deviceAttribute.insert(array([0, 1, 2048, 1], 'i')) # [begin-x, begin-y, end-x, end-y]
        self.lima.getTangoDeviceProxy().write_attribute(deviceAttribute)
        
        print self.lima.getImageROIInt()
        
        #deviceAttribute = DeviceAttribute("roi_bin_offset",1,1)
        #deviceAttribute.insert(array([16,0],'i'))
        #self.frelon.getTangoDeviceProxy().write_attribute(deviceAttribute)
        
        self.lima.setAcqNbFrames(1)
        self.lima.setAcqExpoTime(1)
        self.acquireImages()
        
        img = self.getImage(0)
        print img
        print len(img)