from gda.device.scannable import ScannableMotionBase

from gda.device.scannable import ScannableUtils
import time
from gda.epics import CAClient
from gdascripts.utils import caget
from gdascripts.utils import caput

class FlatField(ScannableMotionBase):
    # constructor
    def __init__(self, name, camera, motor):
        self.setName(name) 
        self.setInputNames(["ff_imgs","ff_cnt","df_imgs"])
        self.setExtraNames(["ff_cur_cnt"])
        self.setOutputFormat(["%5.5g","%5.5g","%5.5g","%5.5g"])
        self.setLevel(10)
        self.iambusy = 0
        self.camera = camera
        self.motor = motor
        self.count = 0
        self.setNumber = 0
        self.images = -1
        self.countMax = -1
        self.darkimages = -1

    # returns the value this scannable represents
    def rawGetPosition(self):
        return [self.images, self.countMax, self.darkimages, self.count]

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        self.iambusy = 1
        #setup if required
        if(self.countMax == -1) :
            self.images = new_position[0]
            self.countMax = new_position[1]
            self.darkimages = new_position[2]
            # if the system has not yet been setup, then it should take some Darks if thats appropriate
            if self.darkimages > 0 :
                self.collectDarkFields()

        if self.count == 0 :
            self.collectFlatfields()
            self.setNumber += 1
            self.count = self.countMax

        self.count -= 1

        self.iambusy = 0

    # Returns the status of this Scannable
    def isBusy(self):
        return self.iambusy


    def atScanStart(self):
        self.count = 0
        self.setNumber = 0
        self.images = -1
        self.countMax = -1
        self.darkimages = -1
        # also need to reset the camera, as this will be used first
        self.camera.resetAndEnableFullFrameCapture()
        # capture the dark images

    def collectFlatfields(self) :
        # wait 2 seconds to let the previous aquisition finish
        #time.sleep(2)
        
        print "Collecting Flatfields"

        # CHANGE THIS - to make the flat field distance larger
        movement = 2.0

        # move the motor
        print "moving sample out of the beam"
        position = self.motor.getPosition()
        self.motor(position+movement)

        # rearm the camera after the pause
        self.cycleCamera();
        # take the images
        self.camera.collectFlatSet(self.images,self.setNumber)
            
        # put the motor back
        print "moving sample back into the beam"
        self.motor(position)

        # put the camera back
        # make sure that the files have finished writing out before 
        
        self.cycleCamera()

    def collectDarkFields(self) :
        # wait 1 second for setup
        self.cycleCamera()
        print "Collecting DarkFields"
        
        # close shutter or something here
        caput("BL12I-PS-SHTR-02:CON", 1)
        
        self.camera.collectDarkSet(self.darkimages)

        # then reopen it here
        caput("BL12I-PS-SHTR-02:CON", 0)
        
        self.cycleCamera()

    def cycleCamera(self):
        # method which rearms the camera to stop problems with long wait periods
        print "Pausing for camera"
        #self.camera.getAreaDetector().stop()
        time.sleep(10.0)
        # rearm
        #self.camera.getAreaDetector().acquire()
        # allow time to rearm
        #time.sleep(1.0)
        

