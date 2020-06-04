from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caget
from gdascripts.pd.time_pds import tictoc
from gda.epics import CAClient
import time
from gdascripts.scannable.epics.PvManager import PvManager
import gov.aps.jca.TimeoutException

class AgilentPsuVoltage(ScannableMotionBase):

    """ This is the constructor for the class. """
    def __init__(self, name, pvroot, timeout): #BL16B-EA-PSU-01
        self.name = name
        self.inputNames = [name + '_v']
        self.extraNames = [name + '_i']
        self.outputFormat = ['%6.4f', '%6.4f']

        self.timeout = timeout

        self.pvs = PvManager(['CPCB:SETDEMAND', 'VOLT:MEAS', 'CURR:MEAS'], pvroot)
        self.pvs.configure()

    def asynchronousMoveTo(self, value):
        self.pvs['CPCB:BUSY'].caput(0)
        try:
            self.pvs['CPCB:SETDEMAND'].caput(self.timeout, value)
        except gov.aps.jca.TimeoutException, e:
            raise Exception('Timed out after %fs setting voltage to %f. The voltage has hung at %f, and the current is %f\n*Is the current set too low?*' % ((self.timeout, value) + self.getPosition()))
    def isBusy(self):
        return False # asynchMoveTo Blocks

    def getPosition(self):    
        return float(self.pvs['VOLT:MEAS'].caget()), float(self.pvs['CURR:MEAS'].caget())
    
    
class AgilentPsuCurrent(ScannableMotionBase):

    """ This is the constructor for the class. """
    def __init__(self, name, pvroot, timeout, tolerance = 0.0005): #BL16B-EA-PSU-01
        self.name = name
        self.inputNames = [name + '_i']
        self.extraNames = [name + '_v']
        self.outputFormat = ['%6.4f', '%6.4f']

        self.timeout = timeout
        self.tol = tolerance
        self.time_triggered = None
        self.last_target = None
        self.pvs = PvManager(['VOLT:MEAS', 'CURR:MEAS', 'CURR:SET'], pvroot)
        self.pvs.configure()

    def asynchronousMoveTo(self, value):
        self.pvs['CURR:SET'].caput(value)
        self.time_triggered = time.time()
        self.last_target =  value
    
    def isBusy(self):
        if self.last_target == None:
            return False
        i = (float(self.pvs['CURR:MEAS'].caget()))
        if abs(i - self.last_target) <= self.tol:
            return False
        if (time.time() - self.time_triggered) > self.timeout:
            raise Exception('Timed out after %fs setting current to %f. The current has hung at %f, and the voltage is %f\n*Is the voltage set too low?*' % ((self.timeout, self.last_target) + self.getPosition()))
        return True

    def getPosition(self):
        return float(self.pvs['CURR:MEAS'].caget()), float(self.pvs['VOLT:MEAS'].caget())

