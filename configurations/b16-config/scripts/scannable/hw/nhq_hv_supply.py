from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caget
from gdascripts.pd.time_pds import tictoc
from gda.epics import CAClient
import time
from gdascripts.scannable.epics.PvManager import PvManager
import gov.aps.jca.TimeoutException

from gda.epics import LazyPVFactory
from gda.epics import Predicate

DELTA = 1

class NhQHighVoltage(ScannableMotionBase):

    """'BL16B-EA-ISEG-01:PSU1:
    """
    def __init__(self, name, pvroot, timeout): #BL16B-EA-PSU-01
        self.name = name
        self.inputNames = [name + '_v']
        self.extraNames = [name + '_i']
        self.outputFormat = ['%6.4f', '%6.4f']

        self.timeout = timeout

        self.pv_set_v1_demand = LazyPVFactory.newNoCallbackFloatPV(pvroot + 'SET_V1_DEMAND')
        self.pv_v1_set = LazyPVFactory.newReadOnlyFloatPV(pvroot + 'V1_SET')
        self.pv_v1_actual = LazyPVFactory.newReadOnlyFloatPV(pvroot + 'V1_ACTUAL')
        self.pv_i1_actual = LazyPVFactory.newReadOnlyFloatPV(pvroot + 'I1_ACTUAL')
        
        
    def asynchronousMoveTo(self, value):
        pass
   
    def isBusy(self):
        return False # asynchMoveTo Blocks

    def getPosition(self):    
        return float(self.pv_v1_actual.get()), float(self.pv_i1_actual)
    
    
    
    
class Equals(Predicate):
    
    def __init__(self, target):
        self.target = float(target)

    def apply(self, actual): #@ReservedAssignment
        return abs(float(actual) - self.target) < DELTA
