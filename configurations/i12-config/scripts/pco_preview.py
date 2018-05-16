'''
Created on 12 May 2010

@author: ssg37927
'''
from time import sleep
from threading import Thread

class PcoLiveView(object):
    
    def __init__(self, camera):
        self.active = True
        self.exposure_time = 0.02
        self.camera = camera
        self.kill = False
        # get the thread running
        self.thread = PcoLiveViewThread(self)
        self.thread.start()
        return
    
    def setExposureTime(self,exposure_time):
        self.exposure_time = exposure_time
        
    def activate(self):
        self.active = True
    
    def deactivate(self):
        self.active = False
        
    def killThread(self):
        self.kill = True
        
    

class PcoLiveViewThread(Thread):
    '''
    PCO live view thread
    '''

    def __init__(self,control_object):
        '''
        Constructor
        '''
        Thread.__init__(self)
        self.control_object = control_object
        return
    
    def run(self):
        while True :
            if self.control_object.kill :
                return
            if (self.control_object.active) :
                self.control_object.camera.preview(1,self.control_object.exposure_time)
                sleep(0.25)
            else :
                sleep(1)
                        