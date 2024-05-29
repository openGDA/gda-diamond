from gda.device.scannable.zebra import ZebraQexafsScannable
from gda.device.scannable import ScannableMotor, ScannableMotionBase
from time import sleep
import math

# Import cvscan to make it easier to run ContinuousScans
from gda.jython.commands.ScannableCommands import cv as cvscan
vararg_alias("cvscan")

# Class for I18 to allow them to reuse the B18 position based continuous scannable classes :
# - Use dummy implementation for 'energy control' related functions
# - Motor control uses keV energy units -> override rawGetCurrentPosition to return energy in eV
#    and asynchronousMoveTo to convert energy from eV to keV,
# - Override performContinuousMove to recalculate desiredSpeed to motor units (i.e. kev per second,
# not degrees per second)
# 16/1/2024

class QexafsTest(ZebraQexafsScannable):
    
    def toggleEnergyControl(self):
        pass

    def stopStartEnergyControl(self):
        pass
    
    def setEnergySwitchOn(self):
        pass

    # Return current position in eV
    def rawGetPosition(self):
        current_position_kev = super(QexafsTest,self).rawGetPosition()
        # print(current_position_kev)
        return float(current_position_kev)*1000
    
    def asynchronousMoveTo(self, position_ev):
        position_kev = float(position_ev)/1000.0
        print(position_kev)
        super(QexafsTest, self).asynchronousMoveTo(position_kev)
    
    def setMaxSpeed(self, max_speed):
        self.maxSpeed = max_speed
        
    def prepareForContinuousMove(self):
         # need to reset zebra before trying to configure it (seems to not disarm properly due to stuck 'point download')
        zebra = self.getZebraDevice()
        zebra.reset()
        
        #wait for reset to finish!
        sleep(2)
        
        # These are not (currently) set in QexafsZebraScannable
        # (but they are shared between time and position based trigger sources!)
        zebra.setPCPulseWidth(1e-5) # width of each position trigger
        zebra.setPCPulseMax(10000)  # max number of position trigger pulses to capture
        
        super(QexafsTest, self).prepareForContinuousMove()
        
    def performContinuousMove(self):
        # set the motor speed to the required scan speed (kev per second)
        self.desiredSpeed = 1e-3*math.fabs(self.continuousParameters.getEndPosition() - self.continuousParameters.getStartPosition())//self.continuousParameters.getNumberDataPoints()
        super(QexafsTest, self).performContinuousMove()
        
#from gda.util import CrystalParameters
#CrystalParameters.CrystalSpacing.Si_111.getLabel()

zebra = zebraContinuousMoveController.getZebra()

qexafs_test = QexafsTest()
qexafs_test.setZebraDevice(zebra)
qexafs_test.setPcEncType(3) # encoder 4

qexafs_test.setAccelPV("BL18I-MO-DCM-01:ENERGY.ACCL") 
qexafs_test.setXtalSwitchPV("BL18I-MO-DCM-01:MP:X:SELECT") # Crystal type PV (Si311 or Si111)
qexafs_test.setBraggMaxSpeedPV("BL18I-MO-DCM-01:ENERGY.VMAX")
qexafs_test.setBraggCurrentSpeedPV("BL18I-MO-DCM-01:ENERGY.VELO")
qexafs_test.setEnergySwitchPV("nothing")

# set motor object to control energy motor (BL18I-MO-DCM-01:ENERGY)
qexafs_test.setMotor(sc_energy_motor.getMotor())
# qexafs_test.setMaxSpeed(1) # can also set max speed - kev per second - if don't want to use the value from the motor record

qexafs_test.setName("qexafs_test")
qexafs_test.setOutputFormat(["%7.7g"])  # extra decimal places
qexafs_test.configure()

# call to set flag to indicate epics channels have been configured
qexafs_test.initializationCompleted()


from gda.device.scannable import DummyScannable
dummy_scannable = DummyScannable()
dummy_scannable.setName("dummy_scannable")
dummy_scannable.configure()

from uk.ac.gda.server.exafs.epics.device.scannable import QexafsTestingScannable
cont_scannable = QexafsTestingScannable()
cont_scannable.setName("cont_scannable")
cont_scannable.setDelegateScannable(dummy_scannable)
cont_scannable.setMaxMotorSpeed(1000)
cont_scannable.configure()

from gda.scan import ContinuousScan

def run_tfg_continuous_scan(num_points, scan_time=5, internal_trigger=False) :
    """
        Run a continuous scan using Tfg (qexafs_counterTimer01) and a 'dummy' motor.
        Parameters : 
            num_points - number of frames of data to collect
            scan_time  - how long the scan should take to run (seconds). Optional, default = 5 seconds)
            internal_trigger - whether each frame is triggered internally. Optional, default = False.
                               If set to False, Tfg will wait for external trigger before collecting each frame.
                               (Use qexafs_counterTimer01.setTtlSocket(..) to set the Tfg TTL port to use for triggers)
    """
    qexafs_counterTimer01.setUseInternalTriggeredFrames(internal_trigger)
    sc=ContinuousScan(cont_scannable, 0, num_points, num_points, scan_time, [qexafs_counterTimer01])
    sc.runScan()
  
print("Adding 'run_tfg_continuous_scan' function. Use help(run_tfg_continuous_scan) for more info. ")

