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

logger = logging.getLogger('gda.i13.robot')

CurrentSample = namedtuple("CurrentSample", "sample state")

VALID_POSITIONS = (2,3,4,5,6,7,9,10,11)

#BL13I-MO-ROBOT-01:JOBTGT
#    Native data type: DBF_ENUM
#    Request type:     DBR_CTRL_ENUM
#    Element count:    1
#    Value:            SMP_TO_HTL
#    Status:           NO_ALARM
#    Severity:         NO_ALARM
#    Enums:            ( 6)
#                      [ 0] NOP
#                      [ 1] RECOVER_TO_HOME
#                      [ 2] HTL_TO_SMP
#                      [ 3] SMP_EXCHANGE
#                      [ 4] SMP_TO_HTL
#                      [ 5] DISPOSE

# Job names
JOB_NOP = 'NOP'
JOB_RECOVER_TO_HOME = 'RECOVER_TO_HOME'
JOB_HTL_TO_SMP = 'HTL_TO_SMP'
JOB_SMP_EXCHANGE = 'SMP_EXCHANGE'
JOB_SMP_TO_HTL = 'SMP_TO_HTL'
JOB_DISPOSE = 'DISPOSE'
#JOB_GO_HOME = 'GO_HOME'

START_CURRENT_JOB = 'START'


class RoboSampleChanger():

    def __init__(self, name, pvroot='BL13I-MO-ROBOT-01:', auto_start_jobs=True, robot_stage=None):
        """
        Create pv channels for controlling robot
        
        Args:
         - pvroot: Common prefix of robot PVs. eg 'BL11J-EA-ROBOT-01:' including last ':'
         - valid_positions: A list of positions available to the robot
         - robot_stage: (optional) tuples of stage/safe position to move robot into safe position
                 before placing sample. eg ((rxs, -234), (rsy, 0))
        """
        self.name = name
        self._pvroot = pvroot
        self.auto_start_jobs = auto_start_jobs
        self._current_sample = CurrentSample(None, NO_SAMPLE)
        
        #self._ca_d010 = PVWithSeparateReadback(
        #    LazyPVFactory.newDoublePV(self._pvroot + 'D010'), # read/write int
        #    LazyPVFactory.newReadOnlyDoublePV(self._pvroot + 'D010:RBV') # read/write int
        #)
                
        self._ca_control_job = LazyPVFactory.newEnumPV(self._pvroot + 'JOBTGT', String)# enum position
        self._ca_control_start = LazyPVFactory.newIntegerPV(self._pvroot + 'START') # control point? ???
        self._ca_control_servo = LazyPVFactory.newEnumPV(self._pvroot + 'SVON', String) # enum?
        self._ca_status1 = LazyPVFactory.newIntegerPV(self._pvroot + 'STA1') # int
        self._ca_status2 = LazyPVFactory.newIntegerPV(self._pvroot + 'STA2') # int
        self._ca_error_code = LazyPVFactory.newIntegerPV(self._pvroot + 'ERR') # int
        #self._ca_safe_to_move = LazyPVFactory.newIntegerPV(self._pvroot + 'IO00010.B0') # int
        #self._ca_gripper = LazyPVFactory.newIntegerPV(self._pvroot + 'IO00010.B5') # ? int
        
        #self._ca_control_servo.addObserver(self._reset)
        
        #self._last_move = None
        
    def _run(self, job):
        logger.debug('Running job "%s"', job)
        self._ca_control_job.putWait(job)
        if not self.auto_start_jobs:
            self._ca_control_start.putNoWait(1)
        sleep(5) # Shouldn't affect the run time of this method as robot move will always be > 5s
        logger.debug('Waiting for job to complete')
        while self.running:
            sleep(1)

