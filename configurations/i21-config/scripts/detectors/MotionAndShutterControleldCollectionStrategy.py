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
from threading import Thread, currentThread
from shutters.detectorShutterControl import erio
import time
from gdascripts.utils import frange
from gda.device import Detector
from gda.device.detector.nxdata import NXDetectorDataAppender, NXDetectorDataDoubleAppender
from gda.data.nexus.extractor import NexusGroupData, NexusExtractor
from java.lang import String  # @UnresolvedImport
from gda.data.nexus.tree import NexusTreeNode
from org.slf4j import LoggerFactory
from gda.jython import InterfaceProvider
from __builtin__ import True
from detectors.generic_observer import GeneralObserver


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

    def __init__(self, name, detector, shutter, exposure_time_limit = 0.1, motors = None, beam_size = None, sample_size = None, sample_centre = None):
        '''
        Constructor
        '''
        self.myname = name
        self.det = detector
        #fast shutter before sample
        self.shutter = shutter
        self.cs = self.det.getCollectionStrategy()
        self.ad_base = self.cs.getDecoratee().getDecoratee().getDecoratee().getAdBase()
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
            self.sampleSizeY = 1000.0
            self.sampleSizeZ = 1000.0
        else:
            self.sampleSizeY = sample_size[0]
            self.sampleSizeZ = sample_size[1]
        
        if sample_centre is None:
            self.sampleCentreY = 0
            self.sampleCentreZ = 0
        else:
            self.sampleCentreY = sample_centre[0]
            self.sampleCentreZ = sample_centre[1]
            
        self.yStep = self.beamSizeY
        self.zStep = self.beamSizeZ
        
        self.zContinuous = True
        self.yContinuous = False
        
        self.expsoureTimeLimit = exposure_time_limit
        self.speedZChanged = False 
        self.speedYChanged = False
        
        self._myStatus = Detector.IDLE
        self.lastPointRealCountTime = 0.0
        
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
    
    #this class internal methods   
    def setMotorSpeed(self):
        '''calculate and set motor speed for continuous moving motor so that X-ray exposure time 
        at every point of the sample will not exceed the exposure time limit set
        '''
        if self.zContinuous:
            min_speed = self.beamSizeZ / self.expsoureTimeLimit
            self.original_z_speed = self.z.getSpeed()
            if self.original_z_speed < min_speed :
                print("Set motor '%s' speed to %f" % (self.z.getName(), min_speed))
                self.z.setSpeed(min_speed)
                self.speedZChanged = True
            return min_speed if self.speedZChanged else self.original_z_speed
        if self.yContinuous:
            min_speed = self.beamSizeY / self.expsoureTimeLimit
            self.original_y_speed = self.y.getSpeed()
            if self.original_y_speed < min_speed:
                print("Set motor '%s' speed to %f" % (self.y.getName(), min_speed))
                self.y.setSpeed(min_speed)
                self.speedYChanged = True
            return min_speed if self.speedYChanged else self.original_y_speed    

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
        self.y_start = self.sampleCentreY + self.sampleSizeY/2
        self.y_open = self.sampleCentreY + self.sampleSizeY/2 + 2*self.beamSizeY
        self.y_close = self.sampleCentreY - self.sampleSizeY/2 + 2*self.beamSizeY
        self.y_end = self.sampleCentreY - self.sampleSizeY/2
        self.z_start = self.sampleCentreZ - self.sampleSizeZ/2
        self.z_open = self.sampleCentreZ - self.sampleSizeZ/2 + 2*self.beamSizeZ
        self.z_close = self.sampleCentreZ + self.sampleSizeZ/2 - 2*self.beamSizeZ 
        self.z_end = self.sampleCentreZ + self.sampleSizeZ/2
        if self.zContinuous:
            self.y_positions = [round(each, 3) for each in frange(self.y_start, self.y_end, self.yStep)]
            self.z_total_distance = abs(self.z_end - self.z_start)*len(self.y_positions)
        if self.yContinuous:
            self.z_positions = [round(each, 3) for each in frange(self.z_start, self.z_end, self.zStep)]
            self.y_total_distance = abs(self.y_end - self.y_start)*len(self.z_positions)
     
    def stop_motors_close_shutter_on_acquire_finish(self):
        self.closeShutter()
        self.end_time = time.time()
        self.y.stop()
        self.z.stop()
                
    def update_motor_shutter_control(self, source, change):
        '''handling detector acquiring event
        '''
        if change == 1: #detector exposure started
            print("\nDetector acquire start")
            self._myStatus = Detector.BUSY
            self.detectorIsAcquiring = True
            self.total_shutter_open_time = 0.0
            if not self.motion_shutter_control_thread.isAlive():
                print("Start motion and shutter control thread")
                self.motion_shutter_control_thread.start()
            else:
                print("motion and shutter control thread is already running")
        elif change == 0: #detector exposure completed
            self.detectorIsAcquiring = False
            if not self.observer_added:
                self.observer_added = True
                return
            if self.motion_shutter_control_thread.isAlive():
                print("\nDetector acquire complete\n")
                time.sleep(3)
            else:
                print("motion and shutter control thread is not running")
            self._myStatus = Detector.IDLE
    
    def openShutter(self):
        fastshutter.moveTo("Open")
    
    def closeShutter(self):
        fastshutter.moveTo("Closed")

    def shutterControl(self):
        if self.zContinuous:
            z_pos = float(self.z.getPosition())
            if (z_pos > self.z_open and z_pos < self.z_close) and self.detectorIsAcquiring and not self.shutterAlreadyOpen:
                self.openShutter()
                self.start_time = time.time()
                self.shutterAlreadyOpen = True
                print("Open  shutter at %f" % self.start_time)
            elif (z_pos < self.z_open or z_pos > self.z_close or not self.detectorIsAcquiring) and self.shutterAlreadyOpen:
                self.closeShutter()
                self.end_time = time.time()
                self.shutterAlreadyOpen = False
                print("Close shutter at %f" % self.end_time)
                print("shutter opening time is %f" % (self.end_time - self.start_time))
                self.total_shutter_open_time += (self.end_time - self.start_time)
                self.setRealCountTime(self.total_shutter_open_time)
                if not self.detectorIsAcquiring:
                    self.total_shutter_open_times.append(self.total_shutter_open_time)
                    print("Total shutter opening time for point %d is %f" % (self.point_number, self.total_shutter_open_time))
                    # self.afterCurrentPointCollected()
                    # self.appenders.append(NXDetectorDataDoubleAppenderWithUnitSupport("real_count_time", self.total_shutter_open_times[self.point_number-1], "s"))
        if self.yContinuous:
            y_pos = float(self.y.getPosition())
            if (y_pos < self.y_open and y_pos > self.y_close) and self.detectorIsAcquiring and not self.shutterAlreadyOpen:
                self.openShutter()
                self.start_time = time.time()
                self.shutterAlreadyOpen = True
                print("Open shutter at %f" % self.start_time)
            elif (y_pos > self.y_open or y_pos < self.y_close or not self.detectorIsAcquiring) and self.shutterAlreadyOpen:
                self.closeShutter()
                self.end_time = time.time()
                self.shutterAlreadyOpen = False
                print("Close shutter at %f" % self.end_time)
                print("shutter opening time is %f" % (self.end_time - self.start_time))
                self.total_shutter_open_time += (self.end_time - self.start_time)
                if not self.detectorIsAcquiring:
                    self.total_shutter_open_times.append(self.total_shutter_open_time)
                    print("Total shutter opening time for point %d is %f" % (self.point_number, self.total_shutter_open_time))
                    self.afterCurrentPointCollected()
                    # self.appenders.append(NXDetectorDataDoubleAppenderWithUnitSupport("real_count_time", self.total_shutter_open_times[self.point_number-1], "s"))

    def afterCurrentPointCollected(self):
        lastPointRealCountTimes = []
        for each in self.total_shutter_open_times:
            lastPointRealCountTimes.append(each)
        self.lastPointRealCountTimeTuple = tuple(lastPointRealCountTimes)
    
    def getRealCountTime(self):
        return self.lastPointRealCountTime
    
    def setRealCountTime(self, t):
        self.lastPointRealCountTime = t
           
    def moveMotorsWhileControlShutter(self, continuous_move_motor, continuous_move_motor_start, continuous_move_motor_end, step_move_motor, step_move_motor_positions):
        t = currentThread()
        step_move_motor_name = step_move_motor.getName()
        continuous_move_motor_name = continuous_move_motor.getName()
        for index, motor_pos in enumerate(step_move_motor_positions[self.step_motor_pos_index:]):
            if getattr(t, "do_stop", False): #support early stop of this thread
                print("this thread's do_stop is set to True before move step motor %s" % step_move_motor.getName())
                break
            print("\nMove motor '%s' to %f" % (step_move_motor_name, motor_pos))
            step_move_motor.moveTo(motor_pos)
            if index % 2 == 0:
                target_position = continuous_move_motor_end
            else:
                target_position = continuous_move_motor_start
            print("Start moving motor '%s' to %f" % (continuous_move_motor_name, target_position))
            continuous_move_motor.asynchronousMoveTo(target_position)
            time.sleep(0.1) #give motor chance to update its status
            while continuous_move_motor.isBusy():
                if getattr(t, "do_stop", False): # scan aborted by users
                    self.closeShutter()
                    self.end_time = time.time()
                    break
                self.shutterControl()
            self.step_motor_pos_index = index
            print("motors %s = %f, %s = %f, steps %d/%d done in %s" % 
                  (step_move_motor_name, float(step_move_motor.getPosition()), continuous_move_motor_name, float(continuous_move_motor.getPosition()), index+1, len(step_move_motor_positions), step_move_motor_name))
        InterfaceProvider.getCurrentScanController().requestFinishEarly()
        print("\nAll '%s' sample positions are used up now !" % step_move_motor_name)
        print("\nRequest current scan to finish earlier")
        if self.shutterAlreadyOpen:
            self.closeShutter()
            self.end_time = time.time()
            self.shutterAlreadyOpen = False
            print("\nClose shutter at %f" % self.end_time)
            print("shutter opening time is %f" % (self.end_time - self.start_time))
            self.total_shutter_open_time += (self.end_time - self.start_time)
            self.total_shutter_open_times.append(self.total_shutter_open_time)
            print("Total shutter opening time for point %s is %f" % (self.point_number, self.total_shutter_open_time))
            self.afterCurrentPointCollected()
            # self.appenders.append(NXDetectorDataDoubleAppenderWithUnitSupport("real_count_time", self.total_shutter_open_times[self.point_number-1], "s"))
        print("\nPlease wait for current exposure for point %d to complete\n" % self.point_number)


    def atPointStart(self):
        time.sleep(3)
        

    def atPointEnd(self):
        time.sleep(3)
        self.point_number += 1 
        
    # implement NXCollectionStrategyPlugin interface
    def getAcquireTime(self):
        return self.ad_base.getAcquireTime()

    def getAcquirePeriod(self):
        return self.ad_base.getAcquirePeriod()

    def configureAcquireAndPeriodTimes(self, t):
        pass #this method deprecated

    def prepareForCollection(self, collection_time, number_images_per_cllection, scan_info):
        print("\nPrepare for collection")
        self.total_shutter_open_times = [] #to capture shutter opening times per detector acquiring
        self.total_shutter_open_time = 0.0
        self.step_motor_pos_index = 0
        self.appenders = []
        self.point_number = 0
        self.lastPointRealCountTimeTuple = ()
        self.detecrmineControlPositions()
        print("Create motor and shutter control thread")
        if self.zContinuous:
            self.motion_shutter_control_thread = Thread(target = self.moveMotorsWhileControlShutter, name="y_step_z_continue", args = (self.z, self.z_start, self.z_end, self.y, self.y_positions))
        if self.yContinuous:
            self.motion_shutter_control_thread = Thread(target = self.moveMotorsWhileControlShutter, name="z_step_y_continue", args = (self.y, self.y_start, self.y_end, self.z, self.z_positions))
        self.motion_shutter_control_thread.do_stop = False # used to abort earlier
        erio() # control fast shutter separately, not as part of detector
        fastshutter.moveTo("Closed") #ensure shutter is closed before collection
        self.shutterAlreadyOpen = False
        print("Configure detector %s" % (self.det.getName()))
        self.cs.getDecoratee().getDecoratee().getDecoratee().setReadAcquisitionTime(True)
        self.cs.prepareForCollection(collection_time, number_images_per_cllection, scan_info) #this configures the actual detector
        print("Setup detector acquiring state observer")
        self.observer_added = False
        self.state_observable = self.ad_base.createAcquireStateObservable()
        self.state_observer = GeneralObserver("state_observer", self.update_motor_shutter_control)
        self.state_observable.addObserver(self.state_observer)
        print("Move motors to start point: y = %f, z = %f" % (self.y_start, self.z_start))
        self.y.asynchronousMoveTo(self.y_start)
        self.z.asynchronousMoveTo(self.z_start)
        self.scanInfo = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation()
        self.scan_number = self.scanInfo.getScanNumber()        
        self.y.waitWhileBusy()
        self.z.waitWhileBusy()
        motor_speed = self.setMotorSpeed()
        if self.zContinuous:
            print("Motor speed is %f for %s" % (motor_speed, self.z.getName()))
        if self.yContinuous:
            print("Motor speed is %f for %s" % (motor_speed, self.y.getName()))
        print("Prepare for collection completed\n")            

    def collectData(self):
        self.ad_base.startAcquiring()
        print("\nStart detector '%s' acquiring ..." % self.det.getName())

    def getStatus(self):
        # return self.det.getCollectionStrategy().getStatus()
        return self._myStatus

    def waitWhileBusy(self):
        # self.det.getCollectionStrategy().waitWhileBusy()
        while self.getStatus() == Detector.BUSY:
            time.sleep(0.1)

    def getNumberImagesPerCollection(self, t):
        return 1


    #implement PositionInputStream interface
    def read(self, max_to_read):
        # while len(self.total_shutter_open_times) == self.point_number:
        #     time.sleep(1)
        # appenders = []
        # print("\nReal actual exposure time for point %d is %f \n" % (self.point_number, self.total_shutter_open_times[self.point_number]))
        # self.appenders.append(NXDetectorDataDoubleAppender("real_count_time", self.total_shutter_open_times))
        self.appenders.append(NXDetectorDataDoubleAppender(self.getInputStreamNames(), [self.getAcquireTime(), self.getRealCountTime()]))
        return self.appenders
    
    
    # implement NXPluginBase interface
    def getName(self):
        return self.myname

    def completeCollection(self):
        self.motion_shutter_control_thread.do_stop = True
        print("completeCollection called ...")
        print("Stop detector acquiring")
        self.ad_base.stopAcquiring()
        self.closeShutter()
        print("Stop motors %s and %s" % (self.y.getName(), self.z.getName()))
        self.y.stop()
        self.z.stop()
        self.restoreMotorSpeed()
        if self.state_observer and self.state_observable:
            print("Remove detector acquiring state observer")
            self.state_observable.removeObserver(self.state_observer)
            self.state_observer = None
            self.state_observable = None
        self.cs.completeCollection()
        print("Exit completeCollection method\n")
                        
    def atCommandFailure(self):
        print("atCommandFailure called!")
        self.completeCollection()

    def stop(self):
        self.motion_shutter_control_thread.do_stop = True
        print("Stop called ...")
        print("Abort detector acquiring")
        self.ad_base.stopAcquiring()
        self.closeShutter()
        print("Stop motors %s and %s" % (self.y.getName(), self.z.getName()))
        self.y.stop()
        self.z.stop()
        self.restoreMotorSpeed()
        if self.state_observer and self.state_observable:
            print("Remove detector acquiring state observer")
            self.state_observable.removeObserver(self.state_observer)
            self.state_observer = None
            self.state_observable = None
        self.cs.completeCollection()
        print("Exit stop method\n")
            
    def getInputStreamNames(self):
        inputnames = self.cs.getInputStreamNames()
        inputnames.append("real_count_time")
        return inputnames
    
    def getInputStreamFormats(self):
        inputformats = self.cs.getInputStreamFormats()
        inputformats.append("%f")
        return inputformats
    

    

        