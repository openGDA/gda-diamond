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
from org.apache.commons.lang3.builder import EqualsBuilder, HashCodeBuilder
from gda.observable import Observer
from threading import Thread, currentThread
from shutters.detectorShutterControl import erio
import time
from gdascripts.utils import frange
from gda.device.detector.nxdata import NXDetectorDataAppender
from gda.data.nexus.extractor import NexusGroupData, NexusExtractor
from java.lang import String  # @UnresolvedImport
from gda.data.nexus.tree import NexusTreeNode
from org.slf4j import LoggerFactory
from gda.jython import JythonServerFacade


logger = LoggerFactory.getLogger(__name__)

class GeneralObserver(Observer):
    def __init__(self, name, update_function):
        self.name =name
        self.updateFunction = update_function # a function point
        
    def update(self, source, change):
        self.updateFunction(source, change)
    
    #both equals and hashCode method required by addIObserver and deleteIOberser in Java observers set.        
    def equals(self, other):
        return EqualsBuilder.reflectionEquals(self, other, True)
      
    def hashCode(self):
        # Apache lang3 org.apache.commons.lang3.builder.HashCodeBuilder
        return HashCodeBuilder.reflectionHashCode(self, True)

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
        '''calculate positions at which motor starts and stops and at which shutther opens and closes
        '''
        self.y_start = self.sampleCentreY - self.sampleSizeY/2
        self.y_open = self.sampleCentreY - self.sampleSizeY/2 + self.beamSizeY
        self.y_close = self.sampleCentreY + self.sampleSizeY/2 - self.beamSizeY
        self.y_end = self.sampleCentreY + self.sampleSizeY/2
        self.z_start = self.sampleCentreZ + self.sampleSizeZ/2
        self.z_open = self.sampleCentreZ + self.sampleSizeZ/2 - self.beamSizeZ
        self.z_close = self.sampleCentreZ - self.sampleSizeZ/2 + self.beamSizeZ 
        self.z_end = self.sampleCentreZ - self.sampleSizeZ/2
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
            print("\ndetector acquire start")
            if not self.motor_shutter_control_thread.isAlive():
                print("Start motion and shutter control thread")
                self.motor_shutter_control_thread.start()
            else:
                print("motion and shutter control thread is already running")
        elif change == 0: #detector exposure completed
            if self.motor_shutter_control_thread.isAlive():
                self.stop_motors_close_shutter_on_acquire_finish()
                print("\ndetector acquire complete\n")
            else:
                print("motion and shutter control thread is not running")
    
    def openShutter(self):
        print("Open fast shutter")
        fastshutter.moveTo("Open")
    
    def closeShutter(self):
        print("Close fast shutter")
        fastshutter.moveTo("Closed")

    def shutterControl(self):
        if self.zContinuous:
            y_pos = float(self.z.getPosition())
            if (y_pos < self.z_open or y_pos > self.z_close) and not self.shutterAlreadyOpen:
                self.openShutter()
                self.start_time = time.time()
                self.shutterAlreadyOpen = True
            elif (y_pos > self.z_open or y_pos < self.z_close) and self.shutterAlreadyOpen:
                self.closeShutter()
                self.end_time = time.time()
                self.shutterAlreadyOpen = False
        if self.yContinuous:
            x_pos = float(self.y.getPosition())
            if (x_pos > self.y_open or x_pos < self.y_close) and not self.shutterAlreadyOpen:
                self.openShutter()
                self.start_time = time.time()
                self.shutterAlreadyOpen = True
            elif (x_pos < self.y_open or x_pos > self.y_close) and self.shutterAlreadyOpen:
                self.closeShutter()
                self.end_time = time.time()
                self.shutterAlreadyOpen = False
               
    def moveMotorsWhileControlShutter(self, continuous_move_motor, continuous_move_motor_start, continuous_move_motor_end, step_move_motor, step_move_motor_positions):
        t = currentThread()
        for index, motor_pos in enumerate(step_move_motor_positions[self.step_motor_pos_index:]):
            if getattr(t, "do_stop", False): #support early stop of this thread
                print("this thread's do_stop is set to True before move step motor %s" % step_move_motor.getName())
                break
            print("\nMove motor '%s' to %f" % (step_move_motor.getName(), motor_pos))
            step_move_motor.moveTo(motor_pos)
            if index % 2 == 0:
                print("Start moving motor '%s' to %f" % (continuous_move_motor.getName(), continuous_move_motor_end))
                continuous_move_motor.asynchronousMoveTo(continuous_move_motor_end)
            else:
                print("Start moving motor '%s' to %f" % (continuous_move_motor.getName(), continuous_move_motor_start))
                continuous_move_motor.asynchronousMoveTo(continuous_move_motor_start)
                time.sleep(0.5) #give motor chance to update its status
            while continuous_move_motor.isBusy():
                if getattr(t, "do_stop", False):
                    self.closeShutter()
                    print("Stop called while '%s' motor is moving" % continuous_move_motor.getName())
                    continuous_move_motor.stop()
                    break
                self.shutterControl()
            print("shutter open time is %f" % (self.end_time - self.start_time))
            self.shutter_open_times.append(self.end_time - self.start_time)
            self.step_motor_pos_index = index
            print("step motor '%s' position at %f, %d steps done, %d steps still available" % (step_move_motor.getName(), float(step_move_motor.getPosition()), index, len(step_move_motor_positions) - index))
        if self.step_motor_pos_index == len(step_move_motor_positions)-1:
            print("\nAll sample positions are used up now !")
            self.closeShutter()
            self.end_time = time.time()
            print("\nRequest current scan to finish earlier")
            JythonServerFacade.getInstance().requestFinishEarly()
            print("Please wait for current exposure for point %d to complete\n" % self.point_number)

    
    # implement NXCollectionStrategyPlugin interface
    def getAcquireTime(self):
        return self.det.getCollectionStrategy().getAcquireTime()

    def getAcquirePeriod(self):
        return self.det.getCollectionStrategy().getAcquirePeriod()

    def configureAcquireAndPeriodTimes(self, t):
        pass #this method deprecated

    def prepareForCollection(self, collection_time, number_images_per_cllection, scan_info):
        print("\nPrepare for collection")
        self.detecrmineControlPositions()
        erio() # control fast shutter separately, not as part of detector
        fastshutter.moveTo("Closed") #ensure shutter is closed before collection
        self.shutterAlreadyOpen = False
        print("Configure detector %s" % (self.det.getName()))
        self.cs.prepareForCollection(collection_time, number_images_per_cllection, scan_info) #this configures the actual detector
        print("Setup detector acquiring state observer")
        self.state_observable = self.ad_base.createAcquireStateObservable()
        self.state_observer = GeneralObserver("state_observer", self.update_motor_shutter_control)
        self.state_observable.addObserver(self.state_observer)
        print("Create motor and shutter control thread")
        if self.zContinuous:
            self.motor_shutter_control_thread = Thread(target = self.moveMotorsWhileControlShutter, name="y_step_z_continue", args = (self.z, self.z_start, self.z_end, self.y, self.y_positions))
        if self.yContinuous:
            self.motor_shutter_control_thread = Thread(target = self.moveMotorsWhileControlShutter, name="z_step_y_continue", args = (self.y, self.y_start, self.y_end, self.z, self.z_positions))
        print("Move motor to start point: y = %f, z = %f" % (self.y_start, self.z_start))
        self.y.asynchronousMoveTo(self.y_start)
        self.z.asynchronousMoveTo(self.z_start)
        self.y.waitWhileBusy()
        self.z.waitWhileBusy()
        self.shutter_open_times = [] #to record shutter opening times
        self.step_motor_pos_index = 0
        self.motor_shutter_control_thread.do_stop = False
        self.accumulated_shutter_open_time_so_far = 0.0
        self.point_number = 0
        motor_speed = self.setMotorSpeed()
        if self.zContinuous:
            print("Motor speed is %f for %s" % (motor_speed, self.z.getName()))
        if self.yContinuous:
            print("Motor speed is %f for %s" % (motor_speed, self.y.getName()))
        print("Prepare for collection completed")
            

    def collectData(self):
        self.point_number += 1
        self.ad_base.startAcquiring()
        print("\nStart detector %s acquiring ..." % self.det.getName())

    def getStatus(self):
        return self.det.getCollectionStrategy().getStatus()

    def waitWhileBusy(self):
        self.det.getCollectionStrategy().waitWhileBusy()

    def getNumberImagesPerCollection(self, t):
        return 1


    #implement PositionInputStream interface
    def read(self, max_to_read):
        appenders = []
        # current_point_number = JythonServerFacade.getInstance().getLastScanDataPoint().getCurrentPointNumber()
        total_shutter_open_time = sum(self.shutter_open_times) - self.accumulated_shutter_open_time_so_far
        self.accumulated_shutter_open_time_so_far =  total_shutter_open_time + self.accumulated_shutter_open_time_so_far
        print("\nTotal shutter open time for point %d is %f \n" % (self.point_number, total_shutter_open_time))
        appenders.append(NXDetectorDataDoubleAppenderWithUnitSupport("total_count_time", total_shutter_open_time, "s"))
        return appenders
    
    
    # implement NXPluginBase interface
    def getName(self):
        return self.myname

    def completeCollection(self):
        self.motor_shutter_control_thread.do_stop = True
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
        self.motor_shutter_control_thread.do_stop = True
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
        return self.cs.getInputStreamNames()
    
    def getInputStreamFormats(self):
        return self.cs.getInputStreamFormats()

    

        