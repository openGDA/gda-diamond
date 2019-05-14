from gda.device.scannable import ScannableBase
from collections import namedtuple
from gda.epics import LazyPVFactory
from gda.epics import PVWithSeparateReadback
import logging
from time import sleep
from uk.ac.diamond.daq.concurrent import Async
from java.lang import String

from contextlib import contextmanager
from functools import wraps

logger = logging.getLogger('gda.lde.robot')

CurrentSample = namedtuple("CurrentSample", "sample state")

VALID_POSITIONS = (2,3,4,5,6,7,9,10,11)

# Job names
RACK_TO_STAGE = 'PICKRACK'
STAGE_TO_RACK = 'PICKSTAGE'
START = 'START'

UNKNOWN = 0
NO_SAMPLE = 1
LOADING = 2
ON_STAGE = 3
UNLOADING = 4

MASKS = {}
# STA1
MASKS['playMode'] = 1<<6
MASKS['teachMode'] = 1<<5
MASKS['safetySpeedOp'] = 1<<4
MASKS['running'] = 1<<3
MASKS['autoMode'] = 1<<2
MASKS['oneCycleMode'] = 1<<1
MASKS['stepMode'] = 1<<0
# STA2
MASKS['servoOn'] = 1<<7
MASKS['errorState'] = 1<<6
MASKS['alarmState'] = 1<<5
MASKS['holdCommand'] = 1<<4
MASKS['holdExternal'] = 1<<3
# 1<<2 is not used
MASKS['holdPanel'] = 1<<1

def needs_safe_to_move(fn):
    @wraps(fn)
    def wrapper(self, *a, **kw):
        if not self.safe_to_move:
            raise ValueError('Could not run while robot is not safe to move')
        return fn(self, *a, **kw)
    return wrapper


# To check
#  - Safe to Move PLC pv - Does it indicate when hutch has been opened?
#  - Monitoring of PVs when used directly from EPICS. Can we still work out where things are. 
#  - RG open? Robot gripper?
#  - Hold = stage grip?
#  - Error code - clear = caput 0?
#  - status 2 0/1 offset? 0-6, 1-7

