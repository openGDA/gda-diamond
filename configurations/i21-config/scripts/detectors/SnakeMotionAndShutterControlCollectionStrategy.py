'''
a detector collection strategy used to collect scattering or diffraction data from detector which is acquiring while sample is moving across the X-ray beam.
Sample motion and shutter control are done in a separate thread while detector is acquiring, the state of the detector acquiring is monitored and used to control shutter open and close.
(This should be replaced in future by directly wiring electric signal using PandA box). It also records the actual total exposure time as 'total_shutter_open_time' when the sample is exposed to X-ray beam.

scan will complete when sample space is run out, or required exposure times number of points are collected.

Created on Feb 10, 2023

@author: fy65
'''
from gda.device.detector.addetector.triggering import AbstractADTriggeringStrategy
from gda.device.detector.nxdetector import NXPlugin
from gdaserver import z, y, fastshutter  # @UnresolvedImport
from shutters.detectorShutterControl import erio
import time
from gdascripts.utils import frange
from gda.device.detector.nxdata import NXDetectorDataAppender, NXDetectorDataDoubleAppender
from gda.data.nexus.extractor import NexusGroupData, NexusExtractor
from java.lang import String  # @UnresolvedImport
from gda.data.nexus.tree import NexusTreeNode
from org.slf4j import LoggerFactory
from detectors.generic_observer import GeneralObserver
from detectors.SnakeMotionWithShutterControlThread import SnakePathWithShutterControlThread
import Queue
import math


logger = LoggerFactory.getLogger(__name__)

class NXDetectorDataDoubleAppenderWithUnitSupport(NXDetectorDataAppender):
    def __init__(self, name, value, unit):
        self.name = name
        self.value = value
        self.unit = unit
        
    def appendTo(self, nx_detector_data, detector_name):
        nx_detector_data.setPlottableValue(self.name, self.value)
        valdata = nx_detector_data.addData(detector_name, self.name, NexusGroupData([self.value]), self.unit, None, None, True);
        valdata.addChildNode(NexusTreeNode("local_name",NexusExtractor.AttrClassName, valdata,  NexusGroupData(String.format("%s.%s", detector_name, self.name))));

                
