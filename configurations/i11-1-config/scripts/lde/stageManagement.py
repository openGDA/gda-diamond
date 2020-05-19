from uk.ac.diamond.daq.concurrent import Async
from java.util.concurrent import ExecutionException
from gdaserver import ms1, ms2, ms3, ms4, ss1, ss2, ss3, ss4, ss5, rs

import logging

logger = logging.getLogger("stageManager")

ALL_STAGES = [ms1, ms2, ms3, ms4, ss1, ss2, ss3, ss4, ss5, rs]
#ALL_STAGES.remove(ss5) # Only for testing


def parkStages(*stages):
    moves = [Async.submit(lambda s=stage:s.XMotor(s.parkPosition)) for stage in stages]
    waitForAll(moves)
            
def parkAllStages():
    parkStages(*ALL_STAGES)
    
def engageUpTo(stage):
    idx = ALL_STAGES.index(stage) + 1
    moves = [Async.submit(lambda s=stage:s.XMotor(s.engagePosition)) for stage in ALL_STAGES[:idx]]
    moves.extend([Async.submit(lambda s=stage:s.XMotor(s.parkPosition)) for stage in ALL_STAGES[idx:] if not stage.isParked()])
    waitForAll(moves)
    
    
def waitForAll(moves):
    for move in moves:
        try:
            move.get()
        except ExecutionException as ee:
            logger.error("Error waiting for stages to move", exc_info=True)
            raise
    