class LdeRobot(ScannableBase):

    def __init__(self, name, pvroot, valid_positions=VALID_POSITIONS, robot_stage=None):
        """
        Create pv channels for controlling robot
        
        Args:
         - pvroot: Common prefix of robot PVs. eg 'BL11J-EA-ROBOT-01:' including last ':'
         - valid_positions: A list of positions available to the robot
         - robot_stage: (optional) tuples of stage/safe position to move robot into safe position
                 before placing sample. eg ((rxs, -234), (rsy, 0))
        """
        self.name = name
        self.outputFormat = ['%d']
        self._pvroot = pvroot
        self._current_sample = CurrentSample(None, NO_SAMPLE)
        self._valid_positions = valid_positions
        
        if robot_stage is not None:
            self._safe_position = self.get_robot_stage_manager(robot_stage)
        else:
            self._safe_position = null_stage_context()
        
        self._ca_d010 = PVWithSeparateReadback(
            LazyPVFactory.newDoublePV(self._pvroot + 'D010'), # read/write int
            LazyPVFactory.newReadOnlyDoublePV(self._pvroot + 'D010:RBV') # read/write int
        )
        self._ca_control_job = LazyPVFactory.newEnumPV(self._pvroot + 'JOB', String)# enum position
        self._ca_control_start = LazyPVFactory.newIntegerPV(self._pvroot + 'START') # control point? ???
        self._ca_control_servo = LazyPVFactory.newEnumPV(self._pvroot + 'SVON', String) # enum?
        self._ca_status1 = LazyPVFactory.newIntegerPV(self._pvroot + 'STA1') # int
        self._ca_status2 = LazyPVFactory.newIntegerPV(self._pvroot + 'STA2') # int
        self._ca_error_code = LazyPVFactory.newIntegerPV(self._pvroot + 'ERR') # int
        self._ca_safe_to_move = LazyPVFactory.newIntegerPV(self._pvroot + 'IO00010.B0') # int
        self._ca_gripper = LazyPVFactory.newIntegerPV(self._pvroot + 'IO00010.B5') # ? int
        
        self._ca_control_servo.addObserver(self._reset)
        
        self._last_move = None
       
    
    def _move_to(self, sample):
        if sample not in self._valid_positions:
            logger.error('Sample position "%s" is not valid')
            raise ValueError('Position not valid')
        if self._current_sample.sample == sample:
            print 'Sample holder %d already on stage' % sample
            return
        with self._safe_position():
            # Check for current sample
            if self._current_sample.sample is not None:
                # Unload current sample
                self.clearSample()
            # Load new sample
            self.sample_number = sample
            self._run(RACK_TO_STAGE)
            self._current_sample = CurrentSample(sample, ON_STAGE)
         
    def rawAsynchronousMoveTo(self, sample):
        logger.debug('Selecting sample %s', sample)
        # Check valid position
        self._last_move = Async.call(lambda: self._move_to(sample))
        sleep(0.2) # let move start so that waitWhileBusy doesn't return immediately

    def rawGetPosition(self):
        # If sample on stage - return rack number
        if self._current_sample.state not in {UNKNOWN, NO_SAMPLE}:
            return self._current_sample.sample
        return -1
    
    def clearSample(self, rack_position=None):
        # Unload sample to where we think it came from
        if rack_position is None and self._current_sample.sample is None:
            raise ValueError('Cannot determine rack position to unload sample')
        rack_position = rack_position or self._current_sample.sample
        if self._current_sample.state == NO_SAMPLE:
            logger.debug("No sample on stage")
        logger.debug('Clearing current sample to position %s', rack_position)
        self.sample_number = rack_position
        with self._safe_position():
            self._run(STAGE_TO_RACK)
            self._current_sample = CurrentSample(None, NO_SAMPLE)
    
    def isBusy(self):
        return (self._last_move is not None and not self._last_move.isDone()) or self.running
    
    def toFormattedString(self):
        if self._current_sample.state is not UNKNOWN:
            posn = self._current_sample.sample
        else:
            posn = 'UNKNOWN'
        return '{}: {}'.format(self.name, posn)
    
    def start(self):
        logger.debug('Starting robot')
        self._ca_control_servo.putWait('Servo On')
        self._run(START)
    
    def _reset(self, *a): # allow ignored args so it can be used as Observer 
        logger.debug('Reseting known sample')
        # Clear known samples
        self._current_sample = CurrentSample(None, UNKNOWN)
        self._ca_error_code.putNoWait(0)
    
    @property
    def running(self):
        return self._ca_status1.get() & MASKS['running']
    
    @property
    def servoOn(self):
        return self._ca_status2.get() & MASKS['servoOn']
    
    @property
    def error(self):
        if self._ca_status2.get() & MASKS['error']:
            return self._ce_error_code.get()
        
    @property
    def safe_to_move(self):
        return self._ca_safe_to_move.get()
    
    @property
    def sample_number(self):
        return self._ca_d010.get()
    
    @property
    def gripper_open(self):
        return self._ca_gripper.get() == 1
        
    @sample_number.setter
    def sample_number(self, sample):
        logger.debug("Setting d010 sample number to %s", sample)
        self._ca_d010.putWait(float(sample))
        
    # @needs_safe_to_move
    def _run(self, job):
        logger.debug('Running job "%s"', job)
        self._ca_control_job.putWait(job)
        self._ca_control_start.putNoWait(1)
        sleep(5) # Shouldn't affect the run time of this method as robot move will always be > 5s
        logger.debug('Waiting for job to complete')
        while self.running:
            sleep(1)
        

    # This should just be a context manager directly - returning one was only needed
    # before this was an instance method
    def get_robot_stage_manager(self, safe_stage_positions):
        """
        Create a context manager that will move a series of stages to their safe space
    
        Each motor will be moved to its safe position at the start of the context
        and will be returned to its original position at the end of the context.
    
        Args:
         - safe_stage_positions: iterable of (motor, position) pairs
        """
        @contextmanager
        def robot_stage():
            initial_positions = [stage.getPosition() for stage, _ in safe_stage_positions]
            initial_str = ', '.join(str(p) for p in initial_positions)
            logger.debug('Storing current robot stage positions: %s', initial_str)
            moves = Async.submitAll(lambda m=stage, p=safe: m.moveTo(p) for stage, safe in safe_stage_positions)
            moves.get() # Wait for all moves to complete
            self._ca_safe_to_move.waitForValue(lambda x: x==1, 5)
            yield
            logger.debug('Moving robot stages back to previous positions: %s', initial_str)
            moves = Async.submitAll(lambda m=stage[0], p=init: m.moveTo(p) for stage, init in zip(safe_stage_positions, initial_positions))
            moves.get() # Wait for all moves to complete
        return robot_stage

@contextmanager
def null_stage_context():
    yield