class ExposureLimitedCollectionStrategy(AbstractADTriggeringStrategy, NXPlugin):
    '''
    a detector collection strategy used to collect scattering or diffraction image from detector which is acquiring while sample is moving across the X-ray beam.
    '''

    def __init__(self, name, detector, shutter, exposure_time_limit = 0.1, motors = None, beam_size = None, sample_size = None, sample_centre = None, sample_start = None, sample_end = None, use_sample_size = False):
        '''
        Constructor
        '''
        self.myname = name
        self.det = detector
        #fast shutter before sample
        self.shutter = shutter
        self.cs = self.det.getCollectionStrategy()
        self.ad_base = self.cs.getDecoratee().getDecoratee().getDecoratee().getAdBase() # based on andor collection strategy
        if motors is None:
            self.y = y
            self.z = z
        else:
            self.y = motors[0]
            self.z = motors[1]
    
        if beam_size is None:
            self.beamSizeY = 0.030
            self.beamSizeZ = 0.005
        else:
            self.beamSizeY = beam_size[0]
            self.beamSizeZ = beam_size[1]
            
        if sample_size is None:
            self.sampleSizeY = 1.0
            self.sampleSizeZ = 1.0
        else:
            self.sampleSizeY = sample_size[0]
            self.sampleSizeZ = sample_size[1]
        
        if sample_centre is None:
            self.sampleCentreY = 0
            self.sampleCentreZ = 0
        else:
            self.sampleCentreY = sample_centre[0]
            self.sampleCentreZ = sample_centre[1]
            
        if sample_start is None:
            self.sampleStartY = 1.0
            self.sampleStartZ = 1.0
        else:
            self.sampleStartY = sample_start[0]
            self.sampleStartZ = sample_start[1]
                
        if sample_end is None:
            self.sampleEndY = 0
            self.sampleEndZ = 0
        else:
            self.sampleEndY = sample_end[0]
            self.sampleEndZ = sample_end[1]
        
        if not use_sample_size:
            self.sampleSizeY = math.fabs(self.sampleStartY - self.sampleEndY)
            self.sampleSizeZ = math.fabs(self.sampleStartZ - self.sampleEndZ)
            self.sampleCentreY = ( self.sampleStartY + self.sampleEndY ) / 2.0
            self.sampleCentreZ = ( self.sampleStartZ + self.sampleEndZ ) / 2.0

        self.yStep = self.beamSizeY
        self.zStep = self.beamSizeZ
        
        self.zContinuous = True
        self.yContinuous = False
        self.use_sample_size = use_sample_size
        
        self.expsoureTimeLimit = exposure_time_limit
        self.speedZChanged = False 
        self.speedYChanged = False
        self.pathReverse = True
        
        self.count_time_q = None
        self.state_observable = None
        self.state_observer =  None
        
        self.y_max_speed = 0.5
        self.y_min_speed = 0.0
        
        self.z_max_speed = 0.5
        self.z_min_speed = 0.0
    
    def setYMaxSpeed(self, speed):
        self.y_max_speed = speed
        
    def getYMaxSpeed(self):
        return self.y_max_speed
    
    def setYMinSpeed(self, speed):
        self.y_min_speed = speed
        
    def getYMinSpeed(self):
        return self.y_min_speed
    
    def setZMaxSpeed(self, speed):
        self.z_max_speed = speed
        
    def getZMaxSpeed(self):
        return self.z_max_speed
    
    def setZMinSpeed(self, speed):
        self.z_min_speed = speed
        
    def getZMinSpeed(self):
        return self.z_min_speed

    #this class property methods 
    def setBeamSize(self, beam_size):
        self.beamSizeY = beam_size[0]
        self.beamSizeZ = beam_size[1]
        self.yStep = self.beamSizeY
        self.zStep = self.beamSizeZ
        
    def setSampleSize(self, sample_size):
        self.sampleSizeY = sample_size[0]
        self.sampleSizeZ = sample_size[1]
        
    def setSampleCentre(self, sample_centre):
        self.sampleCentreY = sample_centre[0]
        self.sampleCentreZ = sample_centre[1]
        
    def setSampleStart(self, sample_start):
        self.sampleStartY = sample_start[0]
        self.sampleStartZ = sample_start[1]
        
    def setSampleEnd(self, sample_end):
        self.sampleEndY = sample_end[0]
        self.sampleEndZ = sample_end[1]
        
    def setUseSampleSize(self, b):
        self.use_sample_size = b

    def isUseSampleSize(self):
        return self.use_sample_size
            
    def setYStep(self, step):
        self.yStep = step
    
    def setZStep(self, step):
        self.zStep = step
        
    def setExposureTimeLimit(self, limit):
        self.expsoureTimeLimit = limit
        
    def setYContinuous(self, b):
        self.yContinuous = b
        
    def setZContinuous(self, b):
        self.zContinuous = b
        
    def setPathReverse(self, b):
        self.pathReverse = b
    
    #this class internal methods   
    def setMotorSpeed(self):
        '''calculate and set motor speed for continuous moving motor so that X-ray exposure time 
        at every point of the sample will not exceed the exposure time limit set
        '''
        if self.zContinuous:
            speed_needed = self.beamSizeZ / self.expsoureTimeLimit
            self.original_z_speed = self.z.getSpeed()
            if speed_needed < self.z_min_speed or speed_needed > self.z_max_speed:
                raise ValueError("Calculated motor speed % falls outside limits (%f, %f)" % (speed_needed, self.z_min_speed, self.z_max_speed))
            print("Set motor '%s' speed to %f" % (self.z.getName(), speed_needed))
            self.z.setSpeed(speed_needed)
            self.speedZChanged = True
            return speed_needed if self.speedZChanged else self.original_z_speed
        if self.yContinuous:
            speed_needed = self.beamSizeY / self.expsoureTimeLimit
            self.original_y_speed = self.y.getSpeed()
            if speed_needed < self.y_min_speed or speed_needed > self.y_max_speed:
                raise ValueError("Calculated motor speed % falls outside limits (%f, %f)" % (speed_needed, self.y_min_speed, self.y_max_speed))
            print("Set motor '%s' speed to %f" % (self.y.getName(), speed_needed))
            self.y.setSpeed(speed_needed)
            self.speedYChanged = True
            return speed_needed if self.speedYChanged else self.original_y_speed    

    def restoreMotorSpeed(self):
        '''restore motor speed if it is changed by this object
        '''
        if self.speedYChanged:
            print("Restore motor %s speed to %f" % (self.y.getName(), self.original_y_speed))
            self.y.setSpeed(self.original_y_speed)
        if self.speedZChanged:
            print("Restore motor %s speed to %f" % (self.z.getName(), self.original_z_speed))
            self.z.setSpeed(self.original_z_speed)
            
    def detecrmineControlPositions(self):
        '''calculate positions at which motor starts and stops and at which shutter opens and closes
        '''
        if self.use_sample_size:
            self.y_start = self.sampleCentreY + self.sampleSizeY/2
            self.y_open = self.sampleCentreY + self.sampleSizeY/2 + 2*self.beamSizeY
            self.y_close = self.sampleCentreY - self.sampleSizeY/2 + 2*self.beamSizeY
            self.y_end = self.sampleCentreY - self.sampleSizeY/2
            self.z_start = self.sampleCentreZ + self.sampleSizeZ/2
            self.z_open = self.sampleCentreZ - self.sampleSizeZ/2 + 2*self.beamSizeZ
            self.z_close = self.sampleCentreZ + self.sampleSizeZ/2 - 2*self.beamSizeZ 
            self.z_end = self.sampleCentreZ - self.sampleSizeZ/2
        else:
            self.y_start = self.sampleStartY
            self.y_end = self.sampleEndY
            self.y_open = self.y_start + 2*self.beamSizeY
            self.y_close = self.y_end - 2*self.beamSizeY
            self.z_start = self.sampleStartZ
            self.z_end = self.sampleEndZ
            self.z_open = self.z_start + 2*self.beamSizeZ
            self.z_close = self.z_end - 2*self.beamSizeZ 
        if self.zContinuous:
            self.y_positions = [round(each, 3) for each in frange(self.y_start, self.y_end, self.yStep)]
            self.z_total_distance = abs(self.z_end - self.z_start)*len(self.y_positions)
        if self.yContinuous:
            self.z_positions = [round(each, 3) for each in frange(self.z_start, self.z_end, self.zStep)]
            self.y_total_distance = abs(self.y_end - self.y_start)*len(self.z_positions)
     
    def update_motor_shutter_control(self, source, change):
        '''handling detector acquiring event
        '''
        if change == 1: #detector exposure started
            logger.debug("Detector acquire start")
            if not self.motion_shutter_control_thread.isAlive():
                print("Start motion and shutter control thread")
                self.motion_shutter_control_thread.start()
        elif change == 0: #detector exposure completed
            if not self.observer_added:
                self.observer_added = True
                return
            if self.motion_shutter_control_thread.isAlive():
                logger.debug("Detector acquire complete")
    
                   
    # implement NXCollectionStrategyPlugin interface
    def getAcquireTime(self):
        return self.ad_base.getAcquireTime()

    def getAcquirePeriod(self):
        return self.ad_base.getAcquirePeriod()

    def configureAcquireAndPeriodTimes(self, t):
        pass #this method deprecated

    def prepareForCollection(self, collection_time, number_images_per_cllection, scan_info):
        logger.debug("Prepare for collection ...")
        self.detecrmineControlPositions()
        self.count_time_q = Queue.Queue()
        self.collection_time = collection_time
        self.detector_collect_observer = GeneralObserver("detector_not_collecting", self.make_detector_collect)

        logger.debug("Create motion and shutter control thread")
        if self.zContinuous:
            self.motion_shutter_control_thread = SnakePathWithShutterControlThread(self.z, self.z_start, self.z_end, self.z_open, self.z_close, self.y, self.y_positions, self.ad_base, self.count_time_q, self.zContinuous, self.yContinuous, self.pathReverse, self.detector_collect_observer)
        if self.yContinuous:
            self.motion_shutter_control_thread = SnakePathWithShutterControlThread(self.y, self.y_start, self.y_end, self.y_open, self.y_close, self.z, self.z_positions, self.ad_base, self.count_time_q, self.zContinuous, self.yContinuous, self.pathReverse,self.detector_collect_observer)

        erio() # control fast shutter separately, not as part of detector
        fastshutter.moveTo("Closed") #ensure shutter is closed before collection
        
        logger.debug("Configure detector {}", self.det.getName())
        self.cs.getDecoratee().getDecoratee().getDecoratee().setReadAcquisitionTime(True)
        self.cs.prepareForCollection(collection_time, number_images_per_cllection, scan_info) #required for save and restore

        logger.debug("Setup detector acquiring state observers")
        self.observer_added = False
        self.state_observable = self.ad_base.createAcquireStateObservable()
        self.state_observer = GeneralObserver("state_observer1", self.update_motor_shutter_control)
        self.state_observable.addObserver(self.state_observer)
        self.motion_shutter_control_thread.addObserver(self.ad_base)
        
        
        self.y.asynchronousMoveTo(self.y_start)
        self.z.asynchronousMoveTo(self.z_start)
        print("Move motors to start point: y = %f, z = %f" % (self.y_start, self.z_start))
        logger.debug("Move motors to start point: y = {}, z = {}", self.y_start, self.z_start)
        self.y.waitWhileBusy()
        self.z.waitWhileBusy()
        
        motor_speed = self.setMotorSpeed()
        if self.zContinuous:
            print("Motor speed is %f for %s" % (motor_speed, self.z.getName()))
            logger.debug("Motor speed is {} for {}", motor_speed, self.z.getName())
        if self.yContinuous:
            print("Motor speed is %f for %s" % (motor_speed, self.y.getName()))
            logger.debug("Motor speed is {} for {}", motor_speed, self.y.getName())
        logger.debug("Prepare for collection completed")            

    def make_detector_collect(self, source, change):
        if not change:
            logger.warn("calling collectData() ...")
            self.collectData()
            
    def collectData(self):
        self.ad_base.startAcquiring()

    def getStatus(self):
        return self.det.getCollectionStrategy().getStatus()

    def waitWhileBusy(self):
        self.det.getCollectionStrategy().waitWhileBusy()
        

    def getNumberImagesPerCollection(self, t):
        return 1


    #implement PositionInputStream interface
    def read(self, max_to_read):
        appenders = []
        appenders.append(NXDetectorDataDoubleAppender(self.getInputStreamNames(), [self.getAcquireTime(), self.count_time_q.get()]))
        return appenders
    
    
    # implement NXPluginBase interface
    def getName(self):
        return self.myname

    def completeCollection(self):
        logger.debug("completeCollection called ...")
        if self.motion_shutter_control_thread.isAlive():
            self.motion_shutter_control_thread.join() # ask thread to die and wait for them to do it
        self.motion_shutter_control_thread.removeObserver()
        logger.debug("Stop detector acquiring")
        self.ad_base.stopAcquiring()
        fastshutter.moveTo("Closed")
        logger.debug("Stop motors {} and {}", self.y.getName(), self.z.getName())
        self.y.stop()
        self.z.stop()
        self.restoreMotorSpeed()
        if self.state_observer and self.state_observable:
            logger.debug("Remove detector acquiring state observers")
            self.state_observable.removeObserver(self.state_observer)
            self.state_observer = None
            self.state_observable = None
        self.count_time_q = None
        self.cs.completeCollection()
        logger.debug("Exit completeCollection method\n")
                        
    def atCommandFailure(self):
        logger.debug("atCommandFailure called!")
        self.completeCollection()

    def stop(self):
        logger.debug("Stop called ...")
        self.completeCollection()
        logger.debug("Exit stop method\n")
            
    def getInputStreamNames(self):
        inputnames = self.cs.getInputStreamNames()
        inputnames.append("shutter_opening_time")
        return inputnames
    
    def getInputStreamFormats(self):
        inputformats = self.cs.getInputStreamFormats()
        inputformats.append("%f")
        return inputformats
    

    

        