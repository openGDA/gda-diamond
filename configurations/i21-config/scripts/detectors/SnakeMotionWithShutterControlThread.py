'''
a snake path "worker" thread implementation

How to stop / kill a thread

This is accomplished by politely asking the thread to die. The join method of Thread is overridden, 
and before calling the actual join of the parent class, it sets the self.stoprequest attribute, 
which is a threading.Event. The main loop in the thread's run method checks this flag, and exits when it's set. 
You can think of threading.Event as a synchronized boolean flag. 
Keep in mind that the join method is called in the context of the main thread, 
while the body of the run method is executed in the context of the worker thread.

How to safely pass data to a thread and back

This is best done with the help of Queue objects from the Queue module. 
When the worker thread is created, it is given a reference to one queue for input, and one queue for output. 
Queue objects can be safely shared between threads (any amount of threads, actually), and provide a synchronized FIFO queue interface.

Note that such worker threads in Python are only useful if the work they do is not CPU bound.
CPU-bound tasks are not a good fit for Python threads, due to the Global Interpreter Lock (GIL). 
Parallel computations in Python should be done in multiple processes, not threads.

Created on Mar 3, 2023

@author: fy65
'''

import time
import threading
from gdaserver import fastshutter  # @UnresolvedImport
from detectors.generic_observer import GeneralObserver
from org.slf4j import LoggerFactory
from gda.jython import InterfaceProvider
from gda.observable import ObservableUtil

logger = LoggerFactory.getLogger(__name__)

