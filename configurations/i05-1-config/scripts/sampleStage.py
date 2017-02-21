'''
Script to safely move the sample stage to predefined positions

This is operating on the 'ss' motors i.e the underlying real axis not the coordinate system 'sm' motors.

It takes care of moving the axis in the correct order and setting soft limits as appropriate for each case.

All position values are in microns. Note the EPICS motors (and soft limits) operate in mm.

Currently the supported positions are:
- Transfer
- Measurement
'''


from time import sleep
from org.slf4j import LoggerFactory


class SampleStageMovements():
        
    def __init__(self):
        self.logger = LoggerFactory.getLogger('sampleStage.py') #@UndefinedVariable
        self.logger.debug('Initialised SampleStageMovements')
   
    
    def toTransfer(self):
        self.logger.info('Moving sample stage to transfer position...')
        print 'Moving sample stage to transfer position...'
        
        # Transfer positions
        safe_z = 3100 # um The position to safely align x and y with the pins (move away from optics)
        transfer_x = 9.0 # um
        transfer_y = 5220.0 # um
        transfer_z = 6800.0 # um
        transfer_pins_tolerance = 25 # um The soft limits are set +- this value when the stage is on the pins 
        transfer_azi = 0.0 # deg
        transfer_polar = 0.0 # deg
        
        # Move z away from the optics where it should be safe to move x and y (blocking)
        if (ssz.getPosition() > transfer_z - transfer_pins_tolerance):
            self.logger.error('Sample stage is already in transfer position (ssz > {})', transfer_z - transfer_pins_tolerance)
            print 'Sample stage is already in transfer position ( ssz >', transfer_z - transfer_pins_tolerance, ')'
            return

        ssz.moveTo(safe_z)
        
        # Move the stage to the position aligned in front of the transfer pins
        ssx.asynchronousMoveTo(transfer_x)
        ssy.asynchronousMoveTo(transfer_y)
        
        # Move the rotations to the transfer positions
        smazimuth.asynchronousMoveTo(transfer_azi)
        # smpolar.asynchronousMoveTo(transfer_polar) Not moving polar for the time being
        
        # Wait for those moves to finish
        self.waitWhileStageIsMoving()
        
        # Change EPICS soft limits while on the pins in mm +-0.01 mm there is a little movement allowed
        ssx.getMotor().setMinPosition((transfer_x - transfer_pins_tolerance)/1000.0)
        ssx.getMotor().setMaxPosition((transfer_x + transfer_pins_tolerance)/1000.0)
        ssy.getMotor().setMinPosition((transfer_y - transfer_pins_tolerance)/1000.0)
        ssy.getMotor().setMaxPosition((transfer_y + transfer_pins_tolerance)/1000.0)
        
        # Change z soft limit to allow movement onto pins
        ssz.getMotor().setMaxPosition((transfer_z + transfer_pins_tolerance)/1000.0)
        
        # Move z onto pins (blocking)
        ssz.moveTo(transfer_z)
        
        self.logger.info('Sample stage is in transfer position')
        print 'Sample stage is in transfer position'


    def toMeasuring(self):
        self.logger.info('Moving sample stage to measuring position...')
        print 'Moving sample stage to measuring position...'
        
        # Measuring positions
        measuring_x = 140.0 # um
        measuring_x_min = -7000.0 # um
        measuring_x_max = 6500.0 # um
        measuring_y = 5720.0 # um
        measuring_y_min = -7000.0 # um
        measuring_y_max = 6500.0 # um
        measuring_z = 3100.0 # um
        measuring_z_max = 3200.0 # um This is the max z where x and y can move freely without touching the pins
        measuring_azi = 0.0 # deg
        measuring_polar = 0.0 # deg
        
        # Move z off the pins (blocking)
        ssz.moveTo(measuring_z)
        
        # Set z soft limit to prevent collisions with the pins
        ssz.getMotor().setMaxPosition(measuring_z_max/1000.0)
        
        # Change EPICS soft limits (in mm) to allow motion now clear of the pins
        ssx.getMotor().setMinPosition(measuring_x_min/1000.0)
        ssx.getMotor().setMaxPosition(measuring_x_max/1000.0)
        ssy.getMotor().setMinPosition(measuring_y_min/1000.0)
        ssy.getMotor().setMaxPosition(measuring_y_max/1000.0)
        
        # Move x and y simultaneously to centre the sample in the beam
        ssx.asynchronousMoveTo(measuring_x)
        ssy.asynchronousMoveTo(measuring_y)
        self.waitWhileStageIsMoving() # Wait until the stage is finished
        
        self.logger.info('Sample stage is in measuring position')
        print 'Sample stage is in measuring position'
        
    def waitWhileStageIsMoving(self):
        self.logger.debug('Waiting for sample stage to finish moving...')
        while(ssx.isBusy() or ssy.isBusy() or ssz.isBusy() or smazimuth.isBusy() or smpolar.isBusy()):
            sleep(0.1) # Wait for 0.1 secs then check again (EPICS polling is 10 Hz)
        self.logger.debug('Sample stage finished moving')


# Instantiate a sampleStage object in the global namespace
sampleStage = SampleStageMovements()
