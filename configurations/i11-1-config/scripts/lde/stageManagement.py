from uk.ac.diamond.daq.concurrent import Async
from java.util.concurrent import ExecutionException
from gdaserver import ms1, ms2, ms3, ms4, ss1, ss2, ss3, ss4, ss5, rs
from gdaserver import detectorZ

import logging

logger = logging.getLogger("stageManager")

ALL_STAGES = [ms1, ms2, ms3, ms4, ss1, ss2, ss3, ss4, ss5, rs]
#ALL_STAGES.remove(ss5) # Only for testing

def parkStages(*stages):
    logger.debug('Parking stages: %s', ', '.join(s.name for s in stages))
    moves = [Async.submit(lambda s=stage:s.XMotor(s.parkPosition)) for stage in stages]
    waitForAll(moves)
    logger.debug('Stages parked')

def engageStages(*stages):
    logger.debug('Engaging stages: %s', ', '.join(s.name for s in stages))
    moves = [Async.submit(lambda s=stage:s.XMotor(s.engagePosition)) for stage in stages]
    waitForAll(moves)
    logger.debug('Stages engaged')

def parkAllStages():
    logger.info('Parking all stages')
    parkStages(*ALL_STAGES)

def engageUpTo(stage):
    if stage not in ALL_STAGES:
        raise ValueError('stage is not recognised')
    logger.debug('Engaging up to stage %s', stage.name)
    idx = ALL_STAGES.index(stage) + 1
    stages_to_park = [st for st in ALL_STAGES[idx:] if not st.isParked()]
    parkStages(*stages_to_park)

    logger.debug('Moving detector to %d', stage.detectorPosition)
    detectorZ.moveTo(stage.detectorPosition)
    logger.debug('Detector move complete')

    engages = [st for st in ALL_STAGES[:idx]]
    engageStages(*engages)

def waitForAll(moves):
    for move in moves:
        try:
            move.get()
        except ExecutionException as ee:
            logger.error("Error waiting for stages to move", exc_info=True)
            raise