class SnakePathWithShutterControlThread(threading.Thread):
    """ A worker thread that moves 2 motors in a snake path - one moves in step while shutter is closed, 
    the other moves continuously within which shutter is opened between 2 specified positions.  

    accumulated shutter opening time during each detector exposure time is placed into the Queue passed in count_time_q.

    Ask the thread to stop by calling its join() method.
    """
    def __init__(self, continuous_move_motor, continuous_move_motor_start, continuous_move_motor_end, shutter_open,
                  shutter_close, step_move_motor, step_move_motor_positions, adbase, output_q, z_cont, y_cont, reverse, observer):
        super(SnakePathWithShutterControlThread, self).__init__()
        self.continuous_move_motor = continuous_move_motor
        self.continuous_move_motor_start = continuous_move_motor_start
        self.continuous_move_motor_end = continuous_move_motor_end
        self.shutter_open = shutter_open
        self.shutter_close = shutter_close
        self.step_move_motor = step_move_motor
        self.step_move_motor_positions = step_move_motor_positions
        self.step_move_motor_positions_reversed = step_move_motor_positions[:]
        self.step_move_motor_positions_reversed.reverse()
        self.ad_base = adbase
        self.count_time_q = output_q
        self.yContinuous = y_cont
        self.zContinuous = z_cont
        self.path_reverse_enabled = reverse
        self.stoprequest = threading.Event()
        self.state_observer = None
        self.state_observable = None
        self.firstTimeRunThis = True
        self.observableUtil = ObservableUtil()
        self.observer = observer

    def run(self):
        while not self.stoprequest.isSet():
            if self.firstTimeRunThis:
                self.shutterAlreadyOpen = False
                self.moveMotorsWhileControlShutter(self.step_move_motor_positions)
                self.firstTimeRunThis = False
            else:
                logger.info("forward move through '{}' positions", self.step_move_motor.getName())
                self.moveMotorsWhileControlShutter(self.step_move_motor_positions)
            if self.path_reverse_enabled:
                logger.info("backward move through '{}' positions", self.step_move_motor.getName())
                self.moveMotorsWhileControlShutter(self.step_move_motor_positions_reversed)
            else:
                self.continuous_move_motor.moveTo(self.continuous_move_motor_start)
                logger.info("repeat move through '{}' positions", self.step_move_motor.getName())
                self.moveMotorsWhileControlShutter(self.step_move_motor_positions)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(SnakePathWithShutterControlThread, self).join(timeout)

    def addObserver(self, ad_base):
        logger.debug("Setup detector acquiring state observer 2")
        self.state_observable = ad_base.createAcquireStateObservable()
        self.state_observer = GeneralObserver("state_observer2", self.update_motor_shutter_control)
        self.state_observable.addObserver(self.state_observer)

        self.observableUtil.addObserver(self.observer)

    def removeObserver(self):
        if self.state_observer and self.state_observable:
            logger.debug("Remove detector acquiring state observer 2")
            self.state_observable.removeObserver(self.state_observer)
            self.state_observer = None
            self.state_observable = None

        self.observableUtil.removeObserver(self.observer)

    def update_motor_shutter_control(self, source, change):
        '''handling detector acquiring event
        '''
        if change == 1: #detector exposure started
            self.detectorIsAcquiring = True
            self.total_shutter_open_time = 0.0
        elif change == 0: #detector exposure completed
            self.detectorIsAcquiring = False

    def openShutter(self):
        fastshutter.moveTo("Open")
        self.start_time = time.time()
        self.shutterAlreadyOpen = True
        logger.debug("Open  shutter at {}", self.start_time)

    def closeShutter(self):
        fastshutter.moveTo("Closed")
        self.end_time = time.time()
        self.shutterAlreadyOpen = False
        logger.debug("Close shutter at {}", self.end_time)
        logger.debug("shutter opening time is {}", (self.end_time - self.start_time))
        self.total_shutter_open_time += (self.end_time - self.start_time)
        if not self.detectorIsAcquiring:
            self.count_time_q.put(self.total_shutter_open_time)
            logger.debug("Total shutter opening time for this point is {}", (self.total_shutter_open_time))

    def shutterControl(self):
        if self.zContinuous:
            z_pos = float(self.continuous_move_motor.getPosition())
            if (z_pos > self.shutter_open and z_pos < self.shutter_close) and self.detectorIsAcquiring and not self.shutterAlreadyOpen:
                self.openShutter()
            elif (z_pos < self.shutter_open or z_pos > self.shutter_close or not self.detectorIsAcquiring) and self.shutterAlreadyOpen:
                self.closeShutter()
        if self.yContinuous:
            y_pos = float(self.continuous_move_motor.getPosition())
            if (y_pos < self.shutter_open and y_pos > self.shutter_close) and self.detectorIsAcquiring and not self.shutterAlreadyOpen:
                self.openShutter()
            elif (y_pos > self.shutter_open or y_pos < self.shutter_close or not self.detectorIsAcquiring) and self.shutterAlreadyOpen:
                self.closeShutter()

    def moveMotorsWhileControlShutter(self, step_move_motor_positions):
        step_move_motor_name = self.step_move_motor.getName()
        continuous_move_motor_name = self.continuous_move_motor.getName()
        for index, motor_pos in enumerate(step_move_motor_positions):
            if self.stoprequest.isSet(): #support early stop of this thread
                logger.debug("stop requested before move step motor {}", step_move_motor_name)
                break

            # make sure detector acquire started before continuous motion path
            i = 1
            while not self.detectorIsAcquiring and i < 50:
                time.sleep(0.1)
                i = i + 1
            # if after wait 5 second, force start detector
            scan_data_point = InterfaceProvider.getScanDataPointProvider().getLastScanDataPoint()
            if scan_data_point:
                number_of_points = scan_data_point.getNumberOfPoints()
                current_point_number = scan_data_point.getCurrentPointNumber()
                logger.debug("point {}/{} is collecting", current_point_number, number_of_points)
                if not self.stoprequest.isSet() and (current_point_number + 1) != number_of_points and not self.detectorIsAcquiring: # not the last scan data point, detector should acquire at here
                    logger.warn("detector should be acquiring by now, but it doesn't, so send {} to {}", self.detectorIsAcquiring, self.observer.name)
                    self.observableUtil.notifyIObservers(self.observableUtil, self.detectorIsAcquiring)

            if self.shutterAlreadyOpen:
                logger.error("Shutter should be closed during '{}' motion", step_move_motor_name)

            logger.debug("Move motor '{}' to {}", step_move_motor_name, motor_pos)
            self.step_move_motor.moveTo(motor_pos)

            if index % 2 == 0:
                target_position = self.continuous_move_motor_end
            else:
                target_position = self.continuous_move_motor_start
            logger.debug("Start moving motor '{}' to {}", continuous_move_motor_name, target_position)
            self.continuous_move_motor.asynchronousMoveTo(target_position)
            time.sleep(0.1) #give motor chance to update its status
            while self.continuous_move_motor.isBusy():
                if self.stoprequest.isSet(): # scan aborted by users
                    self.closeShutter()
                    break
                self.shutterControl()

            logger.debug("motors %s = %f, %s = %f, steps %d/%d done in %s" % 
                  (step_move_motor_name, float(self.step_move_motor.getPosition()), continuous_move_motor_name, float(self.continuous_move_motor.getPosition()), index+1, len(step_move_motor_positions), step_move_motor_name))

        scan_data_point = InterfaceProvider.getScanDataPointProvider().getLastScanDataPoint()
        if scan_data_point:
            number_of_points = scan_data_point.getNumberOfPoints()
            current_point_number = scan_data_point.getCurrentPointNumber()   
            if not self.stoprequest.isSet() and (current_point_number + 1) != number_of_points: # not the last scan data point
                logger.info("All '{}' sample positions are used up now !", step_move_motor_name)
        if index % 2 == 0: #swap start and end points
            continuous_end = self.continuous_move_motor_end
            self.continuous_move_motor_end = self.continuous_move_motor_start
            self.continuous_move_motor_start = continuous_end